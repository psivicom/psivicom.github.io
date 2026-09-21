@dataclass
class OSDRProvenance:
    source_osd_id: str
    mesh_vector_hash: str
    pilot_receipt_hash: str
    timestamp: float
