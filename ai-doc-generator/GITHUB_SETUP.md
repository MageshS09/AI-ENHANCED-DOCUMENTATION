# GitHub Repository Setup

Before deploying to Render and Vercel, your code must be on GitHub.

## Prerequisites

- GitHub account (free at github.com)
- Git installed on your computer
- Your `ai-doc-generator` project on your local machine

## Step-by-Step Setup

### 1. Create a New Repository on GitHub

1. Go to https://github.com/new
2. Enter repository name: `ai-doc-generator`
3. Choose visibility: **Public** (required for deployment)
4. **Do NOT** initialize with README (you already have one)
5. Click "Create repository"
6. Copy the HTTPS URL (e.g., `https://github.com/YOUR_USERNAME/ai-doc-generator.git`)

### 2. Initialize Git in Your Project

Open PowerShell in your project root and run:

```powershell
cd ai-doc-generator
git init
```

### 3. Add Your Files to Git

```powershell
git add .
```

This stages all files for commit.

### 4. Create Initial Commit

```powershell
git commit -m "Initial AI Documentation Generator MVP"
```

### 5. Rename Branch to Main (if needed)

```powershell
git branch -M main
```

### 6. Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-doc-generator.git
```

### 7. Push to GitHub

```powershell
git push -u origin main
```

You may be prompted to authenticate. Use your GitHub credentials or a personal access token.

### 8. Verify on GitHub

Go to `https://github.com/YOUR_USERNAME/ai-doc-generator` and verify your files are there.

## Troubleshooting

### "fatal: not a git repository"

**Solution**: Make sure you're in the correct directory:
```powershell
cd ai-doc-generator
git init
```

### "fatal: remote origin already exists"

**Solution**: The remote is already set. Run:
```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/ai-doc-generator.git
```

### "fatal: refusing to merge unrelated histories"

**Solution**: If pushing fails, try:
```powershell
git push -u origin main --force
```

⚠️ Only use `--force` on your own repository!

### Authentication fails

**Solutions**:
1. Use Personal Access Token instead of password:
   - Create at: https://github.com/settings/tokens
   - When prompted for password, paste the token
2. Or set up SSH keys:
   - Guide: https://github.com/git-guides/install-git

### Large files error

**Issue**: "File is too large" error from Git LFS

**Solution**: Files over 100MB need Git LFS, but your project should be fine. If you have large binary files:

1. Delete them or add to `.gitignore`
2. Run: `git reset HEAD <filename>`
3. Commit and push again

## After Pushing to GitHub

Your repository is now ready for deployment!

### Next Steps:

1. **Deploy Backend**: Follow [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#step-2-deploy-backend-on-render)
2. **Deploy Frontend**: Follow [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#step-3-deploy-frontend-on-vercel)

### Useful Git Commands for Later

```powershell
# Check repository status
git status

# View commit history
git log

# Update your code after making changes
git add .
git commit -m "Your message"
git push

# Create a new branch for features
git checkout -b feature-name
git push -u origin feature-name
```

## Keeping Your Repository Updated

After deployment, you may want to continue developing locally:

```powershell
# Make changes to files
# Then:

git add .
git commit -m "Describe your changes"
git push
```

Render and Vercel will auto-redeploy when you push to `main` branch (if auto-deployment is enabled).

---

For more on GitHub: https://github.com/git-guides
