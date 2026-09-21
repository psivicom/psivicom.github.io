def query_osdr_api(gene: str, organism: str) -> List[Dict]:
    """Fetches additional OSDR records for a gene/organism pair"""
    # Calls https://opensciencedatacloud.org/api
