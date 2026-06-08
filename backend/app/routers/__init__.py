from .auth import router as auth_router
from .users import router as users_router
from .customers import router as customers_router
from .loan_applications import router as loan_applications_router
from .risk_rules import router as risk_rules_router
from .blacklist import router as blacklist_router
from .credit_reports import router as credit_reports_router
from .dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "users_router",
    "customers_router",
    "loan_applications_router",
    "risk_rules_router",
    "blacklist_router",
    "credit_reports_router",
    "dashboard_router",
]
