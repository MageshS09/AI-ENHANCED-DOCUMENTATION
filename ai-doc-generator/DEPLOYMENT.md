# Public Deployment

This app should be deployed as two public services:

- Backend API: Render, Railway, Fly.io, or another container host
- Frontend web app: Vercel, Netlify, or another Next.js host

The Groq API key must live only on the backend. Never expose it in the frontend.

## Recommended MVP Hosting

Use Render for the FastAPI backend and Vercel for the Next.js frontend.

## 1. Push To GitHub

Create a GitHub repository and push this project.

```bash
git init
git add .
git commit -m "Initial AI Documentation Generator MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-generator.git
git push -u origin main
```

## 2. Deploy Backend On Render

1. Open Render and create a new Blueprint or Web Service from the repository.
2. Use `render.yaml` if creating from blueprint.
3. Set these environment variables:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW_SECONDS=3600
```

After deployment, verify:

```text
https://your-render-service.onrender.com/health
```

## 3. Deploy Frontend On Vercel

1. Import the same GitHub repository into Vercel.
2. Set the project root to `frontend`.
3. Add this environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

4. Deploy.

## 4. Update Backend CORS

After Vercel gives you the final public URL, update Render:

```env
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

Redeploy the backend.

## Public Usage Notes

- The backend includes a basic in-memory rate limiter for `/api/generate`.
- For heavy public traffic, replace the in-memory limiter with Redis.
- Keep billing limits enabled on your Groq account.
- Add authentication or CAPTCHA before promoting widely.
