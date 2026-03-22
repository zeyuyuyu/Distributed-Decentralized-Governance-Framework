#!/usr/bin/env python3

import asyncio
import aiohttp
from typing import List, Set, Dict
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class PeerInfo:
    address: str
    last_seen: datetime
    consensus_version: str
    peers: Set[str]

class DistributedCrawler:
    def __init__(self, bootstrap_nodes: List[str], crawl_interval: int = 300):
        self.bootstrap_nodes = bootstrap_nodes
        self.crawl_interval = crawl_interval
        self.known_peers: Dict[str, PeerInfo] = {}
        self.session: aiohttp.ClientSession = None
        self.logger = logging.getLogger(__name__)

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def fetch_peer_info(self, peer_address: str) -> PeerInfo:
        try:
            async with self.session.get(f'{peer_address}/peer_info', timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return PeerInfo(
                        address=peer_address,
                        last_seen=datetime.now(),
                        consensus_version=data.get('version', 'unknown'),
                        peers=set(data.get('peers', []))
                    )
        except Exception as e:
            self.logger.error(f'Error fetching peer info from {peer_address}: {str(e)}')
        return None

    async def crawl_network(self):
        await self.init_session()
        
        while True:
            new_peers = set()
            
            # Start with bootstrap nodes if no known peers
            peers_to_crawl = set(self.known_peers.keys()) or set(self.bootstrap_nodes)
            
            for peer in peers_to_crawl:
                peer_info = await self.fetch_peer_info(peer)
                if peer_info:
                    self.known_peers[peer] = peer_info
                    new_peers.update(peer_info.peers)

            # Add newly discovered peers
            for new_peer in new_peers:
                if new_peer not in self.known_peers:
                    peer_info = await self.fetch_peer_info(new_peer)
                    if peer_info:
                        self.known_peers[new_peer] = peer_info

            # Prune stale peers
            now = datetime.now()
            stale_peers = [
                addr for addr, info in self.known_peers.items()
                if (now - info.last_seen).total_seconds() > self.crawl_interval * 2
            ]
            for peer in stale_peers:
                del self.known_peers[peer]

            self.logger.info(f'Network crawl complete. Known peers: {len(self.known_peers)}')
            await asyncio.sleep(self.crawl_interval)

    def get_network_stats(self) -> Dict:
        return {
            'total_peers': len(self.known_peers),
            'consensus_versions': {
                info.consensus_version: len([p for p in self.known_peers.values() 
                                           if p.consensus_version == info.consensus_version])
                for info in self.known_peers.values()
            },
            'network_density': sum(len(p.peers) for p in self.known_peers.values()) / 
                              max(len(self.known_peers), 1)
        }

    async def run(self):
        try:
            await self.crawl_network()
        finally:
            await self.close()

# Usage example:
# crawler = DistributedCrawler(['http://node1.example.com', 'http://node2.example.com'])
# asyncio.run(crawler.run())