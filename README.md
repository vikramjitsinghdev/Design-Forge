::: {align="center"}

⚒️ DesignForge

Turn a design idea into a clear creative direction.

DesignForge is an AI-assisted fashion design research application that
takes a natural-language design idea and transforms it into structured
requirements, a research direction, and curated visual references.

Python · Flask · JavaScript · SQLite · Groq · Ollama · Pexels
:::

✨ Overview

Designers often start with an idea before they know exactly how to
describe or research it.

DesignForge bridges that gap.

A user can describe a concept naturally, for example:

"I want a gender-neutral fall jacket with an oversized silhouette,
dark green and cream colours, utility pockets, and a beginner-friendly
construction."

The application analyzes the request, identifies the important design
details, creates a research plan, finds visual references, filters the
results, and saves the search for the user's history.

🎯 Features

Natural-language design input --- describe an idea without
technical search terms.

AI requirement extraction --- converts the request into
structured design requirements.

AI research planning --- creates focused search concepts for the
design.

Visual research --- retrieves relevant references through
Pexels.

Image filtering --- removes unsuitable results before displaying
them.

User accounts --- signup, login, logout, and session management.

Search history --- stores previous design requests and
references.

Responsive interface --- presents requirements, research,
images, and statistics together.

Performance tracking --- measures the time taken by the
pipeline.

🧠 How It Works

User
  │
  ▼
Frontend
  │
  ▼
Flask / app.py
  │
  ▼
InputAgent ──────► Groq
  │
  ▼
Design Requirements
  │
  ▼
ResearchAgent ───► Ollama
  │
  ▼
Research Plan
  │
  ▼
PexelsService
  │
  ▼
FilterService
  │
  ▼
Filtered References
  │
  ▼
SQLite Database
  │
  ▼
Results shown in the frontend

Each component has a focused responsibility. Flask coordinates the
application, AI agents process the design request, services handle
external data, and the database stores the user's history.

🛠️ Tech Stack

Technology         Role

Python         Backend and application logic
Flask          Web server and API
HTML / CSS     User interface
JavaScript     Frontend interaction and API requests
Groq           Natural-language design analysis
Ollama         AI research planning
Pexels API     Visual references
SQLite         User and search data
Git / GitHub   Version control

📁 Project Structure

DesignForge/
│
├── app.py                  # Flask application
├── database.py             # Design/search database
├── user_database.py        # User database
├── user_credential.py      # Authentication
│
├── agents/
│   ├── input_agent.py      # Understands the user's request
│   └── research_agent.py   # Creates the research direction
│
├── services/
│   ├── pexel_service.py    # Image retrieval
│   └── filter_service.py   # Image filtering
│
├── templates/
│   └── index.html          # Main frontend
│
├── static/
│   ├── script.js           # Frontend logic
│   └── style.css           # Styling
│
├── .env                    # API keys and secrets
├── .gitignore
└── README.md

🚀 Getting Started

Requirements

You will need:

Python 3.10+

Git

Internet access

API credentials for the services used by the project

The current application uses services such as Groq, Ollama, and
Pexels. If your research configuration uses Tavily, its API key is
also required.

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DesignForge

2. Create a virtual environment

python -m venv .venv

3. Activate it

.venv\Scripts\Activate.ps1

4. Install dependencies

If the project contains requirements.txt:

pip install -r requirements.txt

Otherwise:

pip install flask flask-cors python-dotenv groq requests

5. Create .env

Add the API keys required by your current services:

GROQ_API_KEY=your_groq_key
OLLAMA_API_KEY=your_ollama_key
PEXELS_API_KEY=your_pexels_key
TAVILY_API_KEY=your_tavily_key

DESIGNFORGE_SECRET_KEY=your_secret_key

Use the exact variable names expected by your agent and service files.

Never commit .env or your local database files to GitHub.

▶️ Run DesignForge

With the virtual environment active:

python app.py

Then open:

http://127.0.0.1:5000

DesignForge serves index.html through Flask, so you do not need to
open the HTML file manually.

First use

Create an account.

Log in.

Enter a design idea.

Generate the design research.

Review the requirements and visual references.

Create another design or view the user's search history.

🩺 Health Check

After starting the application, visit:

http://127.0.0.1:5000/api/health

Or run:

curl http://127.0.0.1:5000/api/health

This checks the Flask service, AI agents, and databases.

💾 Database

DesignForge uses SQLite, so no separate database server is required.

user_database.db
└── User accounts and authentication

database.db
├── Users
├── Searches
└── Search images

The design database stores the original request, AI information, search
components, tags, and individual filtered image references.

The database layer is kept separate from the AI and external API
services.

🔌 Main API Routes

Method   Route                   Purpose

GET    /                     Render the application
GET    /api/health           Check system status
GET    /api/session          Get the current session
POST   /api/signup           Create an account
POST   /api/login            Log in
POST   /api/logout           Log out
POST   /api/design           Run the design pipeline
GET    /api/search-history   Get search history
GET    /api/search/<id>      Get a saved search

💡 Skills Demonstrated

DesignForge brings several areas of software engineering together.

AI & LLMs - LLM API integration - Prompt engineering - Structured AI
output - AI-agent workflows - Multi-stage AI pipelines

Full-Stack Development - Flask backend - REST APIs - HTML and CSS -
JavaScript - Asynchronous frontend requests - Frontend/backend
integration

Database Engineering - SQLite - Relational data modeling - Primary
and foreign keys - One-to-many relationships - Search-history
persistence - Database initialization and migration

Software Engineering - Separation of concerns - Modular
architecture - External API integration - Authentication and sessions -
Testing and debugging - Error handling - Performance measurement - Git
and GitHub

🔮 Future Improvements

Possible next steps include:

Saved design collections

A dedicated profile and history interface

Design comparison

Exportable design briefs

More advanced image ranking

AI-generated concept sketches

Material and construction suggestions

Additional specialized AI agents

Automated testing and CI/CD

Production deployment

👨‍💻 About the Project

DesignForge is a software-engineering project built around a simple
idea:

Give designers a natural way to describe an idea and quickly turn it
into a useful starting point for research.

It combines AI, visual search, filtering, authentication, databases, and
a full-stack web interface into one application.

::: {align="center"}

⚒️ DesignForge

Ideas → Requirements → Research → References
:::