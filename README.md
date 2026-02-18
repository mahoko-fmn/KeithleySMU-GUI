# Keithley MSc Python GUI Project

This project implements a modular Python GUI for controlling and simulating Keithley instruments as part of an MSc research project. The main objective being to better improve the efficiency of use of laboratory instruments by simplifications of interactions and thus sensory measurements.

## Structure
- notebooks/: exploratory and analysis notebooks
- src/: reusable Python modules (core application modules)
- data/: raw and processed data (not versioned)
- figures/: figures for thesis and reports
- tests/: unit tests for non-GUI components

## Supported platformdirs
- linux (primary execution)
- Windows (development)

## Setup
'''bash
python -m venv venv
source venv/bin/activate     # linux
pip install -r requirements.txt

## 5. Git Workflow (key)

### Branch strategy

- 'main' **stable, running code**
- 'dev' activate development

No feature-branch overkill

---

## 6. On Windows Machine (execute option B):

'''bash
git init
git add
git commit -m "Initial modularized Keithley GUI structure"
git branch -M main
git remote add origin https://github.com/<you>/keithley-msc-gui.git
git push -u origin main
