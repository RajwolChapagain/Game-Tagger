# 🧭 Introduction
Game Tagger is a CNN-based machine learning model that tags games based on their in-game screenshots. It is a multi-label classifier built from the ground up and trained on data scraped from the Steam games store. This repository contains the complete code for scraping data from the Steam store and using it to create a fully-trained model using PyTorch.

# 🚀 Quickstart
To get started, clone the repository:
```
git clone https://github.com/RajwolChapagain/Game-Tagger.git
```
Install the nix package manager for entering the development environment:
```
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```
Enter the development environment:
```
NIX_CONFIG="experimental-features = nix-command flakes" nix develop
```
Scrape the data:
```
python3 scraper.py
```
Split it into train and test sets:
```
python3 split.py
```
Train the model:
```
python3 trainer.py
```

# 🔗 Deployed Example
To see an example of a deployed model, visit the [project website](https://rajwolchapagain.github.io/Game-Tagger-Website/).
