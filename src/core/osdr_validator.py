def validate_osdr_record(record: Dict) -> bool:
    """Ensures OSDR records have required fields: gene, organism, tissue, evidence"""
    required = ['gene', 'organism', 'tissue', 'evidence', 'item_type']
    return all(k in record for k in required)
