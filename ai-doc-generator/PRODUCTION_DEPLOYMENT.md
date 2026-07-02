# Production Deployment Guide

This guide will help you deploy your AI Documentation Generator as a fully working web app.

## Overview

- **Backend**: FastAPI running on Render
- **Frontend**: Next.js running on Vercel
- **Total Time**: ~15-20 minutes

## Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Groq API key** - Get from https://console.groq.com/keys
3. **Render Account** - Free at https://render.com
4. **Vercel Account** - Free at https://vercel.com

## Step 1: Prepare Your GitHub Repository

```bash
# Navigate to your project root
cd ai-doc-generator

# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial AI Documentation Generator MVP"

# Rename branch to main (if needed)
git branch -M main

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-generator.git

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy Backend on Render

### 2.1: Create Render Account and Connect GitHub
1. Go to https://render.com
2. Sign up and connect your GitHub account
3. Authorize Render to access your repositories

### 2.2: Create Blueprint or Web Service

**Option A: Using Blueprint (Recommended)**
1. In Render dashboard, click "New +" → "Blueprint"
2. Select your GitHub repository
3. Render will auto-detect `render.yaml` and configure the service
4. Click "Deploy"

**Option B: Manual Web Service**
1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Fill in:
   - **Name**: `ai-doc-generator-api`
   - **Runtime**: `Docker`
   - **Root Directory**: `backend`
   - **Branch**: `main`
   - **Build Command**: (leave empty, Dockerfile will handle it)
   - **Start Command**: (leave empty, Dockerfile will handle it)
4. Click "Create Web Service"

### 2.3: Add Environment Variables
In Render dashboard for your service, go to **Environment**:

```
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
ALLOWED_ORIGINS=https://your-app.vercel.app
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
LOG_LEVEL=INFO
```

**Important**: Replace `your_actual_groq_api_key_here` with your real Groq API key.

### 2.4: Wait for Backend Deployment
- Render will build and deploy automatically
- This takes 5-10 minutes
- Once deployed, you'll get a URL like: `https://ai-doc-generator-api.onrender.com`
- **Save this URL** - you'll need it for the frontend

### 2.5: Verify Backend is Live
```
https://your-render-url.onrender.com/health
```
Should return: `{"status":"ok"}`

## Step 3: Deploy Frontend on Vercel

### 3.1: Import Project into Vercel
1. Go to https://vercel.com and sign in
2. Click "Add New..." → "Project"
3. Select "Import an existing project"
4. Search for your GitHub repository and click "Import"

### 3.2: Configure Project Settings
1. **Project Name**: `ai-doc-generator` (or your choice)
2. **Framework**: Next.js (should auto-detect)
3. **Root Directory**: `frontend`
4. Expand "Root Directory" and confirm it's set to `frontend`

### 3.3: Add Environment Variables
Click "Environment Variables" and add:

```
NEXT_PUBLIC_API_BASE_URL=https://your-render-url.onrender.com
```

**Replace** `https://your-render-url.onrender.com` with your actual Render backend URL.

### 3.4: Deploy
- Click "Deploy"
- Vercel will build and deploy (takes 2-5 minutes)
- Once complete, you'll get a URL like: `https://ai-doc-generator.vercel.app`
- **Save this URL** - this is your public web app

## Step 4: Update Backend CORS (Final Step)

Now that you have your Vercel frontend URL, update your backend:

1. Go back to your Render dashboard
2. Select your `ai-doc-generator-api` service
3. Go to **Environment**
4. Update `ALLOWED_ORIGINS` to your Vercel URL:
   ```
   ALLOWED_ORIGINS=https://ai-doc-generator.vercel.app
   ```
5. Click "Save"
6. Render will auto-redeploy (takes 1-2 minutes)

## Step 5: Test Your Live App

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Enter a public GitHub repository URL (e.g., `https://github.com/openai/gpt-engineer`)
3. Click "Generate"
4. Your README should be generated in ~30-60 seconds

## Troubleshooting

### Backend won't deploy
- Check Render logs for errors
- Ensure `GROQ_API_KEY` is set correctly
- Verify Docker builds locally: `docker build -t test backend/`

### Frontend shows API errors
- Ensure `NEXT_PUBLIC_API_BASE_URL` is set in Vercel
- Verify the backend health endpoint works
- Check browser console for CORS errors
- Redeploy frontend after updating backend CORS

### Generation fails
- Verify `GROQ_API_KEY` is valid and has credits
- Check rate limits aren't exceeded
- View Render logs for detailed errors

### CORS errors
- Ensure `ALLOWED_ORIGINS` in backend matches your Vercel URL exactly
- Frontend URL must include the protocol (`https://`)
- Wait 1-2 minutes after updating for changes to take effect

## Production Considerations

### Rate Limiting
Currently using in-memory rate limiting (5 requests per hour). For production with heavy traffic:

1. Set up Redis on Render
2. Update `backend/utils/rate_limit.py` to use Redis
3. Redeploy backend

### Monitoring
- Check Render logs regularly
- Set up Groq usage alerts at https://console.groq.com/keys
- Monitor Vercel performance at https://vercel.com/analytics

### Cost Management
- Set Groq usage limits
- Monitor token usage for each generation
- Consider implementing authentication for heavy users

### Security
- Keep `GROQ_API_KEY` secret (only in backend)
- Use Vercel environment variables for sensitive frontend data
- Never commit `.env` files to GitHub

## Custom Domain (Optional)

### Point to Vercel
1. In Vercel dashboard, go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed by Vercel

### Point to Render
1. In Render dashboard, go to **Settings** → **Custom Domains**
2. Add your domain
3. Update DNS records

## Next Steps

- Monitor your deployment for errors
- Gather user feedback
- Consider adding authentication for public access
- Optimize prompts based on generated READMEs
- Add feature improvements based on usage

---

**Your app is now live! 🎉**

Share your Vercel URL with anyone to let them generate READMEs for public GitHub repositories.
