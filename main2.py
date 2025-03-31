import streamlit as st
import os
import phi
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.serpapi_tools import SerpApiTools

# Page Config
st.set_page_config(page_title="AI Travel Planner", page_icon="🌎", layout="wide")

# Sidebar: User Inputs
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png")
    st.title("Trip Settings")
    
    groq_api_key = st.text_input("🔑 Groq API Key", type="password")
    serpapi_key = st.text_input("🔑 SerpAPI Key", type="password")
    
    if not groq_api_key or not serpapi_key:
        st.warning("⚠️ Enter API keys to proceed.")
        st.stop()

    destination = st.text_input("🌍 Destination")
    duration = st.number_input("📅 Duration (days)", min_value=1, max_value=30, value=5)
    budget = st.select_slider("💰 Budget", ["Budget", "Moderate", "Luxury"], value="Moderate")
    travel_style = st.multiselect("🎯 Travel Style", ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"], ["Culture", "Nature"])
    dietary = st.selectbox("🍽️ Dietary Preference", ["No Preference", "Vegetarian", "Vegan", "Halal", "Gluten-Free"])
    mobility = st.selectbox("🚶‍♂️ Mobility Needs", ["No Issues", "Limited Walking", "Wheelchair Accessible"])
    accommodation = st.selectbox("🏨 Accommodation Type", ["Hostel", "Boutique Hotel", "Resort", "City Center", "Nature Lodge"])

# Set API Keys
os.environ["GROQ_API_KEY"] = groq_api_key
os.environ["SERP_API_KEY"] = serpapi_key

# Initialize Travel Agent
travel_agent = Agent(
    name="Travel Planner",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[SerpApiTools()],
    instructions=[
        "You are a travel planning assistant using Groq Llama.",
        "Guide users through an interactive conversation to refine their travel preferences and itinerary.",
        "Ask clarifying questions based on their responses to personalize the travel plan.",
        "Provide live links for hotels and attractions.",
        "Ensure all recommendations are up-to-date."
    ],
    show_tool_calls=True,
    markdown=True
)

# UI Header
st.title("🌎 AI Travel Planner")
st.markdown(f"""
    **Destination:** {destination}  
    **Duration:** {duration} days  
    **Budget:** {budget}  
    **Travel Style:** {', '.join(travel_style)}  
    **Dietary:** {dietary}  
    **Mobility:** {mobility}  
    **Accommodation:** {accommodation}  
""", unsafe_allow_html=True)

# Session State for Prompt Chaining
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None

# Step 1: Generate Recommendations
if st.button("🔍 Get Top Travel Recommendations"):
    if destination:
        with st.spinner("Fetching top attractions & best time to visit..."):
            prompt = f"""Give top attractions and best time to visit {destination}. 
            - Consider {budget} budget. 
            - Include {', '.join(travel_style)} experiences. 
            - Accommodation preference: {accommodation}. 
            - Dietary: {dietary}. 
            - mobility: {mobility}.
            - Provide relevant links.
            """
            response = travel_agent.run(prompt)
            st.session_state.recommendations = response.content
            st.markdown(response.content)
    else:
        st.warning("Please enter a destination.")

# Step 2: Generate Full Itinerary
if st.session_state.recommendations and st.button("📆 Generate Full Itinerary"):
    with st.spinner("Creating detailed day-by-day itinerary..."):
        prompt = f"""Based on the provided recommendations, create a {duration}-day itinerary for {destination}.
        - Must include sightseeing, activities, food stops, transportation tips, and estimated {budget} budget.
        - Align experiences with {', '.join(travel_style)} travel style , suggest restaurant according to {dietary} options , {mobility} restriction and type of {accommodation} .
         Please provide a detailed itinerary that includes:

    1. 🌞 Best Time to Visit
    - Seasonal highlights
    - Weather considerations

    2. 🏨 Accommodation Recommendations
    - {budget} range hotels/stays
    - Locations and proximity to attractions

    3. 🗺️ Day-by-Day Itinerary
    - Detailed daily activities
    - Must-visit attractions
    - Local experiences aligned with travel styles

    4. 🍽️ Culinary Experiences
    - Local cuisine highlights
    - Recommended restaurants
    - Food experiences matching travel style

    5. 💡 Practical Travel Tips
    - Local transportation options
    - Cultural etiquette
    - Safety recommendations
    - Estimated daily budget breakdown

    6. 💰 Estimated Total Trip Cost
    - Breakdown of expenses
    - Money-saving tips

    Please provide source and relevant links without fail.

    Format the response in a clear, easy-to-read markdown format with headings and bullet points.
        """
        response = travel_agent.run(prompt)
        st.session_state.itinerary = response.content
        st.markdown(response.content)

# Q&A Section
st.divider()
st.expander("🤔 Ask About Your Trip").write("Type your question below!")
question = st.text_input("Your question:")
if question and st.button("Get Answer", key="qa_button"):
    with st.spinner("Finding answer..."):
        context_question = f"""Using the following itinerary:
        {st.session_state.itinerary or st.session_state.recommendations}
        Answer concisely: {question}
        """
        response = travel_agent.run(context_question)
        st.markdown(response.content)

