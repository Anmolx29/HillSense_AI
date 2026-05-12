from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

def train(df):
    X = df[['n','p','k','temperature','humidity','moisture','rainfall']]
    y = df['soil_state']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2
    )

    model = GradientBoostingClassifier(n_estimators=50)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    print("\nAccuracy:", accuracy_score(y_test, pred))
    print("\nClassification Report:\n", classification_report(y_test, pred))

    joblib.dump(model, "models/soil_model.pkl")

    return model