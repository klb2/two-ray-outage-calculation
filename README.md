# Template for Reproducible Research Papers

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD)
![GitHub](https://img.shields.io/github/license/klb2/two-ray-outage-calculation)

This repository belongs to the paper "Outage Probability Calculation for
Two-Ray Ground Reflection Scenarios with Frequency Diversity" (K.-L. Besser, E.
Jorswieck, J. Coon. Asilomar Conference on Signals, Systems & Computers, Oct.
2023).

The code is made publicly accessible in order to allow everybody to reproduce
the results presented in the paper.


## File List
The following files are provided in this repository:

- `run.sh`: Bash script that reproduces the figures presented in the paper.
- `util.py`: Python module that contains utility functions, e.g., for saving results.
```diff
- `main.py`: Python script that...
- ...
```

## Usage
### Running it online
The easiest way is to use services like [Binder](https://mybinder.org/) to run
the notebook online. Simply navigate to
[https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD](https://mybinder.org/v2/gh/klb2/two-ray-outage-calculation/HEAD)
to run the notebooks in your browser without setting everything up locally.

### Local Installation
If you want to run it locally on your machine, Python3 and Jupyter are needed.
The present code was developed and tested with the following versions:
```diff
- Python 3.8
- Jupyter 1.0
- numpy 1.18
- scipy 1.4
```

Make sure you have [Python3](https://www.python.org/downloads/) installed on
your computer.
You can then install the required packages (including Jupyter) by running
```bash
pip3 install -r requirements.txt
jupyter nbextension enable --py widgetsnbextension
```
This will install all the needed packages which are listed in the requirements 
file. The second line enables the interactive controls in the Jupyter
notebooks.

Finally, you can run the Jupyter notebooks with
```bash
jupyter notebook
```

You can also recreate the figures from the paper by running
```bash
bash run.sh
```


## Acknowledgements
This research was supported by
```diff
! Add funding information
```


## License and Referencing
This program is licensed under the GPLv3 license. If you in any way use this
code for research that results in publications, please cite our original
article listed above.

You can use the following BibTeX entry
```bibtex
@article{...,
  author = {...},
  title = {...},
  ...
}
```
```diff
! Add bibtex entry of the published paper
```
