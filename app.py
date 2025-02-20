import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import streamlit as st

# OpenWeather API Key
API_KEY = "6a4be2d9a3f1427ddaabb75a61be6ad2"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
UV_INDEX_URL = "https://api.openweathermap.org/data/2.5/uvi"

# Gemini AI Chatbot
chatbot = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",api_key="AIzaSyCyMdOXtL52eSLZDzHoY6WrpXcDSlA4-bg")

def get_lat_lon(city, country):
    """Fetch latitude and longitude based on city and country."""
    params = {
        "q": f"{city},{country}",
        "appid": API_KEY,
        "limit": 1
    }
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching location data: {e}")
        return None, None

def get_uv_index(city, country):
    """Fetch UV index using city and country name."""
    lat, lon = get_lat_lon(city, country)
    if lat is None or lon is None:
        return "Could not determine location."
    
    url = f"{UV_INDEX_URL}?lat={lat}&lon={lon}&appid={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("value", "No UV index available")
    except requests.exceptions.RequestException as e:
        return f"Error fetching UV index: {e}"

def chatbot_response(query):
    """Generate AI-based UV safety advice using Gemini."""
    context = ("UV and IR exposure safety varies by region. "
               "In Asia, tropical and desert climates increase risks. "
               "Use SPF 50 sunscreen and avoid peak sun hours.")
    response = chatbot([HumanMessage(content=f"{context} User Query: {query}")])
    return response.content

# Streamlit UI
st.set_page_config(page_title="UV & IR Safety Advisor", page_icon="🌞", layout="wide")

st.title("🌞 UV & IR Radiation Safety Advisor")
st.markdown("Get real-time UV index, safety tips, and precautions for your location.")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    city = st.text_input("Enter city name", placeholder="e.g., New York")
with col2:
    country = st.text_input("Enter country name", placeholder="e.g., USA")

if st.button("Get UV & IR Safety Report"):
    if city and country:
        with st.spinner("Fetching data..."):
            uv_index = get_uv_index(city, country)
            chatbot_message = chatbot_response("What are the safety measures for UV and IR exposure in Asia?")
        
        st.success("Data fetched successfully!")
        st.markdown(f"### 🌞 **UV & IR Radiation Report for {city}, {country}**")
        st.markdown(f"🔆 **Current UV Index:** {uv_index}")
        
        st.markdown("---")
        
        st.markdown("### 🤖 **Chatbot Advice**")
        st.info(chatbot_message)
    else:
        st.error("Please enter both city and country names.")
