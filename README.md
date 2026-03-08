# AI Krishi Saathi

An industry-level, modular, scalable AI-powered agriculture decision support system. 
Designed with an offline-first Flutter mobile application, an asynchronous FastAPI backend, and standalone decoupled Machine Learning microservices.

## 📂 Project Structure

- **`backend/`**: FastAPI main application (REST APIs, Auth, App Logic).
- **`mobile_app/`**: Flutter cross-platform mobile app (Android focus, offline-first SQLite synchronization).
- **`ml_pipeline/`**: Standalone ML training, model deployment, and inference wrappers.
- **`data_pipeline/`**: Scheduled ingestion of external data (Weather, market prices).
- **`admin_dashboard/`**: Next.js & React-based web app for system administration and insights.
- **`deployment/`**: DevOps configurations, including Docker Compose, Kubernetes manifests, and Terraform scripts.

## 🚀 Quick Start (Development)

This repository uses a comprehensive `Makefile` for developer ergonomics and standard Git workflows.

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Flutter SDK
- Node.js (for Admin Dashboard)

### Workspace Initialization

1. Configure pre-commit hooks:
   ```bash
   make setup-hooks
   ```
2. Copy the environment configuration:
   ```bash
   cp backend/.env.example backend/.env
   # Update the values inside backend/.env as required
   ```

3. Start local backend infrastructure via Docker Compose:
   ```bash
   make up-build
   ```

4. View running services:
   ```bash
   make logs
   ```
