import tensorflow as tf
import joblib
import numpy as np

# -------- LOAD MODEL --------
model = tf.keras.models.load_model("models/soil_nn_model.h5")

# -------- LOAD SCALER + LABEL ENCODER --------
scaler = joblib.load("models/scaler.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

# -------- INPUT DATA --------
n = 50
p = 30
k = 40
temp = 25
humidity = 60

# -------- FEATURE ENGINEERING --------
moisture = humidity * 0.7
rainfall = 50

# ✅ ONLY 7 FEATURES (MATCH TRAINING)
sample = np.array([[n, p, k, temp, humidity, moisture, rainfall]])

# -------- SCALE --------
sample_scaled = scaler.transform(sample)

# -------- PREDICT --------
prediction = model.predict(sample_scaled)

cls = np.argmax(prediction)

# -------- DECODE LABEL --------
result = label_encoder.inverse_transform([cls])[0]

print("Prediction:", result)