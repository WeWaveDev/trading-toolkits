import datetime
import random


def get_randomized_start_and_end_date_dict(
    start_time_string='1980-01-01',
    end_time_string='2023-11-01',
    random_days_min=20,
    random_days_max=200,
):
    # Convert string to datetime
    start_date = datetime.datetime.strptime(start_time_string, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_time_string, '%Y-%m-%d')
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    # Randomize a number between 20 and 200
    random_days = random.randint(random_days_min, random_days_max)

    # Calculate end_time_to_match_pattern and start_time_to_match_pattern
    end_time_to_match_pattern = random_date
    start_time_to_match_pattern = end_time_to_match_pattern - datetime.timedelta(days=random_days)

    # Display the results
    print("Start Time to Match Pattern: ", start_time_to_match_pattern)
    print("End Time to Match Pattern: ", end_time_to_match_pattern)
    print("random_days for calendar days ", random_days)
    
    # # convert from datetime to string
    # start_time_to_match_pattern = start_time_to_match_pattern.strftime('%Y-%m-%d')
    # end_time_to_match_pattern = end_time_to_match_pattern.strftime('%Y-%m-%d')
    
    #added hours and minute
    
    start_time_to_match_pattern = datetime.datetime.combine(start_time_to_match_pattern, datetime.datetime.min.time())
    end_time_to_match_pattern = datetime.datetime.combine(end_time_to_match_pattern, datetime.datetime.min.time())
    
    return {
        'start_time_string': start_time_to_match_pattern.strftime('%Y-%m-%d'),
        'end_time_to_string': end_time_to_match_pattern.strftime('%Y-%m-%d'),
        'start_time_millisecond': int(start_time_to_match_pattern.timestamp() * 1000),
        'end_time_millisecond': int(end_time_to_match_pattern.timestamp() * 1000),
    }