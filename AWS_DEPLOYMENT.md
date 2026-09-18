# Deploy this marketplace to AWS (no custom domain)

This guide deploys the React/Vite frontend from `frontend/` to S3 (optionally CloudFront) and the Django API from `backend/` to one Ubuntu EC2 instance. The backend uses RDS PostgreSQL. No domain, Route 53, ACM, load balancer, Docker, ECS, or Kubernetes is required.

## 1. AWS Console: account, IAM, networking, and EC2

1. Secure your AWS account with MFA. Create an IAM user for console use with only the permissions you need, rather than using the root account daily.
2. In **EC2**, create an Ubuntu LTS instance in the default VPC. Choose a small learning-appropriate instance and create/download a key pair (`.pem`).
3. Create an EC2 security group: allow inbound TCP **22** only from your current public IP for SSH, and TCP **80** from `0.0.0.0/0` for HTTP. Do not open port 8000 publicly; Nginx talks to Gunicorn locally. Add 443 only later when HTTPS is actually configured.
4. Note the instance **public IPv4 address**. It may change after stop/start unless you use an Elastic IP.

From your computer, connect with:

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP
```

## 2. Set up Django on EC2

On the EC2 instance:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip nginx
# Install the PostgreSQL client headers needed if a wheel is unavailable.
sudo apt install -y libpq-dev

git clone YOUR_REPOSITORY_URL marketplace
cd marketplace/blockchain_deploy/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Edit `backend/.env` with `nano .env`. Set `DEBUG=False`, paste the generated `DJANGO_SECRET_KEY`, and replace `EC2_PUBLIC_IP`, the RDS values, and the eventual frontend URL. Example values are placeholders only:

```dotenv
DEBUG=False
DJANGO_SECRET_KEY=GENERATED_SECRET
ALLOWED_HOSTS=EC2_PUBLIC_IP,localhost,127.0.0.1
USE_POSTGRES=True
DB_NAME=marketplace
DB_USER=marketplace_user
DB_PASSWORD=RDS_PASSWORD
DB_HOST=RDS_ENDPOINT
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://YOUR_CLOUDFRONT_URL
CSRF_TRUSTED_ORIGINS=http://EC2_PUBLIC_IP,https://YOUR_CLOUDFRONT_URL
USE_S3_MEDIA=True
AWS_STORAGE_BUCKET_NAME=YOUR_MEDIA_BUCKET
AWS_S3_REGION_NAME=YOUR_REGION
```

## 3. Create RDS PostgreSQL

In **RDS**, create a PostgreSQL database in the same VPC. For learning, choose an appropriately small configuration and record its endpoint, database name, master username, and password. Create an RDS security group that permits inbound TCP **5432** with the **EC2 security group as source**. Never allow `0.0.0.0/0` on port 5432: that would expose the database to the internet.

After updating `.env`, run:

```bash
cd ~/marketplace/blockchain_deploy/backend
source .venv/bin/activate
python manage.py migrate
# Optional demo data; never run automatically in production:
python seed.py
python manage.py collectstatic --no-input
python manage.py check --deploy
```

`seed.py` uses Django ORM APIs and is database-independent; it can populate PostgreSQL after migrations. It contains test credentials, so use it only for a demo environment.

## 4. Run Gunicorn with systemd

Test first:

```bash
gunicorn --bind 127.0.0.1:8000 backend.wsgi:application
curl http://127.0.0.1:8000/api/
```

Stop it with Ctrl+C, then create `/etc/systemd/system/marketplace.service`:

```ini
[Unit]
Description=Marketplace Django Gunicorn
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/marketplace/blockchain_deploy/backend
EnvironmentFile=/home/ubuntu/marketplace/blockchain_deploy/backend/.env
ExecStart=/home/ubuntu/marketplace/blockchain_deploy/backend/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now marketplace
sudo systemctl status marketplace
sudo journalctl -u marketplace -f
```

## 5. Configure Nginx

Create `/etc/nginx/sites-available/marketplace`:

```nginx
server {
    listen 80;
    server_name EC2_PUBLIC_IP;

    location /static/ {
        alias /home/ubuntu/marketplace/blockchain_deploy/backend/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/marketplace/blockchain_deploy/backend/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

When `USE_S3_MEDIA=True`, media URLs are S3 URLs and the `/media/` block is unused; retaining it supports local-media deployments. Enable Nginx and test:

```bash
sudo ln -s /etc/nginx/sites-available/marketplace /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
curl http://EC2_PUBLIC_IP/api/
```

Nginx owns port 80. Gunicorn stays private on localhost:8000, and Django can still run locally using `python manage.py runserver`.

## 6. S3: frontend and media are different

Create an S3 bucket for the React frontend. Build with the real EC2 address **before** uploading because Vite embeds `VITE_API_URL` into the bundle:

```bash
cd ~/marketplace/blockchain_deploy/frontend
npm install
VITE_API_URL=http://EC2_PUBLIC_IP/api npm run build
aws s3 sync dist/ s3://YOUR_FRONTEND_BUCKET/ --delete
```

Configure S3 static website hosting (index document `index.html`, error document `index.html`) and the required public-read bucket policy for a learning-only public website, or preferably place CloudFront in front of the bucket using its AWS-generated distribution URL. No custom domain is needed.

Create a separate S3 bucket for Django media. Attach an IAM role to EC2 with least-privilege `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` for that media bucket. This is preferred over populating `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`; boto3 automatically obtains role credentials. Set `USE_S3_MEDIA=True`, `AWS_STORAGE_BUCKET_NAME`, and `AWS_S3_REGION_NAME` in `.env`, then restart Gunicorn:

```bash
sudo systemctl restart marketplace
```

## 7. Configure CORS and test end to end

Copy the S3 website URL or CloudFront distribution URL exactly into `CORS_ALLOWED_ORIGINS` (and, where browser CSRF requests apply, `CSRF_TRUSTED_ORIGINS`) in EC2 `.env`. Restart Gunicorn. Open the frontend URL, register/login, and test API calls and an avatar upload. Do not use `*` for CORS in production.

The deployment order is: **EC2 → SSH → RDS → `.env` PostgreSQL → migrate → Gunicorn → Nginx → build React → S3 → optional CloudFront → CORS → end-to-end test**.

## HTTP now, HTTPS later

This initial public-IP setup intentionally leaves `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` false so HTTP works. If you later introduce a valid HTTPS endpoint, set all three true and configure Nginx/proxy headers correctly. A public IP alone does not provide a practical trusted certificate path; this guide does not configure ACM or a custom domain.

## Cost cleanup: shut down after testing

- **EC2:** stopping stops compute charges but EBS volumes can continue charging. Terminate the instance and delete unneeded EBS snapshots/volumes when finished.
- **RDS:** stop is temporary and storage/backups still cost money. Delete the DB instance when done and choose whether to keep/delete the final snapshot; delete retained snapshots you no longer need.
- **S3:** delete objects and buckets you no longer need; storage and requests can incur charges.
- **CloudFront:** disable/delete the distribution after it is no longer needed.
- **Elastic IP:** release it if it is no longer attached to a running instance; unattached addresses cost money.
- **NAT Gateway:** do not create one for this simple public-EC2 learning setup unless you understand the need; it has ongoing charges. Delete it if accidentally created.
- Check **Billing and Cost Management** (and optionally create a budget alert) before and after testing.
