import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import socket

class NetworkCrawler:
    def __init__(self, bootstrap_nodes: List[str] = None):
        self.bootstrap_nodes = bootstrap_nodes or [
            'node1.governance.network:8545',
            'node2.governance.network:8545'
        ]
        self.discovered_peers = set()
        self.validated_peers = set()
        self.peer_metadata: Dict[str, dict] = {}

    def discover_network(self) -> set:
        """Crawl the network to discover active governance nodes"""
        for bootstrap in self.bootstrap_nodes:
            try:
                peers = self._query_node_peers(bootstrap)
                self.discovered_peers.update(peers)
                
                # Recursive discovery through found peers
                for peer in peers:
                    if peer not in self.discovered_peers:
                        new_peers = self._query_node_peers(peer)
                        self.discovered_peers.update(new_peers)
            except Exception as e:
                print(f'Failed to query bootstrap node {bootstrap}: {str(e)}')
        
        return self.discovered_peers

    def validate_peers(self) -> Dict[str, dict]:
        """Validate discovered peers and collect their metadata"""
        for peer in self.discovered_peers:
            try:
                if self._validate_peer(peer):
                    self.validated_peers.add(peer)
                    self.peer_metadata[peer] = self._get_peer_metadata(peer)
            except Exception as e:
                print(f'Failed to validate peer {peer}: {str(e)}')
        
        return self.peer_metadata

    def _query_node_peers(self, node_addr: str) -> set:
        """Query a node for its connected peers"""
        try:
            url = f'http://{node_addr}/peers'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return set(response.json().get('peers', []))
        except:
            pass
        return set()

    def _validate_peer(self, peer: str) -> bool:
        """Validate a peer node meets protocol requirements"""
        try:
            # Check if peer is online
            host, port = peer.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            if result != 0:
                return False

            # Verify peer version and protocol compatibility
            url = f'http://{peer}/version'
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return False
                
            version_data = response.json()
            if not self._check_version_compatibility(version_data):
                return False

            return True

        except Exception:
            return False

    def _get_peer_metadata(self, peer: str) -> dict:
        """Collect metadata about a peer node"""
        try:
            url = f'http://{peer}/status'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                metadata = response.json()
                metadata['last_seen'] = datetime.utcnow().isoformat()
                metadata['peer_addr'] = peer
                return metadata
        except:
            pass
        return {}

    def _check_version_compatibility(self, version_data: dict) -> bool:
        """Check if peer version is compatible"""
        try:
            min_version = '1.0.0'
            peer_version = version_data.get('version')
            if peer_version:
                # Simple version comparison - could be enhanced
                return peer_version >= min_version
        except:
            pass
        return False

    def get_network_status(self) -> Dict[str, any]:
        """Get overall network status and health metrics"""
        return {
            'total_discovered': len(self.discovered_peers),
            'total_validated': len(self.validated_peers),
            'active_peers': [
                peer for peer in self.validated_peers
                if self._is_peer_active(peer)
            ],
            'network_health': self._calculate_health_score(),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _is_peer_active(self, peer: str) -> bool:
        """Check if a peer is currently active"""
        metadata = self.peer_metadata.get(peer, {})
        if not metadata:
            return False
            
        last_seen = metadata.get('last_seen')
        if not last_seen:
            return False
            
        last_seen_dt = datetime.fromisoformat(last_seen)
        diff = datetime.utcnow() - last_seen_dt
        return diff.total_seconds() < 300  # 5 minute threshold

    def _calculate_health_score(self) -> float:
        """Calculate overall network health score (0-1)"""
        if not self.discovered_peers:
            return 0.0
            
        active_peers = len([p for p in self.validated_peers if self._is_peer_active(p)])
        health_score = active_peers / len(self.discovered_peers)
        return round(health_score, 2)
