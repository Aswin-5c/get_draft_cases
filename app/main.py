from fastapi import FastAPI, HTTPException, Query
from typing import List
from app.models import Client, AnalyticsSummary, ClientOverview
from app.services.clickhouse import clickhouse_service
from app.services.external_api import external_api_service
from app.services.analytics import analytics_service
from functools import lru_cache
from datetime import date, timedelta
import time

app = FastAPI(title="Production Analytics Dashboard API")

# Simple in-memory cache for clients (TTL could be added with a more complex cache)
@lru_cache(maxsize=1)
def get_cached_clients():
    return clickhouse_service.get_clients()

@app.get("/clients", response_model=List[Client])
def get_clients():
    try:
        clients = get_cached_clients()
        return clients
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch clients")

@app.get("/analytics", response_model=AnalyticsSummary)
def get_analytics(
    client_id: int = Query(..., description="Client ID"),
    start_date: str = Query(..., description="Start Date (YYYYMMDD)"),
    end_date: str = Query(..., description="End Date (YYYYMMDD)")
):
    # Basic Validation
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be earlier than end date")

    try:
        # Fetch Studies
        studies = external_api_service.get_studies(client_id, start_date, end_date)
        
        # Process Analytics
        summary = analytics_service.process_studies(studies)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

# Global Cache for Overview
overview_cache = {
    "data": [],
    "last_updated": None
}
CACHE_TTL_SECONDS = 900  # 15 minutes

@app.get("/overview", response_model=List[ClientOverview])
def get_overview(refresh: bool = False):
    global overview_cache
    
    try:
        current_time = time.time()
        
        # Return cached data if valid and refresh is not forced
        if (not refresh and 
            overview_cache["data"] and 
            overview_cache["last_updated"] and 
            (current_time - overview_cache["last_updated"] < CACHE_TTL_SECONDS)):
            return overview_cache["data"]

        clients = get_cached_clients()
        overview_data = []
        
        # Default date range for overview: last 3 days
        today = date.today()
        start_date = (today - timedelta(days=3)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")
        
        for client in clients:
            try:
                # We use the same service but we might want to optimize this
                studies = external_api_service.get_studies(client.id, start_date, end_date)
                summary = analytics_service.process_studies(studies)
                
                if summary.draft_cases > 0:
                    overview_data.append(ClientOverview(
                        client_name=client.client_name,
                        draft_cases=summary.draft_cases
                    ))
            except Exception as e:
                print(f"Error processing client {client.client_name}: {e}")
                continue
        
        # Sort by draft cases descending
        overview_data.sort(key=lambda x: x.draft_cases, reverse=True)
        
        # Update Cache
        overview_cache["data"] = overview_data
        overview_cache["last_updated"] = current_time
        
        return overview_data
    except Exception as e:
        print(f"Overview error: {e}")
        return []

@app.get("/health")
def health_check():
    return {"status": "ok"}
