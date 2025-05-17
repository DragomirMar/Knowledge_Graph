# Knowledge_Graph

A program that takes pdf files or urls and generates a Knowledge Graph from the text in them and shows it.

## Prerequisites

Before you get started, ensure you have the following installed on your machine:

- [Ollama](https://ollama.com) (for running LLMs locally)
- Python 3.11 or higher

## Setup and installation

Follow these steps to get started:

### 1. Install Ollama
Download and install [Ollama](https://ollama.com), which is required to run models locally.

### 2. Pull LLaMA 3 (or another model)
Once Ollama is installed, pull the LLaMA 3 model (or another model you prefer):
```bash
ollama pull llama3
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
python main.py
```

## Run in virtual environment
```bash
venv/bin/python main.py
```
