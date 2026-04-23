#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/ubuntu/aguipex-allManagement"
BACKEND_SERVICE="backend.service"
COMMIT_MSG="${1:-Mise a jour automatique}"

cd "$PROJECT_DIR"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Branche courante: $BRANCH"

git add .
if ! git diff --cached --quiet; then
  git commit -m "$COMMIT_MSG"
else
  echo "Aucun changement a commiter."
fi

echo "Push vers origin/$BRANCH..."
git push origin "$BRANCH"

echo "Mise a jour locale depuis origin/$BRANCH..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart "$BACKEND_SERVICE"
sudo systemctl restart nginx

sudo systemctl status "$BACKEND_SERVICE" --no-pager
sudo systemctl status nginx --no-pager

echo "Deploiement termine."
