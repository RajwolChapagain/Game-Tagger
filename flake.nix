{
	description = "A flake for describing a python development shell";

	inputs = {
		nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
	};

	outputs = { self, nixpkgs }: 
	let
		pkgs = nixpkgs.legacyPackages.x86_64-linux;
	in
	{
		devShells.x86_64-linux.default = pkgs.mkShell rec {
			python-packages = with pkgs.python312Packages; [
				requests
				beautifulsoup4
			];

			packages = with pkgs; [
			  python3
			] ++ python-packages;

			shellHook = ''exec zsh'';
		};
	};
}
