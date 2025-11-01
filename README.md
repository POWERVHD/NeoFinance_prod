# AI-Powered Finance Dashboard

A personal finance management application built with FastAPI and React.

## Features (Stage 1)

- User authentication with JWT
- Transaction management (CRUD operations)
- Dashboard with financial summaries
- Category-based expense tracking
- PostgreSQL database

## Tech Stack

### Backend
- FastAPI 0.104.1
- PostgreSQL 15
- SQLAlchemy 2.0.23
- JWT Authentication
- Pydantic for validation

### Frontend
- React 18
- Vite
- React Router
- Axios

## Project Structure

```
finance-dashboard/
├── backend/          # FastAPI backend
│   ├── app/          # Application code
│   ├── tests/        # Tests
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/          # Source files
│   └── package.json
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE finance_db;
\q
```

6. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. Access API docs: http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

4. Access app: http://localhost:5173

## Using Docker (Optional)

Run PostgreSQL with Docker Compose:
```bash
docker-compose up -d
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

### Code Structure

See [CLAUDE.md](./claude.md) for detailed project structure and implementation guide.

## License

MIT
