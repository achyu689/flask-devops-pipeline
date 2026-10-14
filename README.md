# Flask DevOps Pipeline

A small Python Flask application with a complete DevOps setup: containerization, CI/CD, security scanning, Kubernetes deployment, autoscaling, and Prometheus metrics.

## Architecture

```
Developer push
     │
     ▼
GitHub Actions ──► Lint (flake8) ──► Test (pytest)
     │
     ▼
Docker build ──► Trivy scan (blocks HIGH/CRITICAL) ──► Push to GHCR
     │
     ▼
Kubernetes: Deployment (2+ pods) ──► Service ──► HPA (2–5 pods)
     │
     ▼
Prometheus scrapes /metrics
```

## Tech stack

| Area | Tools |
|---|---|
| Application | Python, Flask, Gunicorn |
| Containers | Docker (multi-stage build, non-root user) |
| CI/CD | GitHub Actions |
| Security | Trivy image scanning, non-root containers, read-only filesystem |
| Registry | GitHub Container Registry (GHCR) |
| Orchestration | Kubernetes (Deployment, Service, HPA) |
| Observability | Prometheus metrics, health checks |

## Endpoints

| Path | Purpose |
|---|---|
| `/` | Returns a message, app version, and pod name |
| `/health` | Liveness and readiness probe |
| `/metrics` | Prometheus metrics (request count and latency) |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
python -m app.main
# open http://localhost:5000
```

## Run with Docker

```bash
docker build -t flask-devops-pipeline .
docker run -p 5000:5000 flask-devops-pipeline
```

## Deploy to Kubernetes

Works on minikube, kind, EKS, or AKS.

1. Update the image in `k8s/deployment.yaml` to `ghcr.io/<your-username>/<repo-name>:latest`.
2. Apply the manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
kubectl get pods -n devops-demo
kubectl port-forward svc/flask-app 8080:80 -n devops-demo
# open http://localhost:8080
```

The HPA needs metrics-server (`minikube addons enable metrics-server`).

## CI/CD pipeline

On every pull request, the pipeline lints, tests, builds the image, and scans it with Trivy.
On every push to `main`, it also pushes the image to GHCR, tagged with the commit SHA and `latest`.

## Key design decisions

- **Multi-stage Docker build** keeps the runtime image small.
- **Non-root user and read-only root filesystem** reduce the attack surface.
- **Rolling updates with `maxUnavailable: 0`** give zero-downtime deployments.
- **Readiness and liveness probes** ensure traffic only reaches healthy pods.
- **Resource requests and limits** plus an HPA allow scaling on CPU load.
- **Trivy fails the build** on fixable HIGH or CRITICAL vulnerabilities.

## Future improvements

- Terraform to provision an EKS or AKS cluster
- Helm chart and Argo CD for GitOps deployment
- Grafana dashboard for the exported metrics
