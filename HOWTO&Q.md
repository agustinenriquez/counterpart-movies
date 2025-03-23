# 🎬 Movie Explorer
**by Agustin Enriquez**

---

## 🚀 How to Run

1. Start the services using Docker Compose:

   ```bash
   docker compose up -d
   # or
   docker compose up



## 🌐 Accessing the App

    Frontend: http://localhost:5173

    Backend (Django API): http://127.0.0.1:8000

    Redis: running on port 6379


## ✅ Testing (optional)

docker compose exec web sh
pytest



## 🕒 Approximate Steps & Time Breakdown

This project was completed in **~5 hours**.

1. **🛠 Project Setup** – _15~20 minutes_
   - Initialized backend and frontend structure
   - Configured environment and dependencies

2. **🧱 Model & API Design** – _50~60 minutes_
   - Created Django models for movies, principals, and names
   - Implemented DRF viewsets and serializers

3. **🎨 Frontend Integration** – _1~2 hours_
   - Developed React components using TypeScript
   - Connected to backend API
   - Implemented pagination, sorting, and movie details

4. **🐳 Dockerization & Redis Setup** – _~30 minutes_
   - Added Dockerfile and docker-compose
   - Integrated Redis caching with Django

5. **✅ Testing & Tooling** – _~20 minutes_
   - Added Pytest tests for models and views
   - Configured Pre-commit hooks (Ruff, MyPy, etc.)

6. **🌓 UI Polish & Dark Mode** – _~25 minutes_
   - Added Tailwind styling
   - Implemented light/dark theme toggle
   - Improved accessibility and responsive layout

7. **🧹 Final Cleanup & Documentation** – _~15 minutes_
   - Wrote setup instructions
   - Cleaned code and verified all flows
   - Ensured Docker setup runs smoothly


## Questions:

1. This project balances backend, frontend, and performance trade-offs. In your day-to-day work, how is ownership divided across full stack responsibilities?

2. Do you lean toward pixel-perfect frontends or prioritize functionality and speed of delivery when building internal tools?

3. Is this challenge designed to resemble a real-life project you’ve worked on, or is it more of a proxy to assess fundamentals?

4. The import.py script simulates a data ingestion pipeline. Is this challenge designed to mirror any real-world ingestion or cleaning work your team does with third-party data?"

5. Is the goal of the search endpoint to be fuzzy and user-friendly, or more exact and structured? For example, should 'Moan' return 'Moana'?
