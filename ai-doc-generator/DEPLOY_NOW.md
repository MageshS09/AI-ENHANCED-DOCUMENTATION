# 🚀 Deploying Your AI Documentation Generator

Your app is ready for production! This guide will help you deploy it as a fully working web app.

## What You'll Get

✅ **Live web app** accessible via public URL  
✅ **Production-grade backend** running on cloud servers  
✅ **Static frontend** served globally  
✅ **Automatic HTTPS/SSL** certificates  
✅ **Scalable infrastructure** that handles multiple users  

## The Big Picture

```
You (localhost)
    ↓
GitHub (code repository)
    ↓
Render (backend API)  ←→  Vercel (frontend)
    ↓                           ↓
Users anywhere → https://your-app.vercel.app
```

## What's Different from Localhost?

| Aspect | Localhost | Production |
|--------|-----------|-----------|
| **URL** | `http://localhost:3000` | `https://your-app.vercel.app` |
| **Backend** | Your computer | Render cloud servers |
| **Frontend** | Your computer | Vercel CDN (global) |
| **Access** | Only you | Anyone on the internet |
| **Uptime** | Only when running | 24/7/365 |
| **Database** | Memory | Persistent |

## Quick Timeline

- **Total Time**: 20-30 minutes of active work
- **GitHub Setup**: 5 minutes
- **Backend Deploy**: 10-15 minutes (mostly waiting)
- **Frontend Deploy**: 5-10 minutes (mostly waiting)
- **Configuration**: 5 minutes

## Documentation You'll Need

Read these in order:

### 1️⃣ **Start Here** → [QUICK_START.md](QUICK_START.md)
Quick 3-step summary to get you going.

### 2️⃣ **GitHub Setup** → [GITHUB_SETUP.md](GITHUB_SETUP.md)
Detailed instructions for pushing your code to GitHub.

### 3️⃣ **Full Deployment** → [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
Complete step-by-step guide with screenshots and explanations.

### 4️⃣ **Environment Config** → [ENVIRONMENT_CONFIG.md](ENVIRONMENT_CONFIG.md)
Understand how environment variables work.

### 5️⃣ **Checklist** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
Track your progress through deployment.

## Before You Start

**Have these ready:**
- [ ] Groq API key from https://console.groq.com/keys
- [ ] GitHub account at https://github.com
- [ ] Render account at https://render.com
- [ ] Vercel account at https://vercel.com

## The 3-Step Process

### Step 1: Push to GitHub
```powershell
cd ai-doc-generator
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-generator.git
git push -u origin main
```

### Step 2: Deploy Backend (Render)
- Create Render account and connect GitHub
- Create Web Service from your repository
- Set Root Directory to `backend`
- Add `GROQ_API_KEY` and other environment variables
- Wait for deployment (5-10 min)
- Copy your Render URL

### Step 3: Deploy Frontend (Vercel)
- Create Vercel account and import GitHub repository
- Set Root Directory to `frontend`
- Add `NEXT_PUBLIC_API_BASE_URL` = your Render URL
- Wait for deployment (2-5 min)
- Share your Vercel URL with the world!

## What You Need to Know

### Security
- ✅ `GROQ_API_KEY` stays on backend only
- ✅ Frontend never sees your API key
- ✅ All communication is HTTPS encrypted
- ✅ Keys are managed in secure environment variables

### Costs
- **Render**: Free tier includes 10 preview instances, paid plans start ~$5/month
- **Vercel**: Free tier for frontend, paid plans start ~$20/month
- **Groq**: Pay as you go - set billing limits to avoid surprises

### Limits
- **Rate Limiting**: 5 requests/hour (configurable)
- **Repository Size**: Clones repositories up to ~500MB
- **Generation Time**: ~30-60 seconds per README

## After Deployment

### Monitor Your App
- Check Render logs for backend errors
- Monitor Groq usage at https://console.groq.com/keys
- Set up billing alerts to avoid surprises

### Improve Your App
- Add authentication for heavy users
- Implement Redis for better rate limiting
- Add custom domain (optional)
- Set up email notifications for errors

### Share Your App
- Your Vercel URL is your public app
- Share it on social media, portfolio, GitHub profile
- It will work anywhere - no installation needed

## Troubleshooting Tips

| Problem | Solution |
|---------|----------|
| Backend won't deploy | Check Render logs, verify Docker builds locally |
| Frontend shows API errors | Verify `NEXT_PUBLIC_API_BASE_URL` is set in Vercel |
| CORS errors | Ensure `ALLOWED_ORIGINS` in Render matches your Vercel URL exactly |
| Generation fails | Check Groq API key is valid and has credits |
| "Cannot reach backend" | Test `{backend-url}/health` endpoint directly |

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for detailed troubleshooting.

## Getting Help

- **Render Support**: https://render.com/docs
- **Vercel Support**: https://vercel.com/help
- **Groq Support**: https://docs.groq.com
- **Git Help**: https://github.com/git-guides

## Next Steps Right Now

1. **Read [QUICK_START.md](QUICK_START.md)** (2 minutes)
2. **Follow [GITHUB_SETUP.md](GITHUB_SETUP.md)** (5 minutes)
3. **Follow [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** (20 minutes)
4. **Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** (5 minutes)
5. **Visit your live app!** 🎉

---

## FAQ

**Q: Will my app cost money?**  
A: Render and Vercel have free tiers. Groq usage is pay-as-you-go (~$0.01 per README).

**Q: Can I use my own domain?**  
A: Yes! Both Render and Vercel support custom domains (optional).

**Q: What happens if my app gets popular?**  
A: Render and Vercel auto-scale. Groq usage increases your costs, so set billing limits.

**Q: Can I revert changes?**  
A: Yes! Git allows you to rollback. Both Render and Vercel keep deployment history.

**Q: How do I update my app after deploying?**  
A: Push changes to GitHub's `main` branch. Render and Vercel will auto-redeploy.

---

**Ready? Start with [QUICK_START.md](QUICK_START.md)** →
