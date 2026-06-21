import joblib
import pandas as pd
import os
from collections import deque
import statistics


class Classifier:
    def __init__(self, buffer_size=5):
        model_path = os.path.join(os.path.dirname(__file__), "model", "decision_tree.pkl")
        data = joblib.load(model_path)
        self.model        = data
        self.selector     = None
        self.all_features = ["hu_2", "hu_3"]

        self.buffer_size  = buffer_size
        self.current_id   = None
        self.label_buffer = deque()   # speichert einzelne Label-Vorhersagen

    def classify(self, id, hu_2, hu_3):
        """
        Klassifiziert ein Objekt anhand seiner Features.
        Bei neuer ID wird der Buffer geleert.
        Gibt (smoothed_label, confidence) zurück, oder None wenn noch kein Ergebnis.
        """

        # Neue ID → Buffer leeren
        if id != self.current_id:
            self.label_buffer.clear()
            self.current_id = id

        features = {"hu_2": hu_2, "hu_3": hu_3}
        X = pd.DataFrame([features])[self.all_features]
        X_sel = self.selector.transform(X) if self.selector is not None else X

        prediction = self.model.predict(X_sel)[0]
        confidence = float(self.model.predict_proba(X_sel).max())

        label_map = {"rejected": 0, "cat": 1, "unicorn": 2}

        if isinstance(prediction, str):
            prediction = label_map.get(prediction, 0)
        else:
            prediction = int(prediction)

        self.label_buffer.append(prediction)
        if len(self.label_buffer) > self.buffer_size:
            self.label_buffer.popleft()

        smoothed_label = int(statistics.median(self.label_buffer))

        return smoothed_label, confidence