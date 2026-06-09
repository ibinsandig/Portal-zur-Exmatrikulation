import joblib
import pandas as pd
import os

class Classifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "model", "random_forest_model_1.pkl")
        data = joblib.load(model_path)
        self.model     = data["model"]
        self.selector  = data["selector"]
        self.all_features = data["all_features"]
        
        # Label mapping for converting string labels to integers
        self.label_map = {
            'rejected': 0,
            'accepted': 1,
        }

    def classify(self, hu_2, hu_3):
        features = {
            "hu_2": hu_2,
            "hu_3": hu_3,
        }

        X = pd.DataFrame([features])[self.all_features]
        X_sel = self.selector.transform(X)

        prediction = self.model.predict(X_sel)[0]
        confidence = self.model.predict_proba(X_sel).max()

        if isinstance(prediction, str) and prediction in self.label_map:
            prediction = self.label_map[prediction]
        elif isinstance(prediction, str):
            try:
                prediction = int(prediction)
            except:
                prediction = 0

        return prediction, confidence