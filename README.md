# 🌱 Project-C12: Carbon-Aware Model Router

Project-C12 is an intelligent system that helps select the most carbon-efficient AI models based on real-time carbon intensity data. It provides a dashboard for monitoring and optimizing model selection to minimize carbon emissions.

[📚 Read our detailed introduction](docs/INTRODUCTION.md) | [🗺️ View the project roadmap](docs/MASTERPLAN.md)

## ✨ Features

- 🔄 Real-time carbon intensity monitoring
- 🤖 Smart model selection (TinyLlama, CodeLlama, GPT-2)
- 📊 Performance metrics visualization
- 💡 Optimization recommendations
- 🌍 Carbon footprint tracking
- 💻 Code-aware query routing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-c12.git
cd project-c12
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dashboard.txt
```

3. Run the dashboard:
```bash
streamlit run src/dashboard/app.py
```

## 📁 Project Structure

```
project-c12/
├── data/
│   └── metrics.db         # Centralized metrics database
├── docs/
│   ├── README.md         # Documentation index
│   ├── INTRODUCTION.md   # Detailed project overview
│   └── MASTERPLAN.md     # Project roadmap
├── monitoring/
│   └── prometheus.yml    # Prometheus configuration
├── src/
│   ├── api/             # FastAPI backend
│   │   ├── main.py      # API endpoints
│   │   ├── models/      # AI model files
│   │   ├── routes/      # API route handlers
│   │   ├── schemas/     # Data models
│   │   └── services/    # Core services
│   └── dashboard/       # Streamlit frontend
│       ├── app.py       # Dashboard UI
│       └── data/        # Symlinked to /data
├── tests/               # Test suite
├── Dockerfile.api       # API service Dockerfile
├── Dockerfile.dashboard # Dashboard service Dockerfile
├── docker-compose.yml   # Service orchestration
├── requirements.txt     # API dependencies
└── README.md           # This file
```

## 🐳 Docker Deployment

The project includes a complete Docker setup for all services:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services will be available at:
- Dashboard: http://localhost:8501
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## 🤝 Contributing

Contributions are welcome! Please read our [detailed introduction](docs/INTRODUCTION.md) to understand the project better.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 