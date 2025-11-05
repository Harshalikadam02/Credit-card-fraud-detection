import googlemaps
from datetime import datetime, timedelta
from geopy.distance import geodesic

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
gmaps = googlemaps.Client(key='AIzaSyB9OLTaNIgbICZnqKsJ3rFoAg4aP0zHwYo')

def get_travel_time_estimate(origin, destination):
    try:
        # Request travel time estimate from Google Maps Distance Matrix API
        now = datetime.now()
        response = gmaps.distance_matrix(origin, destination, departure_time=now)
        # print(response)

        # Extract travel time from API response
        travel_time_text = response['rows'][0]['elements'][0]['duration']['text']
        travel_time_value = response['rows'][0]['elements'][0]['duration']['value']

        print(f"Travel time estimate from {origin} to {destination}: {travel_time_text}")

        return travel_time_value  # Return travel time in seconds
    except Exception as e:
        print(f"Error fetching travel time estimate: {e}")
        return None

# Example usage
# origin = "19.186418,73.021341"  # Latitude and longitude of previous location
# destination = "19.143532,73.046473"  # Latitude and longitude of current location
# travel_time = get_travel_time_estimate(origin, destination)
# if travel_time is not None:
#     print(f"Estimated travel time: {travel_time} ")


# Sample data (replace with your data)
previous_location = "19.186418, 73.021341"
current_location = "19.143532, 73.046473"
previous_timestamp = '2024-02-14 21:01:43'
current_timestamp = '2024-02-14 21:05:43'

# Convert timestamp strings to datetime objects
previous_timestamp_dt = datetime.strptime(previous_timestamp, '%Y-%m-%d %H:%M:%S')
current_timestamp_dt = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')

# Get travel time estimate from previous to current location
# travel_time_estimate = get_travel_time_estimate(previous_location, current_location)
# print(travel_time_estimate)
# travel_time_estimate_timedelta = timedelta(minutes=travel_time_estimate)
# print(travel_time_estimate_timedelta)

# Get travel time estimate from previous to current location
travel_time_estimate_seconds = get_travel_time_estimate(previous_location, current_location)
print(travel_time_estimate_seconds)

# Convert travel time estimate from seconds to minutes
travel_time_estimate_minutes = travel_time_estimate_seconds // 60  # Convert seconds to minutes
print(travel_time_estimate_minutes)

# Convert travel time estimate to timedelta object
travel_time_estimate_timedelta = timedelta(minutes=travel_time_estimate_minutes)
print(travel_time_estimate_timedelta)

# Calculate time difference between timestamps
time_difference = current_timestamp_dt- previous_timestamp_dt
print(time_difference)

# # Set a minimum threshold for time difference
# time_threshold = timedelta(minutes=30)  # Example: 30 minutes

# print(time_difference - time_threshold)

# Check if the actual travel time is less than the time difference
if time_difference < travel_time_estimate_timedelta:
    print("Anomaly detected: Suspiciously short time between transactions.")
else:
    print("Transaction appears normal.")