from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV file
file_path = r'C:\Users\shaukat\Desktop\Major\data\FraudDetectionProto1.csv'
historical_data = pd.read_csv(file_path)

# Convert timestamp string to datetime object
historical_data['Timestamp'] = pd.to_datetime(historical_data['Timestamp'])

# Extract time component in seconds since midnight
historical_data['Time'] = historical_data['Timestamp'].dt.hour * 3600 + historical_data['Timestamp'].dt.minute * 60 + historical_data['Timestamp'].dt.second

# Get input from the user
domain = input("Enter domain: ")
amount = float(input("Enter transaction amount: "))
timestamp = input("Enter timestamp (YYYY-MM-DD HH:MM:SS): ")

# Create a dictionary for the new data
new_data = {
    'Domain': domain,
    'Amount': amount,
    'Timestamp': timestamp
}

# Filter historical data by domain
domain_data = historical_data[historical_data['Domain'] == new_data['Domain']].copy()

# Drop rows with missing values
domain_data.dropna(inplace=True)

# Standardize the features
scaler = StandardScaler()
X = domain_data[['Amount', 'Time']]
X_scaled = scaler.fit_transform(X)

# Train the Isolation Forest model
model = IsolationForest(contamination=0.01)
model.fit(X_scaled)

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

# Output the result
if is_anomaly == -1:
    print("The new data is an anomaly.")
else:
    print("The new data is not an anomaly.")

# Visualize anomalies
plt.figure(figsize=(10, 6))
plt.scatter(domain_data['Time'], domain_data['Amount'], color='blue', label='Historical Data')
plt.scatter(new_data['Time'], new_data['Amount'], color='red', marker='o', label='New Data')
plt.title('Amount vs Time with Anomalies')
plt.xlabel('Time (Seconds)')
plt.ylabel('Amount')
plt.legend()
plt.grid(True)
plt.show()
