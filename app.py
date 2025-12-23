import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI Nutrition Helper")

food = st.text_input("What did you eat?")

if st.button("Get nutrition"):
    if food:
        prompt = f"""
        Calculate calories and protein.
        Consider quantities carefully.
        Explain in very simple words.
        Food: {food}
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
       )

        st.success(response.choices[0].message.content)
    else:
        st.warning("Please type what you ate.")