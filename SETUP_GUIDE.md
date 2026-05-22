# 🌊 Flask API Setup - Quick Start

## 📋 What Was Created

Your flood prediction model is now ready to be deployed as an API! Here's what's been set up:

```
📁 sicitra-banjir-ai/
├── 📁 api/
│   └── index.py              ← Flask API (main file)
├── model_banjir.pkl          ← Your trained model
├── vercel.json               ← Vercel deployment config
├── requirements.txt          ← Updated with Flask dependencies
├── test_model.py             ← Test script
├── api_examples.py           ← Usage examples
├── API_DOCUMENTATION.md      ← Full API documentation
└── VERCEL_DEPLOYMENT_GUIDE.md ← Deployment guide
```

---

## ⚡ Quick Start (Choose One)

### Option A: Test Locally (2 minutes)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the test script
python test_model.py

# 3. Start the API
python api/index.py

# 4. In another terminal, test the API
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"tinggi_muka_air": 0.85}'
```

### Option B: Deploy to Vercel (5 minutes)
```bash
# 1. Commit your code
git add .
git commit -m "Add Flask API for flood prediction"
git push origin main

# 2. Go to https://vercel.com/dashboard
# 3. Click "Add New" → "Project"
# 4. Select your repository
# 5. Click "Deploy"

# Your API will be live at: https://your-project.vercel.app/api/predict
```

---

## 📊 Model Understanding

Your `model_banjir.pkl` is an **XGBoost Classifier** that predicts flood levels:

### Inputs (4 features)
```
1. Kecamatan (District)    - Encoded as number (default: 0)
2. Curah Hujan (Rainfall)  - in mm (default: 0.0)
3. Debit Air (Discharge)   - in m³/s (default: 0.0)
4. Muka Air (Water Level)  - in meters (default: 0.0)
```

### Outputs (4 flood levels)
```
Class 0: Normal    (TMA < 0.57 m)           ✅ Safe
Class 1: Waspada   (0.57 ≤ TMA < 0.93 m)   ⚠️  Alert
Class 2: Siaga     (0.93 ≤ TMA ≤ 1.30 m)   🔴 Warning
Class 3: Awas      (TMA > 1.30 m)          🚨 Emergency
```

---

## 🔌 API Endpoints

### 1. Health Check
```bash
GET /
```
**Response:**
```json
{"status": "ok", "model_loaded": true}
```

### 2. Single Prediction (Main)
```bash
POST /api/predict
```
**Request:**
```json
{
  "curah_hujan": 50,
  "debit_air": 25.5,
  "tinggi_muka_air": 0.85
}
```
**Response:**
```json
{
  "success": true,
  "prediction": {
    "flood_level": "1 - Waspada",
    "flood_class": 1,
    "description": "Alert level - monitor closely"
  }
}
```

### 3. Batch Prediction
```bash
POST /api/predict/batch
```
Make multiple predictions at once

---

## 🧪 Testing Options

### Option 1: Using cURL (from terminal)
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"tinggi_muka_air": 0.85}'
```

### Option 2: Using Python
```python
import requests

response = requests.post('http://localhost:5000/api/predict', json={
    'curah_hujan': 50,
    'debit_air': 25,
    'tinggi_muka_air': 0.85
})
print(response.json())
```

### Option 3: Using JavaScript/Fetch
```javascript
fetch('http://localhost:5000/api/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    curah_hujan: 50,
    debit_air: 25,
    tinggi_muka_air: 0.85
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

### Option 4: Postman/Insomnia
- Import the examples from `api_examples.py`
- Set method to POST
- Add JSON body
- Send!

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md) | Step-by-step deployment |
| [api_examples.py](api_examples.py) | Code examples |
| [test_model.py](test_model.py) | Testing & validation |

---

## 🚀 Deployment Checklist

- [ ] Run `python test_model.py` - all tests pass ✅
- [ ] Test API locally: `python api/index.py`
- [ ] Verify `/api/predict` endpoint works
- [ ] Commit all changes to Git
- [ ] Deploy via Vercel dashboard
- [ ] Test deployed API at `https://your-project.vercel.app/api/predict`
- [ ] Share API URL with team

---

## 🔧 Files Modified/Created

### Created Files:
- ✨ `api/index.py` - Flask API
- ✨ `vercel.json` - Vercel config
- ✨ `test_model.py` - Test script
- ✨ `api_examples.py` - Usage examples
- ✨ `API_DOCUMENTATION.md` - Full docs
- ✨ `VERCEL_DEPLOYMENT_GUIDE.md` - Deployment guide
- ✨ `.gitignore` - Git ignore rules

### Modified Files:
- 📝 `requirements.txt` - Added Flask and dependencies

### Existing Files (unchanged):
- `model_banjir.pkl` - Your trained model
- `XGBoost.ipynb` - Model training notebook
- Data files - Training data

---

## ❓ Common Questions

**Q: What if the model file is too large for Vercel?**
A: If `model_banjir.pkl` is > 50MB, use cloud storage (AWS S3, Google Cloud Storage)

**Q: How do I make predictions without knowing Kecamatan?**
A: Leave it out or set it to 0. The API handles it automatically.

**Q: Can I use optional parameters?**
A: Yes! All input parameters are optional. Defaults to 0.0 if not provided.

**Q: What are typical input values?**
- Curah Hujan: 0-200 mm
- Debit Air: 5-100 m³/s  
- Tinggi Muka Air: 0-2 meters

**Q: How do I update the model?**
A: Replace `model_banjir.pkl` and redeploy to Vercel

**Q: Is the API secure?**
A: Basic security is included (input validation, error handling). Consider adding rate limiting for production.

---

## 🎯 Next Steps

1. **Test Locally**
   ```bash
   python test_model.py
   python api/index.py
   ```

2. **Try Some Predictions**
   ```bash
   curl -X POST http://localhost:5000/api/predict \
     -H "Content-Type: application/json" \
     -d '{"tinggi_muka_air": 0.5}'  # Normal
   
   curl -X POST http://localhost:5000/api/predict \
     -H "Content-Type: application/json" \
     -d '{"tinggi_muka_air": 1.0}'  # Warning
   ```

3. **Deploy to Vercel**
   - Follow [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)
   - Takes ~5 minutes

4. **Integrate with Frontend**
   - React/Vue/Angular app
   - Mobile app
   - Web dashboard

5. **Monitor Performance**
   - Check Vercel logs
   - Track prediction accuracy
   - Monitor API usage

---

## 📞 Support

For issues:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for troubleshooting
2. Review [test_model.py](test_model.py) for diagnostics
3. Check Vercel logs in dashboard
4. Verify model file exists and is readable

---

## 📦 Technology Stack

- **Framework**: Flask (Python)
- **Model**: XGBoost
- **Deployment**: Vercel (Serverless)
- **Dependencies**: scikit-learn, numpy, pandas

---

**Your API is ready to serve predictions! 🚀**

Start testing: `python api/index.py`

Deploy: Push to Git → Vercel automatically deploys

Questions? Check the documentation files above.
