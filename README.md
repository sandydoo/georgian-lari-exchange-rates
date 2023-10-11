# Fetch Georgian Lari exchange rates from the National Bank of Georgia

Fetches exchange rate data for the Georgian Lari for a given month and currency. Outputs a CSV file.
Indispensible for reporting income in foreign currencies as a Georgian tax resident.

The dates are converted into a sane format that can be processed by spreadsheet software.
Missing rates are back- and forward-filled for bank holidays.

### Documentation

```console
➜ ./convert_dates.py -h
usage: convert_dates.py [-h] -c CODE -p YYYY-MM

options:
  -h, --help            show this help message and exit
  -c CODE, --currency CODE
                        currency code
  -p YYYY-MM, --period YYYY-MM
                        month and year

```

### Example

```sh
./convert_dates.py -p 2023-09 -c EUR
```

### Supported currencies

- EUR
- USD
- GBP
