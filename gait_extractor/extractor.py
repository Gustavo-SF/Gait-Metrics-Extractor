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

class extractor:
    def __init__(self, file_path):
        self.data = pd.read_csv(file_path, header=None)
    def filter_for_activity(self, window, ssd_thres, minimum_wb):
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
        
    def extract_metrics(self, patient_height, start = 0, end = 0.01):
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
            
        scale = index 
        thres = 0.0  # Can be adjusted to 0.65 for more complicated scenarios.

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
        "Gait Velocity": round(metrics[0],2),
        "Cadence": round(metrics[1],2),
        "Stride length": round(metrics[5],2),
        "Stride velocity": round(metrics[6],2),
        "Step length": round(metrics[8],2),
        "Step velocity": round(metrics[9],2),
        "Stance phase": round(metrics[2],2),
        "Swing phase": round(metrics[3],2),
        "Double support phase": round(metrics[4],2),
        "Step time": round(metrics[7],2),
        "Stance time": round(metrics[10],2),
        "Swing time": round(metrics[11],2),
        "Double support time": round(metrics[12],2),
        "Stride time variability": round(metrics[13],4),
        "Step length variability": round(metrics[14],4),
        "Step time variability": round(metrics[15],4),
        "Step velocity variability": round(metrics[16],4),
        "Stance time variability": round(metrics[17],4),
        "Swing time variability": round(metrics[18],4),
        "Double support variability": round(metrics[19],4),
        "Stride time asymetry": round(metrics[20],4),
        "Step time asymetry": round(metrics[21],4),
        "Stance time asymetry": round(metrics[22],4),
        "Swing time asymetry": round(metrics[23],4),
        "Step length asymetry": round(metrics[24],4),
        "Number of Steps": sum(self.IC),
        "Distance Predicted of Walk": round(metrics[9]*len(self.data)/100, 4),
        }
        self.table = create_table(**values)
        
    def IC_FC_visualization(self):
        legend = ['1st CWT','2nd CWT','IC','FC']
        title = 'Optimized ICs and FCs detection'
        IC_values = [self.IC,normalize(self.cwt1)[self.IC]]
        FC_values = [self.FC,normalize(self.cwt2)[self.FC]]
        visualize_signal(legend, title, normalize(self.cwt1), normalize(self.cwt2), IC = IC_values, FC = FC_values)
    
    def visualize_signal(self):
        plt.figure()
        plt.title('Accelerometer Signal')
        plt.plot(range(len(self.data)), self.data[1])
    
    def freq_optimization(self):
        index = identify_scale(self.vz, True)
        # In case the patient is limping
        if index > 35:
            index = index / 2
        print(f"Scale used is {index}")
