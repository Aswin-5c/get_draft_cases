from typing import List
from app.models import Study, AnalyticsSummary, CaseDetail
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models import Study, AnalyticsSummary, CaseDetail

class AnalyticsService:
    def process_studies(self, studies: List[Study]) -> AnalyticsSummary:
        total_cases = len(studies)
        draft_cases = 0
        finalized_cases = 0
        modality_counts: Dict[str, int] = {}
        detailed_cases = []

        for study in studies:
            # Draft Classification Logic
            # ecomm_status == true -> Non-Draft (Finalized)
            # ecomm_status == false -> Draft
            # ecomm_status == null -> Draft
            if study.ecomm_status is not True:
                draft_cases += 1
                
                # Format Created Time (IST 12hr)
                formatted_time = study.created_time
                try:
                    if study.created_time:
                        # Parse ISO format (e.g., 2025-12-24T16:27:46.599Z)
                        dt = datetime.fromisoformat(study.created_time.replace('Z', '+00:00'))
                        # Convert to IST
                        ist = ZoneInfo("Asia/Kolkata")
                        dt_ist = dt.astimezone(ist)
                        # Format: DD-MM-YYYY HH:MM AM/PM
                        formatted_time = dt_ist.strftime("%d-%m-%Y %I:%M %p")
                except Exception as e:
                    # Fallback if parsing fails
                    print(f"Date parsing error: {e}")
                    formatted_time = study.created_time

                # Collect detailed info
                detailed_cases.append(CaseDetail(
                    patient_name=study.patient_name,
                    patient_id=study.patient_id,
                    created_time=formatted_time,
                    series_count=study.series_count,
                    instance_count=study.instance_count,
                    modality=study.modalities,
                    study_description=study.study_desc
                ))

            # Modality Handling
            # Split by comma, trim, uppercase
            raw_modalities = study.modalities or "OTHER"
            mods = [m.strip().upper() for m in raw_modalities.split(',')]
            
            # Study Description Handling
            study_desc = study.study_desc
            if study_desc and study_desc != "*":
                study_desc = study_desc.strip()
            else:
                study_desc = None

            for mod in mods:
                if not mod:
                    mod = "OTHER"
                
                # Group by Modality + Study Description if available
                if study_desc:
                    key = f"{mod} - {study_desc}"
                else:
                    key = mod
                    
                modality_counts[key] = modality_counts.get(key, 0) + 1

        return AnalyticsSummary(
            total_cases=total_cases,
            draft_cases=draft_cases,
            modality_distribution=modality_counts,
            cases=detailed_cases
        )

analytics_service = AnalyticsService()
