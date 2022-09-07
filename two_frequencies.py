import logging

import numpy as np
from scipy import constants
from scipy import optimize
import matplotlib.pyplot as plt

from util import export_results, to_decibel

from model import length_los, length_ref
from single_frequency import rec_power, crit_dist, rec_power_approx

LOGGER = logging.getLogger(__name__)


def sum_power_lower_envelope_approximation(distance, delta_freq, freq, h_tx,
                                           h_rx, c=constants.c, power_tx=1):
    _factor = power_tx/4
    _part1 = delta_freq**2 * .5* (1/freq**2 + 1/(freq+delta_freq)**2)
    _part2 = (h_rx*h_tx/distance**2)**2
    return _factor * _part1 * _part2

def sum_power(distance, delta_freq, freq, h_tx, h_rx, G_los=1, G_ref=1,
              c=constants.c, power_tx=1):
    power_f1 = rec_power(distance, freq, h_tx, h_rx, G_los=G_los, G_ref=G_ref,
                         c=c)
    power_f2 = rec_power(distance, freq+delta_freq, h_tx, h_rx, G_los=G_los,
                         G_ref=G_ref, c=c)
    _sum_power = 0.5*(power_f1+power_f2)
    return _sum_power

def sum_power_lower_envelope(distance, delta_freq, freq, 
                             h_tx, h_rx, G_los=1, G_ref=1,
                             c=constants.c, power_tx=1):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    freq2 = freq+delta_freq
    omega = 2*np.pi*freq
    omega2 = 2*np.pi*freq2
    delta_omega = omega2-omega
    _part1 = c**2/(4*d_los**2) * (1./omega**2 + 1./omega2**2)
    _part2 = c**2/(4*d_ref**2) * (1./omega**2 + 1./omega2**2)
    A = (c/(2*omega))**2
    B = (c/(2*omega2))**2
    _part3 = -2/(d_los*d_ref) * np.sqrt(A**2 + B**2 + 2*A*B*np.cos(delta_omega/c*(d_ref-d_los)))
    power_rx = power_tx/2 * (_part1 + _part2 + _part3)
    return power_rx


def main_power_two_freq(freq, delta_freq, h_tx, h_rx,
                        plot=False, export=False, **kwargs):
    #distance = np.logspace(0, 3, 2000)
    distance = np.logspace(1, 4, 2000)
    power_rx = rec_power(distance, freq, h_tx, h_rx)
    power_rx_db = to_decibel(power_rx)
    freq2 = freq + delta_freq
    power_rx2 = rec_power(distance, freq2, h_tx, h_rx)
    power_rx2_db = to_decibel(power_rx2)
    power_sum = .5*(power_rx+power_rx2)
    power_sum_db = to_decibel(power_sum)
    power_sum_lower = sum_power_lower_envelope(distance, delta_freq, freq, h_tx, h_rx)
    power_sum_lower_db = to_decibel(power_sum_lower)
    power_sum_approx = rec_power_approx(distance, h_tx, h_rx)
    power_sum_approx_db = to_decibel(power_sum_approx)
    power_sum_lower_approx = sum_power_lower_envelope_approximation(distance, delta_freq, freq, h_tx, h_rx)
    power_sum_lower_approx_db = to_decibel(power_sum_lower_approx)
    results = {
               "distance": distance,
               "powerSum": power_sum_db,
               "envelope": power_sum_lower_db,
               "approx": power_sum_approx_db,
               "approxLower": power_sum_lower_approx_db,
              }

    if plot:
        fig, axs = plt.subplots()
        axs.semilogx(distance, power_sum_db)
        axs.semilogx(distance, power_sum_lower_db)
        axs.semilogx(distance, power_sum_approx_db, '--')
        axs.semilogx(distance, power_sum_lower_approx_db, '--')
    if export:
        LOGGER.debug("Exporting single frequency power results.")
        export_results(results, f"power_sum_approx-{freq:E}-df{delta_freq:E}-t{h_tx:.1f}-r{h_rx:.1f}.dat")
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--h_tx", type=float, default=10.)
    parser.add_argument("-r", "--h_rx", type=float, default=1.5)
    parser.add_argument("-f", "--freq", type=float, default=2.4e9)
    parser.add_argument("-df", "--delta_freq", type=float, default=250e6)
    parser.add_argument("-dmin", "--d_min", type=float, default=10.)
    parser.add_argument("-dmax", "--d_max", type=float, default=100.)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="Increase output verbosity")
    args = vars(parser.parse_args())
    verb = args.pop("verbosity")
    logging.basicConfig(format="%(asctime)s - %(module)s -- [%(levelname)8s]: %(message)s",
                        handlers=[
                            logging.FileHandler("main.log", encoding="utf-8"),
                            logging.StreamHandler()
                        ])
    loglevel = logging.WARNING - verb*10
    LOGGER.setLevel(loglevel)
    main_power_two_freq(**args)
    plt.show()
