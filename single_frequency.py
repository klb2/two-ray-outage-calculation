import logging

import numpy as np
from scipy import constants
from scipy import optimize
import matplotlib.pyplot as plt

from util import export_results, to_decibel

from model import length_los, length_ref


LOGGER = logging.getLogger(__name__)


def rec_power_approx(distance, h_tx, h_rx, G_los=1, G_ref=1, power_tx=1):
    _part1 = (h_tx * h_rx / distance**2) ** 2
    return power_tx * _part1


def delta_phi(distance, freq, h_tx, h_rx, c=constants.speed_of_light):
    omega = 2 * np.pi * freq
    _d_phi = (
        omega
        / c
        * (length_ref(distance, h_tx, h_rx) - length_los(distance, h_tx, h_rx))
    )
    return _d_phi


def rec_power(distance, freq, h_tx, h_rx, G_los=1, G_ref=1, c=constants.c, power_tx=1):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    omega = 2 * np.pi * freq
    phi = omega / c * (d_ref - d_los)
    _factor = power_tx * (c / (2 * omega)) ** 2
    _part1 = G_los / (d_los**2)
    _part2 = G_ref / (d_ref**2)
    _part3 = -2 * np.sqrt(G_los * G_ref) / (d_los * d_ref) * np.cos(phi)
    power_rx = _factor * (_part1 + _part2 + _part3)
    return power_rx


def rec_power_lower_envelope(
    distance, freq, h_tx, h_rx, G_los=1, G_ref=1, c=constants.c, power_tx=1
):
    d_los = length_los(distance, h_tx, h_rx)
    d_ref = length_ref(distance, h_tx, h_rx)
    omega = 2 * np.pi * freq
    _factor = power_tx * (c / (2 * omega)) ** 2
    _part1 = G_los / (d_los**2)
    _part2 = G_ref / (d_ref**2)
    _part3 = -2 * np.sqrt(G_los * G_ref) / (d_los * d_ref)
    power_rx = _factor * (_part1 + _part2 + _part3)
    return power_rx


def crit_dist(freq, h_tx, h_rx, c=constants.c, k=None):
    a = h_tx - h_rx
    b = h_tx + h_rx
    max_phi = 2 * np.pi * freq / c * (b - a)
    max_k = np.divmod(max_phi, 2 * np.pi)[0]
    if k is not None:
        if k > max_k:
            raise ValueError(
                f"Your provided k is too large. The maximum k is {max_k:d}"
            )
        k = k + 0j
    else:
        k = np.arange(max_k) + 1 + 0j
    _d = (
        -1
        / (2 * c * freq * k)
        * np.sqrt(c**2 * k**2 - 4 * freq**2 * h_rx**2)
        * np.sqrt(c**2 * k**2 - 4 * freq**2 * h_tx**2)
    )
    _d = np.real(_d)
    return _d


def crit_dist_pi(freq, h_tx, h_rx, c=constants.c, k=None):
    a = h_tx - h_rx
    b = h_tx + h_rx
    max_phi = 2 * np.pi * freq / c * (b - a)
    max_k = (max_phi / np.pi - 1) // 2
    if k is not None:
        if k > max_k:
            raise ValueError(
                f"Your provided k is too large. The maximum k is {max_k:d}"
            )
        k = k + 0j
    else:
        k = np.arange(max_k + 1) + 0j
    _d = (
        -1
        / (4 * c * freq * (1 + 2 * k))
        * np.sqrt((c + 2 * c * k) ** 2 - (4 * freq * h_rx) ** 2)
        * np.sqrt((c + 2 * c * k) ** 2 - (4 * freq * h_tx) ** 2)
    )
    _d = np.real(_d)
    return _d
