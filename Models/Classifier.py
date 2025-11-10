import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
import numpy as np
import pickle
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class AdaptiveWeightedFusion:
    def __init__(self):
        self.random_forest = GradientBoostingClassifier()
        self.naive_bayes = GaussianNB()
        self.svm = SVC(probability=True)
        self.scaler = MinMaxScaler()
    
    def fit(self, X_train, y_train, X_val, y_val):
        # Normalize features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train classifiers
        self.random_forest.fit(X_train_scaled, y_train)
        self.naive_bayes.fit(X_train_scaled, y_train)
        self.svm.fit(X_train_scaled, y_train)
        
        # Calculate accuracies on validation set
        rf_acc = accuracy_score(y_val, self.random_forest.predict(X_val_scaled))
        nb_acc = accuracy_score(y_val, self.naive_bayes.predict(X_val_scaled))
        svm_acc = accuracy_score(y_val, self.svm.predict(X_val_scaled))
        
        # Calculate weights based on validation accuracies
        total_acc = rf_acc + nb_acc + svm_acc
        self.rf_weight = rf_acc / total_acc
        self.nb_weight = nb_acc / total_acc
        self.svm_weight = svm_acc / total_acc
    
    def predict(self, X):
        # Normalize features
        X_scaled = self.scaler.transform(X)
        
        # Predict probabilities from all classifiers
        rf_probs = self.random_forest.predict_proba(X_scaled)
        nb_probs = self.naive_bayes.predict_proba(X_scaled)
        svm_probs = self.svm.predict_proba(X_scaled)
        
        # Combine predictions using adaptive weights
        weighted_probs = (
            self.rf_weight * rf_probs +
            self.nb_weight * nb_probs +
            self.svm_weight * svm_probs
        )
        
        # Predict the class with the highest probability
        predicted_labels = np.argmax(weighted_probs, axis=1)
        
        # Map predicted labels to class names
        predicted_labels_str = np.where(predicted_labels == 1, 'Legit', 'Fraud')
        
        return predicted_labels_str

# Load the transaction dataset
# Use environment variable for path; default to repository-relative path
data = pd.read_csv(os.getenv("DATA_FIRSTTEST_CSV", "data/Firsttest.csv"))

# Select features and target variable
X = data[['Amount', 'Time', 'Domain']]
y = data['Classification']

# Convert 'Time' to seconds and add as a new column
# Use .copy() to work with a copy of the DataFrame
X_copy = X.copy()
X_copy.loc[:, 'Time_seconds'] = pd.to_timedelta(X['Time']).dt.total_seconds()
X = X_copy.drop(columns=['Time'])

# Handle categorical feature 'Domain' using one-hot encoding
encoder = OneHotEncoder(handle_unknown='ignore')
X_encoded = encoder.fit_transform(X[['Domain']]).toarray()

# Get names of encoded columns using get_feature_names_out
domain_columns = encoder.get_feature_names_out(['Domain'])

# Add encoded features to the dataset
X = X.drop(columns=['Domain'])
X_encoded_df = pd.DataFrame(X_encoded, columns=domain_columns)

# Concatenate encoded columns with the rest of the features
X = pd.concat([X, X_encoded_df], axis=1)


# Split the data into training, validation, and testing sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Initialize SMOTE
smote = SMOTE(random_state=42)

# Apply SMOTE to the training data to balance the dataset
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Initialize the Adaptive Weighted Fusion classifier
awf = AdaptiveWeightedFusion()

# Train the classifier on the resampled training data and original validation data
awf.fit(X_train_resampled, y_train_resampled, X_val, y_val)

# Save the trained Adaptive Weighted Fusion model
model_path = 'awf_model.pkl'
with open(model_path, 'wb') as model_file:
    pickle.dump(awf, model_file)

# Save the OneHotEncoder
encoder_path = 'encoder.pkl'
with open(encoder_path, 'wb') as encoder_file:
    pickle.dump(encoder, encoder_file)

print("Model and encoder saved successfully.")
