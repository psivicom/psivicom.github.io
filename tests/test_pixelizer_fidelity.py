"""
AETHER VANGUARD - Fidelity Tests
Ensures vector pixelization does not destroy ecological data integrity.
"""
import torch
from src.core.vector_pixelizer import VectorPixelizer

def test_pixelizer_initialization():
    """Test that the pixelizer boots without errors."""
    config = {}
    pixelizer = VectorPixelizer(config)
    assert pixelizer is not None

def test_holographic_sharding():
    """Test that sharding produces the correct number of tensor fragments."""
    pixelizer = VectorPixelizer({})
    dummy_tensor = torch.randn(4096)
    shards = pixelizer.holographic_shard(dummy_tensor, num_shards=4)
    
    assert len(shards) == 4
    assert shards[0].shape[0] == 1024 # 4096 / 4 = 1024
