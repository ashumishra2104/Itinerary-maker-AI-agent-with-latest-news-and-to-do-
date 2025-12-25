# Application Flow Diagram - Iteration Planner Agent

This diagram illustrates the logical flow of the `app.py` Streamlit application, from user input to itinerary generation and export.

```mermaid
flowchart TD
    Start([Start Application]) --> Config[Streamlit Page Config & CSS]
    Config --> InitLoad[Load Environment Variables (.env)]
    
    subgraph UI_Input["User Interface & Input"]
        Sidebar[Sidebar: Configuration]
        MainInput[Main Area: Trip Details]
        
        Sidebar --> |Check Keys| API_Status[Display API Key Status]
        
        MainInput --> From[From Location]
        MainInput --> To[Destination]
        MainInput --> Dates[Travel Dates]
        MainInput --> Duration[Duration & Travelers]
        MainInput --> Budget[Budget]
    end
    
    InitLoad --> UI_Input
    
    GenerateBtn{User Clicks\n'Generate Itinerary'}
    UI_Input --> GenerateBtn
    
    GenerateBtn -- No --> Wait[Wait for Input]
    GenerateBtn -- Yes --> Validate{Validate Inputs}
    
    Validate -- Invalid --> ShowError[Show Error Message]
    Validate -- Valid --> Step1[Step 1: Geocode Destination]
    
    subgraph Core_Logic["Data Processing & API Calls"]
        Step1 --> |Open-Meteo Geocoding| GeoResult{Found Location?}
        
        GeoResult -- No --> ShowGeoError[Error: Location Not Found]
        GeoResult -- Yes --> Step2[Step 2: Get Weather Data]
        
        Step2 --> |Open-Meteo Forecast| WeatherData[Weather JSON]
        WeatherData --> Step3[Step 3: Get Attractions]
        
        Step3 --> |Geoapify / Mock DB| AttractionsList[Attractions List]
        AttractionsList --> Step4[Step 4: Get Hotels]
        
        Step4 --> |SerpAPI / Mock DB| HotelsList[Hotels List]
        HotelsList --> Step5[Step 5: Get Images]
        
        Step5 --> |Unsplash API / Fallback| ImageUrls[Image URLs]
        ImageUrls --> Step6[Step 6: AI Recommendations]
        
        Step6 --> |OpenAI API / Mock Logic| ClothingTips[Clothing & Packing Tips]
        ClothingTips --> Step7[Step 7: Generate Daily Plan]
        
        Step7 --> |Logic + Weather + Attractions| DayPlanString[Formatted Daily Itinerary]
    end
    
    subgraph UI_Output["Result Display"]
        DayPlanString --> DispWeather[Display Weather Cards]
        DispWeather --> DispHotels[Display Hotel Recommendations]
        DispHotels --> DispAttractions[Display Top Attractions]
        DispAttractions --> DispTips[Display Packing Tips]
        DispTips --> DispItinerary[Display Daily Itineraries]
        
        DispItinerary --> ExportSection[Download Section]
    end
    
    ExportSection --> GenPDF[Generate PDF (ReportLab)]
    ExportSection --> GenTxt[Generate Text File]
    
    GenPDF --> DownloadPDF[Download PDF Button]
    GenTxt --> DownloadTxt[Download Text Button]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style GenerateBtn fill:#bbf,stroke:#333,stroke-width:2px
    style Core_Logic fill:#e1f5fe,stroke:#01579b,stroke-width:2px,stroke-dasharray: 5 5
    style UI_Output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## Key Components

1.  **Configuration**: Loads API keys securely from `.env`.
2.  **Geocoding**: Converts city names to coordinates (Lat/Lon) for weather data.
3.  **Weather Engine**: Fetches real-time forecast to inform packing and scheduling.
4.  **Content Aggregation**: Combines data from multiple sources (Attractions, Hotels, Images).
5.  **AI Layer**: Uses OpenAI (if available) to interpret data and give human-like advice.
6.  **Export Engine**: Formats all gathered data into a professional PDF report.
