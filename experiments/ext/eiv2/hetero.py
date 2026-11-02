"""Heterogeneous measurement noise across series (eiv2 scenario; the generator's
add_measurement_noise uses one ratio for every series).

Series i gets white noise with variance ratio_i * var(x_i). The ratios are an evenly spaced grid
on [0, 2 * mean_ratio] (so their mean is mean_ratio), assigned to the series by a random
permutation drawn from the same rng that then draws the noise."""
import numpy as np


def hetero_ratios(n: int, mean_ratio: float, rng: np.random.Generator) -> np.ndarray:
    return rng.permutation(np.linspace(0.0, 2.0 * mean_ratio, n))


def add_hetero_noise(data: np.ndarray, mean_ratio: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    if mean_ratio == 0:
        return data, np.zeros(data.shape[1])
    ratios = hetero_ratios(data.shape[1], mean_ratio, rng)
    return data + rng.normal(size=data.shape) * np.sqrt(ratios * data.var(axis=0)), ratios
