from extract_text import TextHandler
from triple_extract import TripleExtractor
from typing import List, Tuple
from plot_graph import GraphPlot

# Test URLs
url = 'https://www.90min.com/why-liverpool-could-still-receive-trent-alexander-arnold-transfer-fee'
url1 = 'https://www.formula1.com/en/latest/article/piastri-storms-to-controlled-victory-in-bahrain-grand-prix-ahead-of-russell.47YQh0Ex2gkZcx58fRaRqJ'
url2 = 'https://www.tandfonline.com/doi/abs/10.1080/0264041031000102105'

pdf_file_path = 'data/Formula.pdf'

#Extract and chunk text
handler = TextHandler()
chunks_pdf = handler.extract_from_pdf(pdf_file_path)
print(len(chunks_pdf))

#Extract triples
extractor = TripleExtractor()

all_triples: List[Tuple[str, str, str]] = []

for i, chunk in enumerate(chunks_pdf[:10]): #get only first 10 results
    tuples_list = extractor.extract_triples(chunk)  
    for triple in tuples_list:
        all_triples.append(triple)

print(len(all_triples))

#Show graph
gp = GraphPlot()
gp.plot(all_triples)