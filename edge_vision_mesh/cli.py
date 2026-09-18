"""
EdgeVisionMesh CLI: Decentralized P2P Edge NPU ReID & Mesh Tracking Suite.
"""
import argparse
from .edge_npu.reid_embedder import EdgeReIDEmbedder
from .mesh_p2p.gossip_protocol import PeerToPeerGossipSwarm
from .spatial.multi_camera_tracker import MultiCameraMeshTracker

def main():
    parser = argparse.ArgumentParser(
        prog="edge-vision-mesh",
        description="Decentralized P2P Edge-NPU Multi-Camera Re-Identification Swarm with Zero Cloud Bandwidth Egress."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # tokenize-reid
    subparsers.add_parser("tokenize-reid", help="Extract on-device 256-bit anonymous ReID token (Zero Video Bytes)")

    # mesh-gossip
    subparsers.add_parser("mesh-gossip", help="Simulate decentralized P2P token gossip across adjoining camera nodes")

    # track-handoff
    subparsers.add_parser("track-handoff", help="Simulate multi-camera sector trajectory handoff")

    args = parser.parse_args()

    if args.command == "tokenize-reid":
        features = [0.2, 0.4, -0.1, 0.8, 0.3]
        token = EdgeReIDEmbedder.extract_token(
            camera_id="CAM_NORTH_GATE_01",
            track_id="TRK_09",
            simulated_rgb_crop_features=features,
            bbox={"x": 100, "y": 200, "w": 60, "h": 140}
        )
        print("[EdgeVisionMesh] On-Device Edge NPU ReID Token:")
        print(f"  Camera ID            : {token.camera_id}")
        print(f"  256-bit Feature Hash : {token.feature_hash_256}")
        print(f"  Appearance Vector    : {token.appearance_vector}")
        print("  Cloud Bandwidth Egress: 0 BYTES (Raw video remains on camera sensor).")

    elif args.command == "mesh-gossip":
        topology = {
            "CAM_GATE": ["CAM_CORRIDOR_A", "CAM_PARKING_WEST"],
            "CAM_CORRIDOR_A": ["CAM_GATE", "CAM_LOBBY"],
            "CAM_PARKING_WEST": ["CAM_GATE"],
            "CAM_LOBBY": ["CAM_CORRIDOR_A"]
        }
        swarm = PeerToPeerGossipSwarm(topology)
        features = [0.5, 0.5, 0.5, 0.5]
        token = EdgeReIDEmbedder.extract_token("CAM_GATE", "TRK_01", features, {"x":0,"y":0,"w":10,"h":10})
        res = swarm.broadcast_local_detection(token)

        print("[EdgeVisionMesh] P2P Camera Mesh Gossip:")
        print(f"  Origin Camera       : {res['origin_camera']}")
        print(f"  Peers Gossiped To   : {', '.join(res['peers_notified'])}")
        print(f"  Mesh Bandwidth Used : {res['egress_bandwidth_bytes']} bytes")
        print(f"  Cloud Egress Cost   : $0.00 (Zero bytes sent to AWS/GCP data centers)")

    elif args.command == "track-handoff":
        tracker = MultiCameraMeshTracker(reid_match_threshold=0.80)
        # Person walking from Gate -> Corridor A -> Lobby
        features_suspect = [0.1, 0.9, 0.2, 0.3]
        t1 = EdgeReIDEmbedder.extract_token("CAM_GATE", "TRK_A1", features_suspect, {"x":10,"y":10,"w":20,"h":50})
        t2 = EdgeReIDEmbedder.extract_token("CAM_CORRIDOR_A", "TRK_B4", features_suspect, {"x":40,"y":50,"w":20,"h":50})
        t3 = EdgeReIDEmbedder.extract_token("CAM_LOBBY", "TRK_C2", features_suspect, {"x":90,"y":80,"w":20,"h":50})

        r1 = tracker.ingest_token(t1)
        r2 = tracker.ingest_token(t2)
        r3 = tracker.ingest_token(t3)

        print("[EdgeVisionMesh] Multi-Camera Spatial Trajectory Fusion:")
        print(f"  Step 1: {r1['event']} -> Assigned: {r1['global_target_id']} ({r1['current_camera']})")
        print(f"  Step 2: {r2['event']} -> Matched: {r2['global_target_id']} (Sim: {r2['similarity_score']})")
        print(f"  Step 3: {r3['event']} -> Matched: {r3['global_target_id']} (Sim: {r3['similarity_score']})")
        print(f"  Total Trajectory Hops: {r3['trajectory_hops']} (Persistent tracking across physical zones)")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
