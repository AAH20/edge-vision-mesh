import unittest
from edge_vision_mesh.edge_npu.reid_embedder import EdgeReIDEmbedder, ReIDToken
from edge_vision_mesh.mesh_p2p.gossip_protocol import PeerToPeerGossipSwarm
from edge_vision_mesh.spatial.multi_camera_tracker import MultiCameraMeshTracker

class TestEdgeVisionMesh(unittest.TestCase):
    def test_reid_tokenization_and_similarity(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.98, 0.05, 0.0]
        t1 = EdgeReIDEmbedder.extract_token("CAM_1", "T_1", v1, {"x":0,"y":0,"w":10,"h":10})
        t2 = EdgeReIDEmbedder.extract_token("CAM_2", "T_2", v2, {"x":0,"y":0,"w":10,"h":10})

        self.assertEqual(len(t1.feature_hash_256), 64)
        sim = EdgeReIDEmbedder.cosine_similarity(t1, t2)
        self.assertTrue(sim > 0.95)

    def test_mesh_gossip_protocol(self):
        topo = {"CAM_A": ["CAM_B", "CAM_C"], "CAM_B": [], "CAM_C": []}
        swarm = PeerToPeerGossipSwarm(topo)
        token = EdgeReIDEmbedder.extract_token("CAM_A", "T_A", [0.5, 0.5], {"x":0,"y":0,"w":10,"h":10})

        res = swarm.broadcast_local_detection(token)
        self.assertEqual(len(res["peers_notified"]), 2)
        self.assertEqual(res["cloud_data_center_bytes_sent"], 0)
        self.assertEqual(len(swarm.camera_token_stores["CAM_B"]), 1)

    def test_multi_camera_trajectory_handoff(self):
        tracker = MultiCameraMeshTracker(reid_match_threshold=0.85)
        vec = [0.3, 0.4, 0.5]
        t_cam1 = EdgeReIDEmbedder.extract_token("CAM_GATE", "TK1", vec, {"x":0,"y":0,"w":10,"h":10})
        t_cam2 = EdgeReIDEmbedder.extract_token("CAM_HALL", "TK2", vec, {"x":0,"y":0,"w":10,"h":10})

        r1 = tracker.ingest_token(t_cam1)
        r2 = tracker.ingest_token(t_cam2)

        self.assertEqual(r1["event"], "NEW_TARGET_ACQUIRED")
        self.assertEqual(r2["global_target_id"], r1["global_target_id"])
        self.assertIn("SECTOR_HANDOFF", r2["event"])
        self.assertEqual(r2["trajectory_hops"], 2)

if __name__ == "__main__":
    unittest.main()
