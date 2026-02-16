# Quantlix — Makefile
.PHONY: build deploy-dev deploy-prod terraform-init terraform-apply

# Docker Compose (local dev)
up:
	docker compose up -d

down:
	docker compose down

seed:
	docker compose exec api python scripts/seed_dev.py

# Build images for K8s
build:
	docker build -t quantlix-api:latest -f api/Dockerfile .
	docker build -t quantlix-orchestrator:latest -f orchestrator/Dockerfile .
	docker build -t quantlix-inference:latest -f inference/Dockerfile ./inference

# K8s deploy
deploy-dev:
	kubectl apply -k infra/kubernetes/overlays/dev

deploy-prod:
	kubectl apply -k infra/kubernetes/overlays/prod

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
