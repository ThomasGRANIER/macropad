#!/bin/bash
# Ce place dans le bon dossier 
cd /home/tgranier/macropad-python/

# Définit le port par défaut
PORT=/dev/ttyACM0

# Lance le script Python
python3 main.py -p "$PORT"