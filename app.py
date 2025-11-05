import os
from datetime import datetime

import streamlit as st
import googlemaps
from googlemaps import exceptions as gmaps_ex
from dotenv import load_dotenv

from models_service import classify_transaction


def get_gmaps_client() -> googlemaps.Client | None:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return None
    try:
        return googlemaps.Client(key=api_key)
    except Exception:
        return None


def get_travel_time_seconds(gmaps_client: googlemaps.Client, origin: str, destination: str) -> tuple[int | None, str | None]:
    try:
        response = gmaps_client.distance_matrix(origin, destination, departure_time=datetime.now())
        value = int(response['rows'][0]['elements'][0]['duration']['value'])
        return value, None
    except gmaps_ex.ApiError as e:
        return None, f"Google Maps API error: {e}"
    except gmaps_ex.TransportError as e:
        return None, f"Network error contacting Google Maps: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def render_location_anomaly_section():
    st.header("Location Anomaly Check")

    gmaps_client = get_gmaps_client()
    if gmaps_client is None:
        if not os.getenv("GOOGLE_MAPS_API_KEY", ""):
            st.warning("Set GOOGLE_MAPS_API_KEY in your .env to enable this section.")
        else:
            st.error("Failed to initialize Google Maps client. Check API key and restrictions.")
        return

    col1, col2 = st.columns(2)
    with col1:
        prev_lat = st.text_input("Previous Latitude", key="prev_lat")
        prev_lng = st.text_input("Previous Longitude", key="prev_lng")
        prev_ts = st.text_input("Previous Timestamp (YYYY-MM-DD HH:MM:SS)", key="prev_ts")
    with col2:
        curr_lat = st.text_input("Current Latitude", key="curr_lat")
        curr_lng = st.text_input("Current Longitude", key="curr_lng")
        curr_ts = st.text_input("Current Timestamp (YYYY-MM-DD HH:MM:SS)", key="curr_ts")

    if st.button("Check Location Anomaly"):
        try:
            prev_dt = datetime.strptime(prev_ts, '%Y-%m-%d %H:%M:%S')
            curr_dt = datetime.strptime(curr_ts, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            st.error("Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
            return

        origin = f"{prev_lat}, {prev_lng}"
        destination = f"{curr_lat}, {curr_lng}"
        travel_secs, travel_err = get_travel_time_seconds(gmaps_client, origin, destination)
        if travel_secs is None:
            st.error(travel_err or "Failed to fetch travel time from Google Maps API.")
            return

        actual_diff_secs = int((curr_dt - prev_dt).total_seconds())
        is_anomaly = actual_diff_secs < travel_secs

        st.write(f"Estimated travel time: {travel_secs // 60} minutes")
        st.write(f"Actual time difference: {actual_diff_secs // 60} minutes")
        if is_anomaly:
            st.error("Anomaly detected: actual time is less than estimated travel time.")
        else:
            st.success("No anomaly based on travel time.")


def render_classification_section():
    st.header("Transaction Classification")

    domain = st.text_input("Domain (e.g., example.com)")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    time_hms = st.text_input("Time of day (HH:MM:SS)", value="12:00:00")

    if st.button("Classify Transaction"):
        try:
            # sanity parse time
            _ = datetime.strptime(time_hms, "%H:%M:%S")
        except ValueError:
            st.error("Invalid time format. Use HH:MM:SS")
            return

        try:
            label = classify_transaction(domain=domain, amount=amount, time_hms=time_hms)
            st.success(f"Prediction: {label}")
        except Exception as e:
            st.error(f"Classification failed: {e}")


def main():
    load_dotenv()  # load .env if present
    st.title("Fraud Detection Demo")
    st.caption("Location anomaly check and transaction classification")

    render_location_anomaly_section()
    st.divider()
    render_classification_section()


if __name__ == "__main__":
    main()


