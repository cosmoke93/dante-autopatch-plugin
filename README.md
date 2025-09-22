# Dante AI Autopatch Plugin

This repository contains a simplified prototype of a Dante AI Autopatch plugin.

The main script is `autopatch_simple.py`, which discovers Dante devices on a network (or simulates them if the Dante Application Library is unavailable), generates routing suggestions, and applies them.

## Running the script

1. Install Python 3.
2. (Optional) Install the Dante Application Library from Audinate if you plan to use it on a real Dante network.
3. Run the script: `python autopatch_simple.py`.

## Building a Windows EXE

A GitHub Actions workflow in this repository builds a standalone Windows executable from the Python script using PyInstaller. The compiled executable will appear in the Actions tab after each commit.
