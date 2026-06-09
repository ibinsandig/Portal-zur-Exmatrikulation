import joblib
import pandas as pd
import os

class Classifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "model", "final.pkl")
        data = joblib.load(model_path)
        self.model        = data
        self.selector     = None
        self.all_features = ["hu_2", "hu_3"]

    def classify(self, hu_2, hu_3):
        features = {
            "hu_2": hu_2,
            "hu_3": hu_3,
        }

        X = pd.DataFrame([features])[self.all_features]
        X_sel = self.selector.transform(X) if self.selector is not None else X

        prediction = self.model.predict(X_sel)[0]
        confidence = self.model.predict_proba(X_sel).max()


        if isinstance(prediction, str):
            try:
                prediction = int(prediction)
            except:
                prediction = 0

        return prediction, confidence 