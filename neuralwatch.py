"""
neuralwatch.py
--------------
This is the defender. It watches the brain's weights every second,
logs everything with a tamper-evident signature, and raises alerts
when drift crosses safe limits.

Three layers of protection:
  Layer 1 - Gesture biometric lock (in dashboard.py)
  Layer 2 - Neural drift detection (this file)
  Layer 3 - Cryptographic tamper-evident audit log (this file)
"""

import hashlib
import json
import time
from datetime import datetime

DRIFT_THRESHOLD = 0.12   # safe learning limit
SPIKE_THRESHOLD = 0.15   # LIF spike firing point


class NeuralWatch:
    def __init__(self, brain):
        self.brain = brain
        self.audit_log = []          # full history of every event
        self.chain_hash = "GENESIS"  # starts the tamper-evident chain
        self.alert_active = False
        self.total_spikes = 0
        self.rollback_count = 0
        self.monitoring_start = datetime.now().strftime("%H:%M:%S")

    def _sign_entry(self, entry):
        """
        Creates a cryptographic signature for each log entry.
        Each entry includes the hash of the PREVIOUS entry — like blockchain.
        If anyone edits any entry, the entire chain breaks.
        This is Layer 3: tamper-evident logging.
        """
        entry["prev_hash"] = self.chain_hash
        entry_str = json.dumps(entry, sort_keys=True)
        new_hash = hashlib.sha256(entry_str.encode()).hexdigest()[:16]
        entry["signature"] = new_hash
        self.chain_hash = new_hash
        return entry

    def verify_log_integrity(self):
        """
        Checks if anyone has tampered with the audit log.
        Replays the entire hash chain from the beginning.
        Returns True if clean, False if tampered.
        """
        if not self.audit_log:
            return True

        prev = "GENESIS"
        for entry in self.audit_log:
            check = dict(entry)
            sig = check.pop("signature")
            check["prev_hash"] = prev
            check_str = json.dumps(check, sort_keys=True)
            expected = hashlib.sha256(check_str.encode()).hexdigest()[:16]
            if expected != sig:
                return False   # chain broken = tampered
            prev = sig
        return True

    def monitor_tick(self, tick, is_under_attack):
        """
        Called every second. Checks drift, updates LIF neuron,
        fires alerts, and writes a signed log entry.
        """
        timestamp = f"T+{tick:03d}s"
        drift = self.brain.get_drift_score()
        spike_fired = self.brain.lif_update(drift, timestamp)
        membrane = round(self.brain.membrane_potential, 4)

        # Determine status
        if spike_fired:
            self.total_spikes += 1
            status = "SPIKE"
        elif drift >= DRIFT_THRESHOLD:
            status = "WARNING"
        else:
            status = "SAFE"

        # If spike fired AND drift is high = confirmed attack
        confirmed_attack = spike_fired and drift >= DRIFT_THRESHOLD

        if confirmed_attack and not self.alert_active:
            self.alert_active = True

        # Build the log entry
        entry = {
            "tick": timestamp,
            "time": datetime.now().strftime("%H:%M:%S"),
            "drift": round(drift, 5),
            "membrane": membrane,
            "status": status,
            "spike": spike_fired,
            "attack_mode": is_under_attack,
        }

        # Sign and store it
        signed = self._sign_entry(entry)
        self.audit_log.append(signed)

        return {
            "drift": drift,
            "membrane": membrane,
            "status": status,
            "spike_fired": spike_fired,
            "confirmed_attack": confirmed_attack,
            "log_entry": signed,
        }

    def perform_rollback(self):
        """Roll brain back to clean state and log the event."""
        self.brain.rollback()
        self.alert_active = False
        self.rollback_count += 1

        entry = {
            "tick": "ROLLBACK",
            "time": datetime.now().strftime("%H:%M:%S"),
            "drift": 0.0,
            "membrane": 0.0,
            "status": "ROLLBACK",
            "spike": False,
            "attack_mode": False,
        }
        self.audit_log.append(self._sign_entry(entry))

    def simulate_tamper(self):
        """
        Demo tool: corrupts the last log entry to show tamper detection.
        In a real attack a hacker would try to delete their tracks.
        """
        if self.audit_log:
            self.audit_log[-1]["drift"] = 0.0   # hacker tries to hide drift
            self.audit_log[-1]["status"] = "SAFE"  # pretend nothing happened
