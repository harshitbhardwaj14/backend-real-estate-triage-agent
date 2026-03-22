from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal

class TriageResult(BaseModel):
    urgency: Literal["High", "Medium", "Low"] = Field(
        description="Priority level: High, Medium, or Low"
    )
    intent: Literal["Buying", "Selling", "Renting", "Viewing", "Complaint", "General Inquiry"] = Field(
        description="Primary intent category"
    )
    property_id: Optional[str] = Field(
        default=None, description="The unique Property ID mentioned (e.g., REF-123)"
    )
    appointment_date: Optional[str] = Field(
        default=None, description="Specific date requested for a meeting or viewing"
    )
    draft_response: str = Field(description="A professional and empathetic response draft")
