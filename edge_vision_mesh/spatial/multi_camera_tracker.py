"""
Multi-Camera Trajectory Fusion & Sector Handoff Engine.
Fuses ReID tokens across physical camera zones to maintain persistent suspect trajectories.
"""
from typing import Dict, List, Any, Optional
from ..edge_npu.reid_embedder import ReIDToken, EdgeReIDEmbedder

class MultiCameraMeshTracker:
    def __init__(self, reid_match_threshold: float = 0.85):
        self.match_threshold = reid_match_threshold
        self.global_tracks: Dict[str, List[ReIDToken]] = {} # global_target_id -> [ReIDToken]

    def ingest_token(self, token: ReIDToken) -> Dict[str, Any]:
        best_target_id = None
        highest_sim = -1.0

        # Match against known global tracks
        for target_id, trajectory in self.global_tracks.items():
            latest_token = trajectory[-1]
            sim = EdgeReIDEmbedder.cosine_similarity(token, latest_token)
            if sim > highest_sim and sim >= self.match_threshold:
                highest_sim = sim
                best_target_id = target_id

        if best_target_id is None:
            # Establish new persistent global track
            best_target_id = f"GLOBAL_TARGET_{len(self.global_tracks) + 1:04d}"
            self.global_tracks[best_target_id] = [token]
            event_type = "NEW_TARGET_ACQUIRED"
        else:
            # Trajectory handoff between cameras
            prev_cam = self.global_tracks[best_target_id][-1].camera_id
            self.global_tracks[best_target_id].append(token)
            event_type = f"SECTOR_HANDOFF_FROM_{prev_cam}_TO_{token.camera_id}" if prev_cam != token.camera_id else "INTRA_SECTOR_TRACK"

        return {
            "global_target_id": best_target_id,
            "event": event_type,
            "current_camera": token.camera_id,
            "similarity_score": round(highest_sim, 3) if highest_sim > 0 else 1.0,
            "trajectory_hops": len(self.global_tracks[best_target_id])
        }
