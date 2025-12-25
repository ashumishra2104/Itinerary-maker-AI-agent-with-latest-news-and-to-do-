"""
Iteration Planner Agent - Streamlit Application
AI-Powered Trip Itinerary Planner with Weather, Attractions, Hotels, and PDF Export
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from typing import List, Dict, Any
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
import wikipedia

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="🌍 Iteration Planner Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def geocode_location(location: str) -> List[Dict[str, Any]]:
    """
    Geocode a location using Open-Meteo Geocoding API (Free, no key needed)
    Returns a list of potential matches.
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": location,
            "count": 10,
            "language": "en",
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if data.get("results"):
            for result in data["results"]:
                results.append({
                    "id": result.get("id"),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "name": result.get("name", location),
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", ""),
                    "timezone": result.get("timezone", "UTC")
                })
        return results
    except Exception as e:
        st.error(f"Geocoding error: {str(e)}")
        return []


def get_weather(latitude: float, longitude: float, timezone: str = "UTC") -> Dict[str, Any]:
    """
    Get weather data using Open-Meteo API (Free, no API key needed)
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "timezone": timezone,
            "forecast_days": 7
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        st.error(f"Weather API error: {str(e)}")
        return None



def generate_daily_image(location: str, activity_highlight: str) -> str:
    """
    Generate an exciting image for the day's itinerary using DALL-E 3
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"A hyper-realistic, exciting travel photography shot of {location}. The scene features {activity_highlight}. Sunny lighting, vibrant colors, cinematic composition, 4k resolution."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt[:1000],
            size="1024x1024",
            quality="standard",
            n=1,
        )

        return response.data[0].url
    except Exception as e:
        print(f"Image Gen Error: {e}")
        return None


def get_attractions(location: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get top attractions using OpenAI (Best for descriptive, curated content)
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback to simple logic if key is missing (though it shouldn't be)
            return []

        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
        List top {limit} tourist attractions in {location}.
        Return a strict JSON array of objects with these keys:
        - name: string
        - type: string (e.g. Museum, Park, Historic Site)
        - lat: float (approximate latitude)
        - lon: float (approximate longitude)
        - summary: string (An exciting, engaging description, max 200 chars)

        Do not include markdown formatting (like ```json), just the raw JSON string.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        
        # Clean up if the model adds markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        attractions = json.loads(content)
        return attractions[:limit]

    except Exception as e:
        print(f"OpenAI Attractions error: {e}")
        return [{
            "name": f"Check out {location}", 
            "type": "City Center", 
            "lat": 0.0, 
            "lon": 0.0, 
            "summary": f"Explore the vibrant streets and landmarks of {location}."
        }]



def get_activities(location: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get activities using OpenAI (Creative things to do)
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return []

        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
        List top {limit} specific activities/experiences to do in {location} (e.g., food tour, kayaking, hiking trail, sunset cruise).
        Return a strict JSON array of objects with these keys:
        - name: string (Title of the activity)
        - type: string (e.g. Adventure, Culinary, Relaxation)
        - summary: string (Exciting description, max 200 chars)

        Do not include markdown formatting.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```json"): content = content[7:]
        if content.endswith("```"): content = content[:-3]
            
        return json.loads(content)[:limit]

    except Exception as e:
        print(f"OpenAI Activities error: {e}")
        return [{
            "name": "Walking Tour",
            "type": "Exploration",
            "summary": f"Take a walk through the beautiful streets of {location}."
        }]


def get_geoapify_attractions(latitude: float, longitude: float, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get attractions using Geoapify Places API (Real-time, Location-based)
    """
    try:
        api_key = os.getenv("GEOAPIFY_API_KEY")
        if not api_key:
            return []
            
        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": "tourism.attraction,entertainment.museum,religion.place_of_worship",
            "filter": f"circle:{longitude},{latitude},10000", # 10km radius
            "limit": limit,
            "apiKey": api_key,
            "lang": "en"
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return []
            
        data = response.json()
        attractions = []
        
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            
            # Skip if name is missing
            if not props.get("name"):
                continue
                
            attraction = {
                "name": props.get("name"),
                "type": props.get("categories", ["landmark"])[0].split('.')[-1].title(),
                "lat": props.get("lat"),
                "lon": props.get("lon"),
                "summary": props.get("formatted", f"Located at {props.get('address_line2', 'city center')}")
            }
            attractions.append(attraction)
            
        return attractions
    except Exception as e:
        print(f"Geoapify error: {e}")
        return []


def get_hotels(location: str, total_budget: int, num_days: int, num_people: int) -> List[Dict[str, Any]]:
    """
    Get hotels using SerpAPI (Google Hotels) with strict budget filtering
    Budget Rule: 50%-75% of per day budget (total_budget / num_days)
    """
    try:
        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            return []
            
        from serpapi import GoogleSearch
        
        # Calculate daily budget and target range
        per_day_budget = total_budget / num_days
        min_price = per_day_budget * 0.5
        max_price = per_day_budget * 0.75
        
        currency = "INR"

        params = {
            "engine": "google_hotels",
            "q": f"hotels in {location}",
            "check_in_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "adults": num_people,
            "currency": currency,
            "gl": "in", # India
            "hl": "en",
            "api_key": api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        
        hotels = []
        if "properties" in results:
            for property in results["properties"]:
                # Extract details
                rating = property.get("overall_rating", 0.0)
                reviews = property.get("reviews", 0)
                link = property.get("link", f"https://www.google.com/search?q=hotel+{property.get('name')}+{location}")
                
                # Extract image (use thumbnail or placeholder)
                image = "https://source.unsplash.com/400x300/?hotel"
                if property.get("images") and len(property["images"]) > 0:
                    image = property["images"][0].get("thumbnail", image)
                
                # Extract price
                price = 0
                if property.get("rate_per_night") and property["rate_per_night"].get("lowest"):
                    price_str = property["rate_per_night"]["lowest"]
                    # Extract digits from string like "₹1,200"
                    price = int(''.join(filter(str.isdigit, price_str)))
                
                # Strict Budget Filtering
                if min_price <= price <= max_price:
                    hotels.append({
                        "name": property.get("name", "Hotel"),
                        "price": price,
                        "rating": rating,
                        "reviews": reviews,
                        "address": property.get("description", location),
                        "link": link,
                        "image": image
                    })
        
        # Sort by rating matching budget
        hotels.sort(key=lambda x: x['rating'], reverse=True)
        
        return hotels[:10]  # Return top 10 matches

    except Exception as e:
        print(f"SerpAPI Hotels error: {e}")
        return []


def get_images(attractions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Get images using Unsplash API, DuckDuckGo (Free), or Wikipedia
    Robust fallbacks to ensure no broken images.
    """
    try:
        unsplash_key = os.getenv("UNSPLASH_API_KEY")
        images = {}

        # Import DuckDuckGo Search inside function to avoid global dependency issues if not installed
        try:
            from duckduckgo_search import DDGS
            ddg_available = True
        except ImportError:
            ddg_available = False
            print("DuckDuckGo Search library not found. Install with: pip install duckduckgo_search")

        for attraction in attractions:
            image_url = None
            query = attraction["name"]
            
            # 1. Try Unsplash (High Quality)
            if unsplash_key:
                try:
                    url = "https://api.unsplash.com/search/photos"
                    params = {
                        "query": query,
                        "per_page": 1,
                        "client_id": unsplash_key,
                        "order_by": "relevant",
                        "orientation": "landscape" 
                    }
                    response = requests.get(url, params=params, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results"):
                            image_url = data["results"][0]["urls"]["regular"]
                except Exception as e:
                    print(f"Unsplash error for {query}: {e}")

            # 2. Try DuckDuckGo (Best Free Web Search)
            if not image_url and ddg_available:
                try:
                    with DDGS() as ddgs:
                        # Simple image search
                        results = list(ddgs.images(
                            keywords=query,
                            region="wt-wt",
                            safesearch="on",
                            size="Large",
                            max_results=1
                        ))
                        if results:
                            image_url = results[0].get("image")
                except Exception as e:
                    print(f"DuckDuckGo error for {query}: {e}")

            # 3. Try Wikipedia (Free, good for landmarks)
            if not image_url:
                try:
                    # Use 'generator=search' to find page even if title doesn't match exactly
                    wiki_url = "https://en.wikipedia.org/w/api.php"
                    params = {
                        "action": "query",
                        "generator": "search",
                        "gsrsearch": query,
                        "gsrlimit": 1,
                        "prop": "pageimages",
                        "pithumbsize": 1000,
                        "format": "json",
                        "origin": "*"
                    }
                    response = requests.get(wiki_url, params=params, timeout=3)
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id in pages:
                        if "thumbnail" in pages[page_id]:
                            image_url = pages[page_id]["thumbnail"]["source"]
                            break
                except Exception as e:
                    print(f"Wikipedia Image error for {query}: {e}")
            
            # 4. Final Fallback
            if not image_url:
                # Reliable static placeholder
                safe_name = query.replace(" ", "+")
                image_url = f"https://placehold.co/600x400/EEE/31343C?text={safe_name}"
            
            images[attraction["name"]] = image_url
        
        return images

    except Exception as e:
        print(f"Global Images error: {str(e)}")
        return {}


def get_clothing_recommendation(weather_data: Dict, num_days: int) -> str:
    """
    Generate clothing recommendations based on weather
    Uses OpenAI API for friendly, personalized suggestions
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and weather_data and "current" in weather_data:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                
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
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
                # Fallback to mock logic below
        
        # Mock recommendation for demo
        if weather_data and weather_data.get("current"):
            temp = weather_data["current"]["temperature_2m"]
            
            if temp < 10:
                return "🧥 Pack warm layers, heavy coat, warm hat, gloves, and thermal underwear. A scarf is essential!"
            elif temp < 20:
                return "🧥 Pack light jacket, sweater, jeans, and comfortable walking shoes. Bring a light scarf."
            elif temp < 25:
                return "👕 Pack t-shirts, light shorts, comfortable walking shoes, and a light cardigan for evenings."
            else:
                return "☀️ Pack light, breathable clothing, shorts, sandals, sunglasses, and sunscreen. Bring a hat!"
        
        return "👕 Pack comfortable, versatile clothing suitable for urban exploration."
    except Exception as e:
        st.error(f"Clothing recommendation error: {str(e)}")
        return ""


def format_weather_code(code: int) -> str:
    """
    Convert WMO weather code to human-readable format
    """
    weather_codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Foggy",
        48: "🌫️ Foggy",
        51: "🌧️ Light drizzle",
        53: "🌧️ Moderate drizzle",
        55: "🌧️ Heavy drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "⛈️ Heavy rain",
        71: "❄️ Slight snow",
        73: "❄️ Moderate snow",
        75: "❄️ Heavy snow",
        80: "🌧️ Slight rain showers",
        81: "🌧️ Moderate rain showers",
        82: "⛈️ Violent rain showers",
        85: "❄️ Slight snow showers",
        86: "❄️ Heavy snow showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with hail",
        99: "⛈️ Thunderstorm with hail",
    }
    return weather_codes.get(code, "🌤️ Fair weather")


def generate_day_plan(day_num: int, attractions: List[Dict], weather_info: str) -> str:
    """
    Generate a friendly day plan
    In production, use OpenAI API for personalized recommendations
    """
    plan = f"""
    ### Day {day_num} - Adventure Awaits! 🌟
    
    **Morning (9:00 AM - 12:00 PM)**
    - Start your day with a hearty breakfast at a local café
    - Visit: {attractions[0]['name'] if attractions else 'Local Landmark'}
    - Time to explore: 3 hours
    
    **Afternoon (12:00 PM - 5:00 PM)**
    - Lunch at a nearby restaurant with local cuisine
    - Visit: {attractions[1]['name'] if len(attractions) > 1 else 'Shopping District'}
    - Leisure time for photos and exploration: 3 hours
    
    **Evening (5:00 PM - 9:00 PM)**
    - Rest and refresh at your hotel
    - Dinner at a highly-rated restaurant
    - Evening walk or cultural experience
    
    **Weather:** {weather_info}
    **Tips:** Stay hydrated, wear comfortable shoes, bring a camera!
    """
    return plan


def create_pdf_content(itinerary_data: Dict) -> str:
    """
    Create PDF content - will use ReportLab for actual generation
    """
    content = f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║           🌍 YOUR PERSONALIZED TRIP ITINERARY 🌍              ║
    ╚════════════════════════════════════════════════════════════════╝
    
    TRIP DETAILS
    ─────────────────────────────────────────────────────────────────
    From: {itinerary_data['from_place']}
    To: {itinerary_data['to_place']}
    Duration: {itinerary_data['num_days']} days
    Travelers: {itinerary_data['num_people']} people
    Budget: ${itinerary_data['budget']}
    
    RECOMMENDED ACCOMMODATIONS
    ─────────────────────────────────────────────────────────────────
    """
    
    for hotel in itinerary_data.get('hotels', []):
        content += f"\n★ {hotel['name']} - ${hotel['price']}/night (Rating: {hotel['rating']}/5)"
    
    content += f"""
    
    WHAT TO PACK
    ─────────────────────────────────────────────────────────────────
    {itinerary_data.get('clothing_tips', '')}
    
    DAILY ITINERARIES
    ─────────────────────────────────────────────────────────────────
    {itinerary_data.get('daily_plans', '')}
    
    TOP ATTRACTIONS NOT TO MISS
    ─────────────────────────────────────────────────────────────────
    """
    
    for i, attraction in enumerate(itinerary_data.get('attractions', []), 1):
        content += f"\n{i}. {attraction['name']} ({attraction['type']})"
    
    content += """
    
    TRAVEL TIPS
    ─────────────────────────────────────────────────────────────────
    • Book accommodations in advance for better prices
    • Use public transportation to explore the city
    • Try local restaurants for authentic cuisine
    • Respect local customs and traditions
    • Keep important documents and valuables safe
    • Stay connected with travel insurance
    
    Generated with ❤️ by Iteration Planner Agent
    """
    
    return content


def fetch_image_for_pdf(url: str, width_in_inches: float = 4.0):
    """
    Fetch image from URL and return ReportLab Image object
    """
    try:
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.units import inch
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img_data = BytesIO(response.content)
            # Create RL Image
            img = RLImage(img_data)
            # Scale
            aspect = img.imageHeight / float(img.imageWidth)
            return RLImage(img_data, width=width_in_inches*inch, height=(width_in_inches*aspect)*inch)
    except Exception as e:
        print(f"PDF Image Fetch Error: {e}")
        return None
    return None


def download_pdf_button(itinerary_data: Dict) -> None:
    """
    Create rich downloadable PDF with images
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        
        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#e67e22'), # Accent color
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderPadding=5,
            borderWidth=0,
            
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            leading=16,
            textColor=colors.HexColor('#2c3e50')
        )
        
        center_style = ParagraphStyle(
            'Center',
            parent=styles['Normal'],
            alignment=TA_CENTER
        )

        # --- CONTENT GENERATION ---
        
        # Title
        elements.append(Paragraph(f"✈️ Trip to {itinerary_data['to_place']} 🌍", title_style))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<i>Your Personalized Itinerary</i>", center_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Cover Image (Try to get one from the attractions or generic)
        all_images = itinerary_data.get('images', {})
        # Find first available image
        cover_url = None
        if all_images:
            cover_url = list(all_images.values())[0]
        
        if cover_url:
            cover_img = fetch_image_for_pdf(cover_url, width_in_inches=6.0)
            if cover_img:
                elements.append(cover_img)
                elements.append(Spacer(1, 0.3*inch))
        
        # Trip Details Section
        elements.append(Paragraph("Trip Summary", heading_style))
        trip_details = [
            ['📍 From:', itinerary_data['from_place']],
            ['📍 To:', itinerary_data['to_place']],
            ['📅 Duration:', f"{itinerary_data['num_days']} days"],
            ['👥 Travelers:', f"{itinerary_data['num_people']} people"],
            ['💰 Budget:', f"INR {itinerary_data['budget']}"], # Safe currency text
        ]
        trip_table = Table(trip_details, colWidths=[2.5*inch, 4*inch])
        trip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ]))
        elements.append(trip_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Hotels Section
        elements.append(Paragraph("🏨 Recommended Hotels", heading_style))
        hotel_data = [['Hotel Name', 'Price/Night', 'Rating']]
        for hotel in itinerary_data.get('hotels', []):
            hotel_data.append([
                hotel['name'],
                f"Rs. {hotel['price']}",
                f"{hotel['rating']}/5"
            ])
        
        if len(hotel_data) > 1:
            hotel_table = Table(hotel_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            hotel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7f9f9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
            ]))
            elements.append(hotel_table)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Clothing Tips
        elements.append(Paragraph("🎒 What to Pack", heading_style))
        elements.append(Paragraph(itinerary_data.get('clothing_tips', ''), normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Daily Itineraries with Images
        elements.append(PageBreak())
        elements.append(Paragraph("📅 Daily Itinerary", heading_style))
        
        daily_plans_list = itinerary_data.get('daily_plans_list', [])
        session_images = st.session_state.get('daily_images', {})
        
        for plan in daily_plans_list:
            day_num = plan['day']
            
            # Container for Day Header
            elements.append(Paragraph(f"Day {day_num}: {plan.get('location', '')}", subheading_style))
            
            # Text content
            clean_text = plan['text'].replace('#', '').replace('*', '')
            elements.append(Paragraph(clean_text, normal_style))
            
            # Try to find specific daily image
            img_key = f"img_{itinerary_data['to_place']}_{day_num}"
            if img_key in session_images:
                img_url = session_images[img_key]
                pdf_img = fetch_image_for_pdf(img_url, width_in_inches=5.5)
                if pdf_img:
                    elements.append(Spacer(1, 0.1*inch))
                    # Add simple "border" or shadow effect notion by placing in table? 
                    # ReportLab images don't have borders easily, but we can wrap in a single-cell table with border.
                    img_table = Table([[pdf_img]], colWidths=[5.5*inch])
                    img_table.setStyle(TableStyle([
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER')
                    ]))
                    elements.append(img_table)
                    elements.append(Paragraph(f"<i>AI Visual for Day {day_num}</i>", center_style))
            
            elements.append(Spacer(1, 0.4*inch))

        # Attractions Gallery
        elements.append(PageBreak())
        elements.append(Paragraph("📸 Attractions Gallery", heading_style))
        
        # Create a flow of images
        attractions = itinerary_data.get('attractions', [])
        
        for attr in attractions:
            img_url = all_images.get(attr['name'])
            if img_url:
                pdf_img = fetch_image_for_pdf(img_url, width_in_inches=4.0)
                if pdf_img:
                    # Keep image and title together in a nice formatted block
                    items = [
                        Paragraph(f"<b>{attr['name']}</b>", subheading_style),
                        Paragraph(f"<font color='gray'>{attr['type']}</font>", normal_style),
                        Spacer(1, 0.05*inch),
                        pdf_img,
                        Spacer(1, 0.05*inch),
                        Paragraph(attr.get('summary', '')[:200] + "...", normal_style),
                        Spacer(1, 0.3*inch)
                    ]
                    elements.append(KeepTogether(items))
        
        # Latest News Section
        news_items = itinerary_data.get('news', [])
        if news_items:
            elements.append(PageBreak())
            elements.append(Paragraph("📰 Latest News & Updates", heading_style))
            
            for article in news_items:
                source_name = article.get('source', {}).get('name', 'Source')
                pub_date = article.get('publishedAt', '')[:10]
                
                # Title as link if possible (ReportLab supports <a href="...">)
                article_url = article.get('url', '#')
                title_text = f'<u><a href="{article_url}" color="blue">{article["title"]}</a></u>'
                
                items = [
                    Paragraph(title_text, subheading_style),
                    Paragraph(f"<font color='gray' size=9>{source_name} • {pub_date}</font>", normal_style),
                    Spacer(1, 0.05*inch),
                    Paragraph(f"<i>{article.get('description', '') or ''}</i>", normal_style),
                    Spacer(1, 0.2*inch)
                ]
                elements.append(KeepTogether(items))

        # Build PDF
        doc.build(elements)
        
        # Return PDF bytes
        pdf_bytes = pdf_buffer.getvalue()
        return pdf_bytes
        
    except ImportError:
        st.error("ReportLab not installed. Install with: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None



def get_latest_news(destination: str) -> List[Dict]:
    """
    Fetch latest news about the destination using NewsAPI
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return []
            
        url = "https://newsapi.org/v2/everything"
        # Refined query for events and local happenings
        params = {
            "q": f'"{destination}" AND (events OR festival OR concert OR exhibition OR "things to do" OR culture OR nightlife)',
            "apiKey": api_key,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 5
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            print(f"NewsAPI Error: {data.get('message')}")
            return []
            
    except Exception as e:
        print(f"News error: {e}")
        return []


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown("""
        <div class="header">
            <h1>🌍 Iteration Planner Agent</h1>
            <p>Create Your Perfect Personalized Trip Itinerary</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.info(f"""
            **Using Mock Data?**
            - Weather: Open-Meteo (Free ✓)
            - Attractions: Built-in database (Add GEOAPIFY_API_KEY to .env for real data)
            - Hotels: Mock database (Add SERP_API_KEY to .env for real data)
            
            **API Keys Loaded:**
            - OpenAI: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Not Found'}
            - Unsplash: {'✅ Configured' if os.getenv('UNSPLASH_API_KEY') else '❌ Not Found'}
        """)
    
    # Main Content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Trip Details")
        
        from_place = st.text_input(
            "📍 From (Your Current Location)",
            placeholder="e.g., New York, USA"
        )
        
        to_place_query = st.text_input(
            "✈️ Destination Search",
            placeholder="e.g., Paris"
        )
        
        selected_destination = None
        
        if to_place_query:
            # Fetch candidates
            candidates = geocode_location(to_place_query)
            
            if candidates:
                # Create friendly labels for dropdown
                options = {
                    f"{c['name']}, {c['country']} {f'({c['admin1']})' if c['admin1'] else ''}": c 
                    for c in candidates
                }
                
                selected_label = st.selectbox(
                    "✅ Confirm Destination",
                    options=list(options.keys())
                )
                
                selected_destination = options[selected_label]
            else:
                st.warning("No location found. Try adding a country name (e.g., 'Paris, France')")
    
    with col2:
        st.header("📋 Trip Info")
        
        travel_dates = st.date_input(
            "📅 Travel Dates",
            value=datetime.now(),
            min_value=datetime.now()
        )
        
        num_days = st.slider(
            "Duration (Days)",
            min_value=1,
            max_value=30,
            value=3
        )
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        num_people = st.number_input(
            "👥 Number of Travelers",
            min_value=1,
            max_value=20,
            value=2
        )
    
    with col4:
        budget = st.number_input(
            "💰 Total Budget (₹)",
            min_value=1000,
            max_value=1000000,
            value=25000,
            step=500
        )
    
    # Generate Button
    if st.button("🚀 Generate My Perfect Itinerary", use_container_width=True):
        
        if not from_place or not selected_destination:
            st.error("❌ Please ensure you have entered a 'From' location and selected a 'Destination'!")
        else:
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Geocode Destination
            status_text.text("📍 Finding your destination...")
            progress_bar.progress(10)
            
            destination_coords = selected_destination
            to_place_name = selected_destination['name']
            
            # Step 2: Get Weather
            status_text.text("🌤️ Fetching weather forecast...")
            progress_bar.progress(25)
            
            weather_data = get_weather(
                destination_coords["latitude"],
                destination_coords["longitude"],
                destination_coords.get("timezone", "UTC")
            )
            
            # Step 3: Get Attractions (Merged Sources)
            status_text.text("🎭 Discovering attractions (OpenAI + Geoapify)...")
            progress_bar.progress(40)
            
            # 1. Get descriptive list from OpenAI
            openai_attractions = get_attractions(to_place_name, limit=4)
            
            # 2. Get specific locations from Geoapify
            geoapify_attractions = get_geoapify_attractions(
                destination_coords["latitude"], 
                destination_coords["longitude"], 
                limit=6
            )
            
            # 3. Merge and deduplicate
            # We prefer OpenAI for descriptions, but want Geoapify's variety
            seen_names = {a["name"].lower() for a in openai_attractions}
            attractions = openai_attractions.copy()
            
            for ga in geoapify_attractions:
                # Simple dedupe: if name not roughly in existing list
                is_duplicate = False
                ga_name = ga["name"].lower()
                for seen in seen_names:
                    if ga_name in seen or seen in ga_name:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    attractions.append(ga)
                    seen_names.add(ga_name)
                    
            # Limit total
            attractions = attractions[:10]
            
            # Step 4: Get Activities
            status_text.text("🏄 Finding exciting activities...")
            progress_bar.progress(50)
            
            activities = get_activities(to_place_name, limit=6)
            
            # Step 5: Get Hotels (Strict Budget Logic)
            status_text.text("🏨 finding best hotels in your budget...")
            progress_bar.progress(60)
            
            hotels = get_hotels(to_place_name, budget, num_days, num_people)
            
            if not hotels:
                st.warning(f"No hotels found strictly between ₹{int((budget/num_days)*0.5)} and ₹{int((budget/num_days)*0.75)}/night. Try adjusting your budget!")
            
            # Step 6: Get Images (Attractions + Activities)
            status_text.text("📸 Fetching beautiful images...")
            progress_bar.progress(75)
            
            # Fetch images for both lists
            attraction_images = get_images(attractions)
            activity_images = get_images(activities) # get_images works for any list with 'name' key
            
            # Combine for itinerary data
            all_images = {**attraction_images, **activity_images}
            
            # Step 7: Generate Recommendations
            status_text.text("🎯 Generating personalized recommendations...")
            progress_bar.progress(85)
            
            clothing_tips = get_clothing_recommendation(weather_data, num_days)
            
            # Step 8: Get Latest News
            status_text.text("📰 Checking latest news...")
            progress_bar.progress(90)
            
            news_data = get_latest_news(to_place_name)
            
            # Step 9: Create Itinerary
            status_text.text("✍️ Creating your itinerary...")
            progress_bar.progress(95)
            
            daily_plans = ""
            daily_plans_list = []
            
            if weather_data and weather_data.get("daily"):
                for i in range(min(num_days, len(weather_data["daily"]["time"]))):
                    weather_code = weather_data["daily"]["weather_code"][i]
                    weather_desc = format_weather_code(weather_code)
                    
                    # Highlight activity for image gen
                    day_attraction = attractions[i % len(attractions)]['name']
                    
                    day_plan_text = generate_day_plan(i+1, attractions[i % len(attractions):], weather_desc)
                    daily_plans += day_plan_text + "\n"
                    
                    daily_plans_list.append({
                        "day": i+1,
                        "text": day_plan_text,
                        "highlight": f"visiting {day_attraction}",
                        "location": to_place_name
                    })
            
            progress_bar.progress(100)
            status_text.text("✅ Itinerary ready!")
            
            # Display Results
            st.success("🎉 Your itinerary has been created! Scroll down to view and download.")
            
            # Store itinerary data in session state
            st.session_state.itinerary_data = {
                'from_place': from_place,
                'to_place': to_place_name,
                'num_days': num_days,
                'num_people': num_people,
                'budget': budget,
                'attractions': attractions,
                'activities': activities,
                'hotels': hotels,
                'clothing_tips': clothing_tips,
                'daily_plans': daily_plans,
                'daily_plans_list': daily_plans_list,
                'images': all_images,
                'weather': weather_data,
                'news': news_data
            }
            
    # DISPLAY RESULTS FROM SESSION STATE
    if 'itinerary_data' in st.session_state:
        data = st.session_state.itinerary_data
        
        # Unpack commonly used variables for easier access in display code
        weather_data = data['weather']
        hotels = data['hotels']
        attractions = data['attractions']
        activities = data['activities']
        daily_plans_list = data['daily_plans_list']
        all_images = data['images']
        clothing_tips = data['clothing_tips']
        daily_plans = data['daily_plans']
        to_place = data['to_place']
        to_place_name = to_place
        itinerary_data = data

        # Display Weather
        if weather_data and weather_data.get("current"):
            st.markdown("---")
            st.header("🌤️ Weather Forecast")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Temperature",
                    f"{weather_data['current']['temperature_2m']}°C"
                )
            
            with col2:
                st.metric(
                    "Humidity",
                    f"{weather_data['current']['relative_humidity_2m']}%"
                )
            
            with col3:
                st.metric(
                    "Wind Speed",
                    f"{weather_data['current']['wind_speed_10m']} km/h"
                )
            
            with col4:
                st.metric(
                    "Conditions",
                    format_weather_code(weather_data['current']['weather_code'])
                )
                
            # Daily forecast
            st.subheader("Daily Forecast")
            # Calculate dates based on user START date
            start_date = travel_dates
            date_list = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(min(num_days, len(weather_data['daily']['time'])))]
            
            forecast_df = pd.DataFrame({
                'Date': date_list,
                'Max Temp': weather_data['daily']['temperature_2m_max'][:len(date_list)],
                'Min Temp': weather_data['daily']['temperature_2m_min'][:len(date_list)],
                'Conditions': [format_weather_code(code) for code in weather_data['daily']['weather_code'][:len(date_list)]]
            })
            st.dataframe(forecast_df, use_container_width=True)
            
            # Display Hotels (Modern Cards with Images)
            st.markdown("---")
            st.header("🏨 Recommended Hotels")
            
            if hotels:
                # Display in a grid
                hotel_cols = st.columns(3)
                for idx, hotel in enumerate(hotels):
                    with hotel_cols[idx % 3]:
                        # Use a container for card-like styling
                        with st.container():
                            st.markdown(f"""
                            <div style="background-color: white; border-radius: 10px; padding: 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden; border: 1px solid #ddd;">
                                <img src="{hotel['image']}" style="width: 100%; height: 150px; object-fit: cover;">
                                <div style="padding: 15px;">
                                    <h4 style="margin: 0 0 5px 0;">
                                        <a href="{hotel['link']}" target="_blank" style="text-decoration: none; color: #333;">{hotel['name']} 🔗</a>
                                    </h4>
                                    <div style="font-size: 14px; color: #666; margin-bottom: 5px;">
                                        ⭐ <b>{hotel['rating']}</b> ({hotel['reviews']} reviews)
                                    </div>
                                    <div style="font-size: 18px; color: #28a745; font-weight: bold; margin-bottom: 10px;">
                                        ₹{hotel['price']}/night
                                    </div>
                                    <p style="font-size: 12px; color: #555; margin: 0;">
                                        {hotel['address']}
                                    </p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No hotels matched your strict budget criteria.")
            
            # Display Attractions
            st.markdown("---")
            st.header("🎭 Top Attractions")

            # Prepare HTML for carousel
            cards_html = ""
            for attraction in attractions:
                image_url = all_images.get(attraction['name'], "https://source.unsplash.com/400x300/?travel,landmark")
                wiki_url = f"https://en.wikipedia.org/wiki/{attraction['name'].replace(' ', '_')}"
                
                cards_html += f"""
                <div style="min-width: 300px; max-width: 300px; background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
                    <img src="{image_url}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
                    <a href="{wiki_url}" target="_blank" style="text-decoration: none; color: inherit;">
                        <h3 style="margin: 0 0 5px 0; font-size: 1.2rem; color: #333; cursor: pointer; transition: color 0.2s;">
                            {attraction['name']} 🔗
                        </h3>
                    </a>
                    <div style="font-size: 0.8rem; color: #e91e63; margin-bottom: 8px; text-transform: uppercase; font-weight: bold;">{attraction['type']}</div>
                    <p style="font-size: 0.9rem; color: #555; line-height: 1.4; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; margin: 0;">
                        {attraction.get('summary', '')}
                    </p>
                </div>
                """
            
            # Render scrollable container
            st.markdown(f"""
                <style>
                .carousel-container {{
                    display: flex;
                    overflow-x: auto;
                    gap: 20px;
                    padding: 20px 0 40px 0; /* Extra bottom padding for scrollbar */
                    scroll-behavior: smooth;
                    scrollbar-width: thin;
                    scrollbar-color: #667eea #f0f2f6;
                }}
                .carousel-container::-webkit-scrollbar {{
                    height: 8px;
                }}
                .carousel-container::-webkit-scrollbar-track {{
                    background: #f0f2f6;
                    border-radius: 4px;
                }}
                .carousel-container::-webkit-scrollbar-thumb {{
                    background-color: #667eea;
                    border-radius: 4px;
                }}
                </style>
                <div class="carousel-container">
                    {cards_html}
                </div>
            """, unsafe_allow_html=True)

            # Display Activities Carousel
            st.markdown("---")
            st.header("🏄 Exciting Activities")
            
            activity_cards_html = ""
            for activity in activities:
                # Use same image logic
                image_url = all_images.get(activity['name'], "https://source.unsplash.com/400x300/?travel,fun")
                
                activity_cards_html += f"""
                <div style="min-width: 300px; max-width: 300px; background: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
                    <img src="{image_url}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">
                    <h3 style="margin: 0 0 5px 0; font-size: 1.2rem; color: #333;">{activity['name']}</h3>
                    <div style="font-size: 0.8rem; color: #e91e63; margin-bottom: 8px; text-transform: uppercase; font-weight: bold;">{activity['type']}</div>
                    <p style="font-size: 0.9rem; color: #555; line-height: 1.4; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; margin: 0;">
                        {activity.get('summary', '')}
                    </p>
                </div>
                """
            
            st.markdown(f"""
                <div class="carousel-container">
                    {activity_cards_html}
                </div>
            """, unsafe_allow_html=True)
            
            # Display Clothing Tips
            st.markdown("---")
            st.header("👕 What to Pack")
            
            st.info(clothing_tips)
            
            # Display Daily Plans
            st.markdown("---")
            st.header("📅 Daily Itineraries")
            
            # Initialize session keys for images if not exist
            if 'daily_images' not in st.session_state:
                st.session_state.daily_images = {}

            # Render each day
            for day_info in daily_plans_list:
                day_num = day_info['day']
                
                # Use columns for layout
                d_col1, d_col2 = st.columns([1.5, 1])
                
                with d_col1:
                    st.markdown(day_info['text'])
                
                with d_col2:
                    st.write("") # Spacer
                    st.write("")
                    
                    img_key = f"img_{to_place_name}_{day_num}"
                    
                    # Check if we already have an image
                    if img_key in st.session_state.daily_images:
                        st.image(st.session_state.daily_images[img_key], use_column_width=True, caption=f"Day {day_num} Vibes ✨")
                    else:
                        st.info("🎨 Visualize this day!")
                        if st.button(f"✨ Generate Day {day_num} Visual", key=f"btn_{day_num}"):
                            with st.spinner("Creating unique visual..."):
                                img_url = generate_daily_image(day_info['location'], day_info['highlight'])
                                if img_url:
                                    st.session_state.daily_images[img_key] = img_url
                                    st.rerun()
                                else:
                                    st.error("Could not generate image.")
            
            # Display News Section
            if itinerary_data.get('news'):
                st.markdown("---")
                st.header("📰 Latest News & Updates")
                
                # Show metadata as requested
                with st.expander("🔍 View News Metadata (Source Data)"):
                    st.json(itinerary_data['news'])
                    
                for article in itinerary_data['news']:
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            if article.get('urlToImage'):
                                st.image(article['urlToImage'], use_column_width=True)
                            else:
                                st.write("📰")
                        with cols[1]:
                            st.markdown(f"**[{article['title']}]({article['url']})**")
                            st.caption(f"{article.get('source', {}).get('name')} • {article.get('publishedAt', '')[:10]}")
                            st.write(article.get('description', ''))
            
            # Download Section
            st.markdown("---")
            st.header("📥 Download Your Itinerary")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # PDF Download
                pdf_content = create_pdf_content(itinerary_data)
                
                try:
                    pdf_bytes = download_pdf_button(itinerary_data)
                    if pdf_bytes:
                        st.download_button(
                            label="📄 Download as PDF",
                            data=pdf_bytes,
                            file_name=f"itinerary_{to_place}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.warning(f"PDF download temporarily unavailable. {str(e)}")
            
            with col2:
                # Text Download
                text_content = create_pdf_content(itinerary_data)
                st.download_button(
                    label="📝 Download as Text",
                    data=text_content,
                    file_name=f"itinerary_{to_place}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )


if __name__ == "__main__":
    main()
