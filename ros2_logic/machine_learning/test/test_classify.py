import pytest
import sys
import os

# Add the parent directory (machine_learning) to the system path to import classify
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from classify import Classifier


class TestClassifier:
    """Test cases for the Classifier class."""

    def setup_method(self):
        """Instantiate Classifier, which will load the final.pkl model."""
        self.classifier = Classifier()

    def test_model_loading(self):
        """Verify that the model loaded successfully and the expected features are set."""
        assert self.classifier.model is not None
        assert self.classifier.all_features == ["hu_2", "hu_3"]
        assert self.classifier.selector is None

    def test_classify_returns_valid_types(self):
        """Verify that classification returns an integer prediction and float confidence."""
        # Call with dummy values
        pred, conf = self.classifier.classify(hu_2=0.01, hu_3=0.02)
        
        # Check that pred is an integer (as the code tries to cast/fallback to int)
        assert isinstance(pred, int)
        
        # Check that confidence is a float between 0.0 and 1.0 (inclusive)
        assert isinstance(conf, float)
        assert 0.0 <= conf <= 1.0

    def test_classify_multiple_inputs(self):
        """Test classification with different inputs to ensure it evaluates successfully."""
        inputs = [
            (0.0, 0.0),
            (0.005, -0.002),
            (-0.1, 0.1),
            (1.0, 1.0)
        ]
        for hu2, hu3 in inputs:
            pred, conf = self.classifier.classify(hu2, hu3)
            assert isinstance(pred, int)
            assert isinstance(conf, float)
            assert 0.0 <= conf <= 1.0
