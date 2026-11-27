## Direct cause of the CI failure

The failing step is not a container/network problem. It is an import-time Python enum mismatch:

```text
File ".../src/agents/neuroplasticity_agent.py", line 25, in NeuroplasticityAgent
    LAYER = AgentLayer.OPTIMIZATION
AttributeError: OPTIMIZATION
```

What happens:

1. CI runs:

```bash
python -m src.agents.critic_agent
```

2. Python imports the package `src.agents`.

3. `src/agents/__init__.py` eagerly imports:

```python
from src.agents.neuroplasticity_agent import NeuroplasticityAgent
```

4. While defining `NeuroplasticityAgent`, the class body evaluates:

```python
LAYER = AgentLayer.OPTIMIZATION
```

5. `AgentLayer` does not contain a member named `OPTIMIZATION`, so Python raises `AttributeError`.

So the immediate fix is: **add `OPTIMIZATION` to `AgentLayer`**, or change `NeuroplasticityAgent.LAYER` to an existing layer. Since the agent is called “neuroplasticity”, the intended layer is probably `OPTIMIZATION`, so adding the enum member is the correct fix.

---

# 1. Minimal patch to unblock CI

First locate where `AgentLayer` is defined:

```bash
rg -n "class AgentLayer" src
```

It may be in something like:

```text
src/agents/base_agent.py
src/core/enums.py
src/agents/types.py
```

Then add the missing member.

## If `AgentLayer` uses string values

Example:

```python
from enum import Enum


class AgentLayer(str, Enum):
    PERCEPTION = "perception"
    COGNITION = "cognition"
    MEMORY = "memory"
    ACTION = "action"
    OPTIMIZATION = "optimization"
```

Patch shape:

```diff
--- a/src/agents/base_agent.py
+++ b/src/agents/base_agent.py
@@
 class AgentLayer(str, Enum):
     PERCEPTION = "perception"
     COGNITION = "cognition"
     MEMORY = "memory"
     ACTION = "action"
+    OPTIMIZATION = "optimization"
```

Adjust the existing members to whatever your file already has. The important part is adding:

```python
OPTIMIZATION = "optimization"
```

---

## If `AgentLayer` uses `auto()`

Example:

```python
from enum import Enum, auto


class AgentLayer(Enum):
    PERCEPTION = auto()
    COGNITION = auto()
    MEMORY = auto()
    ACTION = auto()
    OPTIMIZATION = auto()
```

Patch shape:

```diff
--- a/src/agents/base_agent.py
+++ b/src/agents/base_agent.py
@@
 from enum import Enum, auto
 
 
 class AgentLayer(Enum):
     PERCEPTION = auto()
     COGNITION = auto()
     MEMORY = auto()
     ACTION = auto()
+    OPTIMIZATION = auto()
```

Important: if enum values are persisted as integers somewhere, append the new member at the end so you do not renumber existing values.

---

## If `AgentLayer` uses explicit integers

Example:

```python
from enum import IntEnum


class AgentLayer(IntEnum):
    PERCEPTION = 1
    COGNITION = 2
    MEMORY = 3
    ACTION = 4
    OPTIMIZATION = 5
```

Again, append the new value rather than inserting it in the middle if integers are stored in databases, checkpoints, logs, or serialized messages.

---

# 2. Alternative fix if `OPTIMIZATION` is not intended

If `NeuroplasticityAgent` should not be in the optimization layer, change its class attribute to an existing enum member:

```diff
--- a/src/agents/neuroplasticity_agent.py
+++ b/src/agents/neuroplasticity_agent.py
@@
 class NeuroplasticityAgent(BaseAgent):
-    LAYER = AgentLayer.OPTIMIZATION
+    LAYER = AgentLayer.COGNITION
```

But based on the name, `OPTIMIZATION` looks intentional. I would recommend fixing the enum instead of downgrading the agent layer.

---

# 3. Harden `src/agents/__init__.py` to avoid unrelated import failures

Right now, running `src.agents.critic_agent` fails because importing the `src.agents` package imports every agent, including `NeuroplasticityAgent`.

That is fragile. A lightweight critic agent should not crash just because another agent has an unrelated import/class-definition error.

Replace eager agent-class imports in:

```text
src/agents/__init__.py
```

with lazy imports.

Example replacement:

```python
# src/agents/__init__.py
from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.agents.base_agent import BaseAgent
    from src.agents.critic_agent import CriticAgent
    from src.agents.neuroplasticity_agent import NeuroplasticityAgent

_LAZY_AGENT_EXPORTS: dict[str, str] = {
    "BaseAgent": "src.agents.base_agent",
    "CriticAgent": "src.agents.critic_agent",
    "NeuroplasticityAgent": "src.agents.neuroplasticity_agent",
}

__all__ = sorted(_LAZY_AGENT_EXPORTS)


def __getattr__(name: str) -> Any:
    target_module = _LAZY_AGENT_EXPORTS.get(name)

    if target_module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = importlib.import_module(target_module)
    value = getattr(module, name)

    # Cache it on the package so future lookups are normal attribute lookups.
    globals()[name] = value
    return value
```

Remove or comment out old eager imports like:

```python
from src.agents.neuroplasticity_agent import NeuroplasticityAgent
```

This way:

```bash
python -m src.agents.critic_agent
```

will not force-import `NeuroplasticityAgent` unless something actually asks for it.

---

# 4. Validation commands

After patching, run locally or in CI:

```bash
python -m compileall src
```

Smoke-import the critic agent without executing its `__main__` block:

```bash
python - <<'PY'
import importlib
importlib.import_module("src.agents.critic_agent")
print("critic_agent import OK")
PY
```

Verify the enum member exists:

```bash
python - <<'PY'
from src.agents.base_agent import AgentLayer

assert hasattr(AgentLayer, "OPTIMIZATION"), "AgentLayer.OPTIMIZATION is missing"
print("AgentLayer.OPTIMIZATION =", AgentLayer.OPTIMIZATION)
PY
```

If `AgentLayer` lives in another module, adjust the import path accordingly.

You can also add a CI guard before running agents:

```yaml
- name: Validate AgentLayer enum
  run: |
    python - <<'PY'
    from src.agents.base_agent import AgentLayer
    assert hasattr(AgentLayer, "OPTIMIZATION"), "AgentLayer.OPTIMIZATION missing"
    PY
```

---

# 5. PSVC container setup for Wendy

Once the Python import error is fixed, you can containerize the services properly. The goal is to make each Python service run as an isolated PSVC container with:

- minimal runtime dependencies,
- health checks,
- structured logs,
- vector-aware mesh transport,
- real data mounts,
- realtime chat/voice gateways,
- scalable worker services.

Below is a practical Podman/Docker Compose-compatible PSVC scaffold.

---

## Recommended repository layout

```text
.
├── .psvc/
│   ├── Containerfile
│   ├── entrypoint.sh
│   ├── healthcheck.py
│   └── vector.yaml
├── PSVC-compose.yml
├── requirements-agents.txt
├── requirements-gateway.txt
├── requirements-voice.txt
├── data/
│   └── real/
└── src/
    ├── agents/
    │   ├── __init__.py
    │   ├── base_agent.py
    │   ├── critic_agent.py
    │   └── neuroplasticity_agent.py
    ├── gateway/
    │   ├── chat.py
    │   └── voice.py
    └── mesh/
        └── router.py
```

Make sure your `.dockerignore` does not exclude `.psvc`.

Example `.dockerignore`:

```text
.git
.github
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
.ruff_cache
.coverage
htmlcov
dist
build
*.egg-info
.env
.venv
venv
```

Do **not** add:

```text
.psvc
```

---

# 6. Runtime requirement files

To install only required runtime dependencies, split requirements.

## `requirements-agents.txt`

```text
nats-py>=2.7.0
qdrant-client>=1.10.0
python-json-logger>=2.0.0
```

## `requirements-gateway.txt`

```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
websockets>=12.0
nats-py>=2.7.0
python-json-logger>=2.0.0
```

## `requirements-voice.txt`

```text
-r requirements-gateway.txt

faster-whisper>=1.0.0
piper-tts>=1.2.0
soundfile>=0.12.0
```

Pin exact versions in production after testing.

---

# 7. Generic PSVC container image

Use one Containerfile for all Python PSVC services. The service-specific module is supplied as a build argument.

## `.psvc/Containerfile`

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG PSVC_MODULE
ARG PSVC_SERVICE
ARG REQUIREMENTS=requirements-agents.txt
ARG SYSTEM_PACKAGES="ca-certificates"

ENV PSVC_MODULE=${PSVC_MODULE} \
    PSVC_SERVICE=${PSVC_SERVICE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache \
    WENDY_LOG_FORMAT=json \
    WENDY_ALLOW_SYNTHETIC=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ${SYSTEM_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY ${REQUIREMENTS} ./requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src ./src
COPY .psvc/entrypoint.sh .psvc/healthcheck.py ./

RUN chmod +x /app/entrypoint.sh \
    && groupadd --system wendy \
    && useradd --system --gid wendy --home-dir /home/wendy --shell /usr/sbin/nologin wendy \
    && mkdir -p /var/lib/wendy /tmp/psvc \
    && chown -R wendy:wendy /app /var/lib/wendy /tmp/psvc

USER wendy

ENTRYPOINT ["/app/entrypoint.sh"]

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD ["python", "/app/healthcheck.py"]
```

---

# 8. PSVC entrypoint with heartbeat

## `.psvc/entrypoint.sh`

```sh
#!/bin/sh
set -eu

: "${PSVC_MODULE:?PSVC_MODULE is required}"
: "${PSVC_SERVICE:?PSVC_SERVICE is required}"

HB="${PSVC_HEARTBEAT_FILE:-/tmp/psvc-heartbeat}"
INTERVAL="${PSVC_HEARTBEAT_INTERVAL:-10}"

log() {
    event="$1"
    printf '{"service":"%s","event":"%s","ts":"%s"}\n' \
        "$PSVC_SERVICE" \
        "$event" \
        "$(date -u +%FT%TZ)"
}

log "starting"

python -u -m "$PSVC_MODULE" &
APP_PID=$!

cleanup() {
    log "stopping"
    kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
    exit 0
}

trap cleanup TERM INT

status=0

while kill -0 "$APP_PID" 2>/dev/null; do
    date -u +%s > "$HB"
    sleep "$INTERVAL"
done

wait "$APP_PID" || status=$?

log "exited status=${status}"
exit "$status"
```

This gives every container a heartbeat file. The health check does not need to know whether the service exposes HTTP. It simply verifies that the supervisor loop is alive.

---

# 9. PSVC health check

## `.psvc/healthcheck.py`

```python
#!/usr/bin/env python3
import os
import pathlib
import sys
import time


def main() -> int:
    hb_path = pathlib.Path(os.getenv("PSVC_HEARTBEAT_FILE", "/tmp/psvc-heartbeat"))
    max_age = float(os.getenv("PSVC_HEALTH_MAX_AGE", "30"))

    if not hb_path.exists():
        print(f"missing heartbeat file: {hb_path}", file=sys.stderr)
        return 1

    try:
        raw = hb_path.read_text(encoding="utf-8").strip()
        last_beat = float(raw)
    except (OSError, ValueError) as exc:
        print(f"invalid heartbeat file: {exc}", file=sys.stderr)
        return 1

    age = time.time() - last_beat

    if age > max_age:
        print(f"stale heartbeat: age={age:.1f}s max_age={max_age:.1f}s", file=sys.stderr)
        return 1

    print(f"healthy: age={age:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

# 10. Vector log collector

This sidecar collects structured logs from PSVC containers and writes normalized JSON logs.

## `.psvc/vector.yaml`

```yaml
data_dir: /vector-data

sources:
  psvc_container_logs:
    type: docker_logs
    socket: /var/run/docker.sock
    include:
      - critic-agent
      - neuroplasticity-agent
      - chat-gateway
      - voice-gateway
      - mesh-router

transforms:
  normalize_psvc_logs:
    type: remap
    inputs:
      - psvc_container_logs
    source: |
      .service = get!(., "container_name") ?? "unknown"
      .level = downcase(get!(., "levelname") ?? "info")
      .vector_tag = "wendy.psvc." + .service
      .source = "psvc"

sinks:
  wendy_json_logs:
    type: file
    inputs:
      - normalize_psvc_logs
    path: /vector-data/wendy-%Y-%m-%d.log
    encoding:
      codec: json

  console_debug:
    type: console
    inputs:
      - normalize_psvc_logs
    encoding:
      codec: json
```

For Podman rootless, set the socket path correctly, for example:

```bash
export PSVC_CONTAINER_SOCKET=/run/user/1000/podman/podman.sock
```

For Podman rootful:

```bash
export PSVC_CONTAINER_SOCKET=/run/podman/podman.sock
```

For Docker:

```bash
export PSVC_CONTAINER_SOCKET=/var/run/docker.sock
```

---

# 11. PSVC mesh compose file

This defines Wendy as a small vector service mesh:

- `nats`: durable work-unit bus, inspired by SETI@home-style dispatch but vector-aware.
- `qdrant`: vector memory/store.
- `critic-agent`: independent worker container.
- `neuroplasticity-agent`: independent optimization worker container.
- `chat-gateway`: realtime human chat transport.
- `voice-gateway`: realtime human voice transport.
- `mesh-router`: optional control-plane/router service.
- `vector`: log collector.

## `PSVC-compose.yml`

```yaml
name: wendy-psvc

x-psvc-common: &psvc-common
  restart: unless-stopped
  init: true
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  read_only: true
  tmpfs:
    - /tmp:size=64m,mode=1777
  networks:
    - wendy-mesh
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  nats:
    image: nats:2.10-alpine
    container_name: wendy-nats
    restart: unless-stopped
    command: ["--js", "-m", "8222"]
    ports:
      - "4222:4222"
      - "8222:8222"
    volumes:
      - nats-data:/data
    networks:
      - wendy-mesh
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  qdrant:
    image: qdrant/qdrant:v1.12.4
    container_name: wendy-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - wendy-mesh
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  critic-agent:
    <<: *psvc-common
    container_name: wendy-critic-agent
    build:
      context: .
      dockerfile: .psvc/Containerfile
      args:
        PSVC_MODULE: src.agents.critic_agent
        PSVC_SERVICE: critic-agent
        REQUIREMENTS: requirements-agents.txt
    environment:
      WENDY_DATA_ROOT: /data/real
      WENDY_ALLOW_SYNTHETIC: "false"
      WENDY_MESH_SUBJECT_PREFIX: wendy.vectors
      WENDY_VECTOR_SPACE: critique
      NATS_URL: nats://nats:4222
      QDRANT_URL: http://qdrant:6333
      PSVC_HEARTBEAT_FILE: /tmp/psvc-heartbeat
      PSVC_HEALTH_MAX_AGE: "30"
    volumes:
      - ./data:/data:ro
      - wendy-critic-state:/var/lib/wendy
    depends_on:
      - nats
      - qdrant
    labels:
      psvc.mesh.role: worker
      psvc.mesh.vector-space: critique
      psvc.mesh.max-inflight: "4"
      psvc.mesh.scaling.metric: nats_queue_depth
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 512M

  neuroplasticity-agent:
    <<: *psvc-common
    container_name: wendy-neuroplasticity-agent
    build:
      context: .
      dockerfile: .psvc/Containerfile
      args:
        PSVC_MODULE: src.agents.neuroplasticity_agent
        PSVC_SERVICE: neuroplasticity-agent
        REQUIREMENTS: requirements-agents.txt
    environment:
      WENDY_DATA_ROOT: /data/real
      WENDY_ALLOW_SYNTHETIC: "false"
      WENDY_MESH_SUBJECT_PREFIX: wendy.vectors
      WENDY_VECTOR_SPACE: optimization
      NATS_URL: nats://nats:4222
      QDRANT_URL: http://qdrant:6333
      PSVC_HEARTBEAT_FILE: /tmp/psvc-heartbeat
      PSVC_HEALTH_MAX_AGE: "30"
    volumes:
      - ./data:/data:ro
      - wendy-neuro-state:/var/lib/wendy
    depends_on:
      - nats
      - qdrant
    labels:
      psvc.mesh.role: optimizer
      psvc.mesh.vector-space: optimization
      psvc.mesh.max-inflight: "2"
      psvc.mesh.scaling.metric: nats_queue_depth
    deploy:
      resources:
        limits:
          cpus: "1.00"
          memory: 1G

  chat-gateway:
    <<: *psvc-common
    container_name: wendy-chat-gateway
    build:
      context: .
      dockerfile: .psvc/Containerfile
      args:
        PSVC_MODULE: src.gateway.chat
        PSVC_SERVICE: chat-gateway
        REQUIREMENTS: requirements-gateway.txt
        SYSTEM_PACKAGES: "ca-certificates"
    environment:
      WENDY_DATA_ROOT: /data/real
      WENDY_ALLOW_SYNTHETIC: "false"
      WENDY_REALTIME_TRANSPORT: websocket
      WENDY_CHAT_WS_PATH: /ws/chat
      WENDY_HTTP_PORT: "8080"
      NATS_URL: nats://nats:4222
      QDRANT_URL: http://qdrant:6333
      PSVC_HEARTBEAT_FILE: /tmp/psvc-heartbeat
      PSVC_HEALTH_MAX_AGE: "30"
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data:ro
      - wendy-chat-state:/var/lib/wendy
    depends_on:
      - nats
      - qdrant
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - |
          import urllib.request
          urllib.request.urlopen("http://127.0.0.1:8080/healthz", timeout=2)
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 20s
    labels:
      psvc.mesh.role: realtime-gateway
      psvc.mesh.transport: websocket
      psvc.mesh.modality: text
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 512M

  voice-gateway:
    <<: *psvc-common
    container_name: wendy-voice-gateway
    build:
      context: .
      dockerfile: .psvc/Containerfile
      args:
        PSVC_MODULE: src.gateway.voice
        PSVC_SERVICE: voice-gateway
        REQUIREMENTS: requirements-voice.txt
        SYSTEM_PACKAGES: "ca-certificates libsndfile1 ffmpeg"
    environment:
      WENDY_DATA_ROOT: /data/real
      WENDY_AUDIO_ROOT: /data/audio
      WENDY_ALLOW_SYNTHETIC: "false"
      WENDY_REALTIME_TRANSPORT: websocket
      WENDY_VOICE_WS_PATH: /ws/voice
      WENDY_HTTP_PORT: "8081"
      WHISPER_MODEL: medium
      PIPER_VOICE: en_US-lessac-medium
      NATS_URL: nats://nats:4222
      QDRANT_URL: http://qdrant:6333
      PSVC_HEARTBEAT_FILE: /tmp/psvc-heartbeat
      PSVC_HEALTH_MAX_AGE: "60"
    ports:
      - "8081:8081"
    volumes:
      - ./data:/data:ro
      - voice-models:/models
      - wendy-voice-state:/var/lib/wendy
    depends_on:
      - nats
      - qdrant
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - |
          import urllib.request
          urllib.request.urlopen("http://127.0.0.1:8081/healthz", timeout=2)
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 60s
    labels:
      psvc.mesh.role: realtime-gateway
      psvc.mesh.transport: websocket
      psvc.mesh.modality: voice
    deploy:
      resources:
        limits:
          cpus: "2.00"
          memory: 4G

  mesh-router:
    <<: *psvc-common
    container_name: wendy-mesh-router
    build:
      context: .
      dockerfile: .psvc/Containerfile
      args:
        PSVC_MODULE: src.mesh.router
        PSVC_SERVICE: mesh-router
        REQUIREMENTS: requirements-gateway.txt
        SYSTEM_PACKAGES: "ca-certificates"
    environment:
      WENDY_MESH_SUBJECT_PREFIX: wendy.vectors
      WENDY_HTTP_PORT: "8899"
      NATS_URL: nats://nats:4222
      QDRANT_URL: http://qdrant:6333
      PSVC_HEARTBEAT_FILE: /tmp/psvc-heartbeat
      PSVC_HEALTH_MAX_AGE: "30"
    ports:
      - "8899:8899"
    depends_on:
      - nats
      - qdrant
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - |
          import urllib.request
          urllib.request.urlopen("http://127.0.0.1:8899/healthz", timeout=2)
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 20s
    labels:
      psvc.mesh.role: router
      psvc.mesh.function: vector_work_dispatch
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 512M

  vector:
    image: timberio/vector:0.40.0-alpine
    container_name: wendy-vector
    restart: unless-stopped
    environment:
      VECTOR_LOG: info
    volumes:
      - ./.psvc/vector.yaml:/etc/vector/vector.yaml:ro
      - ${PSVC_CONTAINER_SOCKET:-/var/run/docker.sock}:/var/run/docker.sock:ro
      - vector-data:/vector-data
    networks:
      - wendy-mesh
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  wendy-mesh:
    name: wendy-mesh
    driver: bridge

volumes:
  nats-data:
  qdrant-data:
  vector-data:
  voice-models:
  wendy-critic-state:
  wendy-neuro-state:
  wendy-chat-state:
  wendy-voice-state:
```

---

# 12. Build and run the PSVC mesh

From the repository root:

```bash
podman-compose -f PSVC-compose.yml build
podman-compose -f PSVC-compose.yml up -d
```

Check status:

```bash
podman-compose -f PSVC-compose.yml ps
```

Follow logs:

```bash
podman-compose -f PSVC-compose.yml logs -f critic-agent
podman-compose -f PSVC-compose.yml logs -f neuroplasticity-agent
podman-compose -f PSVC-compose.yml logs -f chat-gateway
podman-compose -f PSVC-compose.yml logs -f voice-gateway
podman-compose -f PSVC-compose.yml logs -f vector
```

Scale workers:

```bash
podman-compose -f PSVC-compose.yml up -d --scale critic-agent=3
podman-compose -f PSVC-compose.yml up -d --scale neuroplasticity-agent=2
```

For Docker Compose users:

```bash
docker compose -f PSVC-compose.yml build
docker compose -f PSVC-compose.yml up -d
```

---

# 13. Real data requirement

The compose file mounts:

```yaml
volumes:
  - ./data:/data:ro
```

and sets:

```yaml
WENDY_DATA_ROOT: /data/real
WENDY_ALLOW_SYNTHETIC: "false"
```

That means Wendy should read real corpora, transcripts, conversation logs, documents, or audio from:

```text
./data/real
```

For voice:

```text
./data/audio
```

Do not use synthetic fixtures in the production PSVC mesh. If you need test data, run a separate test profile with:

```yaml
WENDY_ALLOW_SYNTHETIC: "true"
```

but keep the production mesh on real data.

Example real data layout:

```text
data/
  real/
    conversations/
    documents/
    transcripts/
    feedback/
  audio/
    inbound/
    outbound/
```

Mount read-only so agents cannot accidentally mutate source truth data. State belongs in named volumes:

```text
wendy-critic-state
wendy-neuro-state
wendy-chat-state
wendy-voice-state
```

---

# 14. Realtime chat and voice contract

The compose file expects these Python modules:

```text
src/gateway/chat.py
src/gateway/voice.py
```

They should expose at least:

```text
GET /healthz
```

and realtime endpoints such as:

```text
WS /ws/chat
WS /ws/voice
```

Minimum behavior:

### Chat gateway

- Accept websocket connections from humans.
- Normalize incoming text messages.
- Publish work units to NATS subjects like:

```text
wendy.vectors.critique.work
wendy.vectors.optimization.work
```

- Subscribe to result subjects:

```text
wendy.vectors.results.>
```

- Stream responses back to the human websocket.

### Voice gateway

- Accept realtime audio via websocket, WebRTC, SIP, or another transport.
- Run STT, for example `faster-whisper`.
- Publish transcript work units to the same vector mesh.
- Receive textual responses.
- Run TTS, for example `piper-tts`.
- Stream audio back to the human.

The important architectural point is that chat and voice are transport gateways. The cognitive work happens inside independent PSVC agents.

---

# 15. Vector mesh subject convention

Use a predictable NATS subject scheme:

```text
wendy.vectors.<space>.work
wendy.vectors.<space>.results
wendy.vectors.<space>.heartbeat
wendy.vectors.<space>.metrics
```

Examples:

```text
wendy.vectors.critique.work
wendy.vectors.critique.results
wendy.vectors.optimization.work
wendy.vectors.optimization.results
```

Each worker can declare its vector space:

```yaml
WENDY_VECTOR_SPACE: critique
```

or:

```yaml
WENDY_VECTOR_SPACE: optimization
```

This gives you SETI@home-like distributed work units, but organized around vector spaces and semantic routing instead of raw radio data chunks.

---

# 16. Self-managing resources

The compose setup already provides basic self-management:

- `restart: unless-stopped`
- health checks
- heartbeat files
- resource limits
- read-only root filesystems
- tmpfs for temporary state
- persistent named volumes for service state
- centralized log collection through Vector

For true autonomous scaling, monitor NATS queue depth or mesh-router metrics and adjust replicas.

Example manual scaling policy:

```bash
# If critique queue is backing up
podman-compose -f PSVC-compose.yml up -d --scale critic-agent=5

# If optimization queue is idle
podman-compose -f PSVC-compose.yml up -d --scale neuroplasticity-agent=1
```

For production autonomy, run the same images under Nomad or Kubernetes and use the same health checks. The PSVC compose file is the single-host bootstrap; Nomad/Kubernetes provide the autoscaling control plane.

---

# 17. What to commit right now

At minimum, commit these changes to fix the failing CI job:

1. Add `OPTIMIZATION` to `AgentLayer`.
2. Make `src/agents/__init__.py` lazy instead of eagerly importing every agent.
3. Add a CI smoke test that imports `src.agents.critic_agent`.
4. Rebuild PSVC images after the source fix, because the broken enum is baked into any previously built image.

The critical patch is:

```python
class AgentLayer(...):
    ...
    OPTIMIZATION = "optimization"
```

or the equivalent `auto()`/integer form matching your existing enum style.

Once that is in place, the traceback:

```text
AttributeError: OPTIMIZATION
```

will disappear, and `python -m src.agents.critic_agent` will proceed past package import.