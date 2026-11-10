"""Rotation-ensemble polar correction (SO(3) pitch-rotated ERPs + cos^2 prior fusion)."""
from pano.inference.rotation_inference import predict_rotated_raw, unrotate_predictions
from pano.inference.pipeline import DistortionAwareInference, MethodConfig
__all__ = ["predict_rotated_raw", "unrotate_predictions", "DistortionAwareInference", "MethodConfig"]
