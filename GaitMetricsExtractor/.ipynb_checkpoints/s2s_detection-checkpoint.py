import peakutils
import pywt
import numpy
import math
from src.signal_processing import *

def process_s2s (data, dwt_noise = 0.3):
    #have to pass x,y,z,ts,svmarray
    x = data[1]
    y = data[2]
    z = data[3]
    ts = data[0]
    svm = calc_svm(x,y,z)
    mey_result = apply_filter_meyer(svm,noise_sigma=dwt_noise)
    
    meyer_list = mey_result
    ######## FIND MAXIMUM PEAKS #############
    maximums = getMeyerMaxs(meyer_list, min_dist=40)

    ######## FIND MINIMUM PEAKS #############
    minimums = getMeyerMins(meyer_list, min_dist=40)
    mergedLists = mergeAndSortPeaks(maximums, minimums)

    (numberOfSitStand, sit_sta_indexs) = process_only_sitStand(mergedLists)
    (numberOfStandSit, sta_sit_indexs) = process_only_standSit(mergedLists)


    
    sit_sta_indexs_list = [x for t in sit_sta_indexs for x in t]
    sta_sit_indexs_list = [x for t in sta_sit_indexs for x in t]

    xAnt = 0
    xMax = 0
    sit_sta_max_index_array = list()
    for x,y in sit_sta_indexs:
        if (x - y > 40):
            for i in range(y,x + 1):
                sit_sta_max_index_array.append(i)
    
    for x,y in sta_sit_indexs:
        if ((x in sit_sta_max_index_array  or y in sit_sta_max_index_array) ):
            for i in range(y,x + 1):
                sit_sta_max_index_array.append(i)
        
    maxSitSta = 0 if not sit_sta_indexs_list else  numpy.amax(sit_sta_indexs_list)
    minStaSit = maxSitSta if not sta_sit_indexs_list else numpy.amax(sta_sit_indexs_list)


    return sit_sta_max_index_array,len(ts) - 1



def calc_svm(x,y,z):
    vmArray = list()
    for i in range (0,len(x)):
        vm = math.sqrt(x[i] * x[i] + y[i] * y[i] + z[i] * z[i])
        #vm = vm - 1
        #vm = max (math.sqrt(x[i] * x[i] + y[i] * y[i] + z[i] * z[i]) - 1,0)
        vmArray.append(vm)
    #newVmArray = apply_filter_butter(vmArray,20)
    newVmArray = [max(x,0) for x in vmArray]
    return newVmArray


def apply_filter_butter(data_vm, lower_than,order = 4,btype = "low"):
    fs = 100 # Hz
    return butter_bandpass_filter(data_vm, lower_than, fs, order, btype)

#applies the meyer filter using wavelet
def apply_filter_meyer(dsvm, noise_sigma=0.3):
    
    coefs = pywt.wavedec(dsvm, 'dmey', level=5) #was 5

    #Noise threshold
    threshold = noise_sigma * numpy.sqrt(2 * numpy.log2(len(dsvm)))
     
    new_wavelet_coeffs = map(lambda x: pywt.threshold(x, threshold, mode='soft'),coefs)

    return pywt.waverec(list(new_wavelet_coeffs),'dmey')

    
def getMeyerMaxs(wave, min_dist=40):
    max_indexes = peakutils.indexes(wave , min_dist=min_dist)
    maximums = []
    for value in max_indexes:
        if wave[value] > 0.75: #VALUE TO FILTER MAX PEAKS, was .85
            maximums.append(value)
            # print "ARRAY COM OS INDEXES DOS MAXIMOS DO MEYER: \n", max_indexes, "EEEENNNDDDD"
            # print "ARRAY COM OS INDEXES DOS MAXIMOS DO MEYER POS FILTER: \n", maximums, "EEEENNNDDDD"
    return maximums


def getMeyerMins(wave, min_dist=40):
    inverted_meyer = wave * -1  # used to invert the meyer array so i can use the peakutils to obtain the min indexes
    min_indexes = peakutils.indexes(inverted_meyer, min_dist=min_dist)
    #print "Min indexes = ", min_indexes
    minimums = []
    for value in min_indexes:
        #print inverted_meyer[value]
        if inverted_meyer[value] > -0.63: #VALUE TO FILTER MIN PEAKS was -.65
            minimums.append(value)
            # print "ARRAY COM OS INDEXES DOS MINIMOS DO MEYER: \n", min_indexes, "EEEENNNDDDD"
            # print "ARRAY COM OS INDEXES DOS MINIMOS DO MEYER POS FILTER: \n", minimums, "EEEENNNDDDD"
    return minimums


def mergeAndSortPeaks(maximums, minimums):
    mergedLists = []
    for value in maximums:
        mergedLists.append((value, 'max'))
    for value in minimums:
        mergedLists.append((value, 'min'))
    mergedLists.sort()
    return mergedLists

def process_only_sitStand(mergedLists):
    numberOfSitStand = current_max = 0
    trans_indexs = []

    for value in mergedLists:
        (ind, type) = value
        if type == 'max':
            current_max = ind
        if type == 'min' and 0 < ind - current_max <= 100:
            numberOfSitStand += 1
            trans_indexs.append((ind, current_max))
    return numberOfSitStand, trans_indexs

def process_only_standSit(mergedLists):
    numberOfStandSit = current_min = 0
    trans_indexs = []

    for value in mergedLists:
        (ind, type) = value
        if type == 'min':
            current_min = ind
        if type == 'max' and 0 < ind - current_min <= 100:
            numberOfStandSit += 1
            trans_indexs.append((ind, current_min))
    return numberOfStandSit, trans_indexs
