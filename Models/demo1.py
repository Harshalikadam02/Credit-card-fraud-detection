import streamlit as st
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import googlemaps
from AnomalyDetection import train_model, predict_anomaly
from twilio.rest import Client
import keys
from Classifier import AdaptiveWeightedFusion

# Load the trained classification model and encoder
model_path = 'awf_model.pkl'  # Specify the file path for the model
encoder_path = 'encoder.pkl'  # Specify the file path for the encoder

with open(model_path, 'rb') as model_file:
    awf_model = pickle.load(model_file)

with open(encoder_path, 'rb') as encoder_file:
    encoder = pickle.load(encoder_file)

# Initialize the Google Maps client with your API key
gmaps = googlemaps.Client(key='AIzaSyB9OLTaNIgbICZnqKsJ3rFoAg4aP0zHwYo')

# Twilio client
client = Client(keys.account_sid, keys.auth_token)

# Get last transaction data from CSV file
def get_last_transaction_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    last_transaction = df.head(1)
    previous_latitude = last_transaction['Latitude'].values[0]
    previous_longitude = last_transaction['Longitude'].values[0]
    previous_location = f"{previous_latitude}, {previous_longitude}"
    previous_timestamp = last_transaction['Timestamp'].values[0]
    return previous_location, previous_timestamp

# Get travel time estimate
def get_travel_time_estimate(origin, destination):
    now = datetime.now()
    response = gmaps.distance_matrix(origin, destination, departure_time=now)
    travel_time_value = response['rows'][0]['elements'][0]['duration']['value']
    return travel_time_value

# Function to classify transaction
def classify_transaction(domain, amount, time):
    # Convert time to seconds
    time_seconds = pd.to_timedelta(time).total_seconds()
    
    # Encode domain using the loaded encoder
    domain_encoded = encoder.transform([[domain]]).toarray()
    
    # Create a DataFrame for the input transaction
    input_transaction = pd.DataFrame({
        'Amount': [amount],
        'Time_seconds': [time_seconds]
    })
    
    # Add encoded domain columns to the input transaction
    domain_columns = encoder.get_feature_names_out(['Domain'])
    for i, col in enumerate(domain_columns):
        input_transaction[col] = domain_encoded[0][i]
        
    
    # Use the model to predict the classification
    prediction = awf_model.predict(input_transaction)
    
    return prediction[0]

# def classify_transaction(domain, amount, time):
#     # Convert time to seconds
#     time_seconds = pd.to_timedelta(time).total_seconds()
    
#     # Encode domain using the loaded encoder
#     # Convert the CSR matrix to a dense array
#     domain_encoded = encoder.transform([[domain]]).toarray()
    
#     # Create a DataFrame for the input transaction
#     input_transaction = pd.DataFrame({
#         'Amount': [amount],
#         'Time_seconds': [time_seconds]
#     })
    
#     # Add encoded domain columns to the input transaction
#     domain_columns = encoder.get_feature_names_out(['Domain'])
#     for i, col in enumerate(domain_columns):
#         input_transaction[col] = domain_encoded[0][i]
    
#     # Retrieve the expected feature names from the scaler
#     expected_feature_names = awf_model.scaler.feature_names_in_
    
#     # Ensure input_transaction columns match the expected feature names and order
#     input_transaction = input_transaction[expected_feature_names]
    
#     # Transform the input data using the scaler
#     input_transaction_scaled = awf_model.scaler.transform(input_transaction)
    
#     # Use the model to predict the classification
#     prediction = awf_model.predict(input_transaction_scaled)
    
#     return prediction[0]



# Streamlit application
st.title("Transaction Attributes")

# Check if the initial form has been submitted and validated as normal
if 'initial_form_submitted' not in st.session_state:
    st.session_state.initial_form_submitted = False
    st.session_state.initial_form_normal = False

# Create a form to take user input for the initial form
if not st.session_state.initial_form_submitted:
    with st.form(key='initial_form'):
        latitude = st.text_input("Latitude")
        longitude = st.text_input("Longitude")

        current_location = f"{latitude}, {longitude}"
        
        date_input = st.date_input("Date")
        time_input = st.time_input("Time")

        # Combine date and time into current_timestamp
        current_timestamp = datetime.combine(date_input, time_input).strftime('%Y-%m-%d %H:%M:%S')

        submit_button = st.form_submit_button(label='Submit')

    # Process form submission
    if submit_button:
        current_timestamp_dt = datetime.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S')
        csv_file_path = r'C:\Users\shaukat\Desktop\Major\data\FraudDetectionProto1.csv'
        previous_location, previous_timestamp = get_last_transaction_data(csv_file_path)

        previous_timestamp_dt = datetime.strptime(previous_timestamp, '%d-%m-%Y %H:%M')

        # Convert previous timestamp to match format
        previous_timestamp_formatted = previous_timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
        previous_timestamp_dt_formatted = datetime.strptime(previous_timestamp_formatted, '%Y-%m-%d %H:%M:%S')

        travel_time_estimate_seconds = get_travel_time_estimate(previous_location, current_location)
        travel_time_estimate_minutes = travel_time_estimate_seconds // 60
        travel_time_estimate_timedelta = timedelta(minutes=travel_time_estimate_minutes)

        time_difference = current_timestamp_dt - previous_timestamp_dt_formatted
        total_seconds = int(time_difference.total_seconds())

        # Format time difference
        hours = total_seconds // 3600
        remainder = total_seconds % 3600
        minutes = remainder // 60
        seconds = remainder % 60
        formatted_time_difference = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

        # Anomaly detection
        if time_difference < travel_time_estimate_timedelta:
            st.warning("Anomaly detected: Suspiciously short time between transactions.")
            st.write(f"Estimated Time difference: {travel_time_estimate_timedelta}")
            st.write(f"Actual Time difference: {formatted_time_difference}")
            
            # Send notification using Twilio
            message = client.messages.create(
                body="A Suspicious Transaction has been detected!",
                from_=keys.twilio_number,
                to=keys.target_number,
            )
            print(message.body)
        else:
            st.success("Transaction appears normal.")
            st.write(f"Estimated Time difference: {travel_time_estimate_timedelta}")
            st.write(f"Actual Time difference: {formatted_time_difference}")
            
            # Update session state
            st.session_state.initial_form_normal = True
            st.session_state.initial_form_submitted = True
            st.session_state.current_timestamp_dt = current_timestamp_dt

# Once initial form submitted and validated as normal, prompt for domain and amount
if st.session_state.initial_form_submitted and st.session_state.initial_form_normal:
    with st.form(key='anomaly_detection_form'):
        domain_name = st.text_input("Domain Name")
        transaction_amount = st.number_input("Transaction Amount", min_value=0.0)

        submit_anomaly_button = st.form_submit_button(label='Check Anomaly')
        back_button = st.form_submit_button(label='Back')

    # Anomaly check form submission
    if submit_anomaly_button:
        file_path = r'C:\Users\shaukat\Desktop\Major\data\FraudDetectionProto1.csv'
        model, scaler = train_model(file_path, domain_name)

        # New data dictionary
        new_data = {
            'Domain': domain_name,
            'Amount': transaction_amount,
            'Timestamp': st.session_state.current_timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
        }

        is_anomaly = predict_anomaly(model, scaler, new_data)
        
        # Display the anomaly result
        if is_anomaly:
            st.error("The new data is an anomaly.")
            
            # Now classify the transaction as fraud or legit using the awf_model
            classification_result = classify_transaction(domain_name, transaction_amount, st.session_state.current_timestamp_dt.strftime('%H:%M:%S'))
            st.write(f"The transaction is classified as: {classification_result}")

        else:
            st.success("The new data is not an anomaly.")

            # Now classify the transaction as fraud or legit using the awf_model
            classification_result = classify_transaction(domain_name, transaction_amount, st.session_state.current_timestamp_dt.strftime('%H:%M:%S'))
            st.write(f"The transaction is classified as: {classification_result}")

    # Handle back button
    if back_button:
        st.session_state.initial_form_submitted = False
        st.session_state.initial_form_normal = False
        st.experimental_rerun()
