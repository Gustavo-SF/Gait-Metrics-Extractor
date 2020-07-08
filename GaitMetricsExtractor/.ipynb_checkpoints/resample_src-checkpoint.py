import pandas as pd
import numpy as np

def interpolate(df, frequency):
    dx = np.zeros(len(df))
    dy = np.zeros(len(df))
    dz = np.zeros(len(df))
    xSlope = np.zeros(len(df))
    ySlope = np.zeros(len(df))
    zSlope = np.zeros(len(df))
    xIntercept = np.zeros(len(df))
    yIntercept = np.zeros(len(df))
    zIntercept = np.zeros(len(df))

    new_x = []
    new_y = []
    new_z = []

    for i in range(1, len(df)):
        dtime = df.loc[i, 0] - df.loc[i-1, 0]
        dx[i] = df.loc[i, 1] - df.loc[i-1, 1]
        dy[i] = df.loc[i, 2] - df.loc[i-1, 2]
        dz[i] = df.loc[i, 3] - df.loc[i-1, 3]
        xSlope[i] = dx[i] / dtime
        ySlope[i] = dy[i] / dtime
        zSlope[i] = dz[i] / dtime
        xIntercept[i] = df.loc[i, 1]
        yIntercept[i] = df.loc[i, 2]
        zIntercept[i] = df.loc[i, 3]

    df_new = pd.DataFrame()

    time = list(np.around(np.arange(df.loc[0,0], df.loc[len(df)-1, 0], 1/frequency), 2))

    best_j = 0
    for i in range(len(time)):
        best_value = float("inf")
        j = best_j
        for _ in range(15):
            if j == len(df):
                break
            diff = df.loc[j, 0] - time[i]
            if diff > 0.1:
                break

            if abs(diff) < best_value:
                best_value = abs(diff)
                best_j = j
            j+=1
        timeI = time[i] - df.loc[best_j, 0]

        best_value = df.loc[best_j, 0] - time[i]
        new_x.append(xSlope[best_j] * best_value + xIntercept[best_j])
        new_y.append(ySlope[best_j] * best_value + yIntercept[best_j])
        new_z.append(zSlope[best_j] * best_value + zIntercept[best_j])
    
    df_new[0] = time
    df_new[1] = new_x
    df_new[2] = new_y
    df_new[3] = new_z
    return df_new