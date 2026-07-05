import joblib
import pandas as pd
import os
from collections import deque
import statistics


class Classifier:
    """Klassifiziert Objekte anhand von Hu-Momenten mit einem vortrainierten Decision-Tree-Modell und glättet Vorhersagen per Median-Buffer."""

    def __init__(self, buffer_size=5):
        """Lädt das Decision-Tree-Modell aus model/decision_tree.pkl und initialisiert Label-Buffer.

        Args:
            buffer_size (int): Anzahl der gepufferten Vorhersagen für die Glättung (Standard: 5)
        """

        model_path = os.path.join(os.path.dirname(__file__), "model", "decision_tree.pkl")
        data = joblib.load(model_path)
        self.model        = data
        self.selector     = None
        self.all_features = ["hu_2", "hu_3"]

        self.buffer_size  = buffer_size
        self.current_id   = None
        self.label_buffer = deque()   # speichert einzelne Label-Vorhersagen

    def classify(self, id, hu_2, hu_3):
        """Klassifiziert ein Objekt anhand von hu_2 und hu_3 und gibt ein per Median geglättetes Label sowie die Konfidenz zurück.

        Args:
            id (int): Objekt-ID (Buffer wird bei neuer ID geleert)
            hu_2 (float): Logarithmiertes Hu-Moment hu_2
            hu_3 (float): Logarithmiertes Hu-Moment hu_3

        Returns:
            tuple: (smoothed_label: int, confidence: float)
                Label: 0=rejected, 1=cat, 2=unicorn
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