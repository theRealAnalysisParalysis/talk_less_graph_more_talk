import os
from constants import *
import networkx as nx
from Classes.utils import draw_timeline_1
from Classes.Musical import Musical
import json


def read_and_load_musical():
    with open("data/song_order.json", "r") as f:
        song_order = json.load(f)
    musical = Musical('songs', song_order=song_order)
    musical.load_songs(os.listdir('songs'))
    
    return musical



if __name__ == '__main__':
    musical = read_and_load_musical()
    
    directed_g = musical.create_song_graph_with_motifs(motifs
                                              , min_k=4
                                              , motif_weight=1.5
                                              , motif_rarity_alpha=1.5
                                              , weight_threshold=0.1
                                              , directed= True
                                              )
    undirected_g = musical.create_song_graph_with_motifs(motifs
                                                       , min_k=4
                                                       , motif_weight=1.5
                                                       , motif_rarity_alpha=1.5
                                                       , weight_threshold=0.1
                                                       , directed=False
                                                       )
    
    
    components = list(nx.weakly_connected_components(directed_g))
    largest_cc = max(components, key=len)
    G_main = directed_g.subgraph(largest_cc).copy()
    # draw_timeline(G_main, spacing=5, label_offset=1.2, edge_rad_base=1, height=5)
    
    # --- create act subgraphs ---
    act1_graph = G_main.subgraph([n for n in G_main.nodes if n in act1_songs]).copy()
    act2_graph = G_main.subgraph([n for n in G_main.nodes if n in act2_songs]).copy()
    
    # --- draw Act I ---
    print("🎭 Drawing Act I...")
    draw_timeline_1(
        act1_graph,
        communities=communities,
        cmap=cmap,
        order_attr="order",
        base_node_size = 500,
        min_gap = 0.05,
        edge_rad_base=0.05,
        
    )
    
    # --- draw Act II ---
    print("🎭 Drawing Act II...")
    draw_timeline_1(
        act2_graph,
        communities=communities,
        cmap=cmap,
        order_attr="order",
    )
    
    draw_timeline_1(G_main,  label_offset=1.2, edge_rad_base=1, height=5, communities = communities, cmap = cmap)
    # nx.write_graphml(directed_g, 'outputs/directed_adj_matrix_motif_2.graphml')
    nx.write_graphml(undirected_g, 'outputs/undirected_adj_matrix_motif_2.graphml')
    # nx.write_graphml(G_main, 'outputs/directed_adj_matrix_motif_MAIN.graphml')
    print(1)
