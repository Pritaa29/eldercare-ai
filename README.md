# 🏥 ElderCare AI — Advancing Healthcare for Malaysia 2030

**Track 3: Vital Signs (Healthcare & Wellbeing)** *Build with AI for Local Impact and the Good of Humanity!*

[cite_start]ElderCare AI is a high-fidelity intelligent health ecosystem designed to address the challenges of an aging population in Malaysia[cite: 76, 77]. [cite_start]By integrating multimodal AI diagnostics and agentic workflows, we redefine clinical monitoring and home-care accessibility[cite: 78, 91].

---

## 🤖 AI Disclosure & Technical Mandate
[cite_start]In compliance with Section 4 of the Project 2030 Handbook, we declare that **Google Gemini** was utilized as an AI coding assistant to help architect the framework and optimize the deployment pipeline for this project[cite: 148, 149].

**Google AI Ecosystem Stack Integration:**
* [cite_start]**The Intelligence (Brain):** Gemini 2.0 Flash for high-speed, low-latency multimodal medical analysis[cite: 92].
* [cite_start]**The Orchestrator:** Django/Daphne handling real-time Agentic AI workflows[cite: 93].
* [cite_start]**The Context:** Multimodal RAG (Retrieval-Augmented Generation) allowing Dr. Aida to "see" and interpret medical documents[cite: 95].
* [cite_start]**The Deployment:** Fully containerized and deployed on **Google Cloud Run**[cite: 94, 97].

---

## 🚀 Live Deployment
**Production URL:** [https://eldercare-ai-service-778969720168.us-central1.run.app/](https://eldercare-ai-service-778969720168.us-central1.run.app/)

---

## 🛠️ Step 1 — Add Your API Keys
Create a `.env` file in the root directory and fill in the following:

```env
SECRET_KEY=your_django_secret_key
DEBUG=False
GEMINI_API_KEY=your_key_here          # Required for Dr. Aida Chatbot & Exercise
GOOGLE_MAPS_API_KEY=your_key_here     # Required for Care Centre map
TELEGRAM_BOT_TOKEN=your_key_here      # Optional: for Emergency SOS alerts
📦 Step 2 — Installation (Local Development)⚠️ Requirement: Python 3.10 or 3.11 (Mediapipe dependency)Bash# 1. Clone the repo
git clone [https://github.com/Pritaa29/eldercare-ai.git](https://github.com/Pritaa29/eldercare-ai.git)
cd eldercare-ai

# 2. Set up Virtual Environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Database Setup
python manage.py migrate
🚢 Step 3 — Cloud Run DeploymentTo deploy this project to Google Cloud Run as per the hackathon mandate:Bash# Build the image
gcloud builds submit --tag gcr.io/[PROJECT_ID]/eldercare-ai

# Deploy
gcloud run deploy eldercare-ai-service \
    --image gcr.io/[PROJECT_ID]/eldercare-ai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080

📜 Rules & RegulationsThis project was built entirely during the MyAI Future Hackathon (15 March – 24 April 2026). We retain full ownership of the intellectual property while granting Project 2030 a license to showcase this work.
