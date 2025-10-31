from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import TypedDict
from dotenv import load_dotenv
import json

load_dotenv()

# Define state for ATS analysis
class ATSState(TypedDict):
    extracted_json: dict
    ats_score: int
    keyword_analysis: dict
    formatting_issues: list
    missing_sections: list
    suggestions: list
    final_report: dict

ATS_ANALYSIS_PROMPT = """
You are an ATS (Applicant Tracking System) expert analyzer.

Analyze the following resume data and provide a detailed ATS compatibility report.

Resume Data:
{resume_data}

Provide your analysis in the following JSON format:
{{
  "ats_score": 85,
  "keyword_analysis": {{
    "technical_keywords": ["Python", "JavaScript"],
    "soft_skills": ["Leadership", "Communication"],
    "missing_important_keywords": ["Cloud", "Docker"]
  }},
  "formatting_issues": [
    "Missing consistent date formatting",
    "Email format not standard"
  ],
  "missing_sections": [
    "Professional Summary",
    "Certifications"
  ],
  "suggestions": [
    "Add a professional summary at the top",
    "Include more quantifiable achievements",
    "Add relevant certifications"
  ]
}}

Be specific and actionable in your suggestions.
"""

SCORE_CALCULATION_PROMPT = """
Based on the following analysis, calculate a final ATS score (0-100):

Analysis:
{analysis}

Consider:
- Presence of key sections (name, contact, experience, education, skills)
- Keyword density and relevance
- Formatting consistency
- Completeness of information

Return ONLY a number between 0-100.
"""

# Node 1: Analyze ATS compatibility
def analyze_ats_node(state: ATSState) -> ATSState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)
    
    resume_data = json.dumps(state["extracted_json"], indent=2)
    message = HumanMessage(content=ATS_ANALYSIS_PROMPT.format(resume_data=resume_data))
    
    response = model.invoke([message])
    
    try:
        analysis = json.loads(response.content)
        state["ats_score"] = analysis.get("ats_score", 0)
        state["keyword_analysis"] = analysis.get("keyword_analysis", {})
        state["formatting_issues"] = analysis.get("formatting_issues", [])
        state["missing_sections"] = analysis.get("missing_sections", [])
        state["suggestions"] = analysis.get("suggestions", [])
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        state["ats_score"] = 50
        state["keyword_analysis"] = {}
        state["formatting_issues"] = ["Unable to analyze formatting"]
        state["missing_sections"] = []
        state["suggestions"] = ["Review resume structure manually"]
    
    print("✅ ATS Analysis complete")
    return state

# Node 2: Calculate final score
def calculate_score_node(state: ATSState) -> ATSState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
    
    analysis_summary = {
        "keyword_analysis": state["keyword_analysis"],
        "formatting_issues": state["formatting_issues"],
        "missing_sections": state["missing_sections"]
    }
    
    message = HumanMessage(content=SCORE_CALCULATION_PROMPT.format(
        analysis=json.dumps(analysis_summary, indent=2)
    ))
    
    response = model.invoke([message])
    
    try:
        # Extract number from response
        score = int(''.join(filter(str.isdigit, response.content)))
        state["ats_score"] = min(max(score, 0), 100)  # Clamp between 0-100
    except:
        # Keep the score from analysis node if calculation fails
        pass
    
    print(f"✅ Final ATS Score: {state['ats_score']}/100")
    return state

# Node 3: Generate final report
def generate_report_node(state: ATSState) -> ATSState:
    state["final_report"] = {
        "ats_score": state["ats_score"],
        "score_category": get_score_category(state["ats_score"]),
        "keyword_analysis": state["keyword_analysis"],
        "formatting_issues": state["formatting_issues"],
        "missing_sections": state["missing_sections"],
        "suggestions": state["suggestions"],
        "summary": generate_summary(state)
    }
    
    print("✅ ATS Report generated")
    return state

def get_score_category(score: int) -> str:
    """Categorize ATS score"""
    if score >= 80:
        return "Excellent - High ATS Compatibility"
    elif score >= 60:
        return "Good - Moderate ATS Compatibility"
    elif score >= 40:
        return "Fair - Needs Improvement"
    else:
        return "Poor - Significant Issues"

def generate_summary(state: ATSState) -> str:
    """Generate human-readable summary"""
    score = state["ats_score"]
    issues_count = len(state["formatting_issues"])
    missing_count = len(state["missing_sections"])
    
    summary = f"Your resume scored {score}/100 for ATS compatibility. "
    
    if score >= 80:
        summary += "Your resume is well-optimized for ATS systems!"
    elif score >= 60:
        summary += "Your resume has good ATS compatibility with room for improvement."
    else:
        summary += "Your resume needs significant improvements for better ATS compatibility."
    
    if issues_count > 0:
        summary += f" Found {issues_count} formatting issue(s)."
    
    if missing_count > 0:
        summary += f" Missing {missing_count} recommended section(s)."
    
    return summary

def ats_agent(extracted_json: dict) -> dict:
    """
    Main ATS agent function using LangGraph
    
    Args:
        extracted_json: Structured resume data from extractor_agent
    
    Returns:
        dict: Complete ATS analysis report
    """
    # Create the graph
    workflow = StateGraph(ATSState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_ats_node)
    workflow.add_node("calculate_score", calculate_score_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Define workflow
    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "calculate_score")
    workflow.add_edge("calculate_score", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Compile
    app = workflow.compile()
    
    # Initial state
    initial_state = {
        "extracted_json": extracted_json,
        "ats_score": 0,
        "keyword_analysis": {},
        "formatting_issues": [],
        "missing_sections": [],
        "suggestions": [],
        "final_report": {}
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    return final_state["final_report"]

# For testing
if __name__ == "__main__":
    # Test with sample data
    sample_resume = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1234567890",
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "institution": "University XYZ",
                "year": "2020"
            }
        ],
        "skills": ["Python", "JavaScript", "React"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "responsibilities": ["Developed web applications", "Led team projects"]
            }
        ]
    }
    
    report = ats_agent(sample_resume)
    print("\n📊 ATS Report:")
    print(json.dumps(report, indent=2))