import streamlit as st
import datetime
from datetime import datetime, timedelta
import pandas as pd
import googlemaps
from AnomalyDetection import train_model, predict_anomaly

# Initialize the Google Maps client with your API key
gmaps = googlemaps.Client(key='AIzaSyB9OLTaNIgbICZnqKsJ3rFoAg4aP0zHwYo')

# Function to get the last transaction data from a CSV file
def get_last_transaction_data(csv_file_path):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Get the last row of the data (most recent transaction)
    last_transaction = df.head(1)
    
    # Extract latitude and longitude from the last row
    previous_latitude = last_transaction['Latitude'].values[0]
    previous_longitude = last_transaction['Longitude'].values[0]
    
    # Combine latitude and longitude into a single string for previous_location
    previous_location = f"{previous_latitude}, {previous_longitude}"
    
    # Extract the previous timestamp from the last row
    previous_timestamp = last_transaction['Timestamp'].values[0]
    
    # Return the combined location string and timestamp
    return previous_location, previous_timestamp

# Function to get travel time estimate
def get_travel_time_estimate(origin, destination):
    now = datetime.now()
    response = gmaps.distance_matrix(origin, destination, departure_time=now)
    travel_time_value = response['rows'][0]['elements'][0]['duration']['value']
    return travel_time_value

# Streamlit application
st.title("Data Entry Form")

# Create a form to take user input
with st.form(key='data_form'):
    # Input fields for the form
    latitude = st.text_input("Latitude")
    longitude = st.text_input("Longitude")

    # Combine latitude and longitude into current_location
    current_location = f"{latitude}, {longitude}"

    date_input = st.date_input("Date")
    time_input = st.time_input("Time")

    # Combine date and time into current_timestamp
    current_timestamp = datetime.combine(date_input, time_input).strftime('%Y-%m-%d %H:%M:%S')

    # Submit button for the form
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    # Convert current timestamp string to datetime object
    current_timestamp_dt = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')

    # Get previous location and timestamp from CSV file
    csv_file_path = r'C:\Users\shaukat\Desktop\Major\data\FraudDetectionProto1.csv'
    previous_location, previous_timestamp = get_last_transaction_data(csv_file_path)
    
   # Assuming previous_timestamp is read from a CSV file and is in the format '14-10-2021 20:48'
    previous_timestamp_format = '%d-%m-%Y %H:%M'  # Format of 'previous_timestamp'

    # Convert the previous timestamp string to a datetime object
    previous_timestamp_dt = datetime.strptime(previous_timestamp, previous_timestamp_format)

    # Convert previous_timestamp_dt to match the format of current_timestamp
    previous_timestamp_formatted = previous_timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')

    # Assuming previous_timestamp_formatted is now in the format '2024-02-14 21:01:00'

    # Convert previous_timestamp_formatted from string to datetime object
    previous_timestamp_dt_formatted = datetime.strptime(previous_timestamp_formatted, '%Y-%m-%d %H:%M:%S')

    # Get travel time estimate from previous to current location
    travel_time_estimate_seconds = get_travel_time_estimate(previous_location, current_location)
    travel_time_estimate_minutes = travel_time_estimate_seconds // 60  # Convert seconds to minutes
    travel_time_estimate_timedelta = timedelta(minutes=travel_time_estimate_minutes)

    # Calculate time difference between timestamps
    time_difference = current_timestamp_dt - previous_timestamp_dt_formatted
    
    # # Take the absolute value of the time difference if negative
    # if time_difference < timedelta(0):
    #     time_difference = abs(time_difference)

    # Convert time_difference to total seconds
    total_seconds = int(time_difference.total_seconds())

    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    remainder = total_seconds % 3600
    minutes = remainder // 60
    seconds = remainder % 60

    # Format the time difference as HH:MM:SS
    formatted_time_difference = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    # Check if the actual travel time is less than the time difference
    if time_difference < travel_time_estimate_timedelta:
        st.warning("Anomaly detected: Suspiciously short time between transactions.")
        # st.write(travel_time_estimate_seconds)
        # st.write(travel_time_estimate_minutes)
        # st.write(travel_time_estimate_timedelta)
        st.write(current_timestamp_dt)
        st.write(previous_timestamp_dt_formatted)
        # st.write(time_difference)
        st.write(f"Estimated Time difference: {travel_time_estimate_timedelta}")
        st.write(f"Actual Time difference: {formatted_time_difference}")

    else:
        st.success("Transaction appears normal.")
        # st.write(travel_time_estimate_seconds)
        # st.write(travel_time_estimate_minutes)
        # st.write(travel_time_estimate_timedelta)
        st.write(current_timestamp_dt)
        st.write(previous_timestamp_dt_formatted)
        # st.write(time_difference)
        st.write(f"Estimated Time difference: {travel_time_estimate_timedelta}")
        st.write(f"Actual Time difference: {formatted_time_difference}")

        # Create a new form to take additional input for domain name and transaction amount
        with st.form(key='anomaly_detection_form'):
            domain_name = st.text_input("Domain Name")
            transaction_amount = st.number_input("Transaction Amount", min_value=0.0)

            submit_anomaly_button = st.form_submit_button(label='Check Anomaly')

        