import pytest
import sys
import os

# Füge das übergeordnete Verzeichnis (ros2_logic) zum Pfad hinzu, um das Modul importieren zu können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..') ))

from coord_pred import CoordinatesPrediction


class TestCoordinatesPrediction:
    """Testfälle für die CoordinatesPrediction-Klasse."""

    def setup_method(self):
        """Jeder Test erhält eine neue Instanz."""
        self.prediction = CoordinatesPrediction()

    def test_first_call_returns_negative_one(self):
        """Erster Aufruf mit neuer ID sollte -100 zurückgeben."""
        result = self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=1.0)
        assert result == -100

    def test_second_call_with_same_id_calculates_speed(self):
        """Zweiter Aufruf mit gleicher ID sollte Geschwindigkeit berechnen."""
        # Erster Aufruf
        result1 = self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=1.0)
        assert result1 == -100

        # Zweiter Aufruf mit gleicher ID
        result2 = self.prediction.calculate_speed_with_ID(id=1, x=20.0, t=2.0)
        assert result2 == (20.0 - 10.0) / (2.0 - 1.0)  # sollte 10.0 sein

    def test_speed_calculation_correct(self):
        """Geschwindigkeitsberechnung sollte korrekt sein."""
        # Erster Aufruf
        self.prediction.calculate_speed_with_ID(id=1, x=0.0, t=0.0)
        
        # Zweiter Aufruf
        result = self.prediction.calculate_speed_with_ID(id=1, x=100.0, t=10.0)
        assert result == 10.0  # 100/10 = 10

    def test_id_switch_returns_negative_one(self):
        """Wechsel der ID sollte -100 zurückgeben."""
        # Aufruf mit ID 1
        self.prediction.calculate_speed_with_ID(id=1, x=0.0, t=0.0)
        self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=1.0)
        
        # Wechsel zu ID 2 sollte -100 zurückgeben
        result = self.prediction.calculate_speed_with_ID(id=2, x=20.0, t=2.0)
        assert result == -100

    def test_multiple_ids_independent(self):
        """Verschiedene IDs sollten unabhängig voneinander behandelt werden."""
        # ID 1
        self.prediction.calculate_speed_with_ID(id=1, x=0.0, t=0.0)
        self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=1.0)
        
        # ID 2 (sollte -100 zurückgeben)
        result_id2 = self.prediction.calculate_speed_with_ID(id=2, x=20.0, t=2.0)
        assert result_id2 == -100
        
        # Zurück zu ID 1 (sollte wieder Geschwindigkeit berechnen)
        result_id1 = self.prediction.calculate_speed_with_ID(id=1, x=20.0, t=2.0)
        assert result_id1 == (20.0 - 10.0) / (2.0 - 1.0)  # sollte 10.0 sein

    def test_negative_speed(self):
        """Negative Geschwindigkeit sollte korrekt berechnet werden."""
        self.prediction.calculate_speed_with_ID(id=1, x=100.0, t=0.0)
        result = self.prediction.calculate_speed_with_ID(id=1, x=0.0, t=10.0)
        assert result == -10.0  # (0 - 100) / (10 - 0) = -10

    def test_zero_distance(self):
        """Geschwindigkeit bei gleicher Position sollte 0 sein."""
        self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=0.0)
        result = self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=5.0)
        assert result == 0.0

    def test_state_reset_on_id_change(self):
        """State sollte bei ID-Wechsel zurückgesetzt werden."""
        # ID 1 verwenden
        self.prediction.calculate_speed_with_ID(id=1, x=0.0, t=0.0)
        self.prediction.calculate_speed_with_ID(id=1, x=10.0, t=1.0)
        
        # ID 2 verwenden
        self.prediction.calculate_speed_with_ID(id=2, x=0.0, t=0.0)
        result = self.prediction.calculate_speed_with_ID(id=2, x=5.0, t=1.0)
        assert result == 5.0  # (5 - 0) / (1 - 0) = 5
