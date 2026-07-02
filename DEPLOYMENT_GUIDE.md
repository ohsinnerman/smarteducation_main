# DEPLOYMENT GUIDE

From-zero deployment: Django backend on a single EC2 instance (docker-compose,
nginx + gunicorn, TLS via certbot) with Postgres on RDS, and the React frontend
on Vercel. The AWS CLI blocks below are runnable from your own machine — **they
were not executed in this environment**, so read them before pasting and swap in
your real region/domain/IDs where noted.

> Chosen defaults (each swappable): Ubuntu 24.04 LTS AMI, `t3.small`, Postgres on
> RDS `db.t3.micro`. RDS is the default because it decouples DB lifecycle from the
> box; to run Postgres in a container instead, just point `DATABASE_URL` at the
> compose `db` service and skip the RDS section.

## 0. Prerequisites

- AWS CLI v2 configured (`aws configure`) with an IAM user that can create EC2,
  RDS, security groups, and SSM parameters.
- A domain you control (for TLS). Set once:

```bash
export AWS_REGION=us-east-1
export KEY_NAME=smartedu-key
export MY_IP=$(curl -s https://checkip.amazonaws.com)/32
export DOMAIN=api.example.com   # your backend domain
```

## 1. Networking + key pair

```bash
# SSH key pair (saves smartedu-key.pem locally)
aws ec2 create-key-pair --key-name "$KEY_NAME" --region "$AWS_REGION" \
  --query 'KeyMaterial' --output text > "$KEY_NAME.pem" && chmod 400 "$KEY_NAME.pem"

# Security group: SSH from your IP only; HTTP/HTTPS from anywhere. Nothing else.
SG_ID=$(aws ec2 create-security-group --group-name smartedu-sg \
  --description "Smart Education backend" --region "$AWS_REGION" \
  --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22  --cidr "$MY_IP" --region "$AWS_REGION"
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80  --cidr 0.0.0.0/0 --region "$AWS_REGION"
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0 --region "$AWS_REGION"
# NOTE: gunicorn's raw port (8000) is intentionally NOT exposed — nginx fronts it.
```

## 2. RDS Postgres (default DB)

```bash
aws rds create-db-instance \
  --db-instance-identifier smartedu-db \
  --db-instance-class db.t3.micro \
  --engine postgres --allocated-storage 20 \
  --master-username smartedu --master-user-password 'CHANGE_ME_STRONG' \
  --db-name smarteducation --vpc-security-group-ids "$SG_ID" \
  --region "$AWS_REGION"
# When status is 'available', grab the endpoint:
aws rds describe-db-instances --db-instance-identifier smartedu-db \
  --region "$AWS_REGION" --query 'DBInstances[0].Endpoint.Address' --output text
# Add a 5432 ingress rule on $SG_ID from the instance's SG/subnet for the app to connect.
```

Your `DATABASE_URL` becomes:
`postgres://smartedu:CHANGE_ME_STRONG@<rds-endpoint>:5432/smarteducation`

## 3. Store secrets in SSM (don't put `.env` in git)

```bash
aws ssm put-parameter --name /smartedu/env --type SecureString --region "$AWS_REGION" \
  --value "$(cat <<EOF
DJANGO_ENV=production
DJANGO_SECRET_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(50))')
DJANGO_ALLOWED_HOSTS=$DOMAIN
DATABASE_URL=postgres://smartedu:CHANGE_ME_STRONG@<rds-endpoint>:5432/smarteducation
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
REDIS_URL=redis://redis:6379/0
EOF
)"
```

## 4. Launch the instance

Give it an IAM role that can read that one SSM parameter (least privilege — no
long-lived keys on the box):

```bash
# (Create role smartedu-ec2-role with ssm:GetParameter on /smartedu/* + an
# instance profile of the same name, then:)
aws ec2 run-instances \
  --image-id resolve:ssm:/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --instance-type t3.small --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --iam-instance-profile Name=smartedu-ec2-role \
  --region "$AWS_REGION" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=smartedu-backend}]'
# Optionally allocate + associate an Elastic IP so the frontend has a stable target.
```

## 5. Provision the box (SSH in)

```bash
ssh -i "$KEY_NAME.pem" ubuntu@<public-ip>

sudo apt update && sudo apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx git
sudo usermod -aG docker ubuntu && newgrp docker
git clone <your-repo-url> app && cd app/backend

# Pull the .env from SSM onto the box (never committed):
aws ssm get-parameter --name /smartedu/env --with-decryption \
  --query 'Parameter.Value' --output text --region us-east-1 > .env

docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo_data
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py diagnose_env   # gate: fails if prod config missing
```

## 6. nginx + TLS

Point `$DOMAIN`'s DNS A record at the instance IP, then:

```bash
sudo tee /etc/nginx/sites-available/smartedu >/dev/null <<'NGINX'
server {
    server_name api.example.com;
    location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host;
                 proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                 proxy_set_header X-Forwarded-Proto $scheme; }
}
NGINX
sudo ln -s /etc/nginx/sites-available/smartedu /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.example.com   # issues + auto-renews the cert
```

(compose maps gunicorn to `127.0.0.1:8000`; only nginx faces the internet.)

## 7. Frontend on Vercel

1. Import the repo in Vercel; set **Root Directory** to `frontend`.
2. Add env var `VITE_API_BASE_URL=https://api.example.com/api`.
3. Deploy. Vercel runs `npm run build`; the app needs no other config.
4. Copy the deployed origin (e.g. `https://your-frontend.vercel.app`) into the
   backend's `CORS_ALLOWED_ORIGINS` (update the SSM param + `.env`, restart web).
   Never use `*`.

## 8. Updating

```bash
cd app && git pull && cd backend
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

## 9. CI note

`.github/workflows/deploy.yml` still contains the original ECS/ECR path. This
guide uses direct EC2 + docker-compose, so that deploy job should be replaced with
an SSH-and-`git pull` step (or dropped) — the `test` job (now fixed to run from
the repo root and to call `diagnose_env`) is worth keeping.

## Troubleshooting: "works locally, not on EC2"

This is almost always config not reaching the process. **First command to run:**

```bash
docker compose exec web python manage.py diagnose_env
```

It prints the resolved environment, DB engine/host, and which integrations are
on/off, and exits non-zero if a required production var is missing. If it shows
SQLite in production, `DATABASE_URL` didn't reach the container — check the `.env`
pulled from SSM and that compose passed it through. If email/Twilio/OpenAI show
`[OFF]`, those keys aren't set (loud warning, not a crash — by design).
