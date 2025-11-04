# Knowledge_Graph

A program for extracting, managing, and visualizing knowledge graphs from documents and web content. Built with Streamlit and powered by large language models for intelligent entity and relationship extraction..

## Prerequisites

Before you get started, ensure you have the following installed on your machine:

- [Ollama](https://ollama.com) (for running LLMs locally)
- Python 3.11 or higher
- mongoDB (database to save nodes and relationships)

## Setup and installation

Follow these steps to get started:

### 1. Install Ollama
Download and install [Ollama](https://ollama.com), which is required to run models locally.

### 2. Pull LLaMA 3 (or another model)
Once Ollama is installed, pull the LLaMA 3 model (or another model you prefer):
```bash
ollama pull llama3
```

### 3. Install and run mongodb
Download and install from the website https://www.mongodb.com/try/download/community.
Run it with:
```bash
 mongod --dbpath ~/data/db
```

### 3. Clone this repo
```bash
git clone https://github.com/DragomirMar/Knowledge_Graph.git
cd Knowledge_Graph
```

### 4. Install required libraries
```bash
pip install -r requirements.txt
```

## Run the application
```bash
streamlit run app.py
```

## Run in virtual environment
```bash
venv/bin/python main.py
```
