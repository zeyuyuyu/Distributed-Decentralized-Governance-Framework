import asyncio
import aiohttp
from typing import List, Dict, Set
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class PeerNode:
    id: str
    address: str
    last_seen: datetime
    consensus_version: str

class DistributedCrawler:
    def __init__(self, bootstrap_nodes: List[str]):
        self.bootstrap_nodes = bootstrap_nodes
        self.known_peers: Dict[str, PeerNode] = {}
        self.active_peers: Set[str] = set()
        self.session: aiohttp.ClientSession = None
    
    async def start(self):
        self.session = aiohttp.ClientSession()
        await self.discover_peers()
        
    async def stop(self):
        if self.session:
            await self.session.close()
    
    async def discover_peers(self):
        """Recursively discover and validate peer nodes"""
        for node in self.bootstrap_nodes:
            await self.validate_peer(node)
    
    async def validate_peer(self, address: str):
        """Validate a peer node and collect its metadata"""
        try:
            async with self.session.get(f'{address}/peer/info', timeout=5) as resp:
                if resp.status == 200:
                    peer_data = await resp.json()
                    peer = PeerNode(
                        id=peer_data['id'],
                        address=address,
                        last_seen=datetime.now(),
                        consensus_version=peer_data.get('consensus_version', 'unknown')
                    )
                    self.known_peers[peer.id] = peer
                    self.active_peers.add(peer.id)
                    
                    # Get peer's known nodes
                    async with self.session.get(f'{address}/peer/known_nodes') as peers_resp:
                        if peers_resp.status == 200:
                            new_peers = await peers_resp.json()
                            for new_peer in new_peers:
                                if new_peer not in self.known_peers:
                                    await self.validate_peer(new_peer)
        except Exception as e:
            print(f'Failed to validate peer {address}: {str(e)}')
    
    async def get_consensus_state(self) -> Dict:
        """Gather consensus state from active peers"""
        consensus_states = []
        for peer_id in self.active_peers:
            peer = self.known_peers[peer_id]
            try:
                async with self.session.get(f'{peer.address}/consensus/state') as resp:
                    if resp.status == 200:
                        state = await resp.json()
                        consensus_states.append(state)
            except Exception as e:
                print(f'Failed to get consensus from {peer.address}: {str(e)}')
                self.active_peers.remove(peer_id)
        
        return self._aggregate_consensus(consensus_states)
    
    def _aggregate_consensus(self, states: List[Dict]) -> Dict:
        """Aggregate consensus states using configurable rules"""
        if not states:
            return {}
            
        # Simple majority rules aggregation
        state_counts = {}
        for state in states:
            state_key = json.dumps(state, sort_keys=True)
            state_counts[state_key] = state_counts.get(state_key, 0) + 1
        
        # Get most common state
        majority_state = max(state_counts.items(), key=lambda x: x[1])[0]
        return json.loads(majority_state)

# Example usage:
# crawler = DistributedCrawler(['http://node1.example.com', 'http://node2.example.com'])
# await crawler.start()
# consensus = await crawler.get_consensus_state()
# await crawler.stop()