import os
import sys
import pickle
import pandas as pd
from typing import Tuple, Optional


_awf_model = None
_encoder = None


def load_models(
    model_path: Optional[str] = None,
    encoder_path: Optional[str] = None,
) -> Tuple[object, object]:
    """
    Load the AdaptiveWeightedFusion model and OneHotEncoder once and cache them.
    Paths can be provided or read from env vars MODEL_AWF_PATH and MODEL_ENCODER_PATH.
    """
    global _awf_model, _encoder
    if _awf_model is not None and _encoder is not None:
        return _awf_model, _encoder

    model_path = model_path or os.getenv("MODEL_AWF_PATH", "awf_model.pkl")
    encoder_path = encoder_path or os.getenv("MODEL_ENCODER_PATH", "encoder.pkl")

    # Ensure the pickled class references are resolvable
    # Some pickles may reference 'Models.Classifier' or just 'Classifier'
    try:
        from Models import Classifier as _classifier_module
        # Map both names to support different pickle origins
        sys.modules.setdefault("Models.Classifier", _classifier_module)
        sys.modules.setdefault("Classifier", _classifier_module)
    except Exception:
        # If import fails, continue; pickle may still load if not needed
        pass

    with open(model_path, "rb") as f:
        _awf_model = pickle.load(f)
    with open(encoder_path, "rb") as f:
        _encoder = pickle.load(f)

    return _awf_model, _encoder


def classify_transaction(domain: str, amount: float, time_hms: str) -> str:
    """
    Classify a transaction as 'Fraud' or 'Legit'.

    Inputs:
      - domain: domain string seen during training (OneHotEncoder must know it)
      - amount: numeric amount
      - time_hms: time-of-day string formatted as HH:MM:SS

    Returns:
      - prediction label as string (e.g., 'Fraud' or 'Legit')
    """
    awf_model, encoder = load_models()

    # Convert time to seconds matching training preprocessing
    time_seconds = pd.to_timedelta(time_hms).total_seconds()

    # One-hot encode domain using the fitted encoder
    domain_encoded = encoder.transform([[domain]]).toarray()
    domain_columns = encoder.get_feature_names_out(["Domain"])  # expected col names

    # Base numeric features
    input_df = pd.DataFrame({
        "Amount": [amount],
        "Time_seconds": [time_seconds],
    })

    # Add encoded domain columns to match training feature space
    for i, col in enumerate(domain_columns):
        input_df[col] = domain_encoded[0][i]

    # The model's predict handles scaling internally via its scaler attribute
    y_pred = awf_model.predict(input_df)
    return str(y_pred[0])


