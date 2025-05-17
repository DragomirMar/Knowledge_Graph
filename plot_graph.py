import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List, Tuple
import textwrap

class GraphPlot:

    def plot(self, triples: List[Tuple[str, str, str]]):
        G = nx.DiGraph()

        # Add triples
        for subj, pred, obj in triples:
            G.add_edge(subj, obj, label=pred)

        # Wrap long labels
        wrap_width = 20
        wrapped_labels = {
            node: "\n".join(textwrap.wrap(str(node), width=wrap_width))
            for node in G.nodes()
        }

        # Choose Graphviz layout tuned for large graphs
        pos = graphviz_layout(
            G,
            prog="sfdp",
            args='-Goverlap=prism2 -Gsep=0.5'  
        )

        # Dynamically size figure based on graph size
        n_nodes = G.number_of_nodes()
        fig_w = max(12, n_nodes * 0.2)
        fig_h = max(8, n_nodes * 0.15)
        plt.figure(figsize=(fig_w, fig_h), dpi=100)

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_color="lightgreen",
            node_size=1400,
            linewidths=0.5,
            edgecolors="lightgreen"
        )

        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color='green',
            arrowsize=20,
            arrowstyle='-|>'
        )

        # Draw node labels
        nx.draw_networkx_labels(
            G, pos,
            labels=wrapped_labels,
            font_size= max(8, 200 // n_nodes)
        )

        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        wrapped_edge_labels = {
            (u, v): "\n".join(textwrap.wrap(lbl, width=wrap_width))
            for (u, v), lbl in edge_labels.items()
        }
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=wrapped_edge_labels,
            font_color='red',
            font_size= max(6, 150 // n_nodes)
        )

        plt.title("Knowledge Graph", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        plt.show()


## Local Test of the Graph Visualisation 

# triples = [
#     ("Kylian Mbappé", "is close to joining", "Real Madrid"),
#     ("Kylian Mbappé", "currently plays for", "Paris Saint-Germain"),
#     ("Kylian Mbappé", "is regarded as", "one of the best forwards"),
#     ("Real Madrid", "have pursued", "Kylian Mbappé for years"),
#     ("Real Madrid", "offered", "record-breaking contract"),
#     ("Contract offer", "includes", "performance-based bonuses"),
#     ("Mbappé's entourage", "negotiated with", "Real Madrid representatives"),
#     ("Paris Saint-Germain", "attempted to renew", "Mbappé's contract"),
#     ("Mbappé", "rejected", "PSG’s final extension offer"),
#     ("PSG", "fear losing", "Mbappé on free transfer"),
#     ("Mbappé", "was signed from", "Monaco"),
#     ("Real Madrid", "have scouted", "Mbappé extensively"),
#     ("Mbappé", "has admiration for", "Zinedine Zidane"),
#     ("Zidane", "was", "Real Madrid legend"),
#     ("Mbappé", "grew up watching", "Cristiano Ronaldo at Real Madrid"),
#     ("Mbappé", "believes move will boost", "Ballon d'Or chances"),
#     ("Mbappé", "scored", "42 goals this season"),
#     ("PSG", "value Mbappé at", "€200 million"),
#     ("Real Madrid", "prefer to wait for", "contract expiration"),
#     ("Mbappé’s contract", "expires in", "July 2025"),
#     ("Real Madrid board", "divided over", "paying fee or waiting"),
#     ("Mbappé", "could wear", "number 7 jersey at Madrid"),
#     ("Vinicius Jr", "currently wears", "number 7 jersey"),
#     ("Ancelotti", "approves", "Mbappé signing"),
#     ("Florentino Pérez", "personally involved in", "Mbappé deal"),
#     ("Mbappé’s mother", "acts as", "his agent"),
#     ("Mbappé", "demands", "image rights control"),
#     ("Image rights", "complicate", "contract negotiations"),
#     ("Real Madrid", "typically retain", "50% image rights"),
#     ("Mbappé", "wants to play in", "Champions League final"),
#     ("Mbappé", "hopes to join before", "preseason tour in Asia"),
#     ("Real Madrid", "planning medical in", "Madrid"),
#     ("PSG", "refuse to release", "Mbappé early"),
#     ("FIFA regulations", "allow", "pre-contract agreement"),
#     ("Mbappé", "already signed", "pre-contract with Madrid"),
#     ("Mbappé", "expected to debut in", "El Clásico"),
#     ("Barcelona", "aware of", "Madrid's plans"),
#     ("Barcelona president", "criticized", "Mbappé's high wages"),
#     ("Mbappé", "remains focused on", "PSG’s current campaign"),
#     ("Mbappé", "was benched in", "last league match"),
#     ("PSG coach", "refused to comment on", "Mbappé’s future"),
#     ("Mbappé", "publicly thanked", "PSG fans"),
#     ("PSG ultras", "unhappy with", "Mbappé's decision"),
#     ("Mbappé", "will earn", "€25 million annually"),
#     ("Contract duration", "expected to be", "5 years"),
#     ("Madrid fans", "excited by", "Mbappé’s potential arrival"),
#     ("Spanish media", "report daily updates on", "Mbappé transfer saga"),
#     ("Mbappé", "will attend", "official unveiling at Bernabéu"),
#     ("Presentation event", "planned for", "mid-July"),
#     ("Mbappé", "may join", "Olympic squad for France"),
#     ("Real Madrid", "unwilling to release", "player for Olympics"),
#     ("Olympic participation", "not mandatory under", "FIFA rules"),
#     ("Mbappé", "likely to skip", "Paris 2024 Olympics"),
#     ("Mbappé", "expects", "warm reception from Madrid fans")
# ]


# gp = GraphPlot()
# gp.plot(triples)