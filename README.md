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
Download and install Ollama, which is required to run models locally.


- For **Windows** and **Mac** use the link: https://ollama.com/download

- For **Ubuntu** use the command:
```curl -fsSL https://ollama.com/install.sh | sh ```

#### Pull LLaMA 3.1:8B
Once Ollama is installed, pull the LLaMA 3.1 model (or another model you prefer):
```bash
ollama pull llama3.1:8b
```

### 2. Install MongoDB

#### For Windows & macOS:
Download and install MongoDB:
- **Windows**: https://www.mongodb.com/docs/v7.0/tutorial/install-mongodb-on-windows/
- **macOS**: https://www.mongodb.com/docs/v7.0/tutorial/install-mongodb-on-os-x/

After installation, open a terminal and create MongoDB Data Directory (first time only):
```bash
mkdir -p ~/data/db
```

Start MongoDB:
```bash
mongod --dbpath ~/data/db
```

Keep this terminal window open while using the application.

---

### For Ubuntu:

**Step 1: Install prerequisites**
```bash
sudo apt-get install gnupg curl
```

**Step 2: Import MongoDB public GPG key**
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
```

**Step 3: Create MongoDB repository list file**
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

**Step 4: Reload package database**
```bash
sudo apt-get update
```

**Step 5: Install MongoDB Community Server**
``` bash
sudo apt install -y mongodb-org
```

**Step 6: Start MongoDB service**
``` bash 
sudo systemctl start mongod
```

**Step 7: Verify MongoDB is running**
``` bash 
sudo systemctl status mongod
```

### 3. Clone this repo
```bash
git clone https://github.com/DragomirMar/Knowledge_Graph.git
cd Knowledge_Graph
```

### 4. Create Virtual Environment
```bash
### Navigate to the project folder
cd Knowledge_Graph

### Create a virtual environment
python -m venv venv

### Activate it
source venv/bin/activate
```
**Note:** On many Linux systems, `python` may still point to Python 2 so use  `python3` as a command.

### 5. Install Required Libraries
```bash
pip install -r requirements.txt 
```

**Note:** If you encounter problem with the package `pygraphviz`, run:
```bash
sudo apt update
sudo apt install -y python<your_python_version>-dev build-essential graphviz graphviz-dev pkg-config
```
After that, try installing `requirements.txt` again.

`pygraphviz` compiles native C code, so it requires the appropriate development tools and Graphviz headers to be installed on your system.

**Note 2:** If pip is still using the global environment, run:
```bash
unalias pip
```

### 6. Configure Environment Variables

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

### 2. Ensure MongoDB is Running

**Windows, macOS**

Make sure MongoDB is still running in another terminal:
```bash
mongod --dbpath ~/data/db
```

### Ubuntu

Check if MongoDB is running:
``` bash
sudo systemctl status mongod
```

Start if not running:
``` bash
sudo systemctl start mongod
```

### 3. Activate Virtual Environment
**macOS/Linux**

If not already activated:
```bash
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
