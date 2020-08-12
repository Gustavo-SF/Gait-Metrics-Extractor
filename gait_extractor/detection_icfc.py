from scipy.signal import find_peaks
from scipy import constants
from scipy import integrate
from matplotlib import pyplot as plt
import peakutils
import pywt
import numpy as np


def integrate_Hz(data, Hz=100, change_unit=False):
    """
    This function uses integrate package to integrate
    through cummulative trapezoids over the dataset period.
    Hz is the unit of time that we want to integrate over,
    change_unit is in case we want to change from g to m/s**2
    """
    if change_unit:
        data = np.multiply(data, constants.g)
    return integrate.cumtrapz(data, np.array(range(len(data))) / Hz, initial=0)


def IC_FC_detection(data, scale=10, thres=0.65):
    """
    This function will do two continuous wavelet
    tranformations and will detect IC and FC
    respectively by the peak times detected.
    * Data: is the data we want to do the CWT over
    * Scale: is the scale that we want to use to
    extract a specific frequency
    * Thres: is the threshold used for detecting peaks
    """
    wavelet = pywt.ContinuousWavelet("gaus2")  # We use a Gaussian Wavelet

    # IC
    coefs, _ = pywt.cwt(data, scale, wavelet)
    final = coefs[0]
    IC = peakutils.indexes(
        -final, thres, min_dist=25
    )  # predefined interval from 0.25 to 2.25s

    # FC
    coefs_2, _ = pywt.cwt(final, scale, wavelet)
    final_2 = coefs_2[0]
    FC = peakutils.indexes(
        final_2, thres, min_dist=25
    )  # predefined interval from 0.25 to 2.25s

    return final, final_2, IC, FC


def optimize_IC_FCs(IC, FC, time_restraint = False):
    """
    Optimization function does the following steps:

    1) It initiates the first IC
    2) First FC has to the first after IC[0]
    3) It will loop through most of the ICs and FCs
    (there are breaks that can happen)
    4) In case there is no new FC, the loop breaks
    5) The new IC has to be bigger than last FC and
    should be between 0.25 and 2.25 seconds after
    the last IC
    6) In case there is no new IC, the loop breaks
    7) The new FC has to be bigger than last IC and
    should be between 0.25 and 2.25 seconds after
    the last FC
    8) In case an IC finished without a corresponding
    FC, we take away that IC
    9) Returns new values
    """
    if len(IC) == 0 or len(FC) == 0:
        return IC, FC
    new_IC = [IC[0]]
    new_FC = []

    for i in range(len(FC)):
        if FC[i] > IC[0]:
            new_FC = [FC[i]]
            break

    for k in range(max(len(IC), len(FC))):
        try:
            new_FC[k]
        except:
            break
        for i in IC:
            if time_restraint:
                if (i > new_FC[k]) & (i > (new_IC[k] + 25)) & (i < (new_IC[k] + 225)):
                    new_IC.append(i)
                    break
            else:
                if (i > new_FC[k]):
                    new_IC.append(i)
                    break
        try:
            new_IC[k + 1]
        except:
            break
        for j in FC:
            if time_restraint:
                if (j > new_IC[k + 1]) & (j > (new_FC[k] + 25)) & (j < (new_FC[k] + 225)):
                    new_FC.append(j)
                    break
            else:
                if (j > new_IC[k + 1]):
                    new_FC.append(j)
                    break
    if (len(new_IC) - 1) == (len(new_FC)):
        new_IC = new_IC[:-1]

    return new_IC, new_FC


def identify_scale(Vz, plot_this = False):
    """
    This function will identify the main
    wave scale that the data contains.
    It is optimized to identify walking
    bouts from accelerometer' measurements.
    """
    scale = list(np.arange(1, 150, 1))
    wavelet = pywt.ContinuousWavelet("gaus2")

    coefs, _ = pywt.cwt(Vz, scale, wavelet)

    averages = list()
    for i in coefs:
        averages.append(np.average(abs(i)))

    if plot_this:
        plt.plot(scale, averages)
        plt.title("Scale Optimization")
        plt.show()
    # We want to get the first peak as it should
    # symbolize the first main frequency.
    peaks, _ = find_peaks(averages)

    if len(peaks) == 0:
        return max(averages)

    else:
        return peaks[0]