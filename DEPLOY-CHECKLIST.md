# Quick Deployment Checklist for Vercel

## 🚀 Quick Start (5 minutes)

### Option 1: Separate Projects (Recommended)

#### Deploy Frontend
1. Go to https://vercel.com/new
2. Import: `aakashsapkotaa/Autonomous-Code-Security-Agent`
3. Root Directory: `frontend`
4. Add Environment Variables:
   - `NEXT_PUBLIC_SUPABASE_URL` = `https://ayeoqnvldhrazjpvbrey.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4`
5. Click Deploy
6. Copy your frontend URL (e.g., `https://secureshift.vercel.app`)

#### Deploy Backend
1. Go to https://vercel.com/new again
2. Import same repository
3. Root Directory: `backend`
4. Add Environment Variables:
   - `SUPABASE_URL` = `https://ayeoqnvldhrazjpvbrey.supabase.co`
   - `SUPABASE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NjMyNDAsImV4cCI6MjA5MTIzOTI0MH0.XgtMKnAXyeMPC3AET5MBp7L1Kh-02YExSLpN_KebGt4`
   - `SUPABASE_SERVICE_ROLE_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2MzI0MCwiZXhwIjoyMDkxMjM5MjQwfQ.w3RZhHch0qRfsQtEx4mgMuJVeRT69CvPLNeDIWXXPYw`
   - `OPENROUTER_API_KEY` = `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`
   - `OPENROUTER_MODEL` = `nvidia/nemotron-3-super-120b-a12b:free`
5. Click Deploy
6. Copy your backend URL (e.g., `https://secureshift-api.vercel.app`)

#### Connect Frontend to Backend
1. Go to frontend project → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.vercel.app`
3. Go to Deployments → Click "..." → Redeploy

### Option 2: Single Monorepo Project

1. Deploy from repository root
2. Vercel will auto-detect both Next.js and Python
3. Add all environment variables from both frontend and backend
4. Deploy

## ✅ Post-Deployment

1. **Update Supabase CORS**
   - Supabase Dashboard → Settings → API
   - Add your Vercel URLs to allowed origins

2. **Test Everything**
   - [ ] Frontend loads
   - [ ] Sign up works
   - [ ] Sign in works
   - [ ] Dashboard accessible
   - [ ] Help bot responds
   - [ ] Can add repositories

3. **Optional: Custom Domain**
   - Vercel Dashboard → Settings → Domains
   - Add your custom domain

## 🐛 Common Issues

**Build Fails**
- Check Node.js version (18.x or 20.x)
- Verify all dependencies in package.json

**CORS Errors**
- Add Vercel URLs to Supabase allowed origins
- Check environment variables are set

**API Not Working**
- Verify `NEXT_PUBLIC_API_URL` is set in frontend
- Check backend logs in Vercel

**Authentication Fails**
- Verify Supabase keys are correct
- Check RLS policies in Supabase

## 📊 Monitoring

After deployment, monitor:
- Vercel Analytics (automatic)
- Vercel Logs (for errors)
- Supabase Dashboard (for database usage)

## 💰 Cost

- Vercel Free Tier: 100GB bandwidth
- Supabase Free Tier: 500MB database
- OpenRouter Free Tier: Rate limited

**Total: $0/month** for small-scale production
