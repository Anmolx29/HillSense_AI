import time
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

# =====================================
# FIREBASE CONNECTION
# =====================================

cred = credentials.Certificate(
    'firebase_key.json'
)

firebase_admin.initialize_app(cred, {
    'databaseURL':
    'https://hillsenseai-default-rtdb.firebaseio.com/'
})

# =====================================
# LOAD AI MODEL
# =====================================

model = tf.keras.models.load_model(
    'models/soil_nn_model.h5'
)

scaler = joblib.load(
    'models/scaler.pkl'
)

encoder = joblib.load(
    'models/label_encoder.pkl'
)

print('=================================')
print('🌱 HillSense AI Server Started')
print('=================================')

# =====================================
# MAIN LOOP
# =====================================

while True:

    try:

        # ---------------------------------
        # READ SENSOR DATA
        # ---------------------------------

        sensor_ref = db.reference('/sensor')

        sensor_data = sensor_ref.get()

        if sensor_data:

            temperature = sensor_data.get(
                'temperature', 25
            )

            humidity = sensor_data.get(
                'humidity', 50
            )

            moisture = sensor_data.get(
                'moisture', 50
            )

            # ---------------------------------
            # DEFAULT SOIL VALUES
            # ---------------------------------

            n = 50
            p = 40
            k = 45

            ph = 6.5

            rainfall = 50

            # ---------------------------------
            # FEATURE ENGINEERING
            # ---------------------------------

            np_ratio = n / (p + 1)

            nk_ratio = n / (k + 1)

            pk_ratio = p / (k + 1)

            # ---------------------------------
            # CREATE INPUT SAMPLE
            # ---------------------------------

            sample = pd.DataFrame([[

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

            ]], columns=[

                'n',
                'p',
                'k',
                'temperature',
                'humidity',
                'ph',
                'moisture',
                'rainfall',
                'np_ratio',
                'nk_ratio',
                'pk_ratio'

            ])

            # ---------------------------------
            # SCALE INPUT
            # ---------------------------------

            sample_scaled = scaler.transform(
                sample
            )

            # ---------------------------------
            # AI PREDICTION
            # ---------------------------------

            prediction = model.predict(
                sample_scaled,
                verbose=0
            )

            predicted_class = np.argmax(
                prediction
            )

            soil_quality = encoder.inverse_transform([
                predicted_class
            ])[0]

            # =====================================
            # IRRIGATION RECOMMENDATION
            # =====================================

            if moisture < 30:

                irrigation = (
                    "High irrigation required"
                )

            elif moisture < 50:

                irrigation = (
                    "Moderate irrigation required"
                )

            else:

                irrigation = (
                    "Soil moisture is sufficient"
                )

            # =====================================
            # CROP RECOMMENDATION
            # =====================================

            if temperature > 30 and humidity > 60:

                crop = "Rice"

            elif moisture < 40:

                crop = "Millets"

            elif humidity < 50:

                crop = "Wheat"

            else:

                crop = "Maize"

            # =====================================
            # FERTILIZER RECOMMENDATION
            # =====================================

            if soil_quality == "Poor":

                fertilizer = (
                    "Use NPK fertilizer"
                )

            elif soil_quality == "Medium":

                fertilizer = (
                    "Use Organic Compost"
                )

            else:

                fertilizer = (
                    "Minimal fertilizer needed"
                )

            # =====================================
            # SAVE TO FIREBASE
            # =====================================

            prediction_ref = db.reference(
                '/prediction'
            )

            prediction_ref.set({

                'soil_quality': soil_quality,

                'temperature': temperature,

                'humidity': humidity,

                'moisture': moisture,

                'irrigation': irrigation,

                'crop': crop,

                'fertilizer': fertilizer,

                'timestamp': int(time.time())

            })

            # =====================================
            # TERMINAL OUTPUT
            # =====================================

            print('==============================')

            print(
                '🌡 Temperature:',
                temperature
            )

            print(
                '💧 Humidity:',
                humidity
            )

            print(
                '🌱 Moisture:',
                moisture
            )

            print(
                '🤖 Soil Quality:',
                soil_quality
            )

            print(
                '🚿 Irrigation:',
                irrigation
            )

            print(
                '🌾 Crop:',
                crop
            )

            print(
                '🧪 Fertilizer:',
                fertilizer
            )

        else:

            print(
                '⚠ No sensor data found'
            )

        time.sleep(5)

    except Exception as e:

        print('❌ ERROR:', e)

        time.sleep(5)