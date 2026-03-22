from backend.crew_pipeline import run_triage


def execute_triage(message: str) -> dict:
    return run_triage(message)
