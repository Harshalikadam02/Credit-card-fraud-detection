from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

def train_model(file_path, domain_name):
    # Load historical data
    historical_data = pd.read_csv(file_path)

    # Convert timestamp to datetime and extract time
    historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'])
    historical_data['Time'] = (
        historical_data['Timestamp'].dt.hour * 3600
        + historical_data['Timestamp'].dt.minute * 60
        + historical_data['Timestamp'].dt.second
    )

    # Convert the domain names in historical data to lowercase for consistency
    historical_data['Domain'] = historical_data['Domain'].str.lower()

    # Convert the user input domain name to lowercase for consistency
    domain_name = domain_name.lower()

    # Filter data by domain
    domain_data = historical_data[historical_data['Domain'] == domain_name]

    # Check if domain_data is empty
    if domain_data.empty:
        raise ValueError(f"No data available for the domain: {domain_name}")

    # Drop missing values
    # # Instead of this:
    # domain_data.dropna(inplace=True)
    # You could use:
    domain_data = domain_data.dropna()

    # Standardize the features
    scaler = StandardScaler()
    X = domain_data[['Amount', 'Time']]
    X_scaled = scaler.fit_transform(X)

    # Train the Isolation Forest model
    model = IsolationForest(contamination=0.01)
    model.fit(X_scaled)

    return model, scaler

def predict_anomaly(model, scaler, new_data):
    # Convert timestamp string to datetime object
    new_data['Timestamp'] = pd.to_datetime(new_data['Timestamp'])
    
    # Extract time component for the new data
    new_data['Time'] = new_data['Timestamp'].hour * 3600 + new_data['Timestamp'].minute * 60 + new_data['Timestamp'].second
    
    # Create a DataFrame for the new data and maintain feature names
    new_data_df = pd.DataFrame({
        'Amount': [new_data['Amount']],
        'Time': [new_data['Time']]
    })
    
    # Scale the features of the new data
    new_data_scaled = scaler.transform(new_data_df)
    
    # Predict if the new data is an anomaly
    is_anomaly = model.predict(new_data_scaled)
    
    # Return the prediction result
    return is_anomaly == -1
