import json
import redis.asyncio as redis
from typing import Dict, Any
import os
from decimal import Decimal

# Custom JSON encoder to handle Decimal values (required for financial precision)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string to preserve precision
        return super().default(obj)

# Initialize Redis client (typically configured centrally).
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Fetches revenue summary, utilizing caching to improve performance.
    Uses Decimal for all monetary values to ensure financial precision.
    """
    # Cache key now includes tenant_id to prevent multi-tenant data leaks
    # Example: "revenue:prop-001:tenant:tenant-a" (not shared with "revenue:prop-001:tenant:tenant-b")
    cache_key = f"revenue:{property_id}:tenant:{tenant_id}"
    
    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Revenue calculation is delegated to the reservation service.
    from app.services.reservations import calculate_total_revenue
    
    # Calculate revenue (returns values as Decimal for precision)
    result = await calculate_total_revenue(property_id, tenant_id)
    
    # Cache the result for 5 minutes using custom encoder for Decimal precision
    # Uses DecimalEncoder to convert Decimal values to strings without losing precision
    await redis_client.setex(cache_key, 300, json.dumps(result, cls=DecimalEncoder))
    
    return result
