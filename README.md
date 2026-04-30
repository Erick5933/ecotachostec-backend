# EcoTachosTec — Backend

> AI-powered smart waste classification system. An IoT platform that uses computer vision (YOLOv8) to automatically classify waste in real time and physically direct it to the correct container via ESP32-controlled servomotors. 

---

## What it does

EcoTachosTec is a full IoT + AI system built for institutional environments (schools, universities). A camera captures an image of waste, the backend classifies it using a YOLOv8 model (organic, inorganic, recyclable), and sends motor commands to an ESP32 microcontroller that physically sorts the waste into the right bin — all in under 3 seconds end-to-end.

This repo contains the Django REST Framework backend, including the AI inference service, IoT communication layer, real-time WebSocket updates, and REST API.

---

## Tech stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL (Docker) |
| AI Model | YOLOv8 (Ultralytics) — custom trained |
| Real-time | Django Channels + WebSockets |
| Async tasks | Celery + Redis |
| IoT protocol | HTTP REST + WebSockets (ESP32 communication) |
| Auth | JWT (SimpleJWT) |
| Infrastructure | Docker + docker-compose |
| Cloud (training) | Google Cloud Platform — NVIDIA Tesla V100 |
| Containerization | Docker multi-stage builds, Gunicorn, Nginx |

---

## System architecture

```
[Camera / Mobile App]
        │
        ▼
[Django REST API] ──── [PostgreSQL]
        │                    │
        ├── [YOLOv8 Inference Service]
        │         └── classifies: organic / inorganic / recyclable
        │
        ├── [Django Channels / WebSocket]
        │         └── real-time dashboard updates
        │
        ├── [Celery + Redis]
        │         └── async exports, model upload processing
        │
        └── [IoT Command Endpoint]
                  └── HTTP → ESP32 (servomotor control)
```

---

## Database schema (key models)

- `core_usuario` — users with role-based access (admin, supervisor, operator)
- `core_tacho` — smart waste bins with GPS coordinates, firmware version, fill level
- `core_deteccion` — every AI classification event: category, confidence score, image, timestamp, device reference
- `core_canton` / `core_provincia` — geographic hierarchy for institutional mapping

---

## AI model

- **Architecture:** YOLOv8 (Ultralytics 8.0.43), fine-tuned on custom dataset
- **Dataset:** 15,247 labeled images across 3 classes (organic, inorganic, recyclable)
- **Training:** Google Cloud GPU (NVIDIA Tesla V100), 200 epochs, batch size 16
- **mAP50:** 87.3% overall — 91.2% organic / 85.7% inorganic / 85.0% recyclable
- **Inference time:** ~180ms on CPU (Intel i7), ~45ms on GPU
- **End-to-end classification:** 1.1 seconds (including preprocessing)
- **Model format:** FP16 (87MB), INT8 quantized version for edge deployment

---

## Key API endpoints

```
POST   /api/usuarios/auth/login/          # JWT login
POST   /api/usuarios/auth/register/       # User registration
GET    /api/tachos/                        # List smart bins
POST   /api/tachos/                        # Register new device
GET    /api/detecciones/                   # Detection history (filterable)
POST   /api/detecciones/                   # Create detection record
POST   /api/predict/                       # Run AI classification on image
POST   /api/iot/command/                   # Send motor command to ESP32
POST   /api/models/upload/                 # Upload new trained model
```

---

## IoT integration

The backend communicates with ESP32 microcontrollers via HTTP REST:

- `POST /api/iot/command/` — sends motor position commands (0–180° per servo)
- Supports predefined sequences for classify → transport → drop mechanisms
- Each command generates a transaction ticket for full execution traceability
- OTA firmware update support for remote deployment

**ESP32 hardware used:** ESP32 38-pin dual-core (240MHz), Driver A4988, NEMA 17 stepper motor, 2× precision metal servomotors (15 kg/cm)

---

## Getting started

### Prerequisites
- Docker and docker-compose
- Python 3.11+

### Run locally

```bash
git clone https://github.com/Erick5933/ecotachostec-backend
cd ecotachostec-backend

# Copy environment variables
cp .env.example .env

# Start all services (Django + PostgreSQL + Redis + Celery)
docker-compose up --build

# Apply migrations (first time)
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

The API will be available at `http://localhost:8000/api/`

### Environment variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@db:5432/ecotachostec
REDIS_URL=redis://redis:6379/0
AI_WEIGHTS=path/to/model.pt
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase.json
```

---

## Project structure

```
src/
├── core/           # Main app: users, devices, detections, locations
│   ├── models/     # Django ORM models
│   ├── views/      # DRF viewsets and API views
│   ├── serializers/
│   └── iot_views.py  # ESP32 command endpoints
├── ml_inference/   # YOLOv8 inference service (Singleton pattern)
docker/
├── Dockerfile      # Multi-stage Python build
├── docker-compose.yml
.github/workflows/  # CI/CD pipeline
```

---

## Performance

- API response time < 200ms for critical operations
- Handles 1,000+ concurrent detection records
- End-to-end: image upload → AI classification → motor command → confirmation = **2.8 seconds**
- Tested with 100 concurrent users via Apache JMeter

---

## Related repositories

- [ecotachostec-frontend](https://github.com/Erick5933/ecotachostec-frontend) — React + Vite web dashboard
- [ecotachostec-mobile](https://github.com/Erick5933/ecotachostec-mobile) — React Native mobile app (Expo)

---

## Authors

Built by Erick Chacón & Edwin Choez, Ecuador (2025–2026)
