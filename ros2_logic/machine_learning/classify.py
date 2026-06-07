import joblib
import pandas as pd

class Classifier:
    def __init__(self):
        data = joblib.load("random_forest_model_1.pkl")
        self.model     = data["model"]
        self.selector  = data["selector"]
        self.all_features = data["all_features"]
        
    def classify(self, circularity, hu_4, fd_2, fd_6, hu_1, hu_0, hu_5, hu_6, solidity, area):

        features = {
            "circularity": circularity,
            "hu_4":        hu_4,
            "fd_2":        fd_2,
            "fd_6":        fd_6,
            "hu_1":        hu_1,
            "hu_0":        hu_0,
            "hu_5":        hu_5,
            "hu_6":        hu_6,
            "solidity":    solidity,
            "area":        area,
        }

        X = pd.DataFrame([features])[self.all_features]
        X_sel = self.selector.transform(X)

        prediction  = self.model.predict(X_sel)[0]
        confidence  = self.model.predict_proba(X_sel).max()

        return prediction, confidence