# HealthTracker (AI Nutrition Helper)

A small Streamlit app that gives calories and protein for foods. It prefers the OpenAI API when `OPENAI_API_KEY` is set, otherwise it falls back to a local `food_db` for basic values.

## Quick start (Windows)

1. Create and activate a virtual environment:
   - python -m venv .venv
   - .venv\Scripts\activate
2. Install dependencies:
   - pip install -r requirements.txt
3. Copy `.env.example` to `.env` and add your OpenAI API key if you want AI responses:
   - COPY .env.example .env
   - edit `.env` and set `OPENAI_API_KEY`
4. Run the app:
   - streamlit run app.py --server.port 8501
5. Open your browser at http://127.0.0.1:8501

## Notes
- If you don't provide `OPENAI_API_KEY`, the app will use a small local `food_db` for basic nutrition info.
- The app stores a simple `food_history.txt` file in the project folder when you query foods.

## Security
- If you created a Personal Access Token earlier to push code, revoke it now (https://github.com/settings/tokens).