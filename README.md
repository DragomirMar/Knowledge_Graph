# Knowledge Graph

This application builds, manages, and visualizes knowledge graphs from uploaded documents and web content.

Users can upload PDF files or provide URLs, which are processed using document analysis and LLM-based extraction to identify entities and relationships that are stored in a database. Through a Streamlit web interface, users can search, create, update, and delete entities and their relationships. An interactive graph visualization is also provided that lets users explore the full knowledge graph or view a focused subgraph centered on a specific entity.

## Technologies

It was built with:
- Python
- [Ollama](https://ollama.com) (Model: llama3.1:8B)
- [Streamlit](https://streamlit.io/)
- [MongoDB](https://www.mongodb.com/)


## Prerequisites

Before you get started, ensure you have the following installed on your machine:

- Python 3.11 or higher
- Ollama (for running LLMs locally)
- MongoDB (as database to save nodes and relationships)

## Setup and installation

Follow these steps to get started:

### 1. Install Ollama
Download and install [Ollama](https://ollama.com), which is required to run models locally.

### 2. Pull LLaMA 3.1 (or another model)
Once Ollama is installed, pull the LLaMA 3.1 model (or another model you prefer):
```bash
ollama pull llama3.1
```

### 3. Install mongodb
Download and install MongoDB from the website https://www.mongodb.com/try/download/community.

Create MongoDB Data Directory (first time only):
```bash
mkdir -p ~/data/db
```

Start MongoDB:
```bash
mongod --dbpath ~/data/db
```

Keep this terminal window open while using the application.

### 4. Clone this repo
```bash
git clone https://github.com/DragomirMar/Knowledge_Graph.git
cd Knowledge_Graph
```

### 5. Create Virtual Environment
```bash
### Navigate to the project folder
cd Knowledge_Graph

### Create a virtual environment
python -m venv venv

### Activate it
source venv/bin/activate
```
**Note:** On many Linux systems, `python` may still point to Python 2 so use  `python3` as a command.

### 6. Install Required Libraries
```bash
pip install -r requirements.txt 
```

**Note:** If pip is still using the global environment, run:
```bash
unalias pip
```

### 7. Configure Environment Variables

The application uses environment variables to manage database configuration and separate test/production environments.

#### Copy Environment Templates
```bash
# Create production environment file
cp .env.example .env

# Create test environment file
cp .env.example .env.test
```

#### Edit `.env` (Production Configuration)
Open `.env` in your text editor and configure:
```bash
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/

# Database name for production
MONGODB_DATABASE=knowledge_graph

# Environment mode
ENVIRONMENT=production
```

#### Edit `.env.test` (Test Configuration)
Open `.env.test` in your text editor and configure:
```bash
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/

# Database name for testing (keeps your production data safe!)
MONGODB_DATABASE=knowledge_graph_test

# Environment mode
ENVIRONMENT=test
```

**Important:** The test database (`knowledge_graph_test`) is automatically used when running tests, keeping production data safe.

# Run the application
### 1. Start Ollama
Start Ollama either through the interface or through the terminal:
```bash
ollama serve
```
This starts the Ollama server and lets you reach the model(s).

### 2. Ensure MongoDB is Running
Make sure MongoDB is still running in another terminal:
```bash
mongod --dbpath ~/data/db
```

### 3. Activate Virtual Environment
If not already activated:
```bash
# On macOS/Linux:
source venv/bin/activate
```

### 4. Run the app
Navigate to the source folder (cd src) and run:
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`


# Testing

The application includes a comprehensive test suite to ensure reliability.

### Run All Tests
```bash
pytest
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test Files
```bash
# Database manager tests
pytest test/test_database_manager.py -v

# Document processing tests
pytest test/test_document_processing_service.py -v

# Text extraction tests
pytest test/test_extract_text.py -v
```
