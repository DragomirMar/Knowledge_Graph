from extract_text import *
from llm import OllamaModel
from typing import List, Tuple
from plot_graph import GraphPlot
from io import BytesIO

# Test Data
url = 'https://www.90min.com/why-liverpool-could-still-receive-trent-alexander-arnold-transfer-fee'
url1 = 'https://www.formula1.com/en/latest/article/piastri-storms-to-controlled-victory-in-bahrain-grand-prix-ahead-of-russell.47YQh0Ex2gkZcx58fRaRqJ'
url2 = 'https://www.tandfonline.com/doi/abs/10.1080/0264041031000102105'
pdf_file_path = '../data/Formula.pdf'

with open(pdf_file_path, 'rb') as f:
    file_like = BytesIO(f.read())

#Extract and chunk text
chunks_pdf = extract_from_pdf(file_like)
print(len(chunks_pdf))

#Extract triples
llm = OllamaModel()

all_triples: List[Tuple[str, str, str]] = []

for i, chunk in enumerate(chunks_pdf[:10]): #get only first 10 results
    tuples_list = llm.extract_triples(chunk)  
    for triple in tuples_list:
        all_triples.append(triple)

print(len(all_triples))

#Show graph
gp = GraphPlot()
gp.plot(all_triples)