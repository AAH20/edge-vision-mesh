"""
Decentralized Camera Mesh Gossip Protocol.
Disseminates 256-bit ReID tokens between adjoining cameras with zero central cloud relay.
"""
from typing import Dict, List, Set, Any
from ..edge_npu.reid_embedder import ReIDToken

class PeerToPeerGossipSwarm:
    def __init__(self, camera_topology: Dict[str, List[str]]):
        # camera_id -> list of adjoining peer camera_ids
        self.topology = camera_topology
        self.camera_token_stores: Dict[str, List[ReIDToken]] = {c: [] for c in camera_topology}
        self.bandwidth_consumed_bytes = 0

    def broadcast_local_detection(self, token: ReIDToken) -> Dict[str, Any]:
        origin = token.camera_id
        peers = self.topology.get(origin, [])
        delivered_peers = []

        for peer in peers:
            # Transmit only 256-bit hash and compact vector (approx 128 bytes, zero video)
            self.camera_token_stores[peer].append(token)
            self.bandwidth_consumed_bytes += 128
            delivered_peers.append(peer)

        return {
            "origin_camera": origin,
            "peers_notified": delivered_peers,
            "egress_bandwidth_bytes": 128 * len(peers),
            "cloud_data_center_bytes_sent": 0  # Zero Cloud Egress
        }
