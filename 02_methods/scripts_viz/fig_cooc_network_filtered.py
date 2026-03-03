#!/usr/bin/env python3
"""
fig_cooc_network_filtered.py - Network visualization: co-occurring terms with Louvain detection
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from networkx.algorithms import community
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_export import save_figure_variants


def network_cooc_filtered(cooc_pairs_path, outdir, min_cooc=20, dpi=300):
    """Generate filtered co-occurrence network with static + interactive outputs"""
    
    df_cooc = pd.read_csv(cooc_pairs_path)
    
    # Filter by minimum co-occurrence threshold
    df_filtered = df_cooc[df_cooc['n_cooc'] >= min_cooc].copy()
    
    # Build graph
    G = nx.Graph()
    
    for _, row in df_filtered.iterrows():
        G.add_edge(row['term_1'], row['term_2'], weight=row['n_cooc'])
    
    print(f"Network: {len(G.nodes())} nodes, {len(G.edges())} edges (min_cooc ≥ {min_cooc})")
    
    # Detect communities (Louvain)
    communities_gen = community.greedy_modularity_communities(G)
    
    # Assign community IDs
    community_map = {}
    for comm_id, comm in enumerate(communities_gen):
        for node in comm:
            community_map[node] = comm_id
    
    # Use spring layout with seed for reproducibility
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42, weight='weight')
    
    # Node sizes based on degree
    node_sizes = [G.degree(node) * 300 for node in G.nodes()]
    
    # Colors by community
    node_colors = [community_map.get(node, -1) for node in G.nodes()]
    
    # Generate static visualization (PNG)
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        width=0.5,
        alpha=0.3,
        edge_color='gray',
        ax=ax
    )
    
    # Draw nodes
    nodes = nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=node_colors,
        cmap='tab20',
        alpha=0.8,
        ax=ax
    )
    
    # Draw labels (top N nodes by degree, others hidden for clarity)
    top_n_labels = 15
    top_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:top_n_labels]
    
    labels = {node: node if node in top_nodes else '' for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=8,
        font_weight='bold',
        font_color='#333',
        ax=ax
    )
    
    ax.set_title(
        f'Term Co-occurrence Network (min_cooc≥{min_cooc}, {len(communities_gen)} communities)',
        fontsize=12, fontweight='bold'
    )
    ax.axis('off')
    
    plt.tight_layout()
    
    base_path = Path(outdir) / "fig_cooc_network_filtered"
    save_figure_variants(fig, base_path, dpi=dpi, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    
    plt.close()
    
    # Generate interactive HTML (pyvis)
    try:
        import pyvis.network as net
        
        # Create pyvis network
        g_pyvis = net.Network(
            height='800px',
            width='100%',
            directed=False,
            notebook=False
        )
        
        # Add nodes with colors and titles
        for node in G.nodes():
            degree = G.degree(node)
            comm = community_map.get(node, 0)
            g_pyvis.add_node(
                node,
                label=node,
                title=f"{node} (degree: {degree})",
                size=min(50, 20 + degree * 5),
                color=plt.cm.tab20(comm % 20),
                font={'size': 10}
            )
        
        # Add edges with weights as physics
        for edge in G.edges(data=True):
            term1, term2, attr = edge
            weight = attr.get('weight', 1)
            g_pyvis.add_edge(
                term1, term2,
                weight=weight,
                title=f"{weight} co-occurrences"
            )
        
        # Configure physics
        g_pyvis.show_buttons(filter_=['physics'])
        g_pyvis.toggle_physics(True)
        
        html_path = Path(outdir) / "cooc_network_interactive.html"
        g_pyvis.show(str(html_path))
        print(f"✅ {html_path} (interactive network)")
        
    except ImportError:
        print("⚠️  pyvis not installed (optional). Skipping interactive HTML.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cooc-pairs', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--min-cooc', type=int, default=20)
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PNG output (default: 300)')
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    network_cooc_filtered(args.cooc_pairs, args.outdir, args.min_cooc, dpi=args.dpi)
