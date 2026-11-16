"""SRCI without the stated damage: the data-driven gate and opening budget of ``ext_auto5`` (the stated
damage is dropped inside ``auto5_raw``), returned UNCALIBRATED so that the unit-level order-statistic factor of the
topology-level study can be applied to it like to every other method (docs/ext/p4h8_auto_spec.md)."""
from __future__ import annotations

from .ext_auto5 import auto5_raw


def srci_auto(data, skel, lag_max, H, n_boot, rng):
    return auto5_raw(data, skel, lag_max, H, n_boot, rng, name="srci_auto")


METHODS = {"srci_auto": srci_auto}
