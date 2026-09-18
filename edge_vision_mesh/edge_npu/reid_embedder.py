"""
On-Device Person Re-Identification (ReID) Tokenizer.
Extracts 256-bit compact anonymous tokens from on-device NPU bounding boxes.
Zero raw video bytes leave the local camera sensor.
"""
from dataclasses import dataclass
import hashlib
import time
from typing import List, Dict, Any

@dataclass(frozen=True)
class ReIDToken:
    camera_id: str
    track_id: str
    timestamp_us: int
    feature_hash_256: str
    spatial_bbox: Dict[str, int]
    appearance_vector: List[float]

class EdgeReIDEmbedder:
    @staticmethod
    def extract_token(
        camera_id: str,
        track_id: str,
        simulated_rgb_crop_features: List[float],
        bbox: Dict[str, int]
    ) -> ReIDToken:
        now_us = int(time.time() * 1_000_000)
        # Normalize appearance vector to unit hypersphere
        norm = sum(x * x for x in simulated_rgb_crop_features) ** 0.5
        norm_vec = [round(x / max(1e-6, norm), 4) for x in simulated_rgb_crop_features]
        # 256-bit feature fingerprint
        feat_str = str(norm_vec).encode()
        feat_hash = hashlib.sha256(feat_str).hexdigest()

        return ReIDToken(
            camera_id=camera_id,
            track_id=track_id,
            timestamp_us=now_us,
            feature_hash_256=feat_hash,
            spatial_bbox=bbox,
            appearance_vector=norm_vec
        )

    @staticmethod
    def cosine_similarity(token_a: ReIDToken, token_b: ReIDToken) -> float:
        return sum(a * b for a, b in zip(token_a.appearance_vector, token_b.appearance_vector))
