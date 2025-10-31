from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class ResumePDFGenerator:
    """Generate professional resume PDFs from enhanced JSON data"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the resume"""
        # Name style
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=4,
            backColor=colors.HexColor('#ecf0f1')
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica-Oblique',
            spaceAfter=4
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='Bullet',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#34495e'),
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=10
        ))
        
        # Skills style
        self.styles.add(ParagraphStyle(
            name='Skills',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=4
        ))
    
    def add_header(self, name: str, email: str, phone: str):
        """Add resume header with contact information"""
        # Name
        name_para = Paragraph(name, self.styles['Name'])
        self.story.append(name_para)
        
        # Contact info
        contact_text = f"{email} • {phone}"
        contact_para = Paragraph(contact_text, self.styles['Contact'])
        self.story.append(contact_para)
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_professional_summary(self, summary: str):
        """Add professional summary section"""
        if not summary:
            return
        
        header = Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader'])
        self.story.append(header)
        
        summary_para = Paragraph(summary, self.styles['BodyText'])
        self.story.append(summary_para)
        
        self.story.append(Spacer(1, 0.15*inch))
    
    def add_skills(self, skills: dict):
        """Add skills section"""
        if not skills:
            return
        
        header = Paragraph("SKILLS", self.styles['SectionHeader'])
        self.story.append(header)
        
        # Technical Skills
        if skills.get('technical_skills'):
            tech_skills = ", ".join(skills['technical_skills'])
            tech_para = Paragraph(f"<b>Technical:</b> {tech_skills}", self.styles['Skills'])
            self.story.append(tech_para)
        
        # Soft Skills
        if skills.get('soft_skills'):
            soft_skills = ", ".join(skills['soft_skills'])
            soft_para = Paragraph(f"<b>Soft Skills:</b> {soft_skills}", self.styles['Skills'])
            self.story.append(soft_para)
        
        # Tools & Technologies
        if skills.get('tools_technologies'):
            tools = ", ".join(skills['tools_technologies'])
            tools_para = Paragraph(f"<b>Tools & Technologies:</b> {tools}", self.styles['Skills'])
            self.story.append(tools_para)
        
        self.story.append(Spacer(1, 0.15*inch))
    
    def add_experience(self, experience: list):
        """Add work experience section"""
        if not experience:
            return
        
        header = Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeader'])
        self.story.append(header)
        
        for exp in experience:
            # Job title and duration
            title = exp.get('title', 'Position')
            duration = exp.get('duration', '')
            title_text = f"{title} <font color='#7f8c8d'>({duration})</font>"
            title_para = Paragraph(title_text, self.styles['JobTitle'])
            self.story.append(title_para)
            
            # Company
            company = exp.get('company', '')
            company_para = Paragraph(company, self.styles['Company'])
            self.story.append(company_para)
            
            # Responsibilities
            responsibilities = exp.get('responsibilities', [])
            for resp in responsibilities:
                bullet_text = f"• {resp}"
                bullet_para = Paragraph(bullet_text, self.styles['Bullet'])
                self.story.append(bullet_para)
            
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.05*inch))
    
    def add_education(self, education: list):
        """Add education section"""
        if not education:
            return
        
        header = Paragraph("EDUCATION", self.styles['SectionHeader'])
        self.story.append(header)
        
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            year = edu.get('year', '')
            details = edu.get('details', '')
            
            # Degree and year
            degree_text = f"<b>{degree}</b> ({year})"
            degree_para = Paragraph(degree_text, self.styles['JobTitle'])
            self.story.append(degree_para)
            
            # Institution
            inst_para = Paragraph(institution, self.styles['Company'])
            self.story.append(inst_para)
            
            # Additional details
            if details:
                details_para = Paragraph(details, self.styles['Bullet'])
                self.story.append(details_para)
            
            self.story.append(Spacer(1, 0.1*inch))
    
    def add_footer(self):
        """Add footer with generation timestamp"""
        timestamp = datetime.now().strftime("%B %d, %Y")
        footer_text = f"<i>Generated on {timestamp} using AI Resume Enhancement System</i>"
        footer_para = Paragraph(footer_text, self.styles['Contact'])
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(footer_para)
    
    def generate(self, enhanced_json: dict):
        """Generate the complete PDF from enhanced JSON"""
        # Header
        self.add_header(
            enhanced_json.get('name', 'Your Name'),
            enhanced_json.get('email', 'email@example.com'),
            enhanced_json.get('phone', '+1234567890')
        )
        
        # Professional Summary
        self.add_professional_summary(
            enhanced_json.get('professional_summary', '')
        )
        
        # Skills
        self.add_skills(enhanced_json.get('skills', {}))
        
        # Experience
        self.add_experience(enhanced_json.get('experience', []))
        
        # Education
        self.add_education(enhanced_json.get('education', []))
        
        # Footer
        self.add_footer()
        
        # Build PDF
        self.doc.build(self.story)
        print(f"✅ PDF generated successfully: {self.output_path}")


def generate_resume_pdf(enhanced_json: dict, output_path: str = None):
    """
    Main function to generate PDF from enhanced resume JSON
    
    Args:
        enhanced_json: Enhanced resume data from enhancer_agent
        output_path: Path where PDF should be saved (optional)
    
    Returns:
        str: Path to the generated PDF
    """
    if output_path is None:
        # Generate default filename
        name = enhanced_json.get('name', 'Resume').replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{name}_Enhanced_{timestamp}.pdf"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate PDF
    generator = ResumePDFGenerator(output_path)
    generator.generate(enhanced_json)
    
    return output_path


# For testing
if __name__ == "__main__":
    # Test with sample enhanced resume
    sample_enhanced_resume = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "professional_summary": "Results-driven Software Engineer with 3+ years of experience in full-stack development, cloud architecture, and agile methodologies. Proven track record of delivering high-quality solutions that improve system performance by 40% and reduce operational costs. Expertise in Python, JavaScript, React, and cloud technologies.",
        "skills": {
            "technical_skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "PostgreSQL"],
            "soft_skills": ["Leadership", "Problem Solving", "Communication", "Team Collaboration"],
            "tools_technologies": ["Git", "Jenkins", "CI/CD", "Agile/Scrum", "JIRA"]
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "duration": "2021-Present",
                "responsibilities": [
                    "Architected and deployed 5+ microservices using Docker and Kubernetes, improving system scalability by 60%",
                    "Led a cross-functional team of 6 developers in implementing CI/CD pipelines, reducing deployment time by 45%",
                    "Optimized database queries and implemented caching strategies, resulting in 40% faster application response times",
                    "Mentored junior developers and conducted code reviews to maintain high code quality standards"
                ]
            },
            {
                "title": "Software Developer",
                "company": "StartUp Solutions LLC",
                "duration": "2020-2021",
                "responsibilities": [
                    "Developed and maintained full-stack web applications using React, Node.js, and PostgreSQL",
                    "Collaborated with product managers to design and implement 15+ new features based on user feedback",
                    "Reduced application load time by 35% through performance optimization and code refactoring",
                    "Implemented comprehensive unit and integration tests, achieving 90% code coverage"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "year": "2020",
                "details": "GPA: 3.8/4.0, Dean's List, Relevant Coursework: Data Structures, Algorithms, Database Systems"
            }
        ]
    }
    
    output_file = generate_resume_pdf(sample_enhanced_resume, "sample_resume.pdf")
    print(f"\n🎉 Test PDF created: {output_file}")