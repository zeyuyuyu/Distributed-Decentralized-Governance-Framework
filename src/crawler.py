import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

class GovernanceProposalCrawler:
    def __init__(self, rpc_endpoints: List[str]):
        self.rpc_endpoints = rpc_endpoints
        self.logger = logging.getLogger(__name__)

    def fetch_proposals(self, chain_id: int) -> List[Dict]:
        """Fetch governance proposals from multiple sources for given chain"""
        proposals = []
        
        try:
            # Fetch from Snapshot
            snapshot_proposals = self._fetch_snapshot_proposals(chain_id)
            proposals.extend(snapshot_proposals)

            # Fetch from Tally
            tally_proposals = self._fetch_tally_proposals(chain_id) 
            proposals.extend(tally_proposals)

            # Fetch from on-chain governance
            onchain_proposals = self._fetch_onchain_proposals(chain_id)
            proposals.extend(onchain_proposals)

        except Exception as e:
            self.logger.error(f'Error fetching proposals: {str(e)}')

        return self._deduplicate_proposals(proposals)

    def _fetch_snapshot_proposals(self, chain_id: int) -> List[Dict]:
        """Fetch proposals from Snapshot"""
        snapshot_url = f'https://hub.snapshot.org/graphql'
        query = """
        query Proposals($chainId: Int) {
            proposals(chainId: $chainId) {
                id
                title
                body
                start
                end
                state
                choices
                scores
            }
        }
        """
        try:
            response = requests.post(
                snapshot_url,
                json={'query': query, 'variables': {'chainId': chain_id}}
            )
            return response.json().get('data', {}).get('proposals', [])
        except:
            self.logger.error('Failed to fetch Snapshot proposals')
            return []

    def _fetch_tally_proposals(self, chain_id: int) -> List[Dict]:
        """Fetch proposals from Tally"""
        tally_url = f'https://api.tally.xyz/query'
        # Implementation specific to Tally API
        return []

    def _fetch_onchain_proposals(self, chain_id: int) -> List[Dict]:
        """Fetch proposals directly from blockchain"""
        proposals = []
        for endpoint in self.rpc_endpoints:
            try:
                # Web3 implementation to fetch on-chain governance proposals
                pass
            except Exception as e:
                self.logger.error(f'RPC endpoint {endpoint} failed: {str(e)}')
                continue
        return proposals

    def _deduplicate_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """Remove duplicate proposals based on proposal ID"""
        seen_ids = set()
        unique_proposals = []

        for prop in proposals:
            if prop['id'] not in seen_ids:
                seen_ids.add(prop['id'])
                unique_proposals.append(prop)

        return unique_proposals

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict]:
        """Get current status of a specific proposal"""
        try:
            # Implementation to fetch specific proposal status
            return {
                'id': proposal_id,
                'status': 'active',  # or 'passed', 'failed', 'pending'
                'votes': {},
                'updated_at': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f'Error fetching proposal {proposal_id}: {str(e)}')
            return None
