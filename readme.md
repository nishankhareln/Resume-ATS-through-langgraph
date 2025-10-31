---What This Enhancer Agent Does:
Five-Node LangGraph Workflow:

a.Enhance Summary Node ✍️

--Creates compelling professional summary
--Incorporates ATS feedback
--Adds missing keywords naturally


b.Enhance Experience Node 💼

--Rewrites bullets with action verbs
--Adds quantifiable achievements
--Incorporates missing keywords

c.Enhance Skills Node 🛠️

--Organizes into categories (Technical, Soft, Tools)
--Adds ATS missing keywords
--Prioritizes relevant skills

d.Enhance Education Node 🎓

--Standardizes formatting
--Adds relevant details
--Makes ATS-friendly

e.Compile Resume Node 📋

--Combines all enhanced sections
--Adds metadata about improvements
--------------------------------------------------------------------------------
# 🚀 AI Resume Enhancement System

An intelligent resume analysis and enhancement system powered by LangGraph and AI agents. This system extracts, analyzes, enhances, and generates professional resumes with ATS optimization.

## ✨ Features

- 📄 **PDF Text Extraction** - Extract text from resume PDFs
- 🤖 **AI Resume Classification** - Automatically detect if document is a resume
- 📊 **Structured Data Extraction** - Extract structured information (name, email, experience, skills, etc.)
- 🎯 **ATS Compatibility Analysis** - Get detailed ATS score and improvement suggestions
- ✍️ **AI-Powered Enhancement** - Automatically improve resume content with AI
- 📝 **Professional PDF Generation** - Create beautifully formatted resume PDFs
- 💾 **Database Storage** - Store all resume versions and analysis results

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Pipeline                           │
│  (PDF Upload → Extract → Classify → Analyze → Enhance)      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│  Extractor     │   │   ATS Agent     │   │  Enhancer   │
│  Agent         │   │                 │   │  Agent      │
│  (LangGraph)   │   │  (LangGraph)    │   │ (LangGraph) │
└────────────────┘   └─────────────────┘   └─────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   PostgreSQL DB   │
                    │  (resumes table)  │
                    └───────────────────┘
```

## 📁 Project Structure

```
langgraph_project/
├── agents/
│   ├── __pycache__/
│   ├── ats_agent.py          # ATS compatibility analysis agent
│   ├── enhancer_agent.py     # Resume enhancement agent
│   └── extractor_agent.py    # Structured data extraction agent
├── utils/
│   ├── __pycache__/
│   ├── pdf_generator.py      # Professional PDF generation
│   └── pdf_utils.py          # PDF text extraction utilities
├── generated_resumes/        # Output directory for generated PDFs
├── .env                      # Environment variables
├── database.py               # Database connection and setup
├── main.py                   # Main application pipeline
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Installation

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- Groq API key

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd langgraph_project
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_PORT=5432

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Initialize Database

```bash
python database.py
```

This creates the `resumes` table with the following schema:

```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    file_data BYTEA,
    extracted_json JSONB,
    ats_report JSONB,
    enhanced_json JSONB
);
```

## 🚀 Usage

### Basic Usage

Run the main pipeline:

```bash
python main.py
```

Follow the interactive prompts:

1. Enter the path to your resume PDF
2. System will extract and analyze your resume
3. Choose whether to enhance your resume
4. Choose whether to generate a professional PDF

### Example Session

```bash
🚀 AI Resume Enhancement System
============================================================

📂 Enter PDF file path: my_resume.pdf

⏳ Extracting text from PDF...
✅ Text extraction complete

⏳ Checking if document is a resume...
✅ Confirmed: This is a resume

⏳ Extracting structured data from resume...
✅ Structured extraction complete

⏳ Running ATS compatibility analysis...
✅ ATS analysis complete

============================================================
📊 ATS COMPATIBILITY REPORT
============================================================
🎯 Score: 65/100 - Good - Moderate ATS Compatibility

Would you like to enhance your resume based on ATS feedback? (y/n): y

⏳ Enhancing your resume with AI...
✅ Resume enhancement complete!

Would you like to generate a professional PDF? (y/n): y

⏳ Generating professional PDF...
✅ PDF generated: generated_resumes/John_Doe_Enhanced.pdf

🎉 Process complete!
```

## 🤖 AI Agents

### 1. Extractor Agent
- **Purpose**: Extract structured data from resume text
- **Technology**: LangGraph workflow with validation
- **Output**: JSON with name, email, phone, education, skills, experience

### 2. ATS Agent
- **Purpose**: Analyze ATS compatibility and provide improvement suggestions
- **Workflow**:
  1. Analyze resume structure and keywords
  2. Calculate ATS score (0-100)
  3. Generate detailed report with suggestions
- **Output**: ATS score, keyword analysis, formatting issues, suggestions

### 3. Enhancer Agent
- **Purpose**: Improve resume content based on ATS feedback
- **Workflow**:
  1. Enhance professional summary
  2. Improve experience descriptions with metrics
  3. Optimize skills with keywords
  4. Enhance education section
  5. Compile enhanced resume
- **Output**: Enhanced resume JSON with improved content

## 📊 Database Schema

```sql
resumes (
    id              SERIAL PRIMARY KEY,
    filename        TEXT,              -- Original filename
    file_data       BYTEA,             -- Original PDF binary
    extracted_json  JSONB,             -- Extracted structured data
    ats_report      JSONB,             -- ATS analysis report
    enhanced_json   JSONB              -- Enhanced resume data
)
```

## 🎨 PDF Generation Features

The PDF generator creates professional resumes with:

- Clean, modern design
- Proper typography and spacing
- Color-coded sections
- Professional formatting
- Timestamp footer

## 🔧 Configuration

### Groq Models

The system uses `llama-3.1-8b-instant` model. You can change this in each agent file:

```python
model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
```

### Database Configuration

Update `.env` file with your PostgreSQL credentials.

## 📝 API Functions

### Main Functions

```python
# Extract text from PDF
from utils.pdf_utils import extract_text_from_pdf
text = extract_text_from_pdf("resume.pdf")

# Extract structured data
from agents.extractor_agent import extractor_agent
structured_data = extractor_agent(text)

# Analyze ATS compatibility
from agents.ats_agent import ats_agent
ats_report = ats_agent(structured_data)

# Enhance resume
from agents.enhancer_agent import enhancer_agent
enhanced_resume = enhancer_agent(structured_data, ats_report)

# Generate PDF
from utils.pdf_generator import generate_resume_pdf
pdf_path = generate_resume_pdf(enhanced_resume, "output.pdf")
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection
psql -h localhost -U your_user -d your_database
```

### Groq API Issues

- Verify your API key in `.env`
- Check API rate limits
- Ensure internet connection

### PDF Generation Issues

```bash
# Install missing dependencies
pip install reportlab
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **LangGraph** - For the agent orchestration framework
- **Groq** - For fast AI inference
- **ReportLab** - For PDF generation
- **PyMuPDF** - For PDF text extraction

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Contact: your-email@example.com

---

**Built with ❤️ using LangGraph and AI**