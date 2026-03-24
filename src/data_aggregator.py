import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DataNode:
    timestamp: datetime
    data: Any
    source_id: str
    hash: str = ''

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        content = f'{self.timestamp}{self.data}{self.source_id}'
        return hashlib.sha256(content.encode()).hexdigest()

class DistributedAggregator:
    def __init__(self):
        self.nodes: List[DataNode] = []
        self.merkle_root: str = ''

    def add_data(self, data: Any, source_id: str) -> None:
        """Add new data to the aggregator with source tracking"""
        node = DataNode(
            timestamp=datetime.now(),
            data=data,
            source_id=source_id
        )
        self.nodes.append(node)
        self._update_merkle_root()

    def _update_merkle_root(self) -> None:
        """Update the Merkle root hash based on current nodes"""
        if not self.nodes:
            self.merkle_root = ''
            return

        leaves = [node.hash for node in self.nodes]
        while len(leaves) > 1:
            temp = []
            for i in range(0, len(leaves), 2):
                hash1 = leaves[i]
                hash2 = leaves[i + 1] if i + 1 < len(leaves) else hash1
                combined = hashlib.sha256(f'{hash1}{hash2}'.encode()).hexdigest()
                temp.append(combined)
            leaves = temp
        self.merkle_root = leaves[0]

    def get_aggregated_data(self) -> Dict[str, List[Any]]:
        """Get aggregated data grouped by source"""
        result = {}
        for node in self.nodes:
            if node.source_id not in result:
                result[node.source_id] = []
            result[node.source_id].append(node.data)
        return result

    def verify_integrity(self) -> bool:
        """Verify data integrity using Merkle tree"""
        current_root = self.merkle_root
        self._update_merkle_root()
        return current_root == self.merkle_root

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about aggregated data"""
        return {
            'total_nodes': len(self.nodes),
            'unique_sources': len(set(node.source_id for node in self.nodes)),
            'merkle_root': self.merkle_root,
            'last_updated': max(node.timestamp for node in self.nodes) if self.nodes else None
        }