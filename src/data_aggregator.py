import pandas as pd
from typing import Dict, List, Union
from datetime import datetime
import numpy as np

class ConsensusAggregator:
    def __init__(self):
        self.proposals = {}
        self.votes = {}
        self.participant_weights = {}
    
    def add_participant(self, participant_id: str, weight: float = 1.0):
        """Add participant with optional reputation-based weight"""
        self.participant_weights[participant_id] = weight
    
    def submit_proposal(self, proposal_id: str, proposal_data: Dict):
        """Submit new governance proposal"""
        self.proposals[proposal_id] = {
            'data': proposal_data,
            'timestamp': datetime.now(),
            'status': 'active'
        }
        self.votes[proposal_id] = {}

    def cast_vote(self, proposal_id: str, participant_id: str, vote: bool):
        """Cast weighted vote on proposal"""
        if proposal_id not in self.proposals:
            raise ValueError(f'Invalid proposal ID: {proposal_id}')
        
        if participant_id not in self.participant_weights:
            raise ValueError(f'Unknown participant: {participant_id}')
            
        self.votes[proposal_id][participant_id] = {
            'vote': vote,
            'weight': self.participant_weights[participant_id],
            'timestamp': datetime.now()
        }

    def get_consensus_state(self, proposal_id: str) -> Dict:
        """Calculate current weighted consensus state"""
        if proposal_id not in self.proposals:
            raise ValueError(f'Invalid proposal ID: {proposal_id}')
            
        votes = self.votes[proposal_id]
        total_weight = sum(self.participant_weights.values())
        approve_weight = sum(v['weight'] for v in votes.values() if v['vote'])
        reject_weight = sum(v['weight'] for v in votes.values() if not v['vote'])
        
        consensus_ratio = approve_weight / total_weight if total_weight > 0 else 0
        
        return {
            'proposal_id': proposal_id,
            'total_votes': len(votes),
            'approve_weight': approve_weight,
            'reject_weight': reject_weight,
            'consensus_ratio': consensus_ratio,
            'quorum_reached': len(votes) >= len(self.participant_weights) * 0.5,
            'timestamp': datetime.now()
        }

    def get_all_active_proposals(self) -> List[Dict]:
        """Get status of all active proposals"""
        active_proposals = []
        for pid, proposal in self.proposals.items():
            if proposal['status'] == 'active':
                consensus = self.get_consensus_state(pid)
                active_proposals.append({
                    **proposal,
                    'consensus': consensus
                })
        return active_proposals

    def export_results(self, filepath: str):
        """Export voting results to CSV"""
        results = []
        for pid, proposal in self.proposals.items():
            consensus = self.get_consensus_state(pid)
            results.append({
                'proposal_id': pid,
                'status': proposal['status'],
                'total_votes': consensus['total_votes'],
                'consensus_ratio': consensus['consensus_ratio'],
                'quorum_reached': consensus['quorum_reached']
            })
        
        df = pd.DataFrame(results)
        df.to_csv(filepath, index=False)

def calculate_participant_weight(history: List[Dict]) -> float:
    """Calculate participant weight based on historical participation"""
    if not history:
        return 1.0
    
    participation_rate = len([h for h in history if h['participated']]) / len(history)
    time_weights = np.exp(-np.arange(len(history)) * 0.1) # More recent actions weighted higher
    weighted_score = np.mean(time_weights * participation_rate)
    
    return max(0.1, min(2.0, weighted_score)) # Bound weights between 0.1 and 2.0