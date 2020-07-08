# Gait Metrics Extractor

1. To install package add folder to your working directory.

2. Run:

`pip install -e GaitMetricsExtraction/`

3. Now you can import the constructor.

`from GaitMetricsExtractor.GaitMetricsExtractor import GaitMetricsExtractor`

4. Give a DataFrame when initializing the class

`gme = GaitMetricsExtraction(df)`

5. Extract Metrics

`gme.extract_metrics(patient_height)`

6. Access metrics table

`gme.table`

7. Visualize the signal

`gme.visualize_signal()`
`gme.freq_optimization()`
`gme.IC_FC_visualization()`