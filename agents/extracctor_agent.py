from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from typing import TypedDict
import json

load_dotenv()

# Define the state structure
class ResumeState(TypedDict):
    resume_text: str
    extracted_data: dict
    validation_status: str

# Structure prompt
STRUCTURE_PROMPT = """
You are a resume information extractor. 
Given the resume text below, extract key fields in JSON format:
{{
  "name": "",
  "email": "",
  "phone": "",
  "education": [],
  "skills": [],
  "experience": []
}}

Resume Text:
{resume_text}
"""

VALIDATION_PROMPT = """
You are a resume data validator.
Check if the extracted data looks correct and complete.
Respond with either "VALID" or "INVALID" and explain why.

Extracted Data:
{data}
"""

# Node 1: Extract structured data
def extract_node(state: ResumeState) -> ResumeState:
    model = ChatGroq(model="llama-3.1-8b-instant")
    message = HumanMessage(content=STRUCTURE_PROMPT.format(resume_text=state["resume_text"]))
    response = model.invoke([message])
    
    try:
        structured_data = json.loads(response.content)
    except Exception:
        structured_data = {"raw_output": response.content}
    
    state["extracted_data"] = structured_data
    print("✅ Extraction complete")
    return state

# Node 2: Validate extracted data
def validate_node(state: ResumeState) -> ResumeState:
    model = ChatGroq(model="llama-3.1-8b-instant")
    message = HumanMessage(content=VALIDATION_PROMPT.format(data=json.dumps(state["extracted_data"])))
    response = model.invoke([message])
    
    if "valid" in response.content.lower():
        state["validation_status"] = "VALID"
    else:
        state["validation_status"] = "INVALID"
    
    print(f"✅ Validation: {state['validation_status']}")
    return state

# Build the graph
def extractor_agent(resume_text: str):
    # Create the graph
    workflow = StateGraph(ResumeState)
    
    # Add nodes
    workflow.add_node("extract", extract_node)
    workflow.add_node("validate", validate_node)
    
    # Define edges (workflow)
    workflow.add_edge(START, "extract")
    workflow.add_edge("extract", "validate")
    workflow.add_edge("validate", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Run the workflow
    initial_state = {
        "resume_text": resume_text,
        "extracted_data": {},
        "validation_status": ""
    }
    
    final_state = app.invoke(initial_state)
    return final_state["extracted_data"]

