# Environment Configuration Guide

This guide explains how environment variables work in your production app.

## Overview

Your app uses environment variables to configure the backend API endpoint without changing code.

### Frontend (Vercel)

**Variable**: `NEXT_PUBLIC_API_BASE_URL`
- **Purpose**: Tells frontend where to find the backend API
- **Default**: `http://localhost:8000` (for local development)
- **Production Example**: `https://ai-doc-generator-api.onrender.com`
- **Public Visibility**: YES (prefix `NEXT_PUBLIC_` means it's visible in browser)
- **Security**: Safe - doesn't contain secrets

### Backend (Render)

**Variables**:

| Variable | Purpose | Example |
|----------|---------|---------|
| `GROQ_API_KEY` | Your Groq API key | `sk-proj-abc123...` |
| `GROQ_MODEL` | LLM model to use | `llama-3.3-70b-versatile` |
| `GROQ_BASE_URL=https://api.groq.com/openai/v1
| `ALLOWED_ORIGINS` | Frontend URLs allowed to call API | `https://my-app.vercel.app` |
| `RATE_LIMIT_REQUESTS` | Max requests per window | `5` |
| `RATE_LIMIT_WINDOW_SECONDS` | Time window in seconds | `3600` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

**Security**: All backend variables are private - never exposed to the frontend.

## Local Development

### Backend Setup

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

### Frontend Setup

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Production Deployment

### Step 1: Set Backend Variables on Render

In Render dashboard → Your service → Environment:

```
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
ALLOWED_ORIGINS=https://your-app.vercel.app
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

### Step 2: Set Frontend Variables on Vercel

In Vercel dashboard → Your project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_BASE_URL=https://your-render-backend.onrender.com
```

### Step 3: Update Backend CORS

After getting your Vercel URL, update the backend's `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

Then redeploy backend (Render will auto-redeploy).

## Security Best Practices

✅ **Do:**
- Keep `GROQ_API_KEY` secret - only store on backend
- Use Vercel/Render environment variable editors (not in code)
- Rotate API keys regularly
- Enable billing limits on Groq
- Use HTTPS URLs in production

❌ **Don't:**
- Commit `.env` files to Git
- Expose `GROQ_API_KEY` in frontend code
- Use the same key across environments
- Share API keys in messages/logs
- Store secrets in public repositories

## Troubleshooting

### "Cannot reach backend" error

**Issue**: Frontend can't connect to backend API

**Solutions**:
1. Verify `NEXT_PUBLIC_API_BASE_URL` is set in Vercel
2. Check the URL is correct and doesn't have trailing slash
3. Verify backend is running (test `{backend-url}/health`)
4. Check browser console for CORS errors

### CORS errors

**Issue**: "Access to XMLHttpRequest... has been blocked by CORS policy"

**Solutions**:
1. Verify `ALLOWED_ORIGINS` in backend matches your frontend URL exactly
2. URLs must include protocol (`https://` not just domain)
3. No trailing slashes
4. Redeploy backend after updating `ALLOWED_ORIGINS`
5. Wait 1-2 minutes for changes to take effect

### API key rejected

**Issue**: "401 Unauthorized" or "Invalid API key"

**Solutions**:
1. Verify key is from https://console.groq.com/keys
2. Check key hasn't been revoked
3. Verify key has available credit
4. Try regenerating a new key in Groq dashboard
5. Check key is set in Render environment, not locally

### Generation fails

**Issue**: "Error generating README" after submission

**Solutions**:
1. Check Render logs for detailed error
2. Verify Groq account has available credits
3. Check rate limits aren't exceeded
4. Try with different GitHub repository
5. Verify repository is public

## Environment Variable Reference

### Backend (Render)

```yaml
services:
  - name: ai-doc-generator-api
    envVars:
      - key: GROQ_API_KEY
        sync: false  # Manual entry, not synced
      - key: GROQ_MODEL
        value: llama-3.3-70b-versatile
        value: text-embedding-3-small
      - key: ALLOWED_ORIGINS
        sync: false  # Update after frontend is live
      - key: RATE_LIMIT_REQUESTS
        value: 5
      - key: RATE_LIMIT_WINDOW_SECONDS
        value: 3600
```

### Frontend (Vercel)

```json
{
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "https://your-render-url.onrender.com"
  }
}
```

## Additional Resources

- Groq API keys: https://console.groq.com/keys
- Render Documentation: https://render.com/docs
- Vercel Documentation: https://vercel.com/docs
- Environment Variables in Next.js: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables

---

For deployment steps, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
