#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python310Full -p python310Packages.pandas

import calendar
from datetime import datetime
import pandas as pd
import argparse
import sys

currencies = [ 'EUR', 'USD', 'GBP' ]

parser = argparse.ArgumentParser()
parser.add_argument(
    '-c',
    '--currency',
    choices = currencies,
    required = True,
    metavar = 'CODE',
    help = 'currency code'
)
parser.add_argument(
    '-p',
    '--period',
    required = True,
    metavar = 'YYYY-MM',
    help = 'month and year'
)

args = parser.parse_args()

# Can use map(lambda s: int(s)), but then you'll need to format month for the
# filename
year, month = args.period.split('-')
# The first day of the month
start_date = datetime(int(year), int(month), 1)
# Fetch the rates for the previous week for backfilling in case of holidays
offset_start_date = start_date - pd.DateOffset(weeks=1)
_, last_day_of_month = calendar.monthrange(start_date.year, start_date.month)
# Last day of the month at 23:59:59 UTC
end_date = datetime(int(year), int(month), last_day_of_month, 23, 59, 59)

# Replace the time zone with the military time zone suffix
to_iso = lambda d: d.isoformat() #.replace('+00:00', 'Z')

CSV_URL = f'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/export/csv?currencies={args.currency}&end={to_iso(end_date)}&start={to_iso(offset_start_date)}'
headers = { 'Accept-Language': 'en' }
parse_us_date = lambda x: datetime.strptime(x, '%m/%d/%Y')

print(f'Fetching CSV for {args.currency} from {start_date} to {end_date}...')
df = pd.read_csv(
        CSV_URL,
        storage_options=headers,
        parse_dates=['Date', 'ValidFromDate'],
        date_parser=parse_us_date
     )

df.drop_duplicates(inplace=True)

# Backfill because the rates come in descending order
print('Backfilling rates...')
df = df.set_index('ValidFromDate').asfreq('D', method='bfill').reset_index()

# Get todays date
today = datetime.today()

# Check the last row to see if the date is the last day of the month.
if end_date < today and df['ValidFromDate'].iloc[-1].day != last_day_of_month:
    print('Last day of the month is missing. Inserting...')
    # Add the last date to the dataframe and forward fill the rates
    last_date = pd.DataFrame({'ValidFromDate': [end_date]})
    print('Forward filling rates...')
    df = pd.concat([df, last_date], ignore_index = True).ffill()

# Trim the dataframe to the dates we need
df = df[(df['ValidFromDate'] >= start_date) & (df['ValidFromDate'] <= end_date)]
df.reset_index(drop=True, inplace=True)

date_format = '%d/%m/%Y'
df['Date'] = df['Date'].dt.strftime(date_format)
df['ValidFromDate'] = df['ValidFromDate'].dt.strftime(date_format)

print('Saving processed CSV...')
df.to_csv(f'{args.currency}-{year}-{month}.csv')
print('Done!')

