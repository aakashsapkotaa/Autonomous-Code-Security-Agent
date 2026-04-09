# AWS Quick Start Guide (5 Minutes)

## Fastest Way: AWS Amplify

### Step 1: Deploy Frontend (3 minutes)

1. **Open AWS Amplify Console**
   - Go to: https://console.aws.amazon.com/amplify/
   - Click "New app" → "Host web app"

2. **Connect GitHub**
   - Select "GitHub"
   - Click "Authorize AWS Amplify"
   - Select your repository: `aakashsapkotaa/Autonomous-Code-Security-Agent`
   - Branch: `main`
   - Click "Next"

3. **Configure App**
   - App name: `secureshift`
   - The build settings will auto-detect from `amplify.yml`
   - Click "Advanced settings"

4. **Add Environment Variables** (Copy-paste these exactly):
   ```
   Key: NEXT_PUBLIC_SUPABASE_URL
   Value: https://ayeoqnvldhrazjpvbrey.supabase.co

   Key: NEXT_PUBLIC_SUPABASE_ANON_KEY
   Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
   ```

5. **Deploy**
   - Click "Next" → "Save and deploy"
   - Wait 5-10 minutes
   - Copy your URL (e.g., `https://main.d123.amplifyapp.com`)

### Step 2: Deploy Backend (2 minutes)

**Option A: Use Existing Backend Locally**
- Keep running backend on your local machine
- Use ngrok to expose it: `ngrok http 8000`
- Add ngrok URL to frontend env vars

**Option B: Deploy to AWS Lambda** (requires AWS CLI setup)
- See full AWS-DEPLOYMENT.md guide

### Step 3: Update Frontend with Backend URL

1. Go to Amplify Console → Your App → Environment variables
2. Add: `NEXT_PUBLIC_API_URL` = `your-backend-url`
3. Click "Redeploy this version"

## Done! 🎉

Your app is now live at your Amplify URL.

## What if Amplify fails?

### Common Issues:

**Build fails with "Module not found"**
- Check that `amplify.yml` has correct paths
- Verify `cd frontend` is in preBuild commands

**Environment variables not working**
- Make sure they start with `NEXT_PUBLIC_`
- Check for typos in variable names

**Build timeout**
- Increase build timeout in Amplify settings
- Or use smaller dependencies

## Alternative: Simple EC2 Deployment

If Amplify doesn't work, use EC2:

1. Launch t2.micro instance (free tier)
2. SSH into it
3. Clone your repo
4. Run setup script (see AWS-DEPLOYMENT.md)
5. Access via EC2 public IP

## Need Help?

Check the full AWS-DEPLOYMENT.md guide for detailed instructions.
