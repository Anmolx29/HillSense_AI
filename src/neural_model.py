import pandas as pd
import tensorflow as tf
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

from tensorflow.keras.callbacks import EarlyStopping


def train_model(df):

    print("📊 Total data:", len(df))

    # =====================================================
    # USE ONLY LABELED DATA
    # =====================================================

    df = df[df['label'].notna()]

    print("🏷️ Labeled data:", len(df))

    # =====================================================
    # FEATURES
    # =====================================================

    features = [
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
    ]

    X = df[features]

    # =====================================================
    # TARGET
    # =====================================================

    y = df['label'].astype(str)

    # =====================================================
    # LABEL ENCODING
    # =====================================================

    le = LabelEncoder()

    y = le.fit_transform(y)

    joblib.dump(
        le,
        "models/label_encoder.pkl"
    )

    # =====================================================
    # FEATURE SCALING
    # =====================================================

    scaler = StandardScaler()

    X = scaler.fit_transform(X)

    joblib.dump(
        scaler,
        "models/scaler.pkl"
    )

    # =====================================================
    # TRAIN TEST SPLIT
    # =====================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # =====================================================
    # HYPERPARAMETERS
    # =====================================================

    neurons_1 = 128
    neurons_2 = 64
    neurons_3 = 32

    dropout_rate = 0.3

    learning_rate = 0.0005

    batch_size = 32

    epochs = 50

    # =====================================================
    # MODEL ARCHITECTURE
    # =====================================================

    model = tf.keras.Sequential([

        tf.keras.layers.Input(
            shape=(X.shape[1],)
        ),

        tf.keras.layers.Dense(
            neurons_1,
            activation='relu'
        ),

        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.Dense(
            neurons_2,
            activation='relu'
        ),

        tf.keras.layers.Dropout(
            dropout_rate
        ),

        tf.keras.layers.Dense(
            neurons_3,
            activation='relu'
        ),

        tf.keras.layers.Dense(
            len(set(y)),
            activation='softmax'
        )
    ])

    # =====================================================
    # COMPILE MODEL
    # =====================================================

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=learning_rate
        ),

        loss='sparse_categorical_crossentropy',

        metrics=['accuracy']
    )

    # =====================================================
    # EARLY STOPPING
    # =====================================================

    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )

    # =====================================================
    # TRAIN MODEL
    # =====================================================

    history = model.fit(

        X_train,
        y_train,

        epochs=epochs,

        batch_size=batch_size,

        validation_split=0.2,

        callbacks=[early_stop],

        verbose=1
    )

    # =====================================================
    # EVALUATE MODEL
    # =====================================================

    loss, acc = model.evaluate(
        X_test,
        y_test
    )

    print("🎯 Accuracy:", acc)

    # =====================================================
    # SAVE MODEL
    # =====================================================

    model.save(
        "models/soil_nn_model.h5"
    )

    print("✅ Model saved!")

    # =====================================================
    # ACCURACY GRAPH
    # =====================================================

    plt.figure(figsize=(8, 5))

    plt.plot(
        history.history['accuracy']
    )

    plt.plot(
        history.history['val_accuracy']
    )

    plt.title(
        'Model Accuracy'
    )

    plt.xlabel(
        'Epoch'
    )

    plt.ylabel(
        'Accuracy'
    )

    plt.legend(
        ['Train', 'Validation']
    )

    plt.savefig(
        "models/accuracy_graph.png"
    )

    plt.show()

    # =====================================================
    # LOSS GRAPH
    # =====================================================

    plt.figure(figsize=(8, 5))

    plt.plot(
        history.history['loss']
    )

    plt.plot(
        history.history['val_loss']
    )

    plt.title(
        'Model Loss'
    )

    plt.xlabel(
        'Epoch'
    )

    plt.ylabel(
        'Loss'
    )

    plt.legend(
        ['Train', 'Validation']
    )

    plt.savefig(
        "models/loss_graph.png"
    )

    plt.show()