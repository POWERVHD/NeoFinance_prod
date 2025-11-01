"""
Main API router for v1 endpoints.

Aggregates all endpoint routers into a single router for the API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, transactions, dashboard, ai_chat

api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include transaction endpoints
api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"]
)

# Include dashboard endpoints
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

# Include AI chat endpoints
api_router.include_router(
    ai_chat.router,
    prefix="/ai-chat",
    tags=["ai-chat"]
)
