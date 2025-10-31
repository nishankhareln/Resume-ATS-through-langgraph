from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import TypedDict
from dotenv import load_dotenv
import json

load_dotenv()

# Define state for enhancement
class EnhancerState(TypedDict):
    original_json: dict
    ats_report: dict
    enhanced_summary: str
    enhanced_experience: list
    enhanced_skills: list
    enhanced_education: list
    final_enhanced_json: dict

SUMMARY_ENHANCEMENT_PROMPT = """
You are a professional resume writer specializing in creating compelling professional summaries.

Based on the resume data and ATS feedback below, create a powerful professional summary (3-4 sentences).

Original Resume Data:
{resume_data}

ATS Feedback:
{ats_feedback}

Requirements:
- Highlight key strengths and achievements
- Include relevant keywords from ATS missing keywords
- Make it ATS-friendly and impactful
- Keep it concise (3-4 sentences)

Return ONLY the professional summary text, no JSON or additional formatting.
"""

EXPERIENCE_ENHANCEMENT_PROMPT = """
You are a professional resume writer specializing in achievement-focused experience sections.

Enhance the following work experience entries to be more ATS-friendly and impactful.

Original Experience:
{experience}

ATS Missing Keywords:
{missing_keywords}

For each experience entry, improve it by:
- Using strong action verbs
- Adding quantifiable achievements where possible
- Incorporating relevant keywords naturally
- Making bullet points more impactful

Return the enhanced experience in this EXACT JSON format:
[
  {{
    "title": "Job Title",
    "company": "Company Name",
    "duration": "2020-2023",
    "responsibilities": [
      "Enhanced bullet point 1 with metrics",
      "Enhanced bullet point 2 with impact"
    ]
  }}
]

Return ONLY valid JSON, no other text.
"""

SKILLS_ENHANCEMENT_PROMPT = """
You are a professional resume writer specializing in skills optimization.

Enhance the skills section based on the original skills and ATS feedback.

Original Skills:
{original_skills}

ATS Missing Keywords:
{missing_keywords}

Tasks:
- Organize skills into categories (Technical, Soft Skills, Tools, etc.)
- Add missing important keywords naturally
- Remove redundant or weak skills
- Prioritize most relevant skills

Return enhanced skills in this EXACT JSON format:
{{
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "tools_technologies": ["tool1", "tool2"]
}}

Return ONLY valid JSON, no other text.
"""

EDUCATION_ENHANCEMENT_PROMPT = """
You are a professional resume writer specializing in education sections.

Enhance the education section for better ATS compatibility.

Original Education:
{education}

Requirements:
- Ensure consistent formatting
- Add relevant details (GPA if strong, honors, relevant coursework)
- Make it ATS-friendly

Return enhanced education in this EXACT JSON format:
[
  {{
    "degree": "Degree Name",
    "institution": "University Name",
    "year": "2020",
    "details": "Honors, relevant coursework, or achievements"
  }}
]

Return ONLY valid JSON, no other text.
"""

# Node 1: Enhance Professional Summary
def enhance_summary_node(state: EnhancerState) -> EnhancerState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
    
    resume_data = json.dumps(state["original_json"], indent=2)
    ats_feedback = json.dumps(state["ats_report"].get("suggestions", []), indent=2)
    
    message = HumanMessage(content=SUMMARY_ENHANCEMENT_PROMPT.format(
        resume_data=resume_data,
        ats_feedback=ats_feedback
    ))
    
    response = model.invoke([message])
    state["enhanced_summary"] = response.content.strip()
    
    print("✅ Professional summary enhanced")
    return state

# Node 2: Enhance Experience Section
def enhance_experience_node(state: EnhancerState) -> EnhancerState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.6)
    
    experience = state["original_json"].get("experience", [])
    missing_keywords = state["ats_report"].get("keyword_analysis", {}).get("missing_important_keywords", [])
    
    message = HumanMessage(content=EXPERIENCE_ENHANCEMENT_PROMPT.format(
        experience=json.dumps(experience, indent=2),
        missing_keywords=", ".join(missing_keywords)
    ))
    
    response = model.invoke([message])
    
    try:
        # Try to parse JSON from response
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        enhanced_exp = json.loads(content)
        state["enhanced_experience"] = enhanced_exp
    except json.JSONDecodeError:
        # Fallback: keep original if parsing fails
        state["enhanced_experience"] = experience
        print("⚠️  Experience enhancement parsing failed, keeping original")
    
    print("✅ Experience section enhanced")
    return state

# Node 3: Enhance Skills Section
def enhance_skills_node(state: EnhancerState) -> EnhancerState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)
    
    original_skills = state["original_json"].get("skills", [])
    missing_keywords = state["ats_report"].get("keyword_analysis", {}).get("missing_important_keywords", [])
    
    message = HumanMessage(content=SKILLS_ENHANCEMENT_PROMPT.format(
        original_skills=json.dumps(original_skills),
        missing_keywords=", ".join(missing_keywords)
    ))
    
    response = model.invoke([message])
    
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        enhanced_skills = json.loads(content)
        state["enhanced_skills"] = enhanced_skills
    except json.JSONDecodeError:
        # Fallback: organize original skills into categories
        state["enhanced_skills"] = {
            "technical_skills": original_skills,
            "soft_skills": [],
            "tools_technologies": []
        }
        print("⚠️  Skills enhancement parsing failed, using basic organization")
    
    print("✅ Skills section enhanced")
    return state

# Node 4: Enhance Education Section
def enhance_education_node(state: EnhancerState) -> EnhancerState:
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.4)
    
    education = state["original_json"].get("education", [])
    
    message = HumanMessage(content=EDUCATION_ENHANCEMENT_PROMPT.format(
        education=json.dumps(education, indent=2)
    ))
    
    response = model.invoke([message])
    
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        enhanced_edu = json.loads(content)
        state["enhanced_education"] = enhanced_edu
    except json.JSONDecodeError:
        state["enhanced_education"] = education
        print("⚠️  Education enhancement parsing failed, keeping original")
    
    print("✅ Education section enhanced")
    return state

# Node 5: Compile Final Enhanced Resume
def compile_enhanced_resume_node(state: EnhancerState) -> EnhancerState:
    state["final_enhanced_json"] = {
        "name": state["original_json"].get("name", ""),
        "email": state["original_json"].get("email", ""),
        "phone": state["original_json"].get("phone", ""),
        "professional_summary": state["enhanced_summary"],
        "experience": state["enhanced_experience"],
        "skills": state["enhanced_skills"],
        "education": state["enhanced_education"],
        "enhancement_metadata": {
            "original_ats_score": state["ats_report"].get("ats_score", 0),
            "improvements_applied": [
                "Added professional summary",
                "Enhanced experience with metrics",
                "Optimized skills with keywords",
                "Improved education formatting"
            ]
        }
    }
    
    print("✅ Enhanced resume compiled")
    return state

def enhancer_agent(original_json: dict, ats_report: dict) -> dict:
    """
    Main enhancer agent function using LangGraph
    
    Args:
        original_json: Original extracted resume data
        ats_report: ATS analysis report
    
    Returns:
        dict: Enhanced resume JSON
    """
    # Create the graph
    workflow = StateGraph(EnhancerState)
    
    # Add nodes
    workflow.add_node("enhance_summary", enhance_summary_node)
    workflow.add_node("enhance_experience", enhance_experience_node)
    workflow.add_node("enhance_skills", enhance_skills_node)
    workflow.add_node("enhance_education", enhance_education_node)
    workflow.add_node("compile_resume", compile_enhanced_resume_node)
    
    # Define workflow (parallel processing where possible)
    workflow.add_edge(START, "enhance_summary")
    workflow.add_edge("enhance_summary", "enhance_experience")
    workflow.add_edge("enhance_experience", "enhance_skills")
    workflow.add_edge("enhance_skills", "enhance_education")
    workflow.add_edge("enhance_education", "compile_resume")
    workflow.add_edge("compile_resume", END)
    
    # Compile
    app = workflow.compile()
    
    # Initial state
    initial_state = {
        "original_json": original_json,
        "ats_report": ats_report,
        "enhanced_summary": "",
        "enhanced_experience": [],
        "enhanced_skills": [],
        "enhanced_education": [],
        "final_enhanced_json": {}
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    return final_state["final_enhanced_json"]

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
    
    sample_ats_report = {
        "ats_score": 65,
        "keyword_analysis": {
            "missing_important_keywords": ["Docker", "Cloud", "CI/CD"]
        },
        "suggestions": [
            "Add professional summary",
            "Include more metrics"
        ]
    }
    
    enhanced = enhancer_agent(sample_resume, sample_ats_report)
    print("\n✨ Enhanced Resume:")
    print(json.dumps(enhanced, indent=2))