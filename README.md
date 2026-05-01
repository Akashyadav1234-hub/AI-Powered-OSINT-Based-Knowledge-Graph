🛡️ AI-Powered OSINT Knowledge Graph
An advanced investigative tool designed to transform unstructured forensic reports into interactive, actionable intelligence. This system utilizes Large Language Models (LLMs) to extract high-fidelity entity-relationship triplets and maps them into a Neo4j Graph Database for deep-link analysis.

🚀 Key Features
AI-Automated Intelligence Extraction: Leverages the Gemini API to parse raw OSINT data, identifying key Indicators of Compromise (IoCs) such as Threat Actors, C2 Servers, Malware, and Vulnerabilities.

Graph-Based Persistence: Stores complex relationships in Neo4j, ensuring investigative data is searchable, scalable, and cross-referenced with previous cases.

Forensic Visualization Engine: Generates two specialized report formats for investigators:

Incident Hierarchy (Tree View): A strict top-down flow of an attack from the primary adversary to the end-targets.

Indicator Profiling (Circular View): A 360-degree map of all infrastructure connected to a specific central entity.

Investigative Automation: Replaces manual charting with real-time extraction, reducing the time required for root-cause analysis.

🛠️ Technical Architecture
Language: Python 3.11+

Intelligence Engine: Google Gemini Pro

Database: Neo4j (Graph Database Management System)

Visualization: PyVis & Plotly for interactive web-based reports

Validation: Pydantic for strict schema enforcement of extracted intelligence

📥 Installation & Setup
Clone the Repository:

Bash
git clone https://github.com/Akashyadav1234-hub/AI-Powered-OSINT-Based-Knowledge-Graph.git
cd AI-Powered-OSINT-Based-Knowledge-Graph
Environment Configuration:
Create a .env file in the root directory:

Code snippet
GEMINI_API_KEY=your_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
Deploy System:

Bash
python3 -m pip install -r requirements.txt
python3 main.py
📊 Sample Investigative Output
The system generates standalone HTML reports upon completion:

Incident_Tree_Report.html: Maps the attack chain (e.g., APT-44 ➔ Uses CrypTox ➔ Targets Government Infrastructure).

Target_Profile_Report.html: Concentric view of all indicators linked to a single threat actor or server.

🚀 Future Roadmap: Phase 2
To further empower the Lucknow Police Cyber Crime Department, the following features are in active development:

Native Document Ingestion: Direct processing of .pdf and .docx forensic evidence files.

Investigator Web Dashboard: A Streamlit-based interface allowing officers to drag-and-drop reports for instant visualization.

OCR Integration: Extracting threat intelligence from image-based screenshots of threat actor communications.