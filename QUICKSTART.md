# ⚡ Quick Start Guide - Iteration Planner Agent

## 🎯 Get Running in 3 Minutes

### For Mac/Linux Users
```bash
# 1. Clone/extract project to a folder
cd iteration-planner

# 2. Run setup script
bash setup.sh

# 3. Start the app
streamlit run app.py
```

### For Windows Users
```bash
# 1. Navigate to project folder
cd iteration-planner

# 2. Run setup script
setup.bat

# 3. Start the app (in the activated virtual environment)
streamlit run app.py
```

### Manual Setup (All Platforms)
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/bin/activate          # Mac/Linux
# OR
venv\Scripts\activate.bat         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env              # Mac/Linux
# OR
copy .env.example .env            # Windows

# 5. Run the app
streamlit run app.py
```

---

## 🌐 Open in Browser

Once running, open: **http://localhost:8501**

You should see the Iteration Planner interface!

---

## 🧪 Test It (Without API Keys)

1. Enter "New York, USA" as FROM
2. Enter "Paris, France" as TO
3. Select dates
4. Enter number of people and budget
5. Click "Generate My Perfect Itinerary"

**The app works with built-in mock data!** ✅

---

## 🔑 Add API Keys (Optional)

### To Get Better Experience:

1. **Unsplash API** (Better images) - 5 min
   - Go to: https://unsplash.com/developers
   - Register → Create app → Copy key
   - Add to `.env`: `UNSPLASH_API_KEY=your_key`

2. **OpenAI API** (Better recommendations) - 5 min
   - Go to: https://platform.openai.com/account/api-keys
   - Create key
   - Add to `.env`: `OPENAI_API_KEY=sk-your_key`

3. **SerpAPI** (Real hotel data) - 5 min
   - Go to: https://www.searchapi.io/
   - Sign up → Get key
   - Add to `.env`: `SERP_API_KEY=your_key`

### Add Key Steps:
1. Open `.env` file in text editor
2. Paste your key next to the API name
3. Save file
4. Restart the app (Ctrl+C and `streamlit run app.py`)

---

## 📁 What's in the Box?

```
iteration-planner/
├── app.py                    ← Main app (ready to run!)
├── requirements.txt          ← Dependencies
├── .env.example             ← Copy this to .env
├── README.md                ← Full documentation
├── API_INTEGRATION_GUIDE.md ← How to add API keys
├── setup.sh                 ← Auto setup (Mac/Linux)
├── setup.bat                ← Auto setup (Windows)
└── QUICKSTART.md            ← This file
```

---

## ✨ Features Available NOW

✅ Beautiful input form  
✅ Real weather data (Open-Meteo)  
✅ Top attractions & landmarks  
✅ Hotel recommendations  
✅ Packing suggestions  
✅ Day-wise itineraries  
✅ Beautiful PDF download  
✅ Text file download  

---

## 🚀 Deploy to Cloud (Easy!)

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to: https://streamlit.io/cloud
3. Click "New app"
4. Select your repo and `app.py`
5. Click "Deploy"

**That's it!** Your app is live!

Add secrets in platform:
- Settings → Secrets
- Add your API keys

### Option 2: Railway.app

1. Connect GitHub repo
2. Select Python
3. Add start command: `streamlit run app.py`
4. Deploy

### Option 3: Render

Similar to Railway - super easy!

---

## 🐛 Troubleshooting

### App won't start
```bash
# Make sure you installed requirements
pip install -r requirements.txt

# Try again
streamlit run app.py
```

### ImportError for streamlit
```bash
# Install it specifically
pip install streamlit
```

### Weather not showing
- This should always work (free API, no key needed)
- Check your internet connection
- Try a different city name

### PDF download not working
```bash
# Install reportlab
pip install reportlab
```

### All other issues
- Check README.md for detailed docs
- Check API_INTEGRATION_GUIDE.md for API help
- Test your internet connection
- Restart the app

---

## 📊 File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application - ALL code here |
| `requirements.txt` | Python packages to install |
| `.env.example` | Template for API keys - copy to `.env` |
| `README.md` | Complete documentation |
| `API_INTEGRATION_GUIDE.md` | Detailed API setup guide |
| `setup.sh` / `setup.bat` | Automatic setup scripts |

---

## 🎯 What the App Does

**Input → Process → Output**

1. **User enters:** From city, to city, dates, people, budget
2. **App fetches:**
   - Weather forecast
   - Top attractions
   - Hotel recommendations
   - Images
3. **App generates:** Friendly itinerary with recommendations
4. **User downloads:** PDF or text file

---

## 💰 Costs

- **Without API keys:** $0 (fully free!)
- **With OpenAI:** ~$0.20-0.50 per itinerary
- **With SerpAPI:** ~$0.10 per hotel search
- **Total typical:** $0-1 per user

---

## ✅ Next Steps

1. **Run it now:** `streamlit run app.py`
2. **Test with mock data:** No keys needed
3. **Add API keys:** (Optional) Follow README.md
4. **Deploy:** Push to GitHub + Streamlit Cloud
5. **Share:** Give your friends the URL!

---

## 🆘 Need Help?

1. **Setup issues:** Check README.md
2. **API questions:** Check API_INTEGRATION_GUIDE.md
3. **Streamlit help:** https://docs.streamlit.io/
4. **API docs:**
   - Weather: https://open-meteo.com/
   - Images: https://unsplash.com/developers
   - AI: https://platform.openai.com/docs
   - Hotels: https://serpapi.com/

---

## 🎉 Ready?

```bash
streamlit run app.py
```

That's it! Your app is running! 🚀

---

**Created with ❤️ for AI developers**

