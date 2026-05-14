import pandas as pd
import numpy as np
import tensorflow as tf
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

# =====================================
# LOAD DATASET
# =====================================

df = pd.read_csv(
    'data/processed/processed_data.csv'
)

# =====================================
# FEATURES AND LABEL
# =====================================

X = df.drop(
    'label',
    axis=1
)

y = df['label']

# =====================================
# ENCODE LABELS
# =====================================

encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

# =====================================
# SCALE FEATURES
# =====================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# =====================================
# TRAIN TEST SPLIT
# =====================================

X_train, X_test, y_train, y_test = train_test_split(

    X_scaled,
    y_encoded,

    test_size=0.2,

    random_state=42

)

# =====================================
# BUILD AI MODEL
# =====================================

model = tf.keras.Sequential([

    tf.keras.layers.Input(
        shape=(X_train.shape[1],)
    ),

    tf.keras.layers.Dense(
        256,
        activation='relu'
    ),

    tf.keras.layers.Dropout(0.3),

    tf.keras.layers.Dense(
        128,
        activation='relu'
    ),

    tf.keras.layers.Dropout(0.3),

    tf.keras.layers.Dense(
        64,
        activation='relu'
    ),

    tf.keras.layers.Dense(
        len(np.unique(y_encoded)),
        activation='softmax'
    )

])

# =====================================
# OPTIMIZER
# =====================================

optimizer = tf.keras.optimizers.Adam(

    learning_rate=0.001

)

# =====================================
# COMPILE MODEL
# =====================================

model.compile(

    optimizer=optimizer,

    loss='sparse_categorical_crossentropy',

    metrics=['accuracy']

)

# =====================================
# EARLY STOPPING
# =====================================

early_stop = tf.keras.callbacks.EarlyStopping(

    monitor='val_loss',

    patience=10,

    restore_best_weights=True

)

# =====================================
# TRAIN MODEL
# =====================================

history = model.fit(

    X_train,
    y_train,

    epochs=50,

    batch_size=32,

    validation_split=0.2,

    callbacks=[early_stop]

)

# =====================================
# EVALUATE MODEL
# =====================================

loss, accuracy = model.evaluate(

    X_test,
    y_test

)

print(f"\nFinal Accuracy: {accuracy * 100:.2f}%")

# =====================================
# SAVE CLEAN MODEL
# =====================================

model.save(
    'models/soil_quality.keras'
)

# =====================================
# SAVE SCALER
# =====================================

joblib.dump(

    scaler,

    'models/scaler.pkl'

)

# =====================================
# SAVE LABEL ENCODER
# =====================================

joblib.dump(

    encoder,

    'models/label_encoder.pkl'

)

print("\nSoil quality model saved successfully")

print("Training completed")