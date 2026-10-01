Here is the fully updated `/requirements.txt` optimized specifically for **Python 3.12**. 

This version takes advantage of the latest pre-compiled `cp312` wheels (keeping your `.psvc` image lightweight) and upgrades the vector/math stack to **NumPy 2.x**, which includes massive performance improvements for vector operations.

### `requirements.txt`

```text
# ── Core Utilities ──
python-dateutil>=2.9.0.post0
requests>=2.32.3
pyyaml>=6.0.2
typing-extensions>=4.12.2
python-dotenv>=1.0.1

# ── Data & Visualization ──
# NumPy 2.x is highly optimized for Python 3.12 and critical for vector performance
numpy>=2.1.0
pandas>=2.2.2
matplotlib>=3.9.2
seaborn>=0.13.2

# ── ML, Vectors & Deep Learning ──
scikit-learn>=1.5.1
torch>=2.4.0
torchvision>=0.19.0
torchaudio>=2.4.0
jax>=0.4.31
jaxlib>=0.4.31

# ── PDF Generation ──
# fpdf2 is the actively maintained, Python 3.12 compatible drop-in replacement for fpdf
fpdf2>=2.7.9

# ── REMOVED DEPENDENCIES ──
# subprocess32: Removed. Python 3.12 stdlib `subprocess` is native, faster, and fully featured.
# fpdf: Removed. Replaced by fpdf2.
# jax==0.2.12 / jaxlib==0.1.68: Removed. Replaced with >=0.4.31 for native cp312 wheel support.
```

### Key Architectural Upgrades in this File:
1. **NumPy 2.x (`numpy>=2.1.0`)**: The biggest shift. NumPy 2.0 introduced a new C-API and massive memory/performance optimizations specifically designed for modern vector workloads and Python 3.12.
2. **JAX / JAXlib (`>=0.4.31`)**: Fully supports Python 3.12. Unlike the old 0.1.x versions, these will download as pre-compiled binary wheels, meaning your `.psvc` build won't need to compile C-extensions from source.
3. **PyTorch 2.4+**: Fully supports 3.12 and includes `torch.compile` optimizations which will significantly speed up your vector inference if you use it.
4. **Zero Bloat**: By dropping `subprocess32` and using `fpdf2`, we removed legacy code that either fails to build on 3.12 or forces unnecessary compilation steps.

### Next Step for your `.psvc` Runtime:
Update your `.psvc` manifest or CI pipeline to explicitly target Python 3.12:
```yaml
runtime:
  base: "python:3.12-slim" # Or your custom .psvc 3.12 base image
```
This will clear your CI errors and give WENDY the fastest possible Python execution layer for your vector mesh.