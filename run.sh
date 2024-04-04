#!/bin/sh

# This repository belongs to the following publication
# K. -L. Besser, E. A. Jorswieck and J. P. Coon, "Outage Probability
# Calculation for Two-Ray Ground Reflection Scenarios with Frequency
# Diversity," 2023 57th Asilomar Conference on Signals, Systems, and Computers,
# Pacific Grove, CA, USA, 2023, pp. 237-242, doi:
# 10.1109/IEEECONF59524.2023.10477068.
#
# Copyright (C) 2023
# License: GPLv3

FREQ="2.4e9"
DF="250e6"
HTX="10"
HRX="1.5"

echo "Figure: Monotonic intervals"
python3 monotonic_intervals.py -v -r "$HRX" -t "$HTX" -f "$FREQ" -df "$DF" --plot -s "-79"

echo "Figure: Outage probability"
python3 outage_probability.py -v -r "$HRX" -t "$HTX" -f "$FREQ" -df "$DF" --plot --export --num_samples "100_000_000"

echo "Figure: Sum power, lower envelope, and approximations"
python3 two_frequencies.py -v -r "$HRX" -t "$HTX" -f "$FREQ" -df "$DF" --plot --export

echo "Figure: Eps-outage power over frequency spacing"
python3 eps_outage_dw.py -v -r "$HRX" -t "$HTX" -f "$FREQ" --plot --export --eps "1e-4"
