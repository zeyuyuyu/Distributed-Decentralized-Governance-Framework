import requests
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Proposal:
    id: str
    title: str
    description: str
    votes: int
    status: str

class DecentralizedGovernance:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_proposals(self) -> List[Proposal]:
        response = requests.get(f'{self.api_url}/proposals')
        proposals = [Proposal(**p) for p in response.json()]
        return proposals

    def create_proposal(self, title: str, description: str) -> Proposal:
        data = {
            'title': title,
            'description': description
        }
        response = requests.post(f'{self.api_url}/proposals', json=data)
        return Proposal(**response.json())

    def vote_on_proposal(self, proposal_id: str, vote: int) -> Proposal:
        data = {
            'vote': vote
        }
        response = requests.post(f'{self.api_url}/proposals/{proposal_id}/vote', json=data)
        return Proposal(**response.json())

if __name__ == '__main__':
    governance = DecentralizedGovernance('https://api.example.com')
    proposals = governance.get_proposals()
    for proposal in proposals:
        print(proposal)

    new_proposal = governance.create_proposal(
        title='Increase funding for sustainability initiatives',
        description='We should allocate more resources towards renewable energy projects and environmental conservation efforts.'
    )
    print(new_proposal)

    voted_proposal = governance.vote_on_proposal(new_proposal.id, 1)
    print(voted_proposal)
