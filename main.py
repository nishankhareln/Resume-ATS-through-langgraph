from utils.pdf_utils import extract_text_from_pdf
from utils.pdf_generator import generate_resume_pdf
from agents.extracctor_agent import extractor_agent
from agents.ats_agent import ats_agent
from agents.enhancer_agent import enhancer_agent
from database import get_connection
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import json
import os

load_dotenv()

def save_complete_data(filename, file_bytes, structured_json, ats_report, enhanced_json):
    """Save all data (extracted, ATS report, and enhanced) to database"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes (filename, file_data, extracted_json, ats_report, enhanced_json)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        filename, 
        file_bytes, 
        json.dumps(structured_json), 
        json.dumps(ats_report),
        json.dumps(enhanced_json)
    ))
    
    resume_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Complete resume data saved to DB with ID: {resume_id}")
    return resume_id

def is_resume(text: str) -> bool:
    """Classify if the uploaded PDF is a resume or not."""
    model = ChatGroq(model="llama-3.1-8b-instant")
    prompt = f"""
    You are a document classifier.
    Decide if the following text is a resume or not.
    Answer only 'YES' or 'NO'.

    Text:
    {text[:2000]}  # only the first 2000 chars to limit tokens
    """
    response = model.invoke([HumanMessage(content=prompt)])
    answer = response.content.strip().lower()
    print(f"🧠 Resume Check Model Output: {answer}")
    return "yes" in answer

def print_ats_report(report: dict):
    """Pretty print ATS report"""
    print("\n" + "="*60)
    print("📊 ATS COMPATIBILITY REPORT")
    print("="*60)
    
    # Score
    score = report.get("ats_score", 0)
    category = report.get("score_category", "Unknown")
    print(f"\n🎯 Score: {score}/100 - {category}")
    
    # Summary
    print(f"\n📝 Summary:")
    print(f"   {report.get('summary', 'No summary available')}")
    
    # Keyword Analysis
    keywords = report.get("keyword_analysis", {})
    if keywords:
        print(f"\n🔑 Keyword Analysis:")
        if keywords.get("technical_keywords"):
            print(f"   ✓ Technical: {', '.join(keywords['technical_keywords'][:5])}")
        if keywords.get("soft_skills"):
            print(f"   ✓ Soft Skills: {', '.join(keywords['soft_skills'][:5])}")
        if keywords.get("missing_important_keywords"):
            print(f"   ✗ Missing: {', '.join(keywords['missing_important_keywords'][:5])}")
    
    # Formatting Issues
    issues = report.get("formatting_issues", [])
    if issues:
        print(f"\n⚠️  Formatting Issues ({len(issues)}):")
        for i, issue in enumerate(issues[:3], 1):
            print(f"   {i}. {issue}")
    
    # Missing Sections
    missing = report.get("missing_sections", [])
    if missing:
        print(f"\n❌ Missing Sections ({len(missing)}):")
        for i, section in enumerate(missing, 1):
            print(f"   {i}. {section}")
    
    # Suggestions
    suggestions = report.get("suggestions", [])
    if suggestions:
        print(f"\n💡 Top Suggestions ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
    
    print("\n" + "="*60 + "\n")

def print_enhanced_preview(enhanced_json: dict):
    """Pretty print enhanced resume preview"""
    print("\n" + "="*60)
    print("✨ ENHANCED RESUME PREVIEW")
    print("="*60)
    
    # Professional Summary
    if enhanced_json.get("professional_summary"):
        print("\n📝 Professional Summary:")
        print(f"   {enhanced_json['professional_summary']}")
    
    # Skills
    skills = enhanced_json.get("skills", {})
    if skills:
        print("\n🛠️  Skills:")
        if skills.get("technical_skills"):
            print(f"   Technical: {', '.join(skills['technical_skills'][:8])}")
        if skills.get("soft_skills"):
            print(f"   Soft Skills: {', '.join(skills['soft_skills'][:5])}")
        if skills.get("tools_technologies"):
            print(f"   Tools: {', '.join(skills['tools_technologies'][:8])}")
    
    # Experience Preview
    experience = enhanced_json.get("experience", [])
    if experience:
        print(f"\n💼 Experience ({len(experience)} positions):")
        for i, exp in enumerate(experience[:2], 1):
            print(f"\n   {i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
            print(f"      Duration: {exp.get('duration', 'N/A')}")
            responsibilities = exp.get('responsibilities', [])
            if responsibilities:
                print(f"      • {responsibilities[0]}")
                if len(responsibilities) > 1:
                    print(f"      • {responsibilities[1]}")
    
    # Metadata
    metadata = enhanced_json.get("enhancement_metadata", {})
    if metadata:
        print(f"\n📈 Improvements Applied:")
        improvements = metadata.get("improvements_applied", [])
        for improvement in improvements[:4]:
            print(f"   ✓ {improvement}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("🚀 AI Resume Enhancement System")
    print("="*60)
    
    file_path = input("\n📂 Enter PDF file path: ").strip()
    
    # Read file
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
    except FileNotFoundError:
        print("❌ File not found. Please check the path.")
        exit()

    print("\n⏳ Extracting text from PDF...")
    text = extract_text_from_pdf(file_path)
    print("✅ Text extraction complete")
    print("\n📝 Extracted Text Preview:")
    print(text[:500] + "...\n")

    # Step 1: Classify whether it's a resume
    print("⏳ Checking if document is a resume...")
    if not is_resume(text):
        print("\n⚠️  The uploaded document does NOT look like a resume.")
        print("Please upload a valid resume PDF.")
        exit()

    print("✅ Confirmed: This is a resume\n")

    # Step 2: Extract structured data
    print("⏳ Extracting structured data from resume...")
    structured_json = extractor_agent(text)
    print("✅ Structured extraction complete")
    print("\n📄 Original Extracted Resume Data:")
    print(json.dumps(structured_json, indent=2))

    # Step 3: Run ATS Analysis
    print("\n⏳ Running ATS compatibility analysis...")
    ats_report = ats_agent(structured_json)
    print("✅ ATS analysis complete")
    
    # Display ATS Report
    print_ats_report(ats_report)

    # Step 4: Ask user if they want to enhance
    enhance_choice = input("Would you like to enhance your resume based on ATS feedback? (y/n): ").strip().lower()
    
    enhanced_json = None
    if enhance_choice == 'y':
        print("\n⏳ Enhancing your resume with AI...")
        print("   This may take a minute...\n")
        
        enhanced_json = enhancer_agent(structured_json, ats_report)
        print("✅ Resume enhancement complete!")
        
        # Display enhanced preview
        print_enhanced_preview(enhanced_json)
        
        print("💾 Full enhanced resume data:")
        print(json.dumps(enhanced_json, indent=2))
    else:
        print("\n⏭️  Skipping enhancement...")

    # Step 5: Save to database
    print("\n⏳ Saving data to database...")
    filename = file_path.split("\\")[-1]  # Works for Windows
    if "/" in file_path:
        filename = file_path.split("/")[-1]  # Works for Unix/Mac
    
    resume_id = save_complete_data(filename, file_bytes, structured_json, ats_report, enhanced_json)
    
    print(f"\n🎉 Process complete! Resume ID: {resume_id}")
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"   • Original ATS Score: {ats_report.get('ats_score', 0)}/100")
    if enhanced_json:
        print(f"   • Resume Enhanced: ✓")
        print(f"   • Improvements: {len(enhanced_json.get('enhancement_metadata', {}).get('improvements_applied', []))}")
    else:
        print(f"   • Resume Enhanced: ✗")
    print(f"   • Data saved with ID: {resume_id}")
    print("\n" + "="*60)
    print("Next steps:")
    if enhanced_json:
        print("  • Generate a professional PDF from enhanced resume")
        print("  • Compare original vs enhanced versions")
    else:
        print("  • Run enhancement to improve your resume")
        print("  • Generate PDF after enhancement")
    print("="*60)