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
- mongoDB (as database to save nodes and relationships)

## Setup and installation

Follow these steps to get started:

### 1. Install Ollama
Download and install [Ollama](https://ollama.com), which is required to run models locally.

### 2. Pull LLaMA 3.1 (or another model)
Once Ollama is installed, pull the LLaMA 3.1 model (or another model you prefer):
```bash
ollama pull llama3.1
```

### 3. Install and run mongodb
Download and install MongoDB from the website https://www.mongodb.com/try/download/community.
Run it with:
```bash
 mongod --dbpath ~/data/db
```

### 4. Clone this repo
```bash
git clone https://github.com/DragomirMar/Knowledge_Graph.git
cd Knowledge_Graph
```

### 5. Install required libraries
```bash
pip install -r requirements.txt
```

## Run the application
### 1. Start Ollama
Firstly start Ollama either through the interface or through the terminal with the command:
```bash
ollama serve
```
This starts the Ollama server and lets you reach the model(s).

### 2. Run MongoDB 
#### (macOS / Linux)
Run the mongodb server with path to the data location:

```bash
mongod --dbpath ~/data/db
```

Make sure the data directory exists or create it with this command(only required once):
```bash
mkdir -p ~/data/db
```

### 3. Create Virtual Environment
```bash
### Navigate to the project folder
cd Knowledge_Graph

### Create a virtual environment
python -m venv venv

### Run it
source venv/bin/activate
```
On many Linux systems, python may still point to Python 2 so use  python3 as a command.

Install the requirements if not already done in Prerequisites:
```bash
pip install -r requirements.txt 
```

#### NOTE:
If pip is still using global environment run:
```bash
unalias pip
```

### 4. Run the app
Navigate to the source folder (cd src) and run:
```bash
streamlit run app.py
```