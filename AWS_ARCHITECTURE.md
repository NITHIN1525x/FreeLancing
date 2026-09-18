# AWS architecture

```
                YOUR PROJECT
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
  React Frontend             Django Backend
        │                         │
        ▼                         ▼
   S3 / CloudFront               EC2
   Frontend Hosting          Nginx → Gunicorn → Django REST API
                                  │
                                  ▼
                                RDS
                             PostgreSQL
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
                   VPC                       S3
                Networking              User Files/Media
                     │
              ┌──────┴──────┐
              ▼             ▼
             IAM      Security Groups
         Permissions      Firewall
```

- **S3 frontend hosting** stores the built files in `frontend/dist`. Its website endpoint, or the optional CloudFront distribution URL, is the frontend URL; neither requires a domain.
- **CloudFront** is optional. It caches and serves the S3 frontend from an AWS-generated URL. It does not replace the Django API.
- **EC2** is one Ubuntu virtual server that runs this repository’s Django backend. Its public IP is the initial backend address.
- **Nginx** listens on HTTP port 80, serves static files when configured, and forwards API requests to Gunicorn at `127.0.0.1:8000`.
- **Gunicorn** runs Django’s WSGI app using `gunicorn backend.wsgi:application`; it is not Django’s development server.
- **RDS PostgreSQL** is the managed production database. Unlike SQLite, it is not a file on one server and can be reached securely from EC2.
- **S3 media** stores user uploads. This project currently has `users.User.avatar`; local development still uses `backend/media/`.
- **VPC** is AWS’s private network boundary. EC2 and RDS should be in the same VPC.
- **IAM** grants EC2 permission to upload media to S3. An EC2 IAM role is safer than long-lived access keys in `.env`.
- **Security groups** are virtual firewalls: the EC2 group permits SSH/HTTP, while the RDS group permits PostgreSQL only from the EC2 group.

This learning deployment intentionally uses no Route 53, custom domain, ACM certificate, load balancer, containers, API Gateway, Redis, Celery, or CI/CD.
