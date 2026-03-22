from crewai import Crew, Process

from backend.agents import RealEstateAgents
from backend.tasks import RealEstateTasks


def run_triage(message: str) -> dict:
    agents = RealEstateAgents()
    tasks = RealEstateTasks()

    triage = agents.triage_agent()
    ner = agents.ner_specialist()
    writer = agents.support_writer()

    classification = tasks.classification_task(triage, message)
    extraction = tasks.extraction_task(ner, message)
    response = tasks.response_task(writer, message)

    response.context = [classification, extraction]

    crew = Crew(
        agents=[triage, ner, writer],
        tasks=[classification, extraction, response],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    if hasattr(result, "pydantic") and result.pydantic is not None:
        return result.pydantic.model_dump()

    if hasattr(result, "json_dict") and result.json_dict:
        return result.json_dict

    if hasattr(result, "raw"):
        raw = result.raw
        if isinstance(raw, dict):
            return raw

    raise ValueError("Triage pipeline did not return a structured JSON result.")
