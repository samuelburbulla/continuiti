"""Various data set implementations."""

import torch
import numpy as np
from typing import Tuple
from continuity.data import DataSet, tensor


class Sine(DataSet):
    r"""Creates a data set of sine waves.

    The data set is generated by sampling sine waves at the given number of
    sensors placed evenly in the interval $[-1, 1]$. The wave length of the
    sine waves is evenly distributed between $\pi$ for the first observation
    and $2\pi$ for the last observation, respectively.

    The `Sine` dataset generates $N$ sine waves
    $$
    f(x) = \sin(w_k x), \quad w_k = 1 + \frac{k}{N-1}, \quad k = 0, \dots, N-1.
    $$
    As a `SelfSupervisedDataset` it exports batches of samples for self-supervised
    training, namely
    $$
    \left(\mathbf{x}, f(\mathbf{x}), x_j, f(x_j)\right), \quad \text{for } j = 1, \dots, M,
    $$
    where $\mathbf{x} = (x_i)_{i=1 \dots M}$ are the $M$ equidistantly
    distributed sensor positions.

    - coordinate_dim: 1
    - num_channels: 1

    Args:
        num_sensors: Number of sensors.
        size: Size of data set.
        batch_size: Batch size. Defaults to 32.
        shuffle: Shuffle data set. Defaults to True.
    """

    def __init__(
        self, num_sensors: int, size: int, batch_size: int = 32, shuffle: bool = True
    ):
        self.num_sensors = num_sensors
        self.size = size

        self.coordinate_dim = 1
        self.num_channels = 1

        # Generate observations
        observations = [self.generate_observation(i) for i in range(self.size)]

        x = torch.stack([x for x, _ in observations])
        u = torch.stack([u for _, u in observations])

        # Use observations as labels
        y = x
        v = u

        super().__init__(x, u, y, v, batch_size, shuffle)

    def generate_observation(self, i: float) -> Tuple[np.array, np.array]:
        """Generate observation

        Args:
            i: Index of observation (0 <= i <= size).
        """
        # Create x of shape (n, 1)
        x = np.linspace(-1, 1, self.num_sensors).reshape(-1, 1)

        if self.size == 1:
            w = 1
        else:
            w = 1 + i / (self.size - 1)

        u = np.sin(w * np.pi * x)

        return tensor(x), tensor(u)
