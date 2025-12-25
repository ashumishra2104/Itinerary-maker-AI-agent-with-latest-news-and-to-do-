# 🔧 API Integration Guide - Iteration Planner Agent

## Quick Reference: Which APIs Are Ready?

| API | Status | Key Needed | Priority | Cost |
|-----|--------|-----------|----------|------|
| **Open-Meteo (Weather)** | ✅ Live | No | High | FREE |
| **Geoapify (Attractions)** | ✅ Ready | No | High | FREE |
| **Unsplash (Images)** | ✅ Ready | Yes | Medium | FREE |
| **OpenAI (Recommendations)** | ✅ Ready | Yes | Medium | Paid |
| **SerpAPI (Hotels)** | ✅ Ready | Yes | Low | Paid |

---

## 🌤️ 1. Open-Meteo Weather API

**Status:** ✅ ALREADY WORKING (No key needed!)

### Currently Implemented Features
- Current weather conditions
- 7-day forecast
- Temperature, humidity, wind, precipitation
- Weather code interpretation (sunny, rainy, snowy, etc.)

### Code Location
File: `app.py`, Function: `get_weather()`

### Testing
```bash
# Test with curl
curl "https://api.open-meteo.com/v1/forecast?latitude=48.8584&longitude=2.2945&current=temperature_2m"
```

### Example Output
```json
{
  "current": {
    "temperature_2m": 15.5,
    "weather_code": 2,
    "wind_speed_10m": 12,
    "humidity": 65
  },
  "daily": {
    "temperature_2m_max": [18, 20, 19],
    "weather_code": [2, 1, 3]
  }
}
```

### To Use in Your Code
```python
weather = get_weather(latitude, longitude, timezone)
current_temp = weather['current']['temperature_2m']
forecast = weather['daily']['temperature_2m_max']
```

---

## 📍 2. Geoapify Places API

**Status:** ✅ READY (Free tier available)

### How to Get Started
1. Go to: https://www.geoapify.com/places-api/
2. Click "Get Free API Key" or "Try API"
3. Free tier: 3000 credits per day (MORE than enough)
4. **No API key required for basic usage**

### Code Location
File: `app.py`, Function: `get_attractions()`

### Currently Using Mock Data
The app includes mock data for Paris, New York, and Tokyo.

### To Enable Real API
Uncomment this section in `get_attractions()`:

```python
def get_attractions(location: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get attractions using Geoapify Places API"""
    
    api_key = os.getenv("GEOAPIFY_API_KEY")  # Optional
    
    # If API key available, use real API
    if api_key:
        url = "https://api.geoapify.com/v1/places"
        params = {
            "text": f"tourist attractions {location}",
            "limit": limit,
            "apiKey": api_key,
            "format": "json"
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            attractions = []
            for result in data.get("results", []):
                attractions.append({
                    "name": result.get("name", ""),
                    "lat": result.get("lat", 0),
                    "lon": result.get("lon", 0),
                    "type": result.get("type", "attraction"),
                    "rating": result.get("properties", {}).get("rating", 0)
                })
            
            return attractions
        except Exception as e:
            print(f"Geoapify API error: {e}")
            # Fallback to mock data
    
    # Use mock data
    return get_mock_attractions(location, limit)
```

### Testing
```bash
# Test with curl (free tier, no key needed)
curl "https://api.geoapify.com/v1/places?text=restaurants+Paris&limit=5"
```

---

## 📸 3. Unsplash API (Images)

**Status:** ✅ READY (Add key to enable)

### How to Get Your API Key

**Step 1:** Go to https://unsplash.com/developers

**Step 2:** Click "Register as a Developer"

**Step 3:** Fill out form
- Name: Your Name
- Email: Your Email
- Intended Use: Personal Project / Educational

**Step 4:** Accept terms and submit

**Step 5:** Go to "Your apps" → "Create a new app"

**Step 6:** Fill details:
- Name: "Iteration Planner"
- Description: "Trip planning app"
- Accept terms

**Step 7:** Copy your "Access Key"

**Step 8:** Add to `.env` file
```
UNSPLASH_API_KEY=your_access_key_here
```

### Code Location
File: `app.py`, Function: `get_images()`

### Currently Using
Default Unsplash search URLs (works without key, but has limited quality)

### To Use Your API Key

```python
def get_images(attractions: List[Dict[str, Any]]) -> Dict[str, str]:
    """Get images using Unsplash API"""
    
    api_key = os.getenv("UNSPLASH_API_KEY")
    images = {}
    
    if api_key:
        # Use Unsplash API with your key
        for attraction in attractions:
            try:
                url = "https://api.unsplash.com/search/photos"
                params = {
                    "query": attraction["name"],
                    "per_page": 1,
                    "client_id": api_key,
                    "order_by": "relevant"
                }
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if data["results"]:
                    image_url = data["results"][0]["urls"]["regular"]
                    images[attraction["name"]] = image_url
                else:
                    # Fallback
                    search_query = attraction["name"].replace(" ", "%20")
                    images[attraction["name"]] = f"https://source.unsplash.com/400x300/?{search_query}"
            except Exception as e:
                print(f"Image fetch error: {e}")
                # Use fallback
                search_query = attraction["name"].replace(" ", "%20")
                images[attraction["name"]] = f"https://source.unsplash.com/400x300/?{search_query}"
    else:
        # Use default Unsplash search URLs
        for attraction in attractions:
            search_query = attraction["name"].replace(" ", "%20")
            images[attraction["name"]] = f"https://source.unsplash.com/400x300/?{search_query}"
    
    return images
```

### Rate Limits
- **Free Tier:** 50 requests per hour
- **More than enough** for this app

### Testing
```bash
# Test API (replace with your key)
curl "https://api.unsplash.com/search/photos?query=Paris&client_id=YOUR_KEY"
```

---

## 🤖 4. OpenAI API (Friendly Recommendations)

**Status:** ✅ READY (Add key to enable)

### How to Get Your API Key

**Step 1:** Go to https://platform.openai.com/account/api-keys

**Step 2:** Sign up (if not already)

**Step 3:** Create new API key
- Click "Create new secret key"
- Copy the key immediately (won't show again)

**Step 4:** Add to `.env` file
```
OPENAI_API_KEY=sk-your_key_here
```

### Code Location
File: `app.py`, Function: `get_clothing_recommendation()`

### Currently Using
Mock recommendations based on temperature

### To Use OpenAI

```python
def get_clothing_recommendation(weather_data: Dict, num_days: int) -> str:
    """Generate clothing recommendations using OpenAI"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        import openai
        openai.api_key = api_key
        
        try:
            temp = weather_data["current"]["temperature_2m"]
            conditions = format_weather_code(weather_data["current"]["weather_code"])
            
            prompt = f"""
            Create a friendly, enthusiastic packing list for a {num_days} day trip.
            Weather conditions: {conditions}, Temperature: {temp}°C
            
            Include:
            - Specific clothing items
            - Layers recommendations
            - Accessories
            - Footwear suggestions
            
            Be conversational and helpful!
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback to mock
            return get_mock_clothing_recommendation(weather_data)
    
    else:
        # Use mock recommendation
        return get_mock_clothing_recommendation(weather_data)
```

### Pricing
- **Input:** $0.0005 per 1K tokens
- **Output:** $0.0015 per 1K tokens
- **Typical itinerary cost:** $0.20-0.50

### Testing
```bash
# Test with curl (replace with your key)
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-YOUR_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

---

## 🏨 5. SerpAPI (Hotel Search)

**Status:** ✅ READY (Add key for real data)

### How to Get Your API Key

**Step 1:** Go to https://www.searchapi.io/

**Step 2:** Sign up for free account
- Email and password
- Verify email

**Step 3:** Get API key from dashboard

**Step 4:** Free tier includes:
- 100 calls per month
- Perfect for testing

**Step 5:** Add to `.env` file
```
SERP_API_KEY=your_serp_key_here
```

### Code Location
File: `app.py`, Function: `get_hotels()`

### Currently Using
Mock hotel database

### To Use SerpAPI

```python
def get_hotels(location: str, budget: int, num_people: int) -> List[Dict[str, Any]]:
    """Get hotels using SerpAPI Google Hotels"""
    
    api_key = os.getenv("SERP_API_KEY")
    
    if api_key:
        try:
            from datetime import datetime, timedelta
            
            # Calculate dates
            check_in = datetime.now() + timedelta(days=7)
            check_out = check_in + timedelta(days=3)
            
            url = "https://api.searchapi.io/api/v1/search"
            params = {
                "engine": "google_hotels",
                "q": f"{location} hotels",
                "check_in_date": check_in.strftime("%Y-%m-%d"),
                "check_out_date": check_out.strftime("%Y-%m-%d"),
                "adults": num_people,
                "api_key": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            hotels = []
            for hotel in data.get("hotels", [])[:5]:
                price = hotel.get("price", 0)
                
                # Convert price to numeric
                if isinstance(price, str):
                    price = float(price.replace("$", "").replace(",", ""))
                
                hotels.append({
                    "name": hotel.get("title", ""),
                    "price": int(price),
                    "rating": hotel.get("rating", 0),
                    "address": hotel.get("address", ""),
                    "link": hotel.get("link", "")
                })
            
            return hotels
        
        except Exception as e:
            print(f"SerpAPI error: {e}")
            # Fallback to mock
            return get_mock_hotels(location, budget, num_people)
    
    else:
        # Use mock data
        return get_mock_hotels(location, budget, num_people)
```

### Free Tier Limits
- **100 API calls per month** (3-4 per user) - Free
- Beyond that: $5 per 100 calls

### Testing
```bash
# Test SerpAPI
curl "https://api.searchapi.io/api/v1/search?engine=google_hotels&q=Paris+hotels&api_key=YOUR_KEY"
```

---

## 🔐 Environment Variables Setup

### Create `.env` File

**Step 1:** Duplicate `.env.example`
```bash
cp .env.example .env
```

**Step 2:** Edit `.env` and add your keys
```
# Open-Meteo (No key needed - leave as is)
OPEN_METEO_API=https://api.open-meteo.com/v1/forecast

# Unsplash (Get from https://unsplash.com/developers)
UNSPLASH_API_KEY=your_unsplash_key_here

# OpenAI (Get from https://platform.openai.com/account/api-keys)
OPENAI_API_KEY=sk-your_openai_key_here

# SerpAPI (Get from https://www.searchapi.io/)
SERP_API_KEY=your_serp_key_here

# Geoapify (Get from https://www.geoapify.com/)
GEOAPIFY_API_KEY=your_geoapify_key_here
```

**Step 3:** Load in your app
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

---

## 🧪 Testing Each API

### Test 1: Weather (Open-Meteo) - FREE
```bash
# Should work immediately, no key needed
python -c "
import requests
resp = requests.get('https://api.open-meteo.com/v1/forecast', 
                    params={'latitude': 48.8584, 'longitude': 2.2945, 'current': 'temperature_2m'})
print(resp.json())
"
```

### Test 2: Unsplash (Images)
```bash
# If you added key to .env
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('UNSPLASH_API_KEY')
resp = requests.get('https://api.unsplash.com/search/photos',
                    params={'query': 'Paris', 'client_id': key})
print(f'Found {len(resp.json()[\"results\"])} images')
"
```

### Test 3: OpenAI (Recommendations)
```bash
# If you added key to .env
python -c "
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

resp = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print(resp.choices[0].message.content)
"
```

### Test 4: SerpAPI (Hotels)
```bash
# If you added key to .env
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('SERP_API_KEY')
resp = requests.get('https://api.searchapi.io/api/v1/search',
                    params={'engine': 'google_hotels', 'q': 'Paris hotels', 'api_key': key})
hotels = resp.json().get('hotels', [])
print(f'Found {len(hotels)} hotels')
"
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Test all APIs locally
- [ ] Verify `.env` file NOT in git (add to `.gitignore`)
- [ ] Set environment variables on hosting platform
- [ ] Test each API function with real data
- [ ] Monitor API rate limits
- [ ] Set up error handling fallbacks
- [ ] Test PDF generation
- [ ] Verify all dependencies in `requirements.txt`
- [ ] Test on Streamlit Cloud or chosen platform
- [ ] Monitor API costs (especially OpenAI)

---

## 📊 API Usage Monitoring

### Check Your API Credits

**Unsplash:**
- Go to: https://unsplash.com/developers
- Dashboard shows requests/hour usage

**OpenAI:**
- Go to: https://platform.openai.com/account/usage/overview
- Shows tokens used and estimated cost

**SerpAPI:**
- Go to: https://www.searchapi.io/
- Dashboard shows API calls remaining

---

## 🆘 Common Issues & Solutions

### Issue: "Invalid API Key"
**Solution:** Copy-paste key carefully from dashboard, no extra spaces

### Issue: "Rate limit exceeded"
**Solution:** 
- Add delay between requests: `time.sleep(1)`
- Use caching for repeated requests
- Upgrade to paid plan

### Issue: "Connection refused"
**Solution:**
- Check internet connection
- Verify API endpoint URL is correct
- Check if API service is down

### Issue: "Empty response"
**Solution:**
- Verify API parameters are correct
- Check if location name is valid
- Try with different search term

---

## 🎓 Next Steps

1. **Get Free APIs Running**
   - Open-Meteo: Already working ✅
   - Geoapify: No key needed ✅

2. **Add Optional APIs**
   - Unsplash: Get key (free) - 5 minutes
   - OpenAI: Get key (paid) - 5 minutes
   - SerpAPI: Get key (free trial) - 5 minutes

3. **Test Locally**
   - Add `.env` file
   - Run `streamlit run app.py`
   - Test each feature

4. **Deploy**
   - Push to GitHub
   - Connect to Streamlit Cloud
   - Add secrets in platform settings
   - Launch! 🚀

---

**Ready to integrate real APIs?** Start with Unsplash and OpenAI for the best experience! 🎉
