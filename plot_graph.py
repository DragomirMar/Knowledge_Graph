import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple

class GraphPlot:
    
    def plot(self, triples: List[Tuple[str, str, str]]) :

        # Create a directed graph
        G = nx.DiGraph()

        # Add edges (subject -> object) with predicate as label
        for subj, pred, obj in triples:
            G.add_edge(subj, obj, label=pred)

        # Position nodes with spring layout
        pos = nx.spring_layout(G)

        # Draw nodes and edges
        nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='green', node_size=2000, font_size=8)

        # Draw edge labels (the predicates)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

        # Show the graph
        plt.title("Knowledge Graph")
        # plt.tight_layout()
        plt.show()


# triples = [
#     ("Liverpool", "could receive", "transfer fee"),
#     ("Trent Alexander-Arnold", "closing in on move to", "Real Madrid"),
#     ("Trent Alexander-Arnold", "plays as", "right-back"),
#     ("Trent Alexander-Arnold", "is eager to join", "Real Madrid"),
#     ("Real Madrid", "are", "European Champions"),
#     ("Real Madrid", "are", "Spanish Champions"),
#     ("Trent Alexander-Arnold", "contract expires at", "end of June"),
#     ("Real Madrid", "have monitored", "Trent Alexander-Arnold"),
#     ("Real Madrid", "want to sign", "Trent Alexander-Arnold"),
#     ("Trent Alexander-Arnold", "will earn", "sizeable salary"),
#     ("Trent Alexander-Arnold", "will earn salary in", "Spanish capital"),
#     ("Real Madrid", "expected to acquire", "Trent Alexander-Arnold"),
#     ("Expected transfer", "type", "free transfer"),
#     ("Liverpool", "could still receive", "transfer fee"),
#     ("Real Madrid", "extremely keen to sign", "Trent Alexander-Arnold"),
#     ("Real Madrid", "want player for", "FIFA Club World Cup"),
#     ("FIFA Club World Cup", "starts on", "14 June"),
#     ("FIFA Club World Cup", "hosted in", "United States"),
#     ("Trent Alexander-Arnold", "under contract at", "Liverpool"),
#     ("Real Madrid", "must pay", "Liverpool"),
#     ("Payment to Liverpool", "required for", "early transfer"),
#     ("Trent Alexander-Arnold", "age", "26"),
#     ("Liverpool", "considers", "Trent Alexander-Arnold prized asset")
# ]


# gp = GraphPlot()
# gp.plot(triples)