import logging

import numpy as np
from scipy import constants
from scipy import stats
import matplotlib.pyplot as plt

from single_frequency import rec_power
from two_frequencies import sum_power_lower_envelope, sum_power, crit_dist
from outage_probability import _main_power_rv, calculate_outage_prob
from util import export_results, to_decibel


LOGGER = logging.getLogger(__name__)


def gen_rv_distance():
    N = 5000
    X1 = stats.norm.rvs(loc=20, scale=1, size=N)
    X2 = stats.norm.rvs(loc=50, scale=2, size=N)
    X3 = stats.norm.rvs(loc=100, scale=5, size=N)
    X4 = stats.norm.rvs(loc=200, scale=20, size=N)
    X = np.concatenate([X1, X2, X3, X4])
    X = np.maximum(X, 0)
    _hist = np.histogram(X, bins=150)
    rv_bimod = stats.rv_histogram(_hist)
    return rv_bimod


def approx_eps_power(freq, delta_freq, dist_eps, h_tx, h_rx, power_tx=1.0):
    omega = 2 * np.pi * freq
    dw = 2 * np.pi * delta_freq
    omega2 = omega + dw
    _part1 = power_tx / 8
    _part2 = 1 / omega**2 + 1 / omega2**2
    _part3 = (dw * h_tx * h_rx / dist_eps**2) ** 2
    return _part1 * _part2 * _part3


def main_outage_prob(
    freq,
    h_tx,
    h_rx,
    df: float = None,
    eps=1e-3,
    c=constants.c,
    num_samples=100000,
    plot=False,
    export=False,
    **kwargs,
):
    num_samples = max([int(2 / eps), num_samples])
    LOGGER.info(
        f"Simulating outage probability with parameters: f1={freq:E}, h_tx={h_tx:.1f}, h_rx={h_rx:.1f}"
    )
    LOGGER.info(f"Number of samples: {num_samples:E}")
    rv_distance = stats.expon(loc=10, scale=15)
    distance = rv_distance.rvs(size=num_samples)

    if df is None:
        df = np.logspace(7, np.log10(freq), 300)
    results = {}
    for _df in df:
        LOGGER.info(f"Frequency spacing: {_df:E}")
        powers_rv = _main_power_rv(distance, freq, h_tx, h_rx, _df)
        for _k, _v in powers_rv.items():
            if _k not in results:
                results[_k] = []
            results[_k].append(_v.ppf(eps))

    if plot:
        fig, axs = plt.subplots()
        for _name, _prob in results.items():
            # axs.semilogy(threshold, _prob, label=_name)
            axs.semilogx(df, _prob, label=_name)
        axs.set_xlabel("Frequency Spacing $\\Delta f$ [Hz]")
        axs.set_ylabel("$\\varepsilon$-Outage Power")
        axs.set_title(f"$\\varepsilon=${eps:E}")
        axs.legend()

    results["df"] = df
    if export:
        LOGGER.info("Exporting results.")
        export_results(
            results, f"eps_out_prob_power-{freq:E}-{eps:E}-t{h_tx:.1f}-r{h_rx:.1f}.dat"
        )
    return results


def main_outage_prob_3d(
    freq,
    h_tx,
    h_rx,
    eps=1e-3,
    c=constants.c,
    num_samples=100000,
    plot=False,
    export=False,
    **kwargs,
):
    LOGGER.info(
        f"Simulating outage probability with parameters: f1={freq:E}, h_tx={h_tx:.1f}, h_rx={h_rx:.1f}"
    )
    LOGGER.info(f"Number of samples: {num_samples:E}")
    rv_distance = stats.expon(loc=10, scale=15)
    distance = rv_distance.rvs(size=num_samples)

    df = np.logspace(7, 10, 300)
    sensitivity = np.linspace(-100, -95, 10)
    outage_prob = np.zeros((len(sensitivity), len(df)))
    for idx, s in enumerate(sensitivity):
        print(f"Sensitivity: {idx+1:d}/{len(sensitivity):d}")
        _out_prob = [
            calculate_outage_prob(_df, freq, h_tx, h_rx, s, rv_distance) for _df in df
        ]
        outage_prob[idx, :] = _out_prob
    DF, S = np.meshgrid(df, sensitivity)
    DF = np.log(DF)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.plot_surface(DF, S, np.log10(outage_prob), cmap="viridis")
    ax.plot_wireframe(DF, S, np.log10(eps) * np.ones_like(DF), color="k")
    ax.set_xlabel("Delta Frequency")
    ax.set_ylabel("Sensitivity")
    ax.set_zlabel("Outage Probability")
    # ax.colorbar()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.0)
    parser.add_argument("-r", "--h_rx", type=float, default=1.5)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-e", "--eps", type=float, default=1e-3)
    parser.add_argument("-n", "--num_samples", type=int, default=int(1e6))
    parser.add_argument("-df", type=float, nargs="+", default=None)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="Increase output verbosity"
    )
    args = vars(parser.parse_args())
    verb = args.pop("verbosity")
    logging.basicConfig(
        format="%(asctime)s - [%(levelname)8s]: %(message)s",
        handlers=[
            logging.FileHandler("main.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    loglevel = logging.WARNING - verb * 10
    LOGGER.setLevel(loglevel)
    main_outage_prob(**args)
    # main_outage_prob_3d(**args)
    plt.show()
