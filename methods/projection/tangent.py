"""Tangent-plane polar correction (gnomonic views + baseline alignment + cosine blend)."""
from pano.inference.tangent_inference import predict_tangent_raw, reproject_tangent_predictions
from pano.inference.pipeline import DistortionAwareInference, MethodConfig
__all__ = ["predict_tangent_raw", "reproject_tangent_predictions", "DistortionAwareInference", "MethodConfig"]
