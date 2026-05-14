import os

os.environ["TF_USE_LEGACY_KERAS"] = "0"

from flask import Flask
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

# =====================================
# FLASK APP
# =====================================

app = Flask(__name__)

# =====================================
# FIREBASE
# =====================================

cred = credentials.Certificate(
    'firebase_key.json'
)

firebase_admin.initialize_app(

    cred,

    {
        'databaseURL':
        'https://hillsenseai-default-rtdb.firebaseio.com/'
    }

)

# =====================================
# LOAD MODEL
# =====================================

model = tf.keras.models.load_model(

    "models/soil_quality.keras",

    compile=False

)

# =====================================
# LOAD SCALER
# =====================================

scaler = joblib.load(
    'models/scaler.pkl'
)

print("AI Cloud Server Started")

# =====================================
# HOME ROUTE
# =====================================

@app.route('/')

def home():

    return 'HillSense AI Cloud Server Running'

# =====================================
# PREDICTION ROUTE
# =====================================

@app.route('/predict')

def predict():

    try:

        sensor_ref = db.reference('/sensor')

        sensor_data = sensor_ref.get()

        if not sensor_data:

            return {
                'error': 'No sensor data'
            }

        # =============================
        # SENSOR VALUES
        # =============================

        temperature = float(
            sensor_data.get(
                'temperature', 25
            )
        )

        humidity = float(
            sensor_data.get(
                'humidity', 50
            )
        )

        moisture = float(
            sensor_data.get(
                'moisture', 50
            )
        )

        # =============================
        # FIX INVALID VALUES
        # =============================

        if np.isnan(temperature):
            temperature = 0.0

        if np.isnan(humidity):
            humidity = 0.0

        if np.isnan(moisture):
            moisture = 0.0

        # =============================
        # DYNAMIC VALUES
        # =============================

        n = int(max(20, min(90, moisture + humidity / 2)))

        p = int(max(15, min(80, humidity)))

        k = int(max(20, min(85, temperature * 2)))

        ph = round(
            5.5 + (humidity / 100),
            2
        )

        rainfall = int(
            humidity * 1.5
        )

        # =============================
        # FEATURE ENGINEERING
        # =============================

        np_ratio = n / (p + 1)

        nk_ratio = n / (k + 1)

        pk_ratio = p / (k + 1)

        # =============================
        # CREATE DATAFRAME
        # =============================

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

        # =============================
        # SCALE INPUT
        # =============================

        sample_scaled = scaler.transform(
            sample
        )

        # =============================
        # FIX NAN / INFINITY
        # =============================

        sample_scaled = np.nan_to_num(

            sample_scaled,

            nan=0.0,

            posinf=0.0,

            neginf=0.0

        )

        # =============================
        # AI PREDICTION
        # =============================

        prediction = model.predict(

            sample_scaled,

            verbose=0

        )

        prediction = np.nan_to_num(

            prediction,

            nan=0.0,

            posinf=0.0,

            neginf=0.0

        )

        # =============================
        # SAFE CLASS PREDICTION
        # =============================

        predicted_class = int(
            np.nanargmax(prediction)
        )

        # =============================
        # LABELS
        # =============================

        labels = [

            "Poor",

            "Medium",

            "Good"

        ]

        if predicted_class >= len(labels):

            predicted_class = 1

        soil_quality = labels[predicted_class]

        # =================================
        # REALTIME SOIL QUALITY ADJUSTMENT
        # =================================

        if moisture < 20:

            soil_quality = "Poor"

        elif moisture > 70 and humidity > 70:

            soil_quality = "Good"

        elif temperature > 35:

            soil_quality = "Poor"

        else:

            soil_quality = "Medium"

        # =============================
        # IRRIGATION
        # =============================

        if moisture < 20:

            irrigation = (
                'Very High irrigation required'
            )

        elif moisture < 40:

            irrigation = (
                'Moderate irrigation required'
            )

        elif moisture < 60:

            irrigation = (
                'Low irrigation required'
            )

        else:

            irrigation = (
                'No irrigation needed'
            )

        # =============================
        # CROP RECOMMENDATION
        # =============================

        if moisture < 25:

            crop = 'Millets'

        elif temperature > 32:

            crop = 'Rice'

        elif humidity < 40:

            crop = 'Wheat'

        elif soil_quality == 'Good':

            crop = 'Sugarcane'

        else:

            crop = 'Maize'

        # =============================
        # FERTILIZER
        # =============================

        if soil_quality == 'Poor':

            fertilizer = (
                'Use NPK fertilizer'
            )

        elif soil_quality == 'Medium':

            fertilizer = (
                'Use Organic Compost'
            )

        elif soil_quality == 'Good':

            fertilizer = (
                'Minimal fertilizer needed'
            )

        else:

            fertilizer = (
                'Balanced fertilizer recommended'
            )

        # =============================
        # SAVE TO FIREBASE
        # =============================

        prediction_ref = db.reference(
            '/prediction'
        )

        prediction_ref.set({

            'soil_quality':
                str(soil_quality),

            'temperature':
                float(temperature),

            'humidity':
                float(humidity),

            'moisture':
                float(moisture),

            'irrigation':
                str(irrigation),

            'crop':
                str(crop),

            'fertilizer':
                str(fertilizer)

        })

        # =============================
        # RETURN RESPONSE
        # =============================

        return {

            'soil_quality':
                str(soil_quality),

            'temperature':
                float(temperature),

            'humidity':
                float(humidity),

            'moisture':
                float(moisture),

            'irrigation':
                str(irrigation),

            'crop':
                str(crop),

            'fertilizer':
                str(fertilizer)

        }

    except Exception as e:

        return {
            'error': str(e)
        }

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=8080

    )