import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

# Define Gemini 2.5 Flash using the CrewAI LLM wrapper
gemini_25 = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2 # Low temperature for accurate triage & extraction
)

class RealEstateAgents:
    def triage_agent(self):
        return Agent(
            role="Lead Triage Specialist",
            goal="Categorize inquiries and assess urgency instantly.",
            backstory="You are the first point of contact for a high-volume real estate firm. You excel at identifying serious buyers.",
            llm=gemini_25
        )

    def ner_specialist(self):
        return Agent(
            role="Data Extraction Expert",
            goal="Extract Property IDs and Dates with 100% accuracy.",
            backstory="You are a meticulous analyst who converts messy text into clean data points for CRM entry.",
            llm=gemini_25
        )

    def support_writer(self):
        return Agent(
            role="Client Relations Manager",
            goal="Draft a perfect response based on extracted data.",
            backstory="You write clear, professional, and inviting responses that drive conversion.",
            llm=gemini_25
        )