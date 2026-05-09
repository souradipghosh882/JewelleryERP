# Jewellery ERP System

A comprehensive ERP system for jewellery shops with inventory management, billing, tagging, schemes, and analytics.

## Features

### MVP Features (Priority 1)
1. **Inventory Management** - Track all ornaments with complete details
2. **Dual Billing System**
   - Pakka Bill (with GST, legal)
   - Kacha Bill (no GST, internal)
3. **Smart Tagging** - QR/Barcode based ornament tracking
4. **Scheme Management** - Money & Gold deposit schemes
5. **Rokar Management** - Complete cash flow tracking
6. **Analytics Dashboard** - Comprehensive business insights

### Additional Features
- Staff Attendance (QR-based entry/exit)
- CRM System
- Vendor Purchase Management
- Karigar Management
- Bank Ledger Sync
- Old Gold Exchange
- Metal Rate Management (twice daily)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT

### Frontend
- **Framework**: Flutter
- **Platforms**: Mobile, Tablet, Desktop
- **State Management**: Riverpod
- **Barcode**: mobile_scanner

### Deployment
- **Local**: Docker + Docker Compose
- **Cloud**: AWS (ECS + RDS + S3)

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Docker & Docker Compose
- Flutter 3.0+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
uvicorn app.main:app --reload
```

### With Docker
```bash
docker-compose up -d
```

### Flutter App Setup
```bash
cd mobile_app
flutter pub get
flutter run
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## User Roles
| Role | Billing | Inventory | Analytics | Staff | Rates |
|------|---------|-----------|-----------|-------|-------|
| Owner | ✅ | ✅ | ✅ Full | ✅ | ✅ |
| Manager | ✅ | ✅ | ✅ Partial | ✅ | ❌ |
| Salesman | ✅ Create | ❌ | ❌ | ❌ | ❌ |
| Accountant | ❌ | ❌ | ✅ Full | ❌ | ❌ |
| Tagger | ❌ | ✅ Tag | ❌ | ❌ | ❌ |

## License
Proprietary - All rights reserved
