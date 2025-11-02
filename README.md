# 💰 NeoFinance - AI-Powered Personal Finance Dashboard

A modern, full-stack personal finance management application with AI-powered financial insights, built with FastAPI, React, and Google Gemini AI.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://neo-finance-prod.vercel.app)
[![Backend API](https://img.shields.io/badge/API-docs-blue)](https://neofinance-prod.onrender.com/docs)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🚀 Live Demo

**Production Application:**
- **Frontend:** [https://neo-finance-prod.vercel.app](https://neo-finance-prod.vercel.app)
- **Backend API:** [https://neofinance-prod.onrender.com](https://neofinance-prod.onrender.com)
- **API Documentation:** [https://neofinance-prod.onrender.com/docs](https://neofinance-prod.onrender.com/docs)

> **Note:** Backend uses free tier hosting and may take ~30 seconds to wake up on first request after 15 minutes of inactivity.

---

## ✨ Features

### Core Features
- 🔐 **User Authentication** - Secure JWT-based authentication with password hashing
- 💸 **Transaction Management** - Full CRUD operations for income and expenses
- 📊 **Dashboard Analytics** - Real-time financial summaries and insights
- 🏷️ **Category Tracking** - Organize transactions by customizable categories
- 📈 **Trend Analysis** - Visual representation of spending patterns over time
- 🤖 **AI Financial Coach** - Powered by Google Gemini AI for personalized advice

### Technical Features
- 🎨 **Modern UI** - Built with shadcn/ui components and TailwindCSS
- 🌓 **Dark Mode** - Toggle between light and dark themes
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- 🔄 **Real-time Updates** - Instant feedback on all operations
- 🔒 **Secure API** - Protected endpoints with token-based authentication
- 📝 **API Documentation** - Interactive Swagger UI and ReDoc

---

## 🏗️ Architecture

NeoFinance follows a modern microservices architecture with complete separation of concerns:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  React Frontend │─────▶│  FastAPI Backend│─────▶│   PostgreSQL    │
│   (Vercel)      │      │    (Render)     │      │   (Supabase)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                 │
                                 │
                                 ▼
                         ┌─────────────────┐
                         │   Gemini AI     │
                         │  (Google AI)    │
                         └─────────────────┘
```

**Components:**
- **Frontend (Vercel):** React SPA with CDN distribution
- **Backend (Render):** FastAPI REST API with auto-scaling
- **Database (Supabase):** Managed PostgreSQL with connection pooling
- **AI Service (Google):** Gemini AI for financial insights

**Benefits:**
- Each component scales independently
- Zero-downtime deployments
- Cost-optimized (all free tiers for demo)
- Production-ready architecture

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL 15 (via Supabase)
- **ORM:** SQLAlchemy 2.0.23
- **Migrations:** Alembic 1.12.1
- **Authentication:** JWT with python-jose
- **Password Hashing:** bcrypt 4.0.1
- **Validation:** Pydantic 2.5.0
- **AI Integration:** Google Generative AI (Gemini) 0.8.5
- **Server:** Uvicorn 0.24.0

### Frontend
- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.0.0
- **Routing:** React Router DOM 6.20.0
- **HTTP Client:** Axios 1.6.2
- **UI Components:** shadcn/ui (Radix UI)
- **Styling:** TailwindCSS 3.4.1
- **Charts:** Recharts 3.3.0
- **Themes:** next-themes 0.4.6
- **Icons:** Lucide React 0.548.0

### DevOps & Deployment
- **Frontend Hosting:** Vercel
- **Backend Hosting:** Render
- **Database Hosting:** Supabase
- **Version Control:** Git + GitHub
- **CI/CD:** Automatic deployment on git push

---

## 📁 Project Structure

```
NeoFinance_Prod/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/                      # API routes
│   │   │   └───├
│   │   │       ├── endpoints/        # Endpoint handlers
│   │   │       │   ├── auth.py       # Authentication endpoints
│   │   │       │   ├── transactions.py
│   │   │       │   ├── dashboard.py
│   │   │       │   └── fin_coach.py  # AI coach endpoints
│   │   │       └── router.py         # API router
│   │   ├── core/                     # Core functionality
│   │   │   ├── config.py             # Settings & configuration
│   │   │   └── security.py           # Auth & security
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   └── transaction.py
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   └── token.py
│   │   ├── services/                 # Business logic
│   │   │   └── gemini_service.py     # AI integration
│   │   └── main.py                   # Application entry
│   ├── alembic/                      # Database migrations
│   │   └── versions/
│   ├── tests/                        # Backend tests
│   ├── .env.example                  # Environment template
│   ├── main.py                       # Production entry point
│   ├── requirements.txt              # Python dependencies
│   ├── runtime.txt                   # Python version for Render
│   └── alembic.ini                   # Alembic configuration
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TransactionList.jsx
│   │   │   ├── TransactionForm.jsx
│   │   │   ├── FinancialCoach.jsx
│   │   │   └── ThemeToggle.jsx
│   │   ├── pages/                    # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── context/                  # React context
│   │   │   └── AuthContext.jsx
│   │   ├── services/                 # API services
│   │   │   └── api.js
│   │   ├── lib/                      # Utilities
│   │   │   └── utils.js              # Helper functions
│   │   ├── App.jsx                   # Main app component
│   │   ├── main.jsx                  # Entry point
│   │   └── index.css                 # Global styles
│   ├── public/                       # Static assets
│   ├── .env.example                  # Environment template
│   ├── package.json                  # Node dependencies
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind configuration
│   └── vercel.json                   # Vercel SPA routing config
│
└── .gitignore                        # Git ignore rules

```

---

## 🚀 Quick Start

### Prerequisites

- **Python:** 3.12+ (3.13+ not recommended due to package compatibility)
- **Node.js:** 20.x
- **PostgreSQL:** 15+ (or use Supabase)
- **Git:** For version control

### Local Development Setup

#### 1. Clone Repository

```bash
git clone https://github.com/POWERVHD/NeoFinance_Prod.git
cd NeoFinance_Prod
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

#### 3. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# VITE_API_URL should be http://localhost:8000/api/v1

# Start development server
npm run dev
```

**Frontend will be available at:** http://localhost:5173

---

## ⚙️ Environment Variables

### Backend (.env)

```bash
# Database (PostgreSQL connection string)
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db

# JWT Authentication
SECRET_KEY=your-super-secret-key-generate-new-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=NeoFinance API
DEBUG=True

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Google Gemini API (get from https://aistudio.google.com)
GEMINI_API_KEY=your-gemini-api-key

# Environment
ENVIRONMENT=development
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend (.env)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000/api/v1

# App Configuration
VITE_APP_NAME=NeoFinance
VITE_APP_VERSION=1.0.0
```

**For Production (Vercel):**
```bash
VITE_API_URL=https://neofinance-prod.onrender.com/api/v1
```

---

## 📦 Database Setup

### Option 1: Local PostgreSQL

```bash
# Create database
psql -U postgres
CREATE DATABASE finance_db;
\q

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db

# Run migrations
cd backend
alembic upgrade head
```


---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest

```

### Manual Testing

1. **Backend API:**
   - Visit: http://localhost:8000/docs
   - Test endpoints using Swagger UI

2. **Frontend:**
   - Register new user
   - Login
   - Add transactions
   - View dashboard
   - Test AI financial coach

---

## 📚 API Documentation

### Authentication Endpoints

```
POST   /api/auth/register    - Register new user
POST   /api/auth/login       - Login (returns JWT token)
GET    /api/auth/me          - Get current user info
```

### Transaction Endpoints

```
GET    /api/transactions/           - List all transactions (paginated)
POST   /api/transactions/           - Create new transaction
GET    /api/transactions/{id}       - Get transaction by ID
PUT    /api/transactions/{id}       - Update transaction
DELETE /api/transactions/{id}       - Delete transaction
```

### Dashboard Endpoints

```
GET    /api/dashboard/summary       - Get financial summary
GET    /api/dashboard/trends        - Get spending trends
```

### AI Coach Endpoints

```
POST   /api/fin-coach/advice        - Get personalized financial advice
```

**Full interactive documentation:**
- Swagger UI: [/docs](https://neofinance-prod.onrender.com/docs)
- ReDoc: [/redoc](https://neofinance-prod.onrender.com/redoc)

---

## 🔧 Development

### Adding New Features

1. **Backend:**
   - Add model in `backend/app/models/`
   - Create schema in `backend/app/schemas/`
   - Implement endpoint in `backend/app/api/endpoints/`
   - Add to router in `backend/app/api/router.py`
   - Create migration: `alembic revision --autogenerate -m "description"`

2. **Frontend:**
   - Create component in `frontend/src/components/`
   - Add API call in `frontend/src/services/api.js`
   - Update routes in `frontend/src/App.jsx`

---

## 🐛 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database connection
psql $DATABASE_URL
```

#### Frontend build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for missing lib/utils.js
ls frontend/src/lib/utils.js
```

#### CORS errors in browser
- Verify `CORS_ORIGINS` in backend includes frontend URL
- Check browser console for exact error
- Ensure protocol (http/https) matches

#### Database migration issues
```bash
# Check current revision
alembic current

# Reset and re-run migrations
alembic downgrade base
alembic upgrade head
```

#### Render deployment fails
- Check `runtime.txt` specifies Python 3.12.0
- Verify `requirements.txt` has compatible versions
- Check build logs for specific errors

### Getting Help

- Check [deployment_plan.md](./deployment_plan.md) troubleshooting section
- Review [DEPLOYMENT_READINESS_ANALYSIS.md](./DEPLOYMENT_READINESS_ANALYSIS.md)
- Check API documentation at `/docs` endpoint

---

## 🎯 Project Highlights

### Technical Achievements

✅ **Microservices Architecture** - Production-ready separation of concerns
✅ **AI Integration** - Google Gemini AI for financial insights
✅ **Secure Authentication** - JWT with bcrypt password hashing
✅ **Database Migrations** - Alembic for schema version control
✅ **Modern UI** - shadcn/ui with TailwindCSS and dark mode
✅ **API Documentation** - Auto-generated Swagger UI
✅ **Environment Management** - Proper secrets handling
✅ **Responsive Design** - Mobile-first approach
✅ **CI/CD Pipeline** - Automated deployments from Git
✅ **Connection Pooling** - Supabase for database optimization

### Best Practices

- ✅ Environment-based configuration
- ✅ Secure password hashing with bcrypt
- ✅ JWT token authentication
- ✅ API versioning (`/api/v1/`)
- ✅ Input validation with Pydantic
- ✅ Database migrations with Alembic
- ✅ CORS properly configured
- ✅ Error handling and logging
- ✅ SPA routing configuration
- ✅ Git-based deployment workflow

---

## 📈 Performance

### Metrics

- **Frontend Load Time:** < 2s (CDN-cached)
- **API Response Time:** < 500ms (after warm-up)
- **Cold Start (Free Tier):** ~30s (first request)
- **Database Queries:** Optimized with indexes

### Scaling

**Current Setup (Free Tier):**
- Database: 500MB storage, 2GB bandwidth
- Backend: 750 hours/month, auto-sleep after 15min
- Frontend: 100GB bandwidth, unlimited requests

**Production Scaling:**
- Upgrade Render to paid tier for always-on backend
- Enable Supabase read replicas
- Add Redis for caching
- Implement database indexes
- Add CDN for static assets

---

## 🗺️ Next Steps

### Completed ✅
- User authentication
- Transaction CRUD
- Dashboard analytics
- AI financial coach
- Production deployment
- Dark mode
- Responsive design

### In Progress 🚧
- Budget planning
- Recurring transactions
- Export to CSV/PDF
- Multi-currency support

### Planning Further Enhancements 📝
- Mobile app (React Native)
- Email notifications
- Bank account integration
- Investment tracking
- Tax reporting
- Collaborative budgets

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **shadcn/ui** - Beautiful component library
- **Vercel** - Frontend hosting
- **Render** - Backend hosting
- **Supabase** - Database hosting
- **Google Gemini** - AI integration
- **Claude Code** - Development assistance

---

## 📞 Contact

**Project Link:** [https://github.com/POWERVHD/NeoFinance_Prod](https://github.com/POWERVHD/NeoFinance_Prod)

**Live Demo:** [https://neo-finance-prod.vercel.app](https://neo-finance-prod.vercel.app)

**API Documentation:** [https://neofinance-prod.onrender.com/docs](https://neofinance-prod.onrender.com/docs)

---

<div align="center">

**Built with FastAPI, React, and Gemini AI — because normal apps are boring 😎**

⭐ Star this repo if you find it helpful!

</div>