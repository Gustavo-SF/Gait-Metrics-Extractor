import pandas as pd
import time
from matplotlib import pyplot as plt

from .walking_bouts import (
    runWalkingBoutDetection,
    applyOffsetRemove,
    applyFilter,
)

from .signal_processing import (
    H_V_orth_sys,
    detrend_data,
    butter_bp_data,
    butter_bandpass_filter,

)
from .detection_icfc import (
    integrate_Hz,
    IC_FC_detection,
    optimize_IC_FCs,
    identify_scale
)

from .metrics_extraction import (
    get_gait_stride,
    get_cadence,
    get_gait_step,
    get_gait_stepLen,
    get_gait_strideLen,
    get_step_velocity,
    get_gait_stance,
    get_gait_swing,
    get_gait_doublesupport,
    variability_b,
    asymmetry
)

from .metrics_table import create_table
from .visualization import visualize_signal, normalize

class Extractor:
    def __init__(self, file):
        """
        Give a DataFrame, or the location of the data as a string, 
        when initializing the class
        """
        if type(file) == str:
            self.data = pd.read_csv(file, header=None)
        elif type(file) == pd.DataFrame:
            self.data = file
        else:
            print("file should be a string path or a dataframe.")
    def filter_for_activity(self, window, ssd_thres, minimum_wb):
        """
        It is possible to filter the bout for activity. 
        This will select the first range with activity.
        """
        data_wb = self.data.copy()
        applyOffsetRemove(data_wb)
        applyFilter(data_wb)
        window = window             
        ssd_threshold = ssd_thres
        minimum = minimum_wb
        ranges_ww = runWalkingBoutDetection(
                    data_wb,
                    ssd_threshold,
                    window,
                    minimum,
                )
        try:
            segment = ranges_ww[0]
            lower = self.data.loc[segment[0],0]
            upper = self.data.loc[segment[1],0]
            self.data = self.data[(self.data[0]>lower) & (self.data[0]<=upper)]
        except:
            print("No movement detected")
        
    def extract_metrics(self, patient_height, start = 0, end = 0.01, thres = 0.0):
        """
        Extract Metrics In this case it takes 3 parameters:
        * The patient_height which should be always provided.
        * start and end to adjust the time to start the bout and the time to end. 
        Both must be positive values and are given in seconds.
        * thres, that establishes a threshold for identifying ICs and FCs 
        in case there is noise in the data and we are only interested in the bigger peaks for identifying ICs and FCs.
        """
        self.data = self.data[start*100:int(end*-100)]
        self.data = H_V_orth_sys(self.data)
        self.data = detrend_data(self.data)

        # Del Din. Paper
        fs = 100 # Hz
        cut_frequency = 20 # Hz
        order = 4
        btype = 'low'
        _ = butter_bp_data(self.data,cut_frequency,fs,order,btype)
        
        self.vz = integrate_Hz(self.data[1], fs, True)
        index = identify_scale(self.vz)

        # In case the patient is limping
        if index > 35:
            index = index / 2

        if index < 8: # less than 8 is too fast
        	index = 8
            
        scale = index 
        thres = thres  # Can be adjusted to 0.65 for more complicated scenarios.

        self.cwt1, self.cwt2, IC, FC = IC_FC_detection(self.vz, scale, thres)
        self.IC, self.FC = optimize_IC_FCs(IC, FC)

        h = integrate_Hz(self.vz)
        h = butter_bandpass_filter(h, 1, fs, btype='high') # Need to validate this

        stride_avg , stride = get_gait_stride(self.IC, self.FC)
        cadence = get_cadence(self.IC)
        step_avg, step = get_gait_step(self.IC)
        steplen_avg, steplen = get_gait_stepLen(h, self.IC, patient_height)
        strideLen_avg, _ = get_gait_strideLen(steplen)
        stepv_avg, stepv = get_step_velocity(steplen, step)
        stance_avg, stance = get_gait_stance(self.IC, self.FC)
        swing_avg, swing = get_gait_swing(stance, stride)
        dsupport_time_avg, dsupport_time = get_gait_doublesupport(self.IC, self.FC)

        stride_var_b = variability_b(stride)
        steplen_var_b = variability_b(steplen)
        step_var_b = variability_b(step)
        stepv_var_b = variability_b(stepv)
        stance_var_b = variability_b(stance)
        swing_var_b = variability_b(swing)
        dsupport_var_b = variability_b(dsupport_time)

        stride_asy = asymmetry(stride)
        step_asy = asymmetry(step)
        stance_asy = asymmetry(stance)
        swing_asy = asymmetry(swing)
        steplen_asy = asymmetry(steplen)

        metrics = [
            (stepv_avg+(strideLen_avg / stride_avg))/2,
            cadence,
            (stance_avg)/(stance_avg+swing_avg)*100,
            (swing_avg)/(stance_avg+swing_avg)*100,
            (dsupport_time_avg)/((dsupport_time_avg+swing_avg)*2)*100,
            strideLen_avg,
            (strideLen_avg / stride_avg),
            step_avg,
            steplen_avg,
            stepv_avg,
            stance_avg,
            swing_avg,
            dsupport_time_avg,
            stride_var_b,
            steplen_var_b,
            step_var_b,
            stepv_var_b,
            stance_var_b,
            swing_var_b,
            dsupport_var_b,
            stride_asy,
            step_asy,
            stance_asy,
            swing_asy,
            steplen_asy,
        ]
        values = {
        "Gait Velocity": metrics[0],
        "Cadence": metrics[1],
        "Stride length": metrics[5],
        "Stride velocity": metrics[6],
        "Step length": metrics[8],
        "Step velocity": metrics[9],
        "Stance phase": metrics[2],
        "Swing phase": metrics[3],
        "Double support phase": metrics[4],
        "Step time": metrics[7],
        "Stance time": metrics[10],
        "Swing time": metrics[11],
        "Double support time": metrics[12],
        "Stride time variability": metrics[13],
        "Step length variability": metrics[14],
        "Step time variability": metrics[15],
        "Step velocity variability": metrics[16],
        "Stance time variability": metrics[17],
        "Swing time variability": metrics[18],
        "Double support variability": metrics[19],
        "Stride time asymetry": metrics[20],
        "Step time asymetry": metrics[21],
        "Stance time asymetry": metrics[22],
        "Swing time asymetry": metrics[23],
        "Step length asymetry": metrics[24],
        "Number of Steps": sum(self.IC),
        "Distance Predicted of Walk": metrics[9]*len(self.data)/100,
        }
        self.table = create_table(**values)
        
    def IC_FC_visualization(self):
        """
        To ensure that we are detecting the right ICs and FCs, this visualization allows 
        to see and adjust accordingly the threshold in the extract metrics function. 
        This should happen in case a person is positioning himself between walking 
        bouts which leads to false positives of ICs and FCs        
        """
        legend = ['1st CWT','2nd CWT','IC','FC']
        title = 'Optimized ICs and FCs detection'
        IC_values = [self.IC,normalize(self.cwt1)[self.IC]]
        FC_values = [self.FC,normalize(self.cwt2)[self.FC]]
        visualize_signal(legend, title, normalize(self.cwt1), normalize(self.cwt2), IC = IC_values, FC = FC_values)
    
    def visualize_signal(self):
        """
        To simply visualize the raw signal.
        """
        plt.figure()
        plt.title('Accelerometer Signal')
        plt.plot(range(len(self.data)), self.data[1])
    
    def freq_optimization(self):
        """
        We can visualize the optimization of the frequency. 
        It should contain one single peak, which is the main frequency of the signal. 
        Visualizing other than one normal peak, can mean that there is some complicated 
        walking pattern which might be leading to wront metrics.
        """
        index = identify_scale(self.vz, True)
        # In case the patient is limping
        if index > 35:
            index = index / 2
        print(f"Scale used is {index}")
