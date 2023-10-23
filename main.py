import matplotlib.pyplot as plt
from data import SineWaves
from plotting import plot_observation, plot_evaluation
from model import ContinuityModel
import keras_core as keras
from datetime import datetime

# Set random seed
keras.utils.set_random_seed(316)

def main():
    # Number of sensors in observation
    num_sensors = 32

    # Size of data set
    size = 8

    # Create data set
    dataset = SineWaves(num_sensors, size, batch_size=1)
    coordinate_dim = dataset.coordinate_dim
    num_channels = dataset.num_channels

    # Create model
    model = ContinuityModel(
        coordinate_dim=coordinate_dim,
        num_channels=num_channels,
        num_sensors=num_sensors,
        width=128,
        depth=128,
    )
    
    # Train model
    load = False
    if load:
        model.load_weights("model.weights.h5")
    else:
        optimizer = keras.optimizers.SGD(learning_rate=1e-6)
        model.compile(loss="mse", optimizer=optimizer)
    
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        model.fit(dataset, epochs=1000, callbacks=[
            keras.callbacks.TensorBoard(log_dir=f'./logs/{timestamp}'),
            keras.callbacks.LearningRateScheduler(lambda _, lr: lr * 0.999)
        ])
        model.save_weights("model.weights.h5")

    # Plot
    for i in range(size):
        obs = dataset.get_observation(i)
        plt.cla()
        plot_observation(obs)
        plot_evaluation(model, dataset, obs)
        plt.savefig(f"plot_{i}.png")

if __name__ == '__main__':
    main()