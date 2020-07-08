from datetime import datetime as dt
from datetime import date


def get_time_difference(time_measured, time_start_of_walk):
    """
    This function allows to input a timestamp and a
    time and calculate the difference between both.
        * Time_measured: stands for the timestamp
        * Time_start_of_walk: normal time, in the
        project case it was the video time.

        for example: get_time_difference(124827,"00:07:26")

        It returns the value in centiseconds.
    """
    time_measured_fixed = dt.fromtimestamp(time_measured / 100).time()
    time_object = dt.strptime(time_start_of_walk, "%H:%M:%S").time()
    time_difference = dt.combine(
        date.today(), time_object
    ) - dt.combine(date.today(), time_measured_fixed)
    return time_difference.total_seconds()
