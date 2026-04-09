import numpy as np
import os
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import HashingVectorizer

# Constants for severity mapping
SEVERITY_LEVELS = ["None", "Mild", "Moderate", "Severe", "Contraindicated"]

class SeverityClassifier:
    """
    A RandomForest-based classifier for drug interactions.
    This replaces the simulated logic with an actual trained ML model.
    """
    def __init__(self):
        # We use a HashingVectorizer to convert drug names to features quickly
        self.vectorizer = HashingVectorizer(n_features=20)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self._train_initial_model()
        
    def _train_initial_model(self):
        """
        Train the model with some synthetic/baseline data so it's ready immediately.
        In a real scenario, you would load a pickle file here.
        """
        logger.info("Initializing and training the RandomForest model...")
        X_text = [
            "warfarin aspirin", 
            "warfarin amoxicillin", 
            "alcohol paracetamol", 
            "metformin contrast",
            "ibuprofen vitamin_c",
            "lisinopril amlodipine"
        ]
        y = ["Severe", "Moderate", "Severe", "Contraindicated", "None", "None"]
        
        X = self.vectorizer.fit_transform(X_text)
        self.model.fit(X, y)
        
    def predict(self, drug_a: str, drug_b: str):
        """
        Predict severity label and confidence score.
        """
        combined = (str(drug_a) + " " + str(drug_b)).lower()
        X_input = self.vectorizer.transform([combined])
        
        prediction = self.model.predict(X_input)[0]
        
        # Get probability distribution to calculate confidence
        probs = self.model.predict_proba(X_input)[0]
        confidence = float(np.max(probs))
        
        return prediction, confidence

# Singleton instance
classifier = SeverityClassifier()

def get_severity_prediction(drug_a, drug_b):
    return classifier.predict(drug_a, drug_b)
