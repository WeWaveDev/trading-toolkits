import datetime
import random


def get_randomized_start_and_end_date():
    # Randomize a date between 2000-01-01 and 2023-11-01
    start_date = datetime.date(1980, 1, 1)
    end_date = datetime.date(2023, 11, 1)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    # Randomize a number between 20 and 200
    random_days = random.randint(20, 200)

    # Calculate end_time_to_match_pattern and start_time_to_match_pattern
    end_time_to_match_pattern = random_date
    start_time_to_match_pattern = end_time_to_match_pattern - datetime.timedelta(days=random_days)

    # Display the results
    print("Start Time to Match Pattern: ", start_time_to_match_pattern)
    print("End Time to Match Pattern: ", end_time_to_match_pattern)
    print("random_days: ", random_days)
    
    # convert from datetime to string
    start_time_to_match_pattern = start_time_to_match_pattern.strftime('%Y-%m-%d')
    end_time_to_match_pattern = end_time_to_match_pattern.strftime('%Y-%m-%d')
    
    return start_time_to_match_pattern, end_time_to_match_pattern