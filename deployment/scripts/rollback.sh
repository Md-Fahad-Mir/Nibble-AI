#!/bin/bash
# ─── rollback.sh ──────────────────────────────────────────────────────
# Roll Nibbl AI production back to a previous image tag (git SHA) in ECR.
# Usage:  REGISTRY=<acct>.dkr.ecr.us-west-1.amazonaws.com \
#         EC2_HOST=<ec2-public-ip> ./rollback.sh <git-sha>
set -euo pipefail

ROLLBACK_TAG="${1:?Usage: ./rollback.sh <git-sha-or-tag>}"
PROJECT_NAME="${PROJECT_NAME:-nibblai}"
REGISTRY="${REGISTRY:?REGISTRY env var required (your ECR registry URL)}"
EC2_HOST="${EC2_HOST:?EC2_HOST env var required}"
AWS_REGION="${AWS_REGION:-us-west-1}"

echo "▶ Rolling back Nibbl AI to image tag: $ROLLBACK_TAG"

ssh -i ~/.ssh/id_rsa "ubuntu@$EC2_HOST" << EOF
  set -euo pipefail
  cd /home/ubuntu/$PROJECT_NAME
  export PATH=\$PATH:/usr/local/bin
  export REGISTRY='$REGISTRY'
  export IMAGE_TAG='$ROLLBACK_TAG'

  # Authenticate to ECR via the instance profile, then redeploy the tag.
  aws ecr get-login-password --region $AWS_REGION \
    | docker login --username AWS --password-stdin "$REGISTRY"

  COMPOSE="docker compose \
    -f deployment/compose/docker-compose.base.yml \
    -f deployment/compose/production/docker-compose.yml"

  \$COMPOSE pull
  \$COMPOSE up -d --force-recreate --remove-orphans

  echo "Nibbl AI rollback to $ROLLBACK_TAG complete."
  \$COMPOSE ps
EOF
