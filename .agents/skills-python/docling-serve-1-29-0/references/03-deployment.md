# Deployment

## Container images

| Image | Description | Architectures | Size |
|-------|-------------|---------------|------|
| `quay.io/docling-project/docling-serve` | PyPI base | amd64, arm64 | 4.4–8.7 GB |
| `quay.io/docling-project/docling-serve-cpu` | CPU-only PyTorch | amd64, arm64 | 4.4 GB |
| `quay.io/docling-project/docling-serve-cu128` | CUDA 12.8 | amd64 | 11.4 GB |
| `quay.io/docling-project/docling-serve-cu130` | CUDA 13.0 | amd64, arm64 | TBD |

Also available on `ghcr.io/docling-project/docling-serve`.

**Tagging policy:**
- Base and CPU images: `latest`, `main`, and version tags
- CUDA images: **only explicit version tags** and `main` (no `latest`)

```bash
# Pin CUDA images to explicit versions
podman run quay.io/docling-project/docling-serve-cu128:1.29.0

# Base images can use latest
podman run quay.io/docling-project/docling-serve:latest
```

## Quick start

```bash
# Python package
pip install "docling-serve[ui]"
docling-serve run --enable-ui

# Container (base)
podman run -p 5001:5001 -e DOCLING_SERVE_ENABLE_UI=1 quay.io/docling-project/docling-serve

# CPU-only
podman run -p 5001:5001 quay.io/docling-project/docling-serve-cpu

# CUDA
podman run -p 5001:5001 --gpus all quay.io/docling-project/docling-serve-cu128:1.29.0
```

## NVIDIA GPU (Docker Compose)

Requirements: NVIDIA drivers >=550.54.14, nvidia-container-toolkit.

```yaml
# docker-compose-nvidia.yaml
services:
  docling-serve:
    image: quay.io/docling-project/docling-serve-cu128:1.29.0
    ports:
      - "5001:5001"
    environment:
      - DOCLING_SERVE_ENABLE_UI=true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

```bash
docker compose -f docker-compose-nvidia.yaml up -d
```

## AMD GPU (ROCm)

The ROCm image is not published. Build locally:

```bash
git clone --branch v1.29.0 https://github.com/docling-project/docling-serve.git
cd docling-serve/
make docling-serve-rocm-image
```

Requirements: AMDGPU driver >=6.3, ROCm >=6.3. Mount video and render device groups.

## Kubernetes — simple deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve
spec:
  replicas: 1
  selector:
    matchLabels:
      app: docling-serve
  template:
    metadata:
      labels:
        app: docling-serve
    spec:
      containers:
        - name: api
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          ports:
            - containerPort: 5001
          env:
            - name: DOCLING_SERVE_ENABLE_UI
              value: "true"
          resources:
            requests:
              cpu: "2"
              memory: "8Gi"
            limits:
              cpu: "4"
              memory: "16Gi"
          readinessProbe:
            httpGet:
              path: /ready
              port: 5001
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /livez
              port: 5001
            initialDelaySeconds: 60
            periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: docling-serve
spec:
  selector:
    app: docling-serve
  ports:
    - port: 5001
      targetPort: 5001
```

## Kubernetes — RQ with Redis

```yaml
# Redis
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve-redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: docling-serve-redis
  template:
    metadata:
      labels:
        app: docling-serve-redis
    spec:
      containers:
        - name: redis
          image: redis:7
          ports:
            - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: docling-serve-redis-service
spec:
  selector:
    app: docling-serve-redis
  ports:
    - port: 6379
      targetPort: 6379
```

API server:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve-api
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: api
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          command: ["docling-serve", "run"]
          env:
            - name: DOCLING_SERVE_ENG_KIND
              value: rq
            - name: DOCLING_SERVE_ENG_RQ_REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: docling-serve-rq-secrets
                  key: RQ_REDIS_URL
---
# RQ Workers
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve-workers
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: worker
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          command: ["docling-serve", "rq-worker"]
          env:
            - name: DOCLING_SERVE_ENG_KIND
              value: rq
            - name: DOCLING_SERVE_ENG_RQ_REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: docling-serve-rq-secrets
                  key: RQ_REDIS_URL
```

Create secret:

```bash
kubectl create secret generic docling-serve-rq-secrets \
  --from-literal=REDIS_PASSWORD=myredispassword \
  --from-literal=RQ_REDIS_URL=redis://:myredispassword@docling-serve-redis-service:6379/
```

## Kubernetes — replicas with sticky sessions

For WebSocket support, use sticky sessions (session affinity):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: docling-serve
spec:
  selector:
    app: docling-serve
  ports:
    - port: 5001
      targetPort: 5001
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

## OpenShift — secure with oauth-proxy

Use an `oauth-proxy` sidecar for authentication via OpenShift OAuth:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve
spec:
  template:
    spec:
      containers:
        - name: api
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          ports:
            - containerPort: 5001
        - name: oauth-proxy
          image: quay.io/oauth2-proxy/oauth2-proxy:v7.6.0
          args:
            - --upstream=http://localhost:5001
            - --provider=openshift
            - --skip-provider-button
            - --openshift-service-account=$(SERVICE_ACCOUNT)
          env:
            - name: SERVICE_ACCOUNT
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
          ports:
            - containerPort: 8080
```

## Model persistence (PVC)

For GPU deployments, persist models across pod restarts:

```yaml
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: docling-model-cache-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
# Download job
apiVersion: batch/v1
kind: Job
metadata:
  name: docling-model-cache-load
spec:
  template:
    spec:
      containers:
        - name: loader
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          command:
            - docling-tools
            - models
            - download
            - '--output-dir=/modelcache'
            - '--all'
          volumeMounts:
            - name: docling-model-cache
              mountPath: /modelcache
      volumes:
        - name: docling-model-cache
          persistentVolumeClaim:
            claimName: docling-model-cache-pvc
      restartPolicy: Never
---
# Deployment with mounted models
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-serve
spec:
  template:
    spec:
      containers:
        - name: api
          image: quay.io/docling-project/docling-serve-cpu:1.29.0
          env:
            - name: DOCLING_SERVE_ARTIFACTS_PATH
              value: /modelcache
          volumeMounts:
            - name: docling-model-cache
              mountPath: /modelcache
      volumes:
        - name: docling-model-cache
          persistentVolumeClaim:
            claimName: docling-model-cache-pvc
```

## Resource recommendations

| Deployment | CPU | Memory | GPU |
|------------|-----|--------|-----|
| CPU-only, light | 2 cores | 8 GB | — |
| CPU-only, heavy | 4 cores | 16 GB | — |
| GPU (NVIDIA) | 4 cores | 16 GB | 1x GPU |
| GPU (multi-doc) | 8 cores | 32 GB | 1x GPU |
| RQ worker | 2 cores | 8 GB | per workload |

## Observability

- `/metrics` — Prometheus metrics (default enabled)
- `/ready` — readiness probe (models loaded + orchestrator healthy)
- `/livez` — liveness probe (orchestrator loop running)
- OpenTelemetry traces — enable with `DOCLING_SERVE_OTEL_ENABLE_TRACES=true` and `OTEL_EXPORTER_OTLP_ENDPOINT`
- JSON logs — enable with `DOCLING_SERVE_LOG_FORMAT=json`
