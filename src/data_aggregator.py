import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class DataAggregator:
    def __init__(self):
        self.governance_data = {}
        self.trust_scores = {}
        self.anomaly_thresholds = {
            'participation_rate': 0.2,
            'consensus_deviation': 2.0
        }

    def add_governance_data(self, source: str, data: Dict, timestamp: datetime) -> None:
        """Add new governance data from a source with timestamp"""
        if source not in self.governance_data:
            self.governance_data[source] = []
        self.governance_data[source].append({
            'data': data,
            'timestamp': timestamp
        })

    def calculate_trust_score(self, source: str) -> float:
        """Calculate trust score based on historical accuracy and consistency"""
        if not self.governance_data.get(source):
            return 0.0

        data_points = self.governance_data[source]
        consistency_score = self._evaluate_consistency(data_points)
        timeliness_score = self._evaluate_timeliness(data_points)
        
        trust_score = (consistency_score * 0.7) + (timeliness_score * 0.3)
        self.trust_scores[source] = trust_score
        return trust_score

    def get_weighted_consensus(self) -> Dict:
        """Calculate weighted consensus across all sources"""
        if not self.governance_data:
            return {}

        weighted_data = {}
        total_weight = 0

        for source in self.governance_data:
            trust_score = self.calculate_trust_score(source)
            latest_data = self.governance_data[source][-1]['data']
            
            for key, value in latest_data.items():
                if key not in weighted_data:
                    weighted_data[key] = 0
                weighted_data[key] += value * trust_score
            total_weight += trust_score

        if total_weight > 0:
            return {k: v/total_weight for k, v in weighted_data.items()}
        return weighted_data

    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in governance data"""
        anomalies = []
        consensus = self.get_weighted_consensus()

        for source in self.governance_data:
            latest_data = self.governance_data[source][-1]['data']
            
            for key, value in latest_data.items():
                if key in consensus:
                    deviation = abs(value - consensus[key])
                    if deviation > self.anomaly_thresholds['consensus_deviation']:
                        anomalies.append({
                            'source': source,
                            'metric': key,
                            'value': value,
                            'consensus': consensus[key],
                            'deviation': deviation
                        })

        return anomalies

    def _evaluate_consistency(self, data_points: List[Dict]) -> float:
        """Evaluate data consistency for a source"""
        if len(data_points) < 2:
            return 0.5

        variations = []
        for i in range(1, len(data_points)):
            prev = data_points[i-1]['data']
            curr = data_points[i]['data']
            
            # Calculate average variation across all metrics
            metric_variations = []
            for key in curr:
                if key in prev:
                    variation = abs(curr[key] - prev[key]) / max(prev[key], 1)
                    metric_variations.append(variation)
            
            if metric_variations:
                variations.append(np.mean(metric_variations))

        return 1.0 / (1.0 + np.mean(variations)) if variations else 0.5

    def _evaluate_timeliness(self, data_points: List[Dict]) -> float:
        """Evaluate timeliness of data updates"""
        if len(data_points) < 2:
            return 0.5

        time_gaps = []
        for i in range(1, len(data_points)):
            gap = (data_points[i]['timestamp'] - data_points[i-1]['timestamp']).total_seconds()
            time_gaps.append(gap)

        avg_gap = np.mean(time_gaps)
        return 1.0 / (1.0 + avg_gap/86400)  # Normalize by day
