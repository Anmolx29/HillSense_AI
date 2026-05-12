import pandas as pd
import numpy as np
import os

# -------- COLUMN STANDARDIZATION --------
COLUMN_MAP = {
    'nitrogen': 'n',
    'phosphorous': 'p',
    'phosphorus': 'p',
    'potassium': 'k',
    'temparature': 'temperature',
    'temp': 'temperature',
    'hum': 'humidity',
    'humidity ': 'humidity',
    'ph value': 'ph',
    'soil_ph': 'ph'
}

# -------- REQUIRED FEATURES --------
REQUIRED_FEATURES = [
    'n',
    'p',
    'k',
    'temperature',
    'humidity',
    'ph'
]

# -------- POSSIBLE LABEL COLUMNS --------
OPTIONAL_LABELS = [
    'soil_quality',
    'crop_yield',
    'fertilizer name'
]


# =====================================================
# STANDARDIZE COLUMN NAMES
# =====================================================

def standardize_columns(df):

    df.columns = df.columns.str.lower().str.strip()

    df = df.rename(columns=COLUMN_MAP)

    return df


# =====================================================
# ENSURE REQUIRED FEATURES EXIST
# =====================================================

def ensure_features(df):

    for col in REQUIRED_FEATURES:

        if col not in df.columns:

            # realistic defaults

            if col == 'temperature':
                df[col] = 25 + np.random.normal(0, 2, len(df))

            elif col == 'humidity':
                df[col] = 50 + np.random.normal(0, 5, len(df))

            elif col == 'ph':
                df[col] = np.random.uniform(5.5, 7.5, len(df))

            else:
                df[col] = np.random.randint(20, 100, len(df))

    return df


# =====================================================
# CONVERT NUMERIC SOIL QUALITY → CATEGORY
# =====================================================

def convert_soil_quality(df):

    if 'soil_quality' in df.columns:

        if df['soil_quality'].dtype != 'object':

            try:
                df['soil_quality'] = pd.qcut(
                    df['soil_quality'],
                    3,
                    labels=['Poor', 'Medium', 'Good']
                )

            except:

                df['soil_quality'] = pd.cut(
                    df['soil_quality'],
                    bins=3,
                    labels=['Poor', 'Medium', 'Good']
                )

    return df


# =====================================================
# EXTRACT LABEL
# =====================================================

def extract_label(df):

    for label in OPTIONAL_LABELS:

        if label in df.columns:

            df['label'] = df[label].astype(str).str.strip()

            return df

    df['label'] = np.nan

    return df


# =====================================================
# PROCESS SINGLE FILE
# =====================================================

def process_file(path):

    try:

        df = pd.read_csv(path)

        df = standardize_columns(df)

        df = ensure_features(df)

        df = convert_soil_quality(df)

        df = extract_label(df)

        df = df[REQUIRED_FEATURES + ['label']]

        print(f"Processed: {os.path.basename(path)} | Rows: {len(df)}")

        return df

    except Exception as e:

        print(f"Error processing {path}: {e}")

        return None


# =====================================================
# LOAD + CLEAN ALL DATASETS
# =====================================================

def load_and_clean():

    all_dfs = []

    folder = "data/raw"

    for file in os.listdir(folder):

        if file.endswith(".csv"):

            path = os.path.join(folder, file)

            df = process_file(path)

            if df is not None:

                all_dfs.append(df)

    # -------- MERGE --------

    df = pd.concat(all_dfs, ignore_index=True)

    # -------- CLEAN --------

    df = df.dropna(subset=REQUIRED_FEATURES)

    df = df.drop_duplicates()

    # -------- FILTER --------

    df = df[
        (df['humidity'] >= 0) &
        (df['humidity'] <= 100)
    ]

    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================

    # moisture feature
    df['moisture'] = df['humidity'] * 0.7

    # rainfall feature
    df['rainfall'] = np.random.randint(20, 100, len(df))

    # =====================================================
    # FEATURE RATIOS
    # =====================================================

    df['np_ratio'] = df['n'] / (df['p'] + 1)

    df['nk_ratio'] = df['n'] / (df['k'] + 1)

    df['pk_ratio'] = df['p'] / (df['k'] + 1)

    # -------- SAVE --------

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(
        "data/processed/processed_data.csv",
        index=False
    )

    print("Final dataset size:", len(df))

    print("Processed dataset saved!")

    return df