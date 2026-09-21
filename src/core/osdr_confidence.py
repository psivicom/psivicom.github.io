def calculate_match_confidence(mesh_meta: Dict, osdr_record: Dict) -> float:
    """
    Returns 0.0-1.0 confidence score based on:
    - Number of supporting datasets (n_datasets)
    - Statistical significance (max_q value)
    - Effect size consistency (min/max log2FC)
    """
    # Implementation uses OSDR evidence fields
