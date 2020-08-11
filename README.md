# Gait Metrics Extractor

1. To install package add folder to your working directory.

2. Go inside the folder and run:

`pip install -e .`

3. Now you can import the constructor.

`from gait_extractor import extractor`

4. Give a DataFrame when initializing the class

`gme = extractor(df)`

5. Extract Metrics

`gme.extract_metrics(patient_height)`

6. Access metrics table

`gme.table`

7. Visualize the signal

`gme.visualize_signal()`
`gme.freq_optimization()`
`gme.IC_FC_visualization()`