# 📚 Project-C12 Documentation

Welcome to the Project-C12 documentation! This directory contains detailed information about the project's architecture, implementation, and usage.

## 📑 Core Documents

1. [Introduction](INTRODUCTION.md)
   - Problem Statement
   - Solution Overview
   - Real-World Examples
   - Core Components
   - Benefits
   - Usage Examples

2. [Project Plan](MASTERPLAN.md)
   - Project Overview
   - Core Objectives
   - Architecture Components
   - Implementation Phases
   - Progress Tracking

3. [Development Challenges](CHALLENGES.md)
   - Model Management
   - Performance & Scaling
   - System Integration
   - Carbon Awareness
   - Development & Deployment
   - Future Challenges
   - Lessons Learned

## 🔍 Quick Links

- [Back to Main README](../README.md)
- [View Introduction](INTRODUCTION.md)
- [View Project Plan](MASTERPLAN.md)

## 📖 Document Structure

```
docs/
├── README.md          # This file (Documentation Index)
├── INTRODUCTION.md    # Detailed project overview
├── MASTERPLAN.md      # Project roadmap and phases
└── CHALLENGES.md      # Development challenges & solutions
```

## 📚 Project Components

### Core Components
1. **API Service** (`/src/api/`)
   - FastAPI backend for model selection and routing
   - Integrates with AI models (TinyLlama, CodeLlama)
   - Exposes metrics for Prometheus

2. **Dashboard** (`/src/dashboard/`)
   - Streamlit-based monitoring interface
   - Real-time carbon intensity tracking
   - Model performance visualization

3. **Monitoring** (`/monitoring/`)
   - Prometheus metrics collection
   - Grafana dashboards for visualization

### Data Management
- Centralized metrics database in `/data/metrics.db`
- Symlinked in dashboard for unified data access

### Docker Infrastructure
- `Dockerfile.api`: API service container
- `Dockerfile.dashboard`: Dashboard container
- `docker-compose.yml`: Service orchestration
  - API service
  - Dashboard
  - Prometheus
  - Grafana

## 🔄 Latest Updates

The documentation is regularly updated to reflect:
- New features and improvements
- Best practices and usage guidelines
- Real-world examples and use cases
- Performance optimizations
