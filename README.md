# NeuralGuard — AI-Powered Autonomous Security System

> Multi-agent security intelligence platform that monitors video streams,
> processes IoT sensor data, and uses AI agents + Google Gemini
> to detect threats and generate intelligent alerts.

## Architecture

```
Camera → FastAPI → Frame Queue → YOLO → 7 AI Agents → Gemini → Decision → Alert → Dashboard
```

### Agent Pipeline

| # | Agent         | Role                                     |
|---|---------------|------------------------------------------|
| 1 | Vision Agent  | YOLO object detection, people counting    |
| 2 | Sensor Agent  | IoT environmental data (temp, smoke, noise) |
| 3 | Behavior Agent| Anomaly detection via temporal patterns    |
| 4 | Memory Agent  | Short-term event buffer (5 min window)     |
| 5 | Fusion Agent  | Gemini API integration — holistic reasoning |
| 6 | Decision Agent| Threat → action mapping with cooldown      |
| 7 | Response Agent| Alert message generation                   |

## Tech Stack

| Layer    | Technology                                |
|----------|-------------------------------------------|
| Backend  | Python 3.11+, FastAPI, WebSocket          |
| AI/ML    | YOLOv8 (optional), Google Gemini API      |
| Frontend | React 19, Vite 6, Tailwind CSS 3, Recharts |
| Transport| REST API + WebSocket (real-time)          |

## Quick Start

### 1. Clone & Setup

```bash
cd NeuralGuard

# Create Python virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Start Backend

```bash
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.
Swagger docs at `http://localhost:8000/docs`.

### 4. Start Frontend

```bash
cd dashboard
npm install
npm run dev
```

Dashboard will open at `http://localhost:3000`.

## API Endpoints

| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| GET    | `/`             | Health check             |
| GET    | `/health`       | Health status            |
| GET    | `/api/status`   | System status + agents   |
| GET    | `/api/alerts`   | Alert history            |
| GET    | `/api/latest`   | Latest pipeline event    |
| GET    | `/api/stream`   | Video stream info        |
| GET    | `/api/memory`   | Memory agent summary     |
| WS     | `/ws/dashboard` | Real-time event stream   |

## Project Structure

```
NeuralGuard/
├── server/
│   ├── agents/
│   │   ├── vision_agent.py      # YOLO detection + mock
│   │   ├── sensor_agent.py      # IoT simulation
│   │   ├── behavior_agent.py    # Anomaly detection
│   │   ├── memory_agent.py      # Event buffer
│   │   ├── fusion_agent.py      # Gemini API integration
│   │   ├── decision_agent.py    # Action mapping
│   │   └── response_agent.py    # Alert generation
│   ├── models/
│   │   └── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   └── api.py               # REST endpoints
│   ├── services/
│   │   ├── video_processor.py   # Frame ingestion
│   │   └── frame_queue.py       # Async queue
│   ├── utils/
│   │   └── helpers.py           # Utilities
│   ├── pipeline.py              # Agent orchestrator
│   └── main.py                  # FastAPI app
├── dashboard/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── LiveVideoPanel.jsx
│   │   │   ├── AlertsPanel.jsx
│   │   │   ├── StatusCards.jsx
│   │   │   └── TimelineChart.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── lib/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tailwind.config.js
│   └── vite.config.js
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Gemini Integration

The Fusion Agent calls Gemini to reason about threats. If `GEMINI_API_KEY`
is not set, it automatically falls back to a rule-based scoring system.

## Mock Mode

The system runs fully in **mock mode** by default — no camera or sensors
needed. Vision and sensor agents generate realistic synthetic data so you
can see the full pipeline in action.

## License

MIT
