import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import streamlit as st

# Streamlit Page Configuration
st.set_page_config(page_title="UV & IR Safety Advisor", page_icon="🌞", layout="wide")

# OpenWeather API Key
API_KEY = "6a4be2d9a3f1427ddaabb75a61be6ad2"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
UV_INDEX_URL = "https://api.openweathermap.org/data/2.5/uvi"

# AI Chatbots
chatbot_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key="AIzaSyCyMdOXtL52eSLZDzHoY6WrpXcDSlA4-bg")

def get_lat_lon(city, country):
    params = {"q": f"{city},{country}", "appid": API_KEY, "limit": 1}
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        return None, None
    except requests.exceptions.RequestException as e:
        return None, None

def get_uv_index(city, country):
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

def get_safety_tips(uv_index):
    if isinstance(uv_index, str):
        return uv_index
    tips = [
        ("Low UV exposure. Sunglasses recommended.", 0, 3),
        ("Moderate UV exposure. Use SPF 30 sunscreen and avoid peak hours.", 3, 6),
        ("High UV exposure! Apply SPF 50, cover skin, and avoid direct sun.", 6, 8),
        ("Very high UV exposure! Wear a hat, sunglasses, and stay indoors.", 8, 11),
        ("Extreme UV exposure! Avoid sunlight, hydrate, and take precautions.", 11, float("inf")),
    ]
    for tip, low, high in tips:
        if low <= uv_index < high:
            return tip
    return "UV index out of range."

def get_first_aid_tips(uv_index):
    if isinstance(uv_index, str):
        return uv_index
    if uv_index < 6:
        return "Mild exposure: Stay hydrated and apply moisturizer."
    elif 6 <= uv_index < 8:
        return "Moderate exposure: Apply cool compress and aloe vera."
    else:
        return "Severe exposure: Seek shade, drink water, and seek medical attention if needed."

def get_ir_precautions():
    return ("**Infrared Radiation (IR) Effects & Precautions**\n"
            "- Avoid intense heat sources like fires and industrial machinery.\n"
            "- Wear heat-resistant dark-colored fabrics.\n"
            "- Use SPF 30/50 with Titanium Dioxide & Zinc Oxide.\n"
            "- Use infrared-resistant goggles.\n"
            "- Avoid infrared therapy if you have metal implants or photosensitive medication.")

def get_sunscreen_info():
    sunscreens = {
        "Neutrogena Ultra Sheer": "May cause breakouts in acne-prone skin.",
        "Banana Boat Sport SPF 50": "Contains oxybenzone, which may cause skin irritation.",
        "La Roche-Posay Anthelios": "Generally safe but can cause mild eye irritation.",
        "Coppertone Water Babies": "Mild but may cause rashes in sensitive skin.",
        "Hawaiian Tropic Silk Hydration": "May contain fragrances that irritate sensitive skin."
    }
    return "\n".join([f"{brand}: {effect}" for brand, effect in sunscreens.items()])

def get_natural_remedies():
    return ("**Natural Remedies for UV Protection:**\n"
            "- Aloe Vera: Soothes sunburn and reduces inflammation.\n"
            "- Coconut Oil: Provides mild sun protection and hydration.\n"
            "- Green Tea Extract: Rich in antioxidants.\n"
            "- Carrot & Tomato Juice: Enhances sun protection.\n"
            "- Cotton Clothes: Provides natural UV resistance.")

# def chatbot_flan_response(query):
#     response = chatbot_gemini(f"UV safety tips: {query}", max_length=100, do_sample=False)
#     return response[0]['summary_text']

def chatbot_gemini_response(query):
    response = chatbot_gemini([HumanMessage(content=f"{query}")])
    return response.content

# Streamlit UI
st.title("🌞 UV & IR Safety Advisor")
st.sidebar.header("Enter Location")
city = st.sidebar.text_input("City")
country = st.sidebar.text_input("Country")
if st.sidebar.button("Get UV & IR Safety Report"):
    uv_index = get_uv_index(city, country)
    safety_message = get_safety_tips(uv_index)
    first_aid_message = get_first_aid_tips(uv_index)
    ir_precautions = get_ir_precautions()
    sunscreen_info = get_sunscreen_info()
    natural_remedies = get_natural_remedies()
    chatbot_message = chatbot_gemini_response("What are the safety measures for UV and IR exposure in Asia?")

    st.subheader(f"🌞 UV & IR Radiation Report for {city}, {country}")
    st.write(f"🔆 **Current UV Index:** {uv_index}")
    st.write(f"🛡️ **Safety Tips:** {safety_message}")
    st.write(f"⛑️ **First Aid Tips:** {first_aid_message}")
    st.write(f"🔥 **Infrared (IR) Precautions:**\n{ir_precautions}")
    st.write(f"🧴 **Sunscreen Brands & Side Effects:**\n{sunscreen_info}")
    st.write(f"🌱 **Natural Remedies:**\n{natural_remedies}")
    st.write(f"🤖 **Chatbot Advice:** {chatbot_message}")
