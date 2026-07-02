# Quick Start: Deploy to Production in 3 Steps

## What You Need (2 minutes)
1. **GitHub Account** - Free at github.com
2. **Groq API key** - Get from https://console.groq.com/keys
3. **Render Account** - Free at render.com
4. **Vercel Account** - Free at vercel.com

## Step 1: Push to GitHub (5 minutes)

```powershell
cd ai-doc-generator
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-generator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and create the repo first at github.com/new

## Step 2: Deploy Backend on Render (10 minutes)

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select your `ai-doc-generator` repository
4. Fill in:
   - **Name**: `ai-doc-generator-api`
   - **Runtime**: `Docker`
   - **Root Directory**: `backend`
5. Click "Create Web Service"
6. Go to **Environment** and add:
   ```
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   GROQ_BASE_URL=https://api.groq.com/openai/v1
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   RATE_LIMIT_REQUESTS=5
   RATE_LIMIT_WINDOW_SECONDS=3600
   ```
7. Wait for deployment (5-10 minutes)
8. Copy your URL (e.g., `https://ai-doc-generator-api.onrender.com`)

## Step 3: Deploy Frontend on Vercel (5 minutes)

1. Go to https://vercel.com
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Set **Root Directory** to `frontend`
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-render-url.onrender.com
   ```
6. Click "Deploy"
7. Wait for deployment (2-5 minutes)
8. Visit your new URL!

## Done! 🎉

Your app is now live at your Vercel URL. Share it with anyone!

### Next Steps
- Update Render's `ALLOWED_ORIGINS` with your final Vercel URL
- Monitor Groq usage at console.groq.com/keys
- Add your own domain (optional)

For detailed troubleshooting, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
