# 📰 Daily Scoop

Daily Scoop is a modern news aggregation API that collects and serves news articles from multiple news providers in one unified platform.

The project fetches news from different external APIs, processes the results, and exposes clean endpoints for clients to consume.

---

# ✨ Features

- Aggregates news from multiple sources
- Built with FastAPI
- Asynchronous requests using `httpx` and `asyncio`
- RESTful API structure
- Error handling for failed providers
- Modular and scalable architecture
- Environment variable support with `.env`
- Easy to extend with additional news providers

---

# 🛠️ Tech Stack

- Python
- FastAPI
- HTTPX
- AsyncIO
- Uvicorn
- Pydantic

---

# 📂 Project Structure

```bash
daily_scoop/
│
├── routers/              # API route handlers
├── services/             # External API service logic
├── Exceptions/           # Custom exception classes
├── utils/                # Helper utilities
├── models/               # Pydantic models
├── main.py               # FastAPI application entry point
├── requirements.txt
└── README.md
```

# 📖 API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```bash
http://127.0.0.1:8000/docs
```

ReDoc:

```bash
http://127.0.0.1:8000/redoc
```

---

# 🔄 How It Works

1. A client sends a request to the API.
2. The application concurrently fetches news from multiple providers.
3. Responses are validated and normalized.
4.
5. A clean aggregated response is returned to the client.

---

---

# 👨‍💻 Author

Daniel Mabia

GitHub: https://github.com/princedan-123
