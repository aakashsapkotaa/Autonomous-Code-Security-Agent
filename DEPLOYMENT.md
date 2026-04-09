# SecureShift Deployment Guide - Vercel

This guide will help you deploy SecureShift to Vercel in production.

## Prerequisites

1. GitHub account with your code pushed
2. Vercel account (free tier works)
3. Supabase project (already set up)
4. OpenRouter API key

## Deployment Steps

### Step 1: Prepare Your Repository

Your code is already pushed to GitHub. Make sure you have:
- ✅ Frontend in `/frontend` directory
- ✅ Backend in `/backend` directory
- ✅ Environment variables documented in `.env.example`

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New" → "Project"

2. **Import Your Repository**
   - Select "Import Git Repository"
   - Choose your GitHub repository: `aakashsapkotaa/Autonomous-Code-Security-Agent`
   - Click "Import"

3. **Configure Frontend Project**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

4. **Add Environment Variables**
   Click "Environment Variables" and add:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - You'll get a URL like: `https://your-app.vercel.app`

### Step 3: Deploy Backend to Vercel

1. **Create New Project**
   - Go back to Vercel Dashboard
   - Click "Add New" → "Project"
   - Import the same repository again

2. **Configure Backend Project**
   - **Framework Preset**: Other
   - **Root Directory**: `backend`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements-vercel.txt`

3. **Add Environment Variables**
   Click "Environment Variables" and add:
   ```
   SUPABASE_URL=https://ayeoqnvldhrazjpvbrey.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2MzI0MCwiZXhwIjoyMDkxMjM5MjQwfQ.w3RZhHch0qRfsQtEx4mgMuJVeRT69CvPLNeDIWXXPYw
   OPENROUTER_API_KEY=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
   OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
   ```

4. **Deploy**
   - Click "Deploy"
   - You'll get a backend URL like: `https://your-backend.vercel.app`

### Step 4: Update Frontend to Use Backend URL

1. **Add Backend URL to Frontend Environment**
   - Go to your frontend project in Vercel
   - Settings → Environment Variables
   - Add new variable:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
     ```

2. **Update Frontend Code**
   - Update `frontend/src/components/HelpBot.tsx`
   - Change `http://localhost:8000` to use `process.env.NEXT_PUBLIC_API_URL`

3. **Redeploy Frontend**
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

### Step 5: Configure Supabase for Production

1. **Update CORS in Supabase**
   - Go to Supabase Dashboard → Settings → API
   - Add your Vercel URLs to allowed origins:
     - `https://your-app.vercel.app`
     - `https://your-backend.vercel.app`

2. **Disable Email Confirmation (Optional for Development)**
   - Supabase Dashboard → Authentication → Providers → Email
   - Uncheck "Enable email confirmations"

### Step 6: Test Your Deployment

1. Visit your frontend URL: `https://your-app.vercel.app`
2. Test sign up/sign in
3. Test adding a repository
4. Test the help bot

## Alternative: Single Vercel Project (Monorepo)

If you want both frontend and backend in one Vercel project:

1. Use the root `vercel.json` configuration
2. Deploy from repository root
3. Vercel will automatically detect Next.js and Python
4. Add all environment variables to the single project

## Troubleshooting

### Frontend Issues
- **Build fails**: Check Node.js version (use 18.x or 20.x)
- **Environment variables not working**: Make sure they start with `NEXT_PUBLIC_`
- **404 errors**: Check that root directory is set to `frontend`

### Backend Issues
- **Import errors**: Make sure `requirements-vercel.txt` has all dependencies
- **CORS errors**: Add frontend URL to Supabase allowed origins
- **Timeout errors**: Vercel serverless functions have 10s timeout on free tier

### Database Issues
- **Connection fails**: Verify Supabase URL and keys are correct
- **RLS errors**: Make sure RLS policies are properly configured
- **Auth errors**: Check that JWT secret matches between Supabase and backend

## Production Checklist

- [ ] Frontend deployed and accessible
- [ ] Backend deployed and accessible
- [ ] Environment variables configured
- [ ] Supabase CORS configured
- [ ] Authentication working
- [ ] Help bot responding
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active (automatic with Vercel)

## Cost Estimate

- **Vercel**: Free tier (100GB bandwidth, unlimited requests)
- **Supabase**: Free tier (500MB database, 2GB bandwidth)
- **OpenRouter**: Free tier with rate limits

Total: **$0/month** for development and small-scale production

## Next Steps

After deployment:
1. Set up custom domain in Vercel
2. Configure monitoring and analytics
3. Set up error tracking (Sentry)
4. Enable Vercel Analytics
5. Configure CI/CD for automatic deployments

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for errors
3. Verify all environment variables are set
4. Test API endpoints directly
