from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from decimal import Decimal
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary", )
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # CRITICAL FIX: Return total as string to preserve decimal precision
    # Financial data must never be converted to float (e.g., 333.333 loses precision)
    # JSON serializes Decimal via str() to maintain exact precision
    total_revenue_str = str(revenue_data['total'])
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_str,  # String preserves precision: "1000.00" not 1000.0
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count'],
        "timezone": revenue_data.get('timezone', 'UTC')  # Include timezone in response

    }
