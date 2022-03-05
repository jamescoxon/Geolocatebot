#!/bin/bash

autopep8 --in-place --aggressive --aggressive ./botrun.py

bandit -r ./
prospector
mypy --strict ./botrun.py
#pylint ./botrun.py

