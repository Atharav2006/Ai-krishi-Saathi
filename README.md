# AI Krishi Saathi

An industry-level, modular, scalable AI-powered agriculture decision support system. 
Designed with an offline-first Flutter mobile application, an asynchronous FastAPI backend, and standalone decoupled Machine Learning microservices.

## 📖 Full Working Explanation

AI Krishi Saathi is designed to assist farmers by providing crop disease detection, market price forecasts, and overall crop recommendations.

### Architecture Overview
1.  **Offline-First Mobile App (Flutter)**: The core user interface. It bundles a highly efficient, custom-trained CNN model (TFLite format) locally. This allows the app to perform critical tasks—like crop disease detection from photos—completely offline. Data is cached locally using SQLite (`sqflite`) and gracefully synchronizes with the backend when an internet connection is available.
2.  **Robust Backend (FastAPI)**: Serves as the central nervous system. It handles user authentication (JWT), secure data storage (PostgreSQL for production, SQLite for local dev), and complex background tasks, such as fetching real-time market prices (`Agmarknet/Mandi Prices`) via `APScheduler`.
3.  **Machine Learning Operations**: The ML pipeline is decoupled. Models are trained on Kaggle using a 2.8GB PlantVillage dataset (detecting 38+ crop disease classes). The generated models are exported as `.tflite` for the mobile edge devices and `.onnx` for high-performance cloud inference.

## 📂 Project Structure

- **`backend/`**: FastAPI main application (REST APIs, Auth, App Logic).
- **`mobile_app/`**: Flutter cross-platform mobile app (Android focus, offline-first SQLite synchronization).
- **`ml_pipeline/`**: Standalone ML training, model deployment, and inference wrappers.
- **`data_pipeline/`**: Scheduled ingestion of external data (Weather, market prices).
- **`admin_dashboard/`**: Next.js & React-based web app for system administration and insights.
- **`deployment/`**: DevOps configurations, including Docker Compose, Kubernetes manifests, and Terraform scripts.

---

## 🚀 How To Run the Project Locally

To run the project locally without `Docker` or the `Makefile`, follow the steps below for both the **Backend API** and the **Flutter Mobile App**.

### Prerequisites
- **Git**
- **Backend:** Python 3.11+
- **Mobile App:** Flutter SDK (>= 3.0), Android Studio (for emulator/ADB tools)

---

### 1. Running the FastAPI Backend

The backend provides the API for user auth, data synchronization, and server-side ML tasks.

**Step 1: Navigate to the backend directory**
```bash
cd backend
```

**Step 2: Create and activate a virtual environment**
- **Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux/macOS:**
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

**Step 3: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Environment Variables**
Copy the example environment file and update it if necessary.
```bash
cp .env.example .env
```
*(By default, it will use a local SQLite database `krishi_saathi.db` for easy development).*

**Step 5: Run the Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API Swagger documentation will now be available at: http://localhost:8000/docs

---

### 2. Running the Flutter Mobile App

The mobile application is the primary interface for users.

**Step 1: Navigate to the mobile app directory**
*(Assuming you are at the project root)*
```bash
cd mobile_app
```

**Step 2: Install Flutter dependencies**
```bash
flutter pub get
```

**Step 3: Connect a device**
Launch an Android Emulator via Android Studio, or connect a physical Android device via USB debugging. Verify the device is targeted by running:
```bash
flutter devices
```

**Step 4: Configure the API Base URL**
By default, the Mobile App relies on the backend running at `localhost:8000`. 
- If you are running an **Android Emulator**, change the localhost reference in your Flutter code to `10.0.2.2:8000`.
- If you are running on a **Physical Device**, find your laptop's local IP address (e.g., `192.168.1.5`) and update the backend URL in the Flutter code to point to `http://<YOUR_LAPTOP_IP>:8000`, making sure your laptop and phone are on the exact same Wi-Fi network.

**Step 5: Run the App**
```bash
flutter run
```

---

## 🐳 Quick Start (Docker & Makefile)

If you prefer using Docker:

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
