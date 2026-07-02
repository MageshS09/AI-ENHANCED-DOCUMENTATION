# Deployment Checklist

Use this checklist to track your progress when deploying to production.

## Prerequisites
- [ ] Have a GitHub account
- [ ] Have an Groq API key (get from https://console.groq.com/keys)
- [ ] Have a Render account (free at https://render.com)
- [ ] Have a Vercel account (free at https://vercel.com)

## Step 1: GitHub Setup
- [ ] Navigated to `ai-doc-generator` directory
- [ ] Ran `git init`
- [ ] Ran `git add .`
- [ ] Ran `git commit -m "Initial AI Documentation Generator MVP"`
- [ ] Ran `git branch -M main`
- [ ] Created new GitHub repository
- [ ] Added remote: `git remote add origin <your-github-url>`
- [ ] Pushed to GitHub: `git push -u origin main`

## Step 2: Render Backend Deployment
- [ ] Logged into https://render.com
- [ ] Connected GitHub account to Render
- [ ] Created new Blueprint or Web Service
- [ ] Selected the `ai-doc-generator` repository
- [ ] Set Root Directory to `backend`
- [ ] Added environment variables:
  - [ ] `GROQ_API_KEY` = your actual key
  - [ ] `GROQ_MODEL` = `llama-3.3-70b-versatile`
  - [ ] `GROQ_BASE_URL=https://api.groq.com/openai/v1
  - [ ] `ALLOWED_ORIGINS` = placeholder (will update after Vercel)
  - [ ] `RATE_LIMIT_REQUESTS` = `5`
  - [ ] `RATE_LIMIT_WINDOW_SECONDS` = `3600`
- [ ] Started deployment
- [ ] **Waited for deployment to complete** (5-10 minutes)
- [ ] **Copied Render URL** (e.g., `https://ai-doc-generator-api.onrender.com`)
- [ ] Tested backend health: `{render-url}/health`

## Step 3: Vercel Frontend Deployment
- [ ] Logged into https://vercel.com
- [ ] Clicked "Add New..." → "Project"
- [ ] Selected "Import an existing project"
- [ ] Found and imported GitHub repository
- [ ] Set Project Name (optional)
- [ ] Set Root Directory to `frontend`
- [ ] Added environment variable:
  - [ ] `NEXT_PUBLIC_API_BASE_URL` = your Render backend URL (from Step 2)
- [ ] Started deployment
- [ ] **Waited for deployment to complete** (2-5 minutes)
- [ ] **Copied Vercel URL** (e.g., `https://ai-doc-generator.vercel.app`)

## Step 4: Final Backend Configuration
- [ ] Went back to Render dashboard
- [ ] Selected `ai-doc-generator-api` service
- [ ] Updated `ALLOWED_ORIGINS` environment variable to your Vercel URL
- [ ] Saved changes
- [ ] **Waited for auto-redeploy** (1-2 minutes)

## Step 5: Testing
- [ ] Visited Vercel URL in browser
- [ ] Entered public GitHub repository URL
- [ ] Clicked "Generate"
- [ ] Verified README was generated successfully
- [ ] Tested with multiple repositories

## Post-Deployment
- [ ] Bookmarked Vercel URL for sharing
- [ ] Shared with team/users
- [ ] Set up usage monitoring for Groq
- [ ] Monitored Render and Vercel logs for errors

## Optional: Custom Domain
- [ ] Purchased/configured custom domain
- [ ] Configured DNS for Vercel
- [ ] Updated `ALLOWED_ORIGINS` in Render if needed
- [ ] Verified custom domain works

## Troubleshooting Done
- [ ] Verified Groq API key is valid
- [ ] Checked backend logs for errors
- [ ] Verified CORS settings are correct
- [ ] Tested backend and frontend separately
- [ ] Reviewed browser console for errors

---

**Status**: Not Started / In Progress / ✅ Complete
