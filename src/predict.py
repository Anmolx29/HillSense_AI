import joblib

model = joblib.load("models/soil_model.pkl")

def predict(data):
    result = model.predict([data])[0]

    if result == 0:
        return "IRRIGATE"
    elif result == 1:
        return "ADD N"
    elif result == 2:
        return "ADD P"
    elif result == 3:
        return "ADD K"
    elif result == 4:
        return "OPTIMAL"
    else:
        return "MULTI ACTION"