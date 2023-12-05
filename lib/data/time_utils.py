
import datetime


def get_extended_end_time_based_on_milliseconds(start_time_to_match_pattern, end_time_to_match_pattern):
    # Calculate the duration in milliseconds
    duration_millis = end_time_to_match_pattern - start_time_to_match_pattern

    # Calculate half of the duration
    half_duration_millis = duration_millis // 2

    # Calculate the extended end time in milliseconds
    extended_end_time_millis = end_time_to_match_pattern + half_duration_millis

    return extended_end_time_millis