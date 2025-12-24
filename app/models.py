from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime

class Client(BaseModel):
    id: int
    client_name: str

class Study(BaseModel):
    study_date: str
    study_time: str
    created_time: str
    modalities: Optional[str]
    ecomm_status: Optional[bool]
    patient_name: Optional[str]
    patient_id: Optional[str]
    study_desc: Optional[str]
    accession_no: Optional[str]
    client_name: Optional[str]
    series_count: Optional[int]
    instance_count: Optional[int]

    @validator('modalities', pre=True)
    def normalize_modalities(cls, v):
        if not v:
            return "OTHER"
        return v

class CaseDetail(BaseModel):
    patient_name: Optional[str]
    patient_id: Optional[str]
    created_time: Optional[str]
    series_count: Optional[int]
    instance_count: Optional[int]
    modality: Optional[str]
    study_description: Optional[str]

class AnalyticsSummary(BaseModel):
    total_cases: int
    draft_cases: int
    modality_distribution: dict[str, int]
    cases: List[CaseDetail] = []

class ClientOverview(BaseModel):
    client_name: str
    draft_cases: int
