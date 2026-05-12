import serial
import numpy as np
import tensorflow as tf
import joblib

# ==========================================
# LOAD MODEL
# ==========================================

model = tf.keras.models.load_model(
    "models/soil_nn_model.h5"
)

scaler = joblib.load(
    "models/scaler.pkl"
)

label_encoder = joblib.load(
    "models/label_encoder.pkl"
)

# ==========================================
# SERIAL CONNECTION
# ==========================================

ser = serial.Serial(
    'COM3',
    115200
)

print("🚀 Live AI Started")

while True:

    try:

        line = ser.readline().decode().strip()

        # ----------------------------------
        # CLEAN SERIAL TEXT
        # ----------------------------------

        line = line.replace(
            "Temperature: ", ""
        )

        line = line.replace(
            " °C | Humidity: ", ","
        )

        line = line.replace(
            " % | Moisture: ", ","
        )

        # ----------------------------------
        # SPLIT VALUES
        # ----------------------------------

        values = line.split(',')

        temperature = float(values[0])

        humidity = float(values[1])

        moisture = float(values[2])

        # ==================================
        # TEMPORARY VALUES
        # ==================================

        n = 50
        p = 40
        k = 45
        ph = 6.5
        rainfall = 50

        # ==================================
        # FEATURE RATIOS
        # ==================================

        np_ratio = n / (p + 1)

        nk_ratio = n / (k + 1)

        pk_ratio = p / (k + 1)

        # ==================================
        # CREATE INPUT
        # ==================================

        sample = np.array([[
            n,
            p,
            k,
            temperature,
            humidity,
            ph,
            moisture,
            rainfall,
            np_ratio,
            nk_ratio,
            pk_ratio
        ]])

        # ==================================
        # SCALE
        # ==================================

        sample_scaled = scaler.transform(
            sample
        )

        # ==================================
        # PREDICT
        # ==================================

        prediction = model.predict(
            sample_scaled,
            verbose=0
        )

        predicted_class = np.argmax(
            prediction
        )

        label = label_encoder.inverse_transform(
            [predicted_class]
        )[0]

        # ==================================
        # OUTPUT
        # ==================================

        print("\n======================")

        print("🌡 Temperature:", temperature)

        print("💧 Humidity:", humidity)

        print("🌱 Moisture:", moisture)

        print("🧠 Soil Quality:", label)

        print("======================")

    except Exception as e:

        print("Error:", e)