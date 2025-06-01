from triple_extract import TripleExtractor
from plot_graph import GraphPlot as gp

text_chunk = """
Liverpool could still receive a transfer fee for Trent Alexander-Arnold this summer as he closes in on a move to Real Madrid.
Recent reports have revealed that the Liverpool right-back is eager to team up with the reigning European and Spanish champions when his contract expires at the end of June and a deal now looks inevitable.
Madrid have monitored the 26-year-old for some time and appear destined to finally land the defender, who will earn a sizeable salary in the Spanish capital.
Los Blancos were expected to acquire Alexander-Arnold on a free transfer at the beginning of July but Liverpool could yet pocket a fee for one of their prized assets, according to the Mail.
Madrid are said to be "extremely keen" to sign Alexander-Arnold before the newly-expanded FIFA Club World Cup this summer, which kicks off on 14 June when the right-back is still under contract at Liverpool.
If Alexander-Arnold is to play in the opening stages of the tournament in the United States, Madrid would be required to pay Liverpool a sum for his services.
"""
extractor = TripleExtractor()
triples = extractor.extract_triples(text_chunk)

# print(triples)
for triple in triples:
    print(triple)

gp.plot(triples)