# Outage Probability Calculation for Two-Ray Ground Reflection Scenarios with Frequency Diversity

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD)
![GitHub](https://img.shields.io/github/license/klb2/two-ray-outage-calculation)
[![IEEExplore](https://img.shields.io/badge/doi-10.1109/IEEECONF59524.2023.10477068-informational)](https://doi.org/10.1109/IEEECONF59524.2023.10477068)

This repository belongs to the paper "Outage Probability Calculation for
Two-Ray Ground Reflection Scenarios with Frequency Diversity" (K.-L. Besser, E.
Jorswieck, J. Coon. Asilomar Conference on Signals, Systems & Computers, Oct.
2023, pp. 237-242.) [doi:
10.1109/IEEECONF59524.2023.10477068](https://doi.org/10.1109/IEEECONF59524.2023.10477068).

The code is made publicly accessible in order to allow everybody to reproduce
the results presented in the paper.


## File List
The following files are provided in this repository:

- `run.sh`: Bash script that reproduces the figures presented in the paper.
- `util.py`: Python module that contains utility functions, e.g., for saving results.
- `model.py`: Python module that contains utility functions around the two-ray
  ground reflection model.
- `single_frequency.py`: Python module that contains the functions to calculate
  the receive power when a single frequency is used.
- `two_frequencies.py`: Python module that contains the functions to calculate
  the receive power when two frequencies are used in parallel.
- `outage_probability.py`: Python module that contains the functions to
  estimate the outage probabilities.
- `eps_outage_dw.py`: Python module that contains the functions to calculate
  the eps-outage power for varying frequency spacings.
- `monotonic_intervals.py`: Python module that contains functions to illustrate
  the monotonic intervals of the receive power.


## Usage
### Running it online
The easiest way is to use services like [Binder](https://mybinder.org/) to run
the notebook online. Simply navigate to
[https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD](https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD)
to run the notebooks in your browser without setting everything up locally.

### Local Installation
If you want to run it locally on your machine, Python3 and Jupyter are needed.
The present code was developed and tested with the following versions:

- Python 3.11
- numpy 1.26
- scipy 1.10
- pandas 2.0

Make sure you have [Python3](https://www.python.org/downloads/) installed on
your computer.
You can then install the required packages (including Jupyter) by running
```bash
pip3 install -r requirements.txt
```

This will install all the needed packages which are listed in the requirements 
file.

You can then recreate the figures from the paper by running
```bash
bash run.sh
```


## Acknowledgements
This research was supported by the Federal Ministry of Education and Research
Germany (BMBF) as part of the 6G Research and Innovation Cluster 6G-RIC under
Grant 16KISK031, by the German Research Foundation (DFG) under grant BE
8098/1-1, and by the EPSRC under grant number EP/T02612X/1.


## License and Referencing
This program is licensed under the GPLv3 license. If you in any way use this
code for research that results in publications, please cite our original
article listed above.

You can use the following BibTeX entry
```bibtex
@inproceedings{Besser2023asilomar,
  author = {Besser, Karl-Ludwig and Jorswieck, Eduard A. and Coon, Justin P.},
  title = {Outage Probability Calculation for Two-Ray Ground Reflection Scenarios with Frequency Diversity},
  booktitle = {2023 57th Asilomar Conference on Signals, Systems, and Computers},
  year = {2023},
  month = {10},
  pages = {237--242},
  publisher = {IEEE},
  venue = {Pacific Grove, CA, USA},
  doi = {10.1109/IEEECONF59524.2023.10477068},
}
```
