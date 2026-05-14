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
        # STATIC VALUES
        # =============================

        n = 50
        p = 40
        k = 45
        ph = 6.5
        rainfall = 50

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
        # FIXED LABELS
        # =============================

        labels = [

            "Poor",

            "Medium",

            "Good"

        ]

        if predicted_class >= len(labels):

            predicted_class = 1

        soil_quality = labels[predicted_class]

        # =============================
        # IRRIGATION
        # =============================

        if moisture < 30:

            irrigation = (
                'High irrigation required'
            )

        elif moisture < 50:

            irrigation = (
                'Moderate irrigation required'
            )

        else:

            irrigation = (
                'Soil moisture sufficient'
            )

        # =============================
        # CROP RECOMMENDATION
        # =============================

        if temperature > 30 and humidity > 60:

            crop = 'Rice'

        elif moisture < 40:

            crop = 'Millets'

        elif humidity < 50:

            crop = 'Wheat'

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

        else:

            fertilizer = (
                'Minimal fertilizer needed'
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