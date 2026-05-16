# Jewellery ERP — Local Setup Guide

This guide covers three ways to run the project locally.

---

## What to Install on Your Machine

Install the tools for the path you want to follow.

### 1. Git *(required for all options)*
Download and install from https://git-scm.com/downloads

Verify:
```bash
git --version
```

---

### 2. A Modern Browser *(Option A only)*
Any of these work — no install needed if already present:
- Google Chrome / Chromium
- Mozilla Firefox
- Microsoft Edge
- Safari (macOS)

---

### 3. Docker Desktop *(Option B & C — recommended)*
The easiest way to run the backend without manually installing PostgreSQL, Redis, or Python.

| OS | Download |
|---|---|
| macOS | https://docs.docker.com/desktop/install/mac-install |
| Windows | https://docs.docker.com/desktop/install/windows-install |
| Linux | https://docs.docker.com/desktop/install/linux-install |

Verify after install:
```bash
docker --version
docker compose version
```

> **Windows users**: Enable WSL 2 backend in Docker Desktop settings for best performance.

---

### 4. Python 3.10+ *(only if NOT using Docker)*
Required only if you want to run the backend without Docker.

| OS | Install |
|---|---|
| macOS | `brew install python@3.12` or https://python.org/downloads |
| Windows | https://python.org/downloads — check "Add to PATH" during install |
| Linux | `sudo apt install python3.12 python3.12-venv python3-pip` |

Verify:
```bash
python3 --version
pip3 --version
```

---

### 5. PostgreSQL 14+ *(only if NOT using Docker)*

| OS | Install |
|---|---|
| macOS | `brew install postgresql@16` then `brew services start postgresql@16` |
| Windows | https://www.postgresql.org/download/windows (use the installer) |
| Linux | `sudo apt install postgresql postgresql-contrib` |

Verify:
```bash
psql --version
```

---

### 6. Redis 7+ *(only if NOT using Docker)*

| OS | Install |
|---|---|
| macOS | `brew install redis` then `brew services start redis` |
| Windows | Use WSL2 + Linux instructions, or https://github.com/microsoftarchive/redis/releases |
| Linux | `sudo apt install redis-server` |

Verify:
```bash
redis-cli ping   # should return PONG
```

---

### 7. Flutter SDK 3.19+ *(Option C — mobile app only)*

1. Download from https://docs.flutter.dev/get-started/install (choose your OS)
2. Extract and add `flutter/bin` to your PATH
3. Run the Flutter doctor to check setup:
   ```bash
   flutter doctor
   ```
4. Install any missing items it reports (Android Studio, Xcode, etc.)

Verify:
```bash
flutter --version
dart --version
```

#### For Android development (Flutter):
- Install **Android Studio** from https://developer.android.com/studio
- Open Android Studio → SDK Manager → install Android SDK 33+
- Create a virtual device (AVD) via Device Manager

#### For iOS development (Flutter — macOS only):
- Install **Xcode** from the Mac App Store
- Run: `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`
- Install CocoaPods: `sudo gem install cocoapods`

---

### Quick Install Summary

| You want to... | Install |
|---|---|
| Just preview the UI | Nothing — open `ui_interactive.html` in browser |
| Run backend with Docker | Git + Docker Desktop |
| Run backend without Docker | Git + Python 3.10+ + PostgreSQL 14+ + Redis 7+ |
| Run mobile app too | Everything above + Flutter SDK + Android Studio / Xcode |

---

| Option | What runs | Best for |
|---|---|---|
| **A. Prototype only** | `ui_interactive.html` in browser | Quickest — no install needed |
| **B. Backend + DB (Docker)** | FastAPI + PostgreSQL + Redis | Backend/API development |
| **C. Full stack** | Backend + Mobile app (Flutter) | End-to-end development |

---

## Option A — Interactive Prototype (No Install)

The entire UI is a single self-contained HTML file.

1. Clone the repo:
   ```bash
   git clone https://github.com/souradipghosh882/JewelleryERP.git
   cd JewelleryERP
   ```

2. Open the file in any browser:
   ```bash
   # macOS
   open ui_interactive.html

   # Windows
   start ui_interactive.html

   # Linux
   xdg-open ui_interactive.html
   ```

3. Login with:
   - **Phone**: any number (e.g. `9876543210`)
   - **Password**: `demo`
   - **Role**: choose Owner / Manager / Salesman / Tagger / Accountant

No server, no database, no dependencies needed.

---

## Option B — Backend + Database (Docker)

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Git | any | https://git-scm.com |
| Docker | 24+ | https://docs.docker.com/get-docker |
| Docker Compose | v2+ | Included with Docker Desktop |

### Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/souradipghosh882/JewelleryERP.git
   cd JewelleryERP
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   If `.env.example` does not exist, create `.env` manually:
   ```env
   SECRET_KEY=change-me-to-a-random-32-char-string
   DEBUG=true
   ```

3. **Start all services**
   ```bash
   docker compose up --build
   ```
   This starts:
   - PostgreSQL on port `5432` (databases: `shared_db`, `pakka_db`, `kacha_db`)
   - Redis on port `6379`
   - FastAPI backend on port `8000`

4. **Run database migrations**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

5. **Verify it's running**
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

6. **Stop services**
   ```bash
   docker compose down
   ```
   To also delete the database volume:
   ```bash
   docker compose down -v
   ```

---

## Option C — Full Stack (Backend + Flutter Mobile App)

### Additional Prerequisites (beyond Option B)

| Tool | Version | Install |
|---|---|---|
| Flutter SDK | 3.19+ | https://docs.flutter.dev/get-started/install |
| Dart | 3.3+ | Included with Flutter |
| Android Studio **or** Xcode | latest | For emulator/simulator |

### Steps

1. Complete **Option B** steps 1–4 (backend must be running).

2. **Install Flutter dependencies**
   ```bash
   cd mobile_app
   flutter pub get
   ```

3. **Set the backend URL**

   Open `mobile_app/lib/core/api_client.dart` and update the base URL:
   ```dart
   // For Android emulator
   static const String baseUrl = 'http://10.0.2.2:8000';

   // For iOS simulator or physical device on same network
   static const String baseUrl = 'http://localhost:8000';

   // For physical device (replace with your machine's local IP)
   static const String baseUrl = 'http://192.168.x.x:8000';
   ```

4. **Run the app**

   Check available devices:
   ```bash
   flutter devices
   ```

   Run on a specific device:
   ```bash
   # Android emulator
   flutter run -d emulator-5554

   # iOS simulator
   flutter run -d "iPhone 15"

   # Chrome (web)
   flutter run -d chrome
   ```

---

## Manual Backend Setup (without Docker)

If you prefer not to use Docker:

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 7+

### Steps

1. **Create and activate a virtual environment**
   ```bash
   cd backend
   python -m venv venv

   # macOS / Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create PostgreSQL databases**
   ```sql
   CREATE DATABASE shared_db;
   CREATE DATABASE pakka_db;
   CREATE DATABASE kacha_db;
   CREATE USER erp_user WITH PASSWORD 'erp_password';
   GRANT ALL PRIVILEGES ON DATABASE shared_db TO erp_user;
   GRANT ALL PRIVILEGES ON DATABASE pakka_db TO erp_user;
   GRANT ALL PRIVILEGES ON DATABASE kacha_db TO erp_user;
   ```

4. **Set environment variables**

   Create `backend/.env`:
   ```env
   SHARED_DATABASE_URL=postgresql://erp_user:erp_password@localhost:5432/shared_db
   PAKKA_DATABASE_URL=postgresql://erp_user:erp_password@localhost:5432/pakka_db
   KACHA_DATABASE_URL=postgresql://erp_user:erp_password@localhost:5432/kacha_db
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=change-me-to-a-random-32-char-string
   DEBUG=true
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Running Tests

```bash
# With Docker
docker compose exec backend pytest

# Without Docker (from backend/ with venv active)
pytest
```

---

## Project Structure

```
JewelleryERP/
├── ui_interactive.html     # Standalone UI prototype (no server needed)
├── docker-compose.yml      # Docker setup for all services
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── api/            # Route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── core/           # Config, security
│   ├── alembic/            # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── mobile_app/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── features/       # Screens by feature
│   │   └── core/           # API client, theme
│   └── pubspec.yaml
└── infrastructure/
    └── postgres/           # DB init scripts
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `port 5432 already in use` | Stop local PostgreSQL: `sudo service postgresql stop` or change port in `docker-compose.yml` |
| `port 8000 already in use` | Change to `"8001:8000"` in `docker-compose.yml` |
| Docker build fails | Run `docker compose build --no-cache` |
| Flutter `pub get` fails | Run `flutter doctor` and fix any reported issues |
| Android emulator can't reach backend | Use `10.0.2.2` instead of `localhost` |
| iOS simulator can't reach backend | Ensure backend listens on `0.0.0.0`, not `127.0.0.1` |

---

## Default Credentials (Prototype)

| Role | Phone | Password |
|---|---|---|
| Owner | any | `demo` |
| Manager | any | `demo` |
| Salesman | any | `demo` |
| Tagger | any | `demo` |
| Accountant | any | `demo` |
