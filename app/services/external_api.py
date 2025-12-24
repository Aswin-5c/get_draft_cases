from typing import List, Optional
from app.models import Study
from app.config import config
import requests
import time

class ExternalApiService:
    def get_studies(self, client_id: int, start_date: str, end_date: str) -> List[Study]:
        # Format dates as YYYY-MM-DD for the API if needed, or keep as is.
        # User example: start_date=2025-12-18
        # Input start_date is YYYYMMDD from app/main.py
        
        try:
            formatted_start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            formatted_end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
            
            url = "https://api.5cnetwork.com/dicom/v2/studies"
            params = {
                "start_date": formatted_start,
                "end_date": formatted_end,
                "clientId": client_id
            }
            
            # Authorization Header
            # User provided: NWNuZXR3b3JrOjVjbmV0d29yaw== (Decodes to 5cnetwork:5cnetwork)
            headers = {
                "Authorization": "NWNuZXR3b3JrOjVjbmV0d29yaw=="
            }

            print(f"DEBUG: Requesting {url}")
            print(f"DEBUG: Params: {params}")
            print(f"DEBUG: Headers: {headers}")

            # Screenshot shows POST method
            response = requests.post(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                studies = []
                for item in data:
                    try:
                        study = Study(**item)
                        studies.append(study)
                    except Exception as e:
                        # print(f"Error parsing study: {e}")
                        continue
                return studies
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"External API Request Failed: {e}")
            return []

external_api_service = ExternalApiService()

external_api_service = ExternalApiService()
