"""
`continuity.data`

Data sets in Continuity.
Every data set is a list of `(x, u, y, v)` tuples.
"""

import os
import torch

from .dataset import OperatorDataset, SelfSupervisedOperatorDataset
from .shape import DatasetShape
from .sine import Sine
from .flame import Flame

__all__ = [
    "OperatorDataset",
    "SelfSupervisedOperatorDataset",
    "DatasetShape",
    "Sine",
    "Flame",
    "device",
    "split",
]


def get_device() -> torch.device:
    """Get torch device.

    Defaults to `cuda` or `mps` if available, otherwise to `cpu`.

    Use the environment variable `USE_MPS_BACKEND` to disable the `mps` backend.

    Returns:
        Device.
    """
    device = torch.device("cpu")
    use_mps_backend = os.environ.get("USE_MPS_BACKEND", "True").lower() in ("true", "1")

    if use_mps_backend and torch.backends.mps.is_available():
        device = torch.device("mps")

    if torch.cuda.is_available():
        device = torch.device("cuda")

    return device


device = get_device()


def split(dataset, split=0.5, seed=None):
    """
    Split data set into two parts.

    Args:
        split: Split fraction.
    """
    assert 0 < split < 1, "Split fraction must be between 0 and 1."

    generator = torch.Generator()
    if seed is not None:
        generator.manual_seed(seed)

    return torch.utils.data.random_split(
        dataset,
        [split, 1 - split],
        generator=generator,
    )


def dataset_loss(dataset, operator, loss_fn):
    """Evaluate operator performance on data set.

    Args:
        dataset: Data set.
        operator: Operator.
        loss_fn: Loss function.
    """
    loss = 0.0

    for x, u, y, v in dataset:
        x, u, y, v = x.unsqueeze(0), u.unsqueeze(0), y.unsqueeze(0), v.unsqueeze(0)
        loss += loss_fn(operator, x, u, y, v)

    return loss
