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

    def classify(self, corners, fd_4, perimeter, circularity, hu_4, fd_2, bbox_w, fd_1, fd_3, fd_5, fd_7, fd_6, hu_1, hu_0, hu_2, hu_3, hu_5, hu_6, solidity, area):

        features = {
            "corners": corners,
            "fd_4": fd_4,
            "perimeter": perimeter,
            "circularity": circularity,
            "hu_4": hu_4,
            "fd_2": fd_2,
            "bbox_w": bbox_w,
            "fd_1": fd_1,
            "fd_3": fd_3,
            "fd_5": fd_5,
            "fd_7": fd_7,
            "fd_6": fd_6,
            "hu_1": hu_1,
            "hu_0": hu_0,
            "hu_2": hu_2,
            "hu_3": hu_3,
            "hu_5": hu_5,
            "hu_6": hu_6,
            "solidity": solidity,
            "area": area,
        }

        X = pd.DataFrame([features])[self.all_features]
        X_sel = self.selector.transform(X)

        prediction  = self.model.predict(X_sel)[0]
        confidence  = self.model.predict_proba(X_sel).max()
        
        # Convert string label to integer if mapping exists
        if isinstance(prediction, str) and prediction in self.label_map:
            prediction = self.label_map[prediction]
        elif isinstance(prediction, str):
            # If label not in map, try to convert directly to int
            try:
                prediction = int(prediction)
            except:
                # Default to 0 if conversion fails
                prediction = 0

        return prediction, confidence