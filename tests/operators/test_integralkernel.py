import torch
import matplotlib.pyplot as plt
from continuity.data.sine import Sine
from continuity.data.shape import DatasetShapes, TensorShape
from continuity.operators.integralkernel import NeuralNetworkKernel, NaiveIntegralKernel


def test_neuralnetworkkernel():
    n_obs = 8
    x_num, x_dim = 10, 2
    y_num, y_dim = 20, 3
    u_dim = 4
    v_dim = 1
    x = torch.rand(n_obs, x_num, x_dim)
    y = torch.rand(n_obs, y_num, y_dim)

    shapes = DatasetShapes(
        num_observations=n_obs,
        x=TensorShape(num=x_num, dim=x_dim),
        u=TensorShape(num=x_num, dim=u_dim),
        y=TensorShape(num=y_num, dim=y_dim),
        v=TensorShape(num=y_num, dim=v_dim),
    )

    # Kernel
    kernel = NeuralNetworkKernel(
        shapes=shapes,
        kernel_width=32,
        kernel_depth=1,
    )

    k = kernel(x, y)
    assert k.shape == (n_obs, x_num, y_num, u_dim, v_dim)


def test_naiveintegralkernel():
    # Parameters
    num_sensors = 16
    num_evals = num_sensors

    # Data set
    dataset = Sine(num_sensors, size=1)
    x, u, _, _ = [a.unsqueeze(0) for a in dataset[0]]

    # Kernel
    class Dirac(torch.nn.Module):
        shapes = dataset.shapes

        def forward(self, x, y):
            x_reshaped, y_reshaped = x.unsqueeze(2), y.unsqueeze(1)
            dist = ((x_reshaped - y_reshaped) ** 2).sum(dim=-1)
            dist = dist.reshape(
                -1,
                dataset.shapes.x.num,
                dataset.shapes.y.num,
                dataset.shapes.u.dim,
                dataset.shapes.v.dim,
            )
            zero = torch.zeros(1)
            return torch.isclose(dist, zero).to(torch.get_default_dtype())

    # Operator
    operator = NaiveIntegralKernel(kernel=Dirac())

    # Create tensors
    y = torch.linspace(-1, 1, num_evals).reshape(1, -1, 1)

    # Apply operator
    v = operator(x.reshape((1, -1, 1)), u.reshape((1, -1, 1)), y.reshape((1, -1, 1)))

    # Plotting
    fig, ax = plt.subplots(1, 1)
    x_plot = x[0].squeeze().detach().numpy()
    ax.plot(x_plot, u[0].squeeze().detach().numpy(), "x-")
    ax.plot(x_plot, v[0].squeeze().detach().numpy(), "--")
    fig.savefig(f"test_naiveintegralkernel.png")

    # For num_sensors == num_evals, we get v = u / num_sensors.
    if num_sensors == num_evals:
        v_expected = u / num_sensors
        assert (v == v_expected).all(), f"{v} != {v_expected}"


if __name__ == "__main__":
    test_neuralnetworkkernel()
    test_naiveintegralkernel()
