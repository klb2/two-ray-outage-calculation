import logging

import numpy as np
from scipy import constants
from scipy import stats
from scipy import optimize
import matplotlib.pyplot as plt

from single_frequency import rec_power, crit_dist, crit_dist_pi
from two_frequencies import sum_power_lower_envelope, sum_power
from util import export_results, to_decibel


LOGGER = logging.getLogger(__name__)


def get_intersections(intervals, sensitivity, df, freq, h_tx, h_rx):
    def func_intersect(d, *args):
        return to_decibel(sum_power_lower_envelope(d, *args)) - sensitivity

    d_intersect = []
    for _d_lower, _d_upper in intervals:
        try:
            _d_intersect = optimize.root_scalar(
                func_intersect,
                args=(df, freq, h_tx, h_rx),
                x0=_d_lower,
                bracket=[_d_lower, _d_upper],
            )
            _d_intersect = _d_intersect.root
            d_intersect.append(_d_intersect)
            # print(f"Interval [{_d_lower:.1f}, {_d_upper:.1f}]:\t{_d_intersect}")
        except ValueError:
            pass
            # print(f"Interval [{_d_lower:.1f}, {_d_upper:.1f}]:\tNo Intersection")
    return d_intersect


def calculate_outage_prob(df, freq, h_tx, h_rx, sensitivity, rv_distance):
    dist_min = crit_dist(df, h_tx, h_rx)
    dist_max = crit_dist_pi(df, h_tx, h_rx)

    sens_lin = 10 ** (sensitivity / 10.0)
    _dist_upper_limit = (
        2 ** (-3 / 4)
        * ((freq**2 + (freq + df) ** 2) / sens_lin) ** (1 / 4)
        * np.sqrt(h_tx * h_rx * df / (freq * (freq + df)))
    )

    _decreasing_intervals = zip(
        dist_max, np.concatenate(([_dist_upper_limit], dist_min))
    )
    _d_intersect_positive = get_intersections(
        _decreasing_intervals, sensitivity, df, freq, h_tx, h_rx
    )
    _increasing_intervals = zip(np.concatenate((dist_min, [0])), dist_max)
    _d_intersect_negative = get_intersections(
        _increasing_intervals, sensitivity, df, freq, h_tx, h_rx
    )
    prob_mass_neg = rv_distance.cdf(_d_intersect_positive)
    prob_mass_pos = rv_distance.cdf(_d_intersect_negative)
    outage_prob = 1 + sum(prob_mass_pos) - sum(prob_mass_neg)
    return outage_prob


def _main_power_rv(distance, freq, h_tx, h_rx, df):
    LOGGER.debug("Work on single frequency scenario...")
    power_single = rec_power(distance, freq, h_tx, h_rx)

    LOGGER.info(f"Frequency spacing: {df:E}")
    LOGGER.debug("Work on two frequency scenario...")
    power_two = sum_power(distance, df, freq, h_tx, h_rx)

    LOGGER.debug("Work on two frequency scenario (lower bound)...")
    power_two_lower = sum_power_lower_envelope(distance, df, freq, h_tx, h_rx)

    powers = {
        "singleActual": power_single,
        "twoActual": power_two,
        "twoLower": power_two_lower,
    }
    powers_hist = {k: np.histogram(to_decibel(v), bins=200) for k, v in powers.items()}
    powers_rv = {k: stats.rv_histogram(v) for k, v in powers_hist.items()}
    return powers_rv


def main_outage_prob_power(
    freq,
    h_tx,
    h_rx,
    df: float,
    c=constants.c,
    num_samples=100000,
    plot=False,
    export=False,
    **kwargs,
):
    LOGGER.info(
        f"Simulating outage probability with parameters: "
        f"f1={freq:E}, h_tx={h_tx:.1f}, h_rx={h_rx:.1f}"
    )
    LOGGER.info(f"Number of samples: {num_samples:E}")

    rv_distance = stats.uniform(loc=50, scale=40)
    distance = rv_distance.rvs(size=num_samples)
    powers_rv = _main_power_rv(distance, freq, h_tx, h_rx, df)

    threshold = np.linspace(-120, -60, 1500)
    threshold_lin = 10 ** (threshold / 10.0)
    results = {k: v.cdf(threshold) for k, v in powers_rv.items()}

    outage_prob_analytical = [
        calculate_outage_prob(df, freq, h_tx, h_rx, sens, rv_distance)
        for sens in threshold
    ]
    approx_out_prob = rv_distance.sf(
        (1.0 / threshold_lin) ** (1 / 4) * np.sqrt(h_tx * h_rx)
    )
    _approx_min_d = 4 * np.pi * (freq + df) * h_rx * h_tx / c
    _approx_min_power_exact = (c / (2 * np.pi * (freq + df))) ** 4 / (
        4 * h_rx * h_tx
    ) ** 2
    LOGGER.info(
        f"The approximation is valid for: s < {to_decibel(_approx_min_power_exact):.1f}dB"
    )

    _approx_min_s = sum_power_lower_envelope(
        crit_dist(df, h_tx, h_rx, k=1), df, freq, h_tx, h_rx
    )
    _dist_approx_lower = (
        2 ** (-3 / 4)
        * ((freq**2 + (freq + df) ** 2) / threshold_lin) ** (1 / 4)
        * np.sqrt(h_tx * h_rx * df / (freq * (freq + df)))
    )
    approx_out_prob_upper = rv_distance.sf(_dist_approx_lower)
    LOGGER.info(
        f"The worst-case approximation is valid for: s < {to_decibel(_approx_min_s):.1f}dB"
    )

    if plot:
        fig, axs = plt.subplots()
        for _name, _prob in results.items():
            axs.semilogy(threshold, _prob, label=_name, marker="o")
        axs.semilogy(threshold, outage_prob_analytical, "k-", label="Analytical")
        axs.semilogy(threshold, approx_out_prob, "k--", label="Approximation")
        axs.semilogy(threshold, approx_out_prob_upper, "k--", label="Approximation")
        axs.set_xlabel("Receiver Sensitivity [dB]")
        axs.set_ylabel("Outage Probability")
        axs.set_xlim([min(threshold), max(threshold)])
        axs.set_ylim([1e-8, 1.5])
        axs.legend()

    results["twoLowerAnalytical"] = outage_prob_analytical
    results["twoLowerApprox"] = approx_out_prob_upper
    results["twoApprox"] = approx_out_prob
    results["threshold"] = threshold
    if export:
        LOGGER.info("Exporting results.")
        export_results(
            results, f"out_prob_power-{freq:E}-df{df:E}-t{h_tx:.1f}-r{h_rx:.1f}.dat"
        )
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.0)
    parser.add_argument("-r", "--h_rx", type=float, default=1.0)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-n", "--num_samples", type=int, default=int(1e6))
    parser.add_argument("-df", type=float, default=250e6)
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
    main_outage_prob_power(**args)
    # main_power_intervals(**args)
    plt.show()
