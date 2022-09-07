import logging

import numpy as np
from scipy import constants
from scipy import stats
import matplotlib.pyplot as plt

from single_frequency import rec_power
from two_frequencies import sum_power_lower_envelope, sum_power
from outage_probability import _main_power_rv
from util import export_results, to_decibel


LOGGER = logging.getLogger(__name__)


def main_outage_prob(freq, h_tx, h_rx, df: float = None,
                     eps=1e-3, c=constants.c, num_samples=100000,
                     plot=False, export=False, **kwargs):
    LOGGER.info(f"Simulating outage probability with parameters: f1={freq:E}, h_tx={h_tx:.1f}, h_rx={h_rx:.1f}")
    LOGGER.info(f"Number of samples: {num_samples:E}")
    #rv_distance = stats.ncx2(5, 50, scale=2)
    rv_distance = stats.uniform(loc=10, scale=50-10)
    #rv_distance = stats.expon(loc=10, scale=15)
    distance = rv_distance.rvs(size=num_samples)

    if df is None:
        df = np.logspace(7, np.log10(freq), 200)
        #df = np.logspace(7, 10, 300)
    results = {}
    for _df in df:
        LOGGER.info(f"Frequency spacing: {_df:E}")
        powers_rv = _main_power_rv(distance, freq, h_tx, h_rx, _df)
        for _k, _v in powers_rv.items():
            if _k not in results: results[_k] = []
            results[_k].append(_v.ppf(eps))

    if plot:
        fig, axs = plt.subplots()
        for _name, _prob in results.items():
            #axs.semilogy(threshold, _prob, label=_name)
            axs.semilogx(df, _prob, label=_name)
        axs.set_xlabel("Frequency Spacing $\\Delta f$ [Hz]")
        axs.set_ylabel("$\\varepsilon$-Outage Power")
        axs.set_title(f"$\\varepsilon=${eps:E}")
        axs.legend()

    results['df'] = df
    if export:
        LOGGER.info("Exporting results.")
        export_results(results, f"eps_out_prob_power-{freq:E}-{eps:E}-t{h_tx:.1f}-r{h_rx:.1f}.dat")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-e", "--eps", type=float, default=1e-3)
    parser.add_argument("-n", "--num_samples", type=int, default=int(1e6))
    parser.add_argument("-df", type=float, nargs="+", default=None)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Increase output verbosity")
    args = vars(parser.parse_args())
    verb = args.pop("verbosity")
    logging.basicConfig(format="%(asctime)s - [%(levelname)8s]: %(message)s",
                        handlers=[
                            logging.FileHandler("main.log", encoding="utf-8"),
                            logging.StreamHandler()
                        ])
    loglevel = logging.WARNING - verb*10
    LOGGER.setLevel(loglevel)
    main_outage_prob(**args)
    plt.show()
