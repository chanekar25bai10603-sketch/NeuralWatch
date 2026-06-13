"""
neural_brain.py
---------------
This simulates a neuromorphic AI's "brain" — its synaptic weights.
Think of weights as the AI's memory of what is safe vs dangerous.
A hacker poisons these weights slowly over time.
"""

import numpy as np
import time

class NeuromorphicBrain:
    def __init__(self):
        # The brain starts with balanced weights (0.3 to 0.7 = healthy range)
        # Think of these as 100 neurons, each storing a value
        np.random.seed(42)
        self.weights = np.random.uniform(0.3, 0.7, size=(10, 10))

        # Baseline = the clean, original brain. We compare against this.
        self.baseline = self.weights.copy()

        # Membrane potential = charge building up (neuromorphic LIF model)
        # A neuron fires a spike when this crosses the threshold
        self.membrane_potential = 0.0
        self.threshold = 0.15        # spike fires when drift crosses this
        self.leak_rate = 0.95        # charge slowly leaks away (like real neurons)
        self.spike_log = []          # record of every time a spike fired

    def learn_normally(self):
        """Healthy learning = tiny random weight changes in all directions."""
        noise = np.random.uniform(-0.005, 0.005, size=(10, 10))
        self.weights += noise
        # Keep weights in a realistic range
        self.weights = np.clip(self.weights, 0.0, 1.0)

    def receive_poison(self, intensity=0.008):
        """
        Attacker feeds malicious data = weights drift consistently upward.
        In real attacks this is so slow humans never notice.
        """
        poison = np.random.uniform(0, intensity, size=(10, 10))
        self.weights += poison
        self.weights = np.clip(self.weights, 0.0, 1.0)

    def get_drift_score(self):
        """How far have weights moved from the original baseline?"""
        return float(np.mean(np.abs(self.weights - self.baseline)))

    def lif_update(self, drift_score, timestamp):
        """
        Leaky Integrate-and-Fire neuron model.
        This is the core neuromorphic mechanism:
        - Drift adds charge to the membrane
        - Charge leaks away naturally over time
        - When charge crosses threshold -> SPIKE -> alert fires
        """
        # Add current drift to membrane potential
        self.membrane_potential += drift_score

        # Apply leak (charge naturally dissipates — like a real neuron)
        self.membrane_potential *= self.leak_rate

        # Check if threshold crossed -> fire spike
        if self.membrane_potential >= self.threshold:
            self.spike_log.append(timestamp)
            self.membrane_potential = 0.0  # reset after firing (refractory period)
            return True  # spike fired!
        return False

    def rollback(self):
        """Restore the brain to its last clean baseline state."""
        self.weights = self.baseline.copy()
        self.membrane_potential = 0.0
