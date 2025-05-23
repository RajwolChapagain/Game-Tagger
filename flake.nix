{
	description = "A flake for describing a python development shell";

	inputs = {
		nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
	};

	nixConfig = {
		substituters = [
				"https://nix-community.cachix.org"
		];
		trusted-public-keys = [
				"nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
		];
	};

	outputs = { self, nixpkgs }: 
	let
		system = "x86_64-linux";
		pkgs = import nixpkgs { 
			system = system; 
			config.allowUnfree = true;

		};
	in
	{
		devShells.x86_64-linux.default = pkgs.mkShell rec {
			python-packages = with pkgs.python312Packages; [
				requests
				beautifulsoup4
				numpy
				torchWithCuda
			];

			packages = with pkgs; [
			  python3
			] ++ python-packages;

			shellHook = ''exec zsh'';
		};
	};
}
