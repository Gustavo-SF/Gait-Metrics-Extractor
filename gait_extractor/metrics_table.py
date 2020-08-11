import numpy as np
import pandas as pd


def create_table(**Kwargs):
    columns = list()
    values = list()
    for key, value in Kwargs.items():
        columns.append(key)
        values.append(value)

    df = pd.DataFrame(
        np.array([values]),
        columns = columns
    )
    return df