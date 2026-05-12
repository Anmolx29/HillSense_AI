import time
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(
    'firebase_key.json'
)

firebase_admin.initialize_app(cred, {
    'databaseURL':
    'https://hillsenseai-default-rtdb.firebaseio.com/'
})

model = tf.keras.models.load_model(
    'models/soil_nn_model.h5'
)

scaler = joblib.load(
    'models/scaler.pkl'
)

encoder = joblib.load(
    'models/label_encoder.pkl'
)

print('AI Server Started')

while True:

    try:

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

            n = 50
            p = 40
            k = 45
            ph = 6.5
            rainfall = 50

            np_ratio = n / (p + 1)
            nk_ratio = n / (k + 1)
            pk_ratio = p / (k + 1)

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

            sample_scaled = scaler.transform(
                sample
            )

            prediction = model.predict(
                sample_scaled,
                verbose=0
            )

            predicted_class = np.argmax(
                prediction
            )

            label = encoder.inverse_transform([
                predicted_class
            ])[0]

            prediction_ref = db.reference(
                '/prediction'
            )

            prediction_ref.set({

                'soil_quality': label,
                'temperature': temperature,
                'humidity': humidity,
                'moisture': moisture,
                'timestamp': int(time.time())

            })

            print('Prediction:', label)

        time.sleep(5)

    except Exception as e:

        print(e)

        time.sleep(5)