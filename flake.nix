{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python310Full.withPackages (ps: [
          ps.pandas
          ps.requests
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv ];
        };
      }
    );
}
