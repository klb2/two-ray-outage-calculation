import logging

import numpy as np
from scipy import constants
from scipy import stats
from scipy import optimize
import matplotlib.pyplot as plt

from single_frequency import crit_dist, crit_dist_pi
from two_frequencies import sum_power_lower_envelope, sum_power
from outage_probability import get_intersections
from util import export_results, to_decibel


LOGGER = logging.getLogger(__name__)


def main_power_intervals(freq, h_tx, h_rx, df: float, sensitivity: float,
                         c=constants.c, plot=False, **kwargs):
    distance = np.logspace(0, 3, 1000)
    power = sum_power_lower_envelope(distance, df, freq, h_tx, h_rx)
    power_db = to_decibel(power)
    dist_min = crit_dist(df, h_tx, h_rx)
    dist_max = crit_dist_pi(df, h_tx, h_rx)
    LOGGER.info(f"Distances of local minima: {dist_min}")
    LOGGER.info(f"Distances of local maxima: {dist_max}")

    sens_lin = 10**(sensitivity/10.)

    _dist_upper_limit = 2**(-3/4)*((freq**2+(freq+df)**2)/sens_lin)**(1/4) * np.sqrt(h_tx*h_rx*df/(freq*(freq+df)))
    _decreasing_intervals = zip(dist_max, np.concatenate(([_dist_upper_limit], dist_min)))
    _d_intersect_positive = get_intersections(_decreasing_intervals, sensitivity,
                                              df, freq, h_tx, h_rx)
    _increasing_intervals = zip(np.concatenate((dist_min, [0])), dist_max)
    _d_intersect_negative = get_intersections(_increasing_intervals, sensitivity,
                                              df, freq, h_tx, h_rx)
    LOGGER.info(f"Sensitivity threshold: {sensitivity:.1f}dB")
    LOGGER.info(f"Intersections in increasing intervals: {_d_intersect_negative}")
    LOGGER.info(f"Intersections in decreasing intervals: {_d_intersect_positive}")

    if plot:
        fig, axs = plt.subplots()
        xlim = [min(distance), max(distance)]
        ylim = [-120, -50]
        axs.set_xlim(xlim)
        axs.set_ylim(ylim)
        axs.semilogx(distance, power_db)
        axs.vlines(dist_min, *ylim, colors='g', ls='--')
        axs.vlines(dist_max, *ylim, colors='r', ls='-.')
        axs.vlines(_d_intersect_positive, *ylim, colors='k', ls='dotted')
        axs.vlines(_d_intersect_negative, *ylim, colors='k', ls='dotted')
        axs.hlines(sensitivity, *xlim, colors='k')



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-s", "--sensitivity", type=float, default=-79)
    parser.add_argument("-df", type=float, default=250e6)
    parser.add_argument("--plot", action="store_true")
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
    main_power_intervals(**args)
    plt.show()
