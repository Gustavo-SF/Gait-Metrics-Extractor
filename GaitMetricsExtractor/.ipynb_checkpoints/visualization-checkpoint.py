from matplotlib import pyplot as plt
import numpy as np
from pywt import ContinuousWavelet, scale2frequency


def normalize(dg):
    """
    Helper function to normalize data before plotting it.
    Uses (data-average)/std
    """
    return (dg - np.average(dg)) / np.std(dg)


def visualize_signal(
    legend,
    title,
    *args,
    ylabel = "m/s (normalized)",
    **kwargs
    ):
    """
    Function to visualize the IC and FC detection
    both before and after optimization.
    * *args should be the different plots to visualize,
    normaly, both continuous wavelet tranformations and
    possibly the variations of the axis accelerations
    or velocities.
    * **kwargs can have the plots of the cwt(s) and the
    respective index for IC and FC.
    """
    plt.figure(figsize=(10, 8))
    for arg in args:
        plt.plot(range(len(arg)), arg)
    for event, values in kwargs.items():
        if event == "FC":
            plt.plot(values[0], values[1], "bo", markersize=7)
        elif event == "IC":
            plt.plot(values[0], values[1], "rx", markersize=10)
    plt.legend(legend)
    plt.ylabel(ylabel)
    plt.xlabel("0.01 seconds")
    plt.title(title)
    plt.show()


def showCharts(
    window,
    ranges,
    data_std,
    ssd_threshold,
    ):

    Ln = len(data_std)
    xAxis = np.arange(Ln)
 
    plt.figure()
    plt.title('Walking Bouts over SSD')
    plt.scatter(xAxis,data_std,s=0.7,label = 'SSD', color = "orange")
    plt.axhline(y = ssd_threshold, label = 'SSD Threshold', color='red')

    for pair in ranges:
        if(pair == ranges[-1]):
            plt.axvspan(pair[0]+window, pair[1]+window, facecolor='0.05', alpha = 0.2, zorder=-100,label = 'Walking bout')
        else:
            plt.axvspan(pair[0]+window, pair[1]+window, facecolor='0.05', alpha = 0.2, zorder=-100)
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()


def showCharts_freq(
    ranges,
    data_scale,
    scale_threshold,
    ):

    Ln = len(data_scale)
    xAxis = np.arange(Ln)

    # data_freq = list()

    # wavelet = ContinuousWavelet("gaus2")
    # for i in range(len(data_scale)):
    #     data_freq.append(scale2frequency(wavelet, data_scale[i])/0.01)

    # freq_threshold = scale2frequency(wavelet, scale_threshold)/0.01

    plt.figure()
    plt.title('Walking Bouts over Scale')
    plt.scatter(xAxis, data_scale ,s=0.7,label = 'Scale', color = "green")
    plt.axhline(y = scale_threshold, label = 'Scale Threshold', color='red')

    for pair in ranges:
        if(pair == ranges[-1]):
            plt.axvspan(pair[0], pair[1], facecolor='0.05', alpha = 0.2, zorder=-100,label = 'Walking bout')
        else:
            plt.axvspan(pair[0], pair[1], facecolor='0.05', alpha = 0.2, zorder=-100)
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()
