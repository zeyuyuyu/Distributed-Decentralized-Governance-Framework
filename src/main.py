import time
import random
from typing import List, Tuple

class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.neighbors = []
        self.state = 'IDLE'
        self.proposal = None
        self.votes = []

    def add_neighbor(self, neighbor: 'Node'):
        self.neighbors.append(neighbor)

    def propose(self, value: any):
        self.proposal = value
        self.state = 'PROPOSED'
        self.broadcast_proposal()

    def broadcast_proposal(self):
        for neighbor in self.neighbors:
            neighbor.receive_proposal(self.proposal)

    def receive_proposal(self, proposal: any):
        if self.state == 'IDLE':
            self.proposal = proposal
            self.state = 'CONSIDERING'
            self.vote()

    def vote(self):
        vote = random.choice([True, False])
        self.votes.append(vote)
        self.state = 'VOTED'
        self.broadcast_vote(vote)

    def broadcast_vote(self, vote: bool):
        for neighbor in self.neighbors:
            neighbor.receive_vote(self.node_id, vote)

    def receive_vote(self, voter_id: str, vote: bool):
        self.votes.append(vote)
        if len(self.votes) == len(self.neighbors):
            self.finalize_decision()

    def finalize_decision(self):
        total_votes = sum(self.votes)
        if total_votes > len(self.neighbors) // 2:
            self.state = 'DECIDED'
            self.broadcast_decision(self.proposal)
        else:
            self.state = 'IDLE'
            self.proposal = None
            self.votes = []

    def broadcast_decision(self, decision: any):
        for neighbor in self.neighbors:
            neighbor.receive_decision(decision)

    def receive_decision(self, decision: any):
        print(f'Node {self.node_id} has reached consensus: {decision}')

def simulate_consensus(nodes: List[Node]):
    for node in nodes:
        node.propose(random.randint(1, 100))

    while True:
        time.sleep(1)
        for node in nodes:
            if node.state == 'DECIDED':
                return

if __name__ == '__main__':
    node1 = Node('node1')
    node2 = Node('node2')
    node3 = Node('node3')
    node4 = Node('node4')
    node5 = Node('node5')

    node1.add_neighbor(node2)
    node1.add_neighbor(node3)
    node2.add_neighbor(node1)
    node2.add_neighbor(node3)
    node2.add_neighbor(node4)
    node3.add_neighbor(node1)
    node3.add_neighbor(node2)
    node3.add_neighbor(node4)
    node3.add_neighbor(node5)
    node4.add_neighbor(node2)
    node4.add_neighbor(node3)
    node4.add_neighbor(node5)
    node5.add_neighbor(node3)
    node5.add_neighbor(node4)

    nodes = [node1, node2, node3, node4, node5]
    simulate_consensus(nodes)