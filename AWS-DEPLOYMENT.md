# SecureShift AWS Deployment Guide

Complete guide to deploy SecureShift on AWS using Amplify (Frontend) and Lambda (Backend).

## Architecture Overview

- **Frontend**: AWS Amplify (Next.js)
- **Backend**: AWS Lambda + API Gateway
- **Database**: Supabase (already set up)
- **Cost**: ~$5-10/month for small-scale production

## Prerequisites

1. AWS Account (free tier eligible)
2. AWS CLI installed
3. GitHub repository with your code
4. Supabase project credentials
5. OpenRouter API key

## Option 1: AWS Amplify (Easiest - Recommended)

### Step 1: Deploy Frontend with AWS Amplify

1. **Go to AWS Amplify Console**
   - Visit: https://console.aws.amazon.com/amplify/
   - Click "Get Started" under "Amplify Hosting"

2. **Connect Repository**
   - Select "GitHub"
   - Authorize AWS Amplify to access your GitHub
   - Select repository: `aakashsapkotaa/Autonomous-Code-Security-Agent`
   - Select branch: `main`
   - Click "Next"

3. **Configure Build Settings**
   - App name: `secureshift`
   - Environment: `production`
   - Build settings will auto-detect Next.js
   
   Edit the build settings to:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```

4. **Add Environment Variables**
   - Click "Advanced settings"
   - Add environment variables:
     ```
     NEXT_PUBLIC_SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
     ```

5. **Deploy**
   - Click "Next" → "Save and deploy"
   - Wait 5-10 minutes for deployment
   - You'll get a URL like: `https://main.d1234567890.amplifyapp.com`

### Step 2: Deploy Backend with AWS Lambda

#### Option A: Using AWS SAM (Recommended)

1. **Install AWS SAM CLI**
   ```bash
   # Windows (using pip)
   pip install aws-sam-cli
   
   # Or download installer from:
   # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Default region: us-east-1
   # Default output format: json
   ```

3. **Deploy Backend**
   ```bash
   cd backend
   sam init --runtime python3.11 --name secureshift-api
   # Copy your app code to the SAM project
   sam build
   sam deploy --guided
   ```

#### Option B: Using Serverless Framework (Alternative)

1. **Install Serverless Framework**
   ```bash
   npm install -g serverless
   ```

2. **Deploy**
   ```bash
   cd backend
   serverless deploy
   ```

### Step 3: Connect Frontend to Backend

1. **Get Backend API URL**
   - From SAM/Serverless output, copy the API Gateway URL
   - Example: `https://abc123.execute-api.us-east-1.amazonaws.com/prod`

2. **Update Amplify Environment Variables**
   - Go to Amplify Console → App Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `your-api-gateway-url`
   - Redeploy: App Settings → Redeploy this version

## Option 2: AWS EC2 (Traditional Hosting)

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**
   - Visit: https://console.aws.amazon.com/ec2/
   - Click "Launch Instance"

2. **Configure Instance**
   - Name: `secureshift-server`
   - AMI: Ubuntu Server 22.04 LTS
   - Instance type: t2.micro (free tier)
   - Key pair: Create new or use existing
   - Security group: Allow HTTP (80), HTTPS (443), SSH (22)
   - Storage: 20 GB
   - Click "Launch Instance"

3. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install PM2 (process manager)
sudo npm install -g pm2
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/aakashsapkotaa/Autonomous-Code-Security-Agent.git
cd Autonomous-Code-Security-Agent

# Setup Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2MzI0MCwiZXhwIjoyMDkxMjM5MjQwfQ.w3RZhHch0qRfsQtEx4mgMuJVeRT69CvPLNeDIWXXPYw
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
EOF

# Start backend with PM2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name secureshift-api
pm2 save
pm2 startup

# Setup Frontend
cd ../frontend
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Build frontend
npm run build

# Start frontend with PM2
pm2 start "npm start" --name secureshift-frontend
pm2 save
```

### Step 4: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/secureshift
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 IP

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/secureshift /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Setup SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Option 3: AWS Elastic Beanstalk

### Deploy Backend

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize and Deploy**
   ```bash
   cd backend
   eb init -p python-3.11 secureshift-api
   eb create secureshift-api-env
   eb setenv SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
   eb deploy
   ```

### Deploy Frontend

Use Amplify (Option 1) for frontend, as it's optimized for Next.js.

## Cost Comparison

### AWS Amplify + Lambda
- Amplify: $0.01/build minute + $0.15/GB served
- Lambda: Free tier 1M requests/month
- **Estimated**: $5-10/month

### EC2 t2.micro
- Instance: Free tier (1 year) then $8.50/month
- Data transfer: $0.09/GB
- **Estimated**: $10-15/month

### Elastic Beanstalk
- Same as EC2 + $0.02/hour for environment
- **Estimated**: $15-20/month

## Recommended: AWS Amplify

**Pros:**
- Easiest to set up
- Auto-scaling
- Built-in CI/CD
- Free SSL
- Global CDN

**Cons:**
- Slightly more expensive at scale

## Post-Deployment Checklist

- [ ] Frontend accessible via Amplify URL
- [ ] Backend API responding
- [ ] Environment variables configured
- [ ] Supabase CORS updated with AWS URLs
- [ ] SSL certificate active
- [ ] Custom domain configured (optional)
- [ ] CloudWatch monitoring enabled
- [ ] Backup strategy in place

## Troubleshooting

### Amplify Build Fails
- Check build logs in Amplify Console
- Verify Node.js version (18.x or 20.x)
- Check environment variables

### Lambda Timeout
- Increase timeout in Lambda configuration (max 15 minutes)
- Optimize cold start with provisioned concurrency

### EC2 Connection Issues
- Check security group rules
- Verify SSH key permissions
- Check instance status

## Support

For AWS-specific issues:
- AWS Support Center
- AWS Documentation
- Stack Overflow with `aws` tag
