# 🌍 Iteration Planner Agent ✈️

**Your Personal AI Travel Assistant for Creating the Perfect Itinerary!**

Welcome to the **Iteration Planner Agent**, a powerful Streamlit application designed to plan your trips down to the finest detail. Whether you're a budget backpacker or a luxury traveler, this agent uses AI to curate a personalized schedule, find strictly budgeted hotels, discover local attractions, and even keep you updated with the latest happenings in your destination.

## 🌟 Key Features

*   **⚡ AI-Powered Itineraries:** Generates day-by-day travel plans using OpenAI's GPT models, customized for your vibe and pace.
*   **🏨 Smart Hotel Finder:** strictly adheres to your budget (50-75% of your daily allowance) to find the best hotels using real-time data.
*   **📸 Visual Richness:** Fetches high-quality images for every attraction and hotel (Unsplash, Wikipedia, DuckDuckGo) + **AI-Generated Daily Visuals** for your specific trip moments!
*   **📰 Latest News Integration:** Fetches real-time news about events, festivals, and concerts in your destination so you don't miss out on what's happening *now*.
*   **📄 PDF Export:** Downloads a beautifully formatted, image-rich PDF itinerary to take with you offline.
*   **💰 Currency Support:** Fully localized for Indian Rupees (₹) and US Dollars ($).

## 🚀 Live Demo & Walkthrough

Watch the agent in action planning a trip to **Mumbai**:

![App Walkthrough](demo_walkthrough.webp)

*Note: The video above shows the full flow from search to PDF generation.*

### 📍 Example User Journey (Mumbai Trip)
1.  **Search:** User starts from "New Delhi" and searches for "Mumbai".
2.  **Budget:** User sets a strict budget of **₹50,000** for **4 Days**.
3.  **Generate:** The agent processes weather, hotels, and attractions.
4.  **Results:**
    *   **Hotels:** Finds highly-rated hotels costing ~₹6,000-8,000/night (within 50-75% budget rule).
    *   **Visuals:** User clicks "✨ Generate Day 1 Visual" and gets a custom AI image of the Mumbai skyline.
    *   **News:** Agent displays upcoming events like "Design Mumbai 2025" and music festivals.
5.  **Download:** User downloads the complete **[Sample Itinerary PDF](sample_itinerary.pdf)**.

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **Logic & AI:** Python, OpenAI API
*   **Data Sources:**
    *   **Hotels:** SerpAPI (Google Hotels)
    *   **Weather:** Open-Meteo API
    *   **News:** NewsAPI
    *   **Images:** Unsplash, DuckDuckGo, Wikipedia
    *   **Map/Geocoding:** Open-Meteo / Geoapify (Optional)
*   **PDF Generation:** ReportLab

## ⚙️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/ashumishra2104/Itinerary-maker-AI-agent-with-latest-news-and-to-do-.git
    cd Itinerary-maker-AI-agent-with-latest-news-and-to-do-
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    Create a `.env` file in the root directory (or use Streamlit Secrets for deployment):
    ```ini
    OPENAI_API_KEY=your_openai_key
    SERP_API_KEY=your_serpapi_key_for_hotels
    NEWS_API_KEY=your_newsapi_key
    UNSPLASH_API_KEY=your_unsplash_key_(optional)
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## 🔐 Deployment on Streamlit Cloud

1.  Push this code to your GitHub.
2.  Login to [Streamlit Community Cloud](https://streamlit.io/cloud).
3.  Connect your repo and deploy!
4.  **Crucial:** Go to your app's **Settings > Secrets** and paste your API keys there in TOML format:
    ```toml
    OPENAI_API_KEY = "sk-..."
    SERP_API_KEY = "..."
    NEWS_API_KEY = "..."
    UNSPLASH_API_KEY = "..."
    ```

## 📄 License

MIT License. Feel free to fork and modify!

---
*Built with ❤️ by Ashu Mishra*

### 🤝 Connect with Me
For more exciting projects, please follow **[Ashu Mishra](https://www.linkedin.com/in/ashumish/)** on LinkedIn, and get in touch to discuss more on AI! 🚀
