# Quantlix — Makefile
.PHONY: build deploy-dev deploy-prod terraform-init terraform-apply

# Docker Compose (local dev)
up:
	docker compose up -d

down:
	docker compose down

seed:
	docker compose exec api python scripts/seed_dev.py

# Build images for K8s (linux/amd64 for cloud nodes, e.g. Hetzner)
build:
	docker build --platform linux/amd64 -t quantlix-api:latest -f api/Dockerfile .
	docker build --platform linux/amd64 -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
	docker build --platform linux/amd64 -t quantlix-inference:latest -f inference/Dockerfile ./inference

build-api:
	docker build --platform linux/amd64 -t quantlix-api:latest -f api/Dockerfile .

# K8s deploy
deploy-dev:
	kubectl apply -k infra/kubernetes/overlays/dev

deploy-prod:
	kubectl apply -k infra/kubernetes/overlays/prod

# Build, push API to Docker Hub, and deploy to prod (imagePullPolicy: Always ensures new image is used)
deploy-prod-api:
	$(MAKE) build-api
	docker tag quantlix-api:latest docker.io/jesperjensen888/quantlix-api:latest
	docker push docker.io/jesperjensen888/quantlix-api:latest
	kubectl apply -k infra/kubernetes/overlays/prod
	kubectl rollout restart deploy/api -n quantlix
	kubectl rollout status deploy/api -n quantlix --timeout=120s

# Sync api secret from .env (JWT_SECRET, SMTP_USER, SMTP_PASSWORD)
sync-api-secret:
	python infra/kubernetes/scripts/sync-api-secret-from-env.py

# Terraform
terraform-init:
	cd infra/terraform && terraform init

terraform-plan:
	cd infra/terraform && terraform plan

terraform-apply:
	cd infra/terraform && terraform apply

# k3d local cluster
k3d-create:
	k3d cluster create quantlix --port 6443:6443

k3d-delete:
	k3d cluster delete quantlix

k3d-import: build
	k3d image import quantlix-api:latest quantlix-orchestrator:latest quantlix-inference:latest -c quantlix
