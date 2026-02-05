# 🚀 AWS Deployment Guide

This guide walks you through deploying the Employee Management System to AWS using ECS Fargate and RDS MySQL.

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Docker** installed locally
4. **GitHub repository** (for CI/CD)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                        VPC                            │   │
│  │  ┌─────────────────┐    ┌─────────────────┐          │   │
│  │  │  Public Subnet  │    │  Public Subnet  │          │   │
│  │  │  ┌───────────┐  │    │                 │          │   │
│  │  │  │    ALB    │◄─┼────┼── Internet      │          │   │
│  │  │  └─────┬─────┘  │    │                 │          │   │
│  │  └────────┼────────┘    └─────────────────┘          │   │
│  │           │                                           │   │
│  │  ┌────────▼────────┐    ┌─────────────────┐          │   │
│  │  │ Private Subnet  │    │ Private Subnet  │          │   │
│  │  │  ┌───────────┐  │    │  ┌───────────┐  │          │   │
│  │  │  │ECS Fargate│  │    │  │  RDS MySQL │  │          │   │
│  │  │  │  (API)    │──┼────┼─►│ (Database) │  │          │   │
│  │  │  └───────────┘  │    │  └───────────┘  │          │   │
│  │  └─────────────────┘    └─────────────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Deployment Options

### Option 1: Quick Deploy with CloudFormation (Recommended)

#### Step 1: Deploy Infrastructure

```bash
# Navigate to project directory
cd employee_management_system

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name employee-management-system \
  --template-body file://.aws/cloudformation-template.yml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=production \
    ParameterKey=DBUsername,ParameterValue=admin \
    ParameterKey=DBPassword,ParameterValue=YourSecurePassword123! \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for stack creation (takes ~15-20 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name employee-management-system \
  --region us-east-1
```

#### Step 2: Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name employee-management-system \
  --query 'Stacks[0].Outputs' \
  --output table
```

#### Step 3: Push Docker Image to ECR

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t employee-management-api .
docker tag employee-management-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/employee-management-api:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/employee-management-api:latest
```

#### Step 4: Create ECS Service

```bash
# Update task definition with correct values, then register it
aws ecs register-task-definition --cli-input-json file://.aws/task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster employee-management-cluster \
  --service-name employee-management-service \
  --task-definition employee-management-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=employee-management-api,containerPort=8000"
```

---

### Option 2: CI/CD with GitHub Actions (Automated)

#### Step 1: Set Up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

#### Step 2: Push to GitHub

```bash
git add .
git commit -m "Add AWS deployment configuration"
git push origin main
```

The GitHub Action will automatically:
1. Build the Docker image
2. Push to ECR
3. Update ECS task definition
4. Deploy to ECS

---

## 📊 Estimated Costs (Monthly)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| ECS Fargate | 0.25 vCPU, 0.5 GB | ~$9/month |
| RDS MySQL | db.t3.micro | ~$15/month |
| ALB | Basic usage | ~$18/month |
| ECR | 1 GB storage | ~$0.10/month |
| Data Transfer | 10 GB | ~$1/month |
| **Total** | | **~$43/month** |

> 💡 **Cost Saving Tips:**
> - Use RDS Free Tier (750 hours/month for 12 months)
> - Use Fargate Spot for non-production
> - Stop resources when not in use

---

## 🔧 Environment Variables

Make sure to update these in your ECS task definition or Secrets Manager:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | RDS endpoint | `xxx.rds.amazonaws.com` |
| `DB_PORT` | Database port | `3306` |
| `DB_USER` | Database username | `admin` |
| `DB_PASSWORD` | Database password | `(use Secrets Manager)` |
| `DB_NAME` | Database name | `employee_db` |

---

## 🔒 Security Best Practices

1. **Use Secrets Manager** for database credentials
2. **Enable RDS encryption** at rest
3. **Use private subnets** for ECS and RDS
4. **Enable WAF** on ALB for production
5. **Enable CloudTrail** for auditing
6. **Use HTTPS** with ACM certificates

---

## 📝 Cleanup

To avoid charges, delete the stack when done:

```bash
# Delete ECS service first
aws ecs update-service --cluster employee-management-cluster --service employee-management-service --desired-count 0
aws ecs delete-service --cluster employee-management-cluster --service employee-management-service

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name employee-management-system

# Delete ECR images (optional)
aws ecr batch-delete-image --repository-name employee-management-api --image-ids imageTag=latest
```

---

## 🆘 Troubleshooting

### Container won't start
- Check CloudWatch logs: `/ecs/employee-management`
- Verify environment variables
- Check security group allows traffic

### Database connection fails
- Verify RDS security group allows ECS security group
- Check DB_HOST is the RDS endpoint (not localhost)
- Verify credentials in Secrets Manager

### Health check fails
- Ensure `/health` endpoint returns 200
- Check target group health check settings
- Verify container port is 8000
