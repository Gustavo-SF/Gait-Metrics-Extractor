# Gait Metrics Extractor
Developed to extract gait metrics from accelerometry data. 
*WARNING*: Data should concern *only* walking data.

## Data

Data should follow the next requirements:
* Lower back placement
* Three axis acceleration data
* Sampling rate of 100Hz

## Instalation

1. To install package add folder to your working directory.

2. Go inside the folder and run:

`pip install .`
You can replace `.` by the location of the folder if you want to install it from outside the folder.

## Using Gait Metrics Extractor

The package consists of:
1. A Class which allows to do a simple filtering of activity, extracting metrics, and visualizing some graphs
2. Access to the multiple functions used for metrics extraction, from signal processing to calculating the metrics themselves.

1. You can import the constructor in the following way:

`from gait_extractor import Extractor`

2. Give a DataFrame, or the location of the data as a string, when initializing the class:

`gme = Extractor(df)`
or
`gme = Extractor('data/data.csv')`

5. Extract Metrics
In this case it takes 3 parameters. 
* The `patient_height` which should be *always* provided.
* `start` and `end` to adjust the time to start the bout and the time to end. Both must be positive values and are given in seconds.
* `thres`, that establishes a threshold for identifying ICs and FCs in case there is noise in the data and we are only interested in the bigger peaks for identifying ICs and FCs.

Note: IC=Initial Contact points FC=Final Contact points

`gme.extract_metrics(patient_height, start=1, end=1, thres=0.65)`

Ideally we want to avoid using the start, end and threshold. In case they are used, they should be supervised with the help of the visualization functions.

6. Access metrics table
After extracting the metrics, they are not immediately visible. For this we must access the table in the following way:

`gme.table`

The table provides 25 gait metrics, the number of steps found, which is equivalent to the number of ICs, and the predicted distance walked, which is the gait velocity times the number of time-length of the bout.

7. Visualize the signal

There are three options to visualize the signal. It is advised to visualize the signal every time a new dataset is used, as there can be outliers in patterns of walking which lead to problems with the metrics.

* We can visualize the raw signal
`gme.visualize_signal()`

* We can visualize the optimization of the frequency. It should contain one single peak, which is the main frequency of the signal. Visualizing other than one normal peak, can mean that there is some complicated walking pattern which might be leading to wront metrics.
`gme.freq_optimization()`

* To ensure that we are detecting the right ICs and FCs, this visualization allows to see and adjust accordingly the threshold in the extract metrics function. This should happen in case a person is positioning himself between walking bouts which leads to false positives of ICs and FCs.
`gme.IC_FC_visualization()`