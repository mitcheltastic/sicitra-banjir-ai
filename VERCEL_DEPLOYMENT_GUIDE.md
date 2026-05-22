# 🚀 Vercel Deployment Guide

## Quick Start (5 minutes)

### Step 1: Prepare Your Repository
Make sure all files are committed to Git:
```bash
git add .
git commit -m "Add Flask API with Vercel configuration"
git push origin main
```

**Files that must be included:**
- ✅ `api/index.py` - Flask API
- ✅ `model_banjir.pkl` - Trained model
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements.txt` - Python dependencies

---

## Option 1: Deploy via Vercel Website (Easiest)

### 1. Create a Vercel Account
- Go to https://vercel.com
- Sign up with GitHub, GitLab, or Bitbucket
- Authorize Vercel to access your repositories

### 2. Import Your Project
- Click "Add New" → "Project"
- Select your `sicitra-banjir-ai` repository
- Click "Import"

### 3. Configure Project
- **Project Name**: `sicitra-banjir-ai` (or your preferred name)
- **Framework**: Auto-detected as Python
- **Root Directory**: `./` (default)
- Click "Deploy"

### 4. Your API is Live! 🎉
After ~2-3 minutes, you'll get a URL like:
```
https://sicitra-banjir-ai.vercel.app
```

Test it:
```bash
curl https://sicitra-banjir-ai.vercel.app/
```

---

## Option 2: Deploy via Vercel CLI

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Deploy
```bash
cd /path/to/sicitra-banjir-ai
vercel
```

### 3. Follow the prompts
- Link to an existing Vercel project or create new
- Set project name
- Choose to deploy to production

---

## Option 3: Deploy via GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Vercel

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Testing Your Deployment

### 1. Health Check
```bash
curl https://your-project.vercel.app/
```

### 2. Make a Prediction
```bash
curl -X POST https://your-project.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "curah_hujan": 50,
    "debit_air": 25,
    "tinggi_muka_air": 0.85
  }'
```

### 3. Test in Browser
Visit: `https://your-project.vercel.app/`

You should see:
```json
{"status": "ok", "message": "Flood Prediction API is running", "model_loaded": true}
```

---

## Common Issues & Solutions

### ❌ Issue: Model file too large
**Error**: `Artifact size exceeded maximum allowed size`

**Solution**: 
1. Check file size: `ls -lh model_banjir.pkl`
2. If > 50MB, use AWS S3 or cloud storage:
   ```python
   import boto3
   s3 = boto3.client('s3')
   s3.download_file('bucket-name', 'model_banjir.pkl', '/tmp/model.pkl')
   ```

### ❌ Issue: Module not found error
**Error**: `ModuleNotFoundError: No module named 'xgboost'`

**Solution**: Verify `requirements.txt` has all packages:
```
flask
flask-cors
pandas
scikit-learn
xgboost
numpy
```

### ❌ Issue: Build fails
**Error**: `Build failed`

**Solution**:
1. Check build logs in Vercel dashboard
2. Ensure `api/index.py` and `vercel.json` are correct
3. Test locally first: `python api/index.py`

### ❌ Issue: Model loads but predictions fail
**Error**: `prediction error` or `shape mismatch`

**Solution**:
- Model expects exactly 4 features in this order: `[Kecamatan, Curah Hujan, Debit Air, Muka Air]`
- Check the loaded model shape and feature names
- Verify input preprocessing

---

## Custom Domain (Optional)

### Add Your Own Domain
1. Go to Vercel Dashboard → Your Project
2. Click "Settings" → "Domains"
3. Enter your domain
4. Update DNS records at your registrar
5. Done! Your API is at `api.yourdomain.com`

---

## Monitoring & Logs

### View Logs
```bash
# Using Vercel CLI
vercel logs https://your-project.vercel.app

# Or in Vercel Dashboard
# Go to your project → Deployments → Select deployment → Logs
```

### Monitor Performance
Vercel Dashboard shows:
- Response times
- Error rates
- Resource usage
- Function invocations

---

## Environment Variables (if needed)

1. In Vercel Dashboard: Project → Settings → Environment Variables
2. Add variables (e.g., API keys, database URLs)
3. Redeploy after adding

Example:
```
MODEL_PATH=/tmp/model_banjir.pkl
LOG_LEVEL=INFO
```

Access in code:
```python
import os
model_path = os.getenv('MODEL_PATH', './model_banjir.pkl')
```

---

## Scaling & Performance

### Default Vercel Settings (Free Tier)
- ✅ Automatic scaling
- ✅ HTTPS included
- ✅ Global CDN
- ⚠️ Function timeout: 60 seconds
- ⚠️ Cold start time: 1-3 seconds

### Optimization Tips
1. Keep model file size small
2. Pre-load model on container startup
3. Use caching for repeated predictions
4. Monitor cold start times

---

## Rollback to Previous Version

```bash
# In Vercel Dashboard
# Deployments → Select previous version → Promote to Production
```

Or via CLI:
```bash
vercel rollback
```

---

## Continuous Integration

### Automatic Deploys
- Every push to `main` branch deploys automatically
- Preview deployments for pull requests
- Automatic rollback on failure

---

## Security

### Best Practices
1. ✅ Use environment variables for sensitive data
2. ✅ Keep `requirements.txt` up to date
3. ✅ Enable Vercel's built-in WAF (Pro tier)
4. ✅ Add input validation (already done in API)
5. ✅ Monitor logs for suspicious activity

---

## API Rate Limiting (Optional)

Add rate limiting to prevent abuse:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    # ... prediction logic
```

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- **Flask on Vercel**: https://vercel.com/docs/concepts/frameworks/flask

---

## Next Steps

After deployment:
1. ✅ Test all API endpoints
2. ✅ Monitor logs for errors
3. ✅ Share API URL with team
4. ✅ Document API changes
5. ✅ Set up automated backups
6. ✅ Monitor model performance

---

**Your API URL will be**: `https://your-project.vercel.app`

**Prediction endpoint**: `https://your-project.vercel.app/api/predict`

**Test it with**:
```bash
curl -X POST https://your-project.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{"tinggi_muka_air": 0.85}'
```

Happy deploying! 🚀
