import googlemaps
from datetime import datetime

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
gmaps = googlemaps.Client(key='AIzaSyB9OLTaNIgbICZnqKsJ3rFoAg4aP0zHwYo')

def get_travel_time_estimate(origin, destination):
    try:
        # Request travel time estimate from Google Maps Distance Matrix API
        now = datetime.now()
        response = gmaps.distance_matrix(origin, destination, departure_time=now)

        # Extract travel time from API response
        travel_time_text = response['rows'][0]['elements'][0]['duration']['text']
        travel_time_value = response['rows'][0]['elements'][0]['duration']['value']

        print(f"Travel time estimate from {origin} to {destination}: {travel_time_text}")

        return travel_time_value  # Return travel time in seconds
    except Exception as e:
        print(f"Error fetching travel time estimate: {e}")
        return None

# Example usage
origin = "19.186418,73.021341"  # Latitude and longitude of previous location
destination = "19.143532,73.046473"  # Latitude and longitude of current location
travel_time = get_travel_time_estimate(origin, destination)
if travel_time is not None:
    print(f"Estimated travel time: {travel_time} seconds")