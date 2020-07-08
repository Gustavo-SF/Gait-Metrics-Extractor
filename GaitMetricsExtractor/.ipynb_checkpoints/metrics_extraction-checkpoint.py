import numpy as np


def get_gait_doublesupport(IC, FC, Hz = 100):
    """
    Get Double Support:
    The time that both feet were on the ground
    """
    Ln = len(IC)

    dsupport_time = np.empty((Ln,1))
    for i in range(Ln):
        dsupport_time[i] = (FC[i]-IC[i]) / Hz
    dsupport_time_avg = np.average(dsupport_time)

    return dsupport_time_avg, dsupport_time


def get_gait_stance(IC, FC, Hz = 100):
    """
    Get Stance Time: The time that a foot is in contact with
    the ground by introducing the IC and FC times, and the 
    frequency of the data. Default for AX3 is 100Hz
    """
    Ln = len(IC)

    stance_time = np.empty((Ln-1,1))
    for i in range(Ln-1):
        stance_time[i] = (FC[i+1]-IC[i]) / Hz
    stance_time_avg = np.average(stance_time)

    return stance_time_avg, stance_time


def get_gait_stride(IC, FC, Hz = 100):
    """
    Get Stride Time: The time since a foot has made 
    contact to the next time it makes contact with the 
    ground. 
    Just need to introduce the IC and FC times, and the 
    frequency of the data. Default for AX3 is 100Hz
    """
    Ln = len(IC)

    stride_time = np.empty((Ln-2,1))
    for i in range(Ln-2):
        stride_time[i] = (IC[i+2]-IC[i]) / Hz
    stride_time_avg = np.average(stride_time)

    return stride_time_avg, stride_time


def get_gait_swing(stance_time, stride_time):
    """
    Get Swing Time: The time that a foot is suspended.
    Just need to introduce the swing and stride times.
    """
    swing_time = stride_time - stance_time[:-1]
    swing_time_avg = np.average(swing_time)

    return swing_time_avg, swing_time


def get_gait_step(IC, Hz = 100):
    """
    Get Step Time: The time from a initial contact of
    one foot to the the initial contact of the other 
    with the ground.
    Just need to introduce the IC times and and the 
    frequency of the data. Default for AX3 is 100Hz
    """
    Ln = len(IC)
    step_time = np.empty((Ln-1,1))
    for i in range(Ln-1):
        step_time[i] = (IC[i+1]-IC[i]) / Hz
    step_time_avg = np.average(step_time)

    return step_time_avg, step_time


def get_gait_strideLen(stepLen):
    """
    Get distance walked after two steps
    """
    strideLen = list()
    for i in range(len(stepLen)-1):
        stridelen = stepLen[i] + stepLen[i+1]
        strideLen.append(stridelen)
    strideLen_avg = np.average(strideLen)
    return strideLen_avg, strideLen


def get_gait_stepLen(h, IC, patient_height):
    """
    Get the step length by using the height (h)
    variation from one step to the next (max, min)
    and applying the pendulum formula with the
    patient's height.
    """
    Ln = len(IC)
    min_height = np.empty((Ln-1,1))
    max_height = np.empty((Ln-1,1))

    for i in range(Ln-1):
        min_height[i] = min(h[IC[i]:IC[i+1]])
        max_height[i] = max(h[IC[i]:IC[i+1]])
    height = np.subtract(max_height,min_height) 

    wearableHeight = patient_height * 0.53 # +-

    step_length = 2 * np.sqrt(
        np.subtract(
            2 * wearableHeight * height,
            height**2
        )
    )  # 2*sqrt(2lh - h^2)

    step_length_avg = np.average(step_length)
    return step_length_avg, step_length


def get_step_velocity(step_length,step_time):
    """
    By knowing the step_length and step_time we  can
    easily get the volocity. this function returns that.
    """
    step_velocity = step_length / step_time
    step_velocity_avg = np.average(step_velocity)
    return step_velocity_avg, step_velocity


def variability_a(data):
    """
    This variability measure checks for the variability by
    taking in account the right and the left variability.
    """
    right = [data[i] for i in range(len(data)) if i%2==0] #TODO find a better way to identify left and right
    left = [data[i] for i in range(len(data)) if i%2!=0]

    return np.sqrt((np.var(left)+np.var(right))/2) 


def variability_b(data):
    """
    Returns overall variability of the dataset.
    """
    return np.std(data)


def asymmetry(data):
    """
    Returns the asymmetry or difference between the measures on
    both sides of the walk (right and left)
    """
    right = [data[i] for i in range(len(data)) if i%2==0] #TODO find a better way to identify left and right
    left = [data[i] for i in range(len(data)) if i%2!=0]

    return abs(np.average(left)-np.average(right))


def get_cadence(IC):
    """
    We assume that ICs are in centiseconds.
    Through the ICs we get the number of steps
    per minute = cadence
    """
    return len(IC)/((IC[-1]-IC[0])/6000)