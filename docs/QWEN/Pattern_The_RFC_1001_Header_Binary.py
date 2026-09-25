header = MAGIC          # b'PSVI'
header += struct.pack('B', VERSION)       # 1
header += struct.pack('B', PRECISION_FLOAT32) # 2
header += struct.pack('<I', len(vector))  # Vector length
header += struct.pack('<I', len(compressed_payload)) # Payload size
