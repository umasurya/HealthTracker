import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None  # fallback to local food_db if not available

st.title("AI Nutrition Helper")

provider = st.selectbox("Data provider", options=["OpenAI (chat)", "OpenFoodFacts (free)"], index=1)

food = st.text_input("What did you eat?")

food_db = {
    "apple": {"calories": 52, "protein": 0.3},
    "banana": {"calories": 89, "protein": 1.1},
    "chapati": {"calories": 105, "protein": 2.4},
    "chicken": {"calories": 165, "protein": 31.0},
    "egg": {"calories": 78, "protein": 6.3},
    "milk": {"calories": 103, "protein": 8.1},
    "rice": {"calories": 130, "protein": 2.7},
    "quinoa": {"calories": 111, "protein": 4.4},
    "wheat": {"calories": 138, "protein": 5.7},
    "grapes": {"calories": 69, "protein": 0.7},
    "orange": {"calories": 62, "protein": 1.3},
    "spinach": {"calories": 24, "protein": 2.9},
}

if st.button("Get nutrition"):
    if not food:
        st.warning("Please type what you ate.")
    else:
        # Prefer OpenAI when API key present
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": f"Give calories and protein for {food} in very simple words."
                        }
                    ],
                )

                answer = response.choices[0].message.content
                st.success(answer)

                with open("food_history.txt", "a") as f:
                    time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    f.write(f"{time} - {food}\n")
            except Exception as e:
                # Log the error and fall back to local DB for quota errors
                msg = str(e)
                time = datetime.now().strftime("%Y-%m-%d %H:%M")
                with open("openai_errors.log", "a") as log:
                    log.write(f"{time} - OpenAI error: {msg}\n")

                # Check for quota/429 errors and fallback
                if "insufficient_quota" in msg or "quota" in msg or "429" in msg:
                    st.warning("OpenAI quota exceeded — falling back to local food database.")
                    key = food.strip().lower()
                    if key in food_db:
                        info = food_db[key]
                        st.success(f"{food.title()}: {info['calories']} kcal, {info['protein']} g protein")
                        with open("food_history.txt", "a") as f:
                            f.write(f"{time} - {food} (local fallback)\n")
                    else:
                        st.info("No local data available for that food. Please add an OPENAI_API_KEY or try another item.")
                else:
                    st.error(f"OpenAI error: {e}")
        else:
            # Provider selection: OpenFoodFacts or local DB fallback
            if provider == "OpenFoodFacts (free)":
                from providers.openfoodfacts import search_openfoodfacts

                info = search_openfoodfacts(food)
                if info:
                    cal = info.get('calories')
                    prot = info.get('protein')
                    note = info.get('note') or ''
                    parts = []
                    if cal is not None:
                        parts.append(f"{cal} kcal")
                    if prot is not None:
                        parts.append(f"{prot} g protein")
                    st.success(f"{food.title()}: {', '.join(parts)} ({note})")

                    with open("food_history.txt", "a") as f:
                        time = datetime.now().strftime("%Y-%m-%d %H:%M")
                        f.write(f"{time} - {food} (openfoodfacts)\n")
                else:
                    # fallback to local DB
                    key = food.strip().lower()
                    if key in food_db:
                        info = food_db[key]
                        st.success(f"{food.title()}: {info['calories']} kcal, {info['protein']} g protein")

                        with open("food_history.txt", "a") as f:
                            time = datetime.now().strftime("%Y-%m-%d %H:%M")
                            f.write(f"{time} - {food} (local)\n")
                    else:
                        st.info("No data available from OpenFoodFacts or local DB. Try a different item or use OpenAI for broader coverage.")
            else:
                # Local DB fallback
                key = food.strip().lower()
                if key in food_db:
                    info = food_db[key]
                    st.success(f"{food.title()}: {info['calories']} kcal, {info['protein']} g protein")

                    with open("food_history.txt", "a") as f:
                        time = datetime.now().strftime("%Y-%m-%d %H:%M")
                        f.write(f"{time} - {food} (local)\n")
                else:
                    st.info("No data in local DB for that food. Consider adding an OPENAI_API_KEY for broader coverage.")