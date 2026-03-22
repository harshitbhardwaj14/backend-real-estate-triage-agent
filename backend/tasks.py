from crewai import Task
from backend.models import TriageResult

class RealEstateTasks:
    def classification_task(self, agent, text):
        return Task(
            description=(
                "Analyze the inquiry and classify it.\n"
                f"Inquiry: '{text}'\n"
                "Return urgency using exactly one of: High, Medium, Low.\n"
                "Return intent using exactly one of: Buying, Selling, Renting, Viewing, Complaint, General Inquiry.\n"
                "If the user reports a service issue, unresolved issue, or dissatisfaction, classify intent as Complaint.\n"
                "Output only a concise JSON object with keys: urgency, intent."
            ),
            expected_output='JSON with keys "urgency" and "intent" using only the allowed labels.',
            agent=agent
        )

    def extraction_task(self, agent, text):
        return Task(
            description=(
                "Extract structured entities from the inquiry.\n"
                f"Inquiry: '{text}'\n"
                "Extract Property ID if present (format REF-XXXX) and any date/time references.\n"
                "Output only a concise JSON object with keys: property_id, appointment_date."
            ),
            expected_output='JSON with keys "property_id" and "appointment_date". Use null when missing.',
            agent=agent
        )

    def response_task(self, agent, text):
        return Task(
            description=(
                "Create the final triage result.\n"
                f"Inquiry: '{text}'\n"
                "You will be given previous task outputs in the context.\n"
                "Use classification output (urgency, intent) and extraction output (property_id, appointment_date).\n"
                "Do not re-classify or re-extract. Focus on drafting a professional response.\n"
                "Generate a professional draft_response based strictly on this data."
            ),
            expected_output="A complete JSON-formatted TriageResult.",
            output_json=TriageResult,
            agent=agent
        )
