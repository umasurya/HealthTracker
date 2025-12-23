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

import json

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

# Load persisted custom foods (foods.json) if present and merge
FOODS_FILE = "foods.json"
if os.path.exists(FOODS_FILE):
    try:
        with open(FOODS_FILE, "r", encoding="utf-8") as jf:
            custom = json.load(jf)
            if isinstance(custom, dict):
                # normalize keys
                for k, v in custom.items():
                    food_db[k.lower()] = v
    except Exception:
        pass

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
                # Log the error and attempt graceful fallbacks
                msg = str(e)
                time = datetime.now().strftime("%Y-%m-%d %H:%M")
                with open("openai_errors.log", "a") as log:
                    log.write(f"{time} - OpenAI error: {msg}\n")

                st.warning("OpenAI error occurred — attempting alternative providers and local DB.")

                # First try OpenFoodFacts when available
                try:
                    from providers.openfoodfacts import search_openfoodfacts
                    off = search_openfoodfacts(food)
                    if off:
                        cal = off.get('calories')
                        prot = off.get('protein')
                        note = off.get('note') or ''
                        parts = []
                        if cal is not None:
                            parts.append(f"{cal} kcal")
                        if prot is not None:
                            parts.append(f"{prot} g protein")
                        st.success(f"{food.title()}: {', '.join(parts)} ({note})")

                        with open("food_history.txt", "a") as f:
                            f.write(f"{time} - {food} (openfoodfacts fallback)\n")
                        # done
                        continue
                except Exception:
                    pass

                # Next try local DB
                key = food.strip().lower()
                if key in food_db:
                    info = food_db[key]
                    st.success(f"{food.title()}: {info['calories']} kcal, {info['protein']} g protein")
                    with open("food_history.txt", "a") as f:
                        f.write(f"{time} - {food} (local fallback)\n")
                else:
                    st.info("No data available via alternative providers or local DB. You can add this food below.")
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

# Add UI for adding custom foods
st.write("---")
with st.expander("Add custom food to local database"):
    new_name = st.text_input("Food name (e.g. avocado)")
    new_cal = st.number_input("Calories (kcal per 100g)", min_value=0.0, value=100.0, format="%.1f")
    new_prot = st.number_input("Protein (g per 100g)", min_value=0.0, value=1.0, format="%.1f")
    if st.button("Add food"):
        if not new_name:
            st.warning("Enter a food name")
        else:
            key = new_name.strip().lower()
            food_db[key] = {"calories": float(new_cal), "protein": float(new_prot)}
            # persist to foods.json
            try:
                existing = {}
                if os.path.exists(FOODS_FILE):
                    with open(FOODS_FILE, "r", encoding="utf-8") as jf:
                        existing = json.load(jf) or {}
                existing[key] = food_db[key]
                with open(FOODS_FILE, "w", encoding="utf-8") as jf:
                    json.dump(existing, jf, indent=2)
                st.success(f"Added {new_name} to local foods")
            except Exception as ex:
                st.error(f"Could not save food: {ex}")