"""
Market Basket Analysis - Network Visualization
===============================================
Creates network graphs showing product relationships using NetworkX and PyVis.
Node size represents product popularity (support), edge thickness represents Lift.
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import warnings
warnings.filterwarnings('ignore')


def load_rules(csv_path='association_rules.csv'):
    """Load association rules from CSV."""
    rules = pd.read_csv(csv_path)
    print(f"Loaded {len(rules)} association rules")
    return rules


def create_networkx_graph(rules, min_lift=1.5, top_n_edges=50):
    """
    Create a NetworkX graph from association rules.

    Args:
        rules: DataFrame of association rules
        min_lift: Minimum lift threshold for edges
        top_n_edges: Maximum number of edges to include

    Returns:
        NetworkX graph
    """
    # Filter rules by lift and take top N
    filtered_rules = rules[rules['Lift'] >= min_lift].nlargest(top_n_edges, 'Lift')

    G = nx.Graph()

    # Add nodes with popularity (support) as size attribute
    # Calculate product popularity from rules
    product_support = {}

    for _, row in filtered_rules.iterrows():
        antecedent = row['Antecedent (If)']
        consequent = row['Consequent (Then)']
        support = row['Support']
        lift = row['Lift']
        confidence = row['Confidence']

        # Parse items (they may be comma-separated)
        ant_items = [item.strip() for item in antecedent.split(',')]
        cons_items = [item.strip() for item in consequent.split(',')]

        all_items = ant_items + cons_items
        for item in all_items:
            if item not in product_support:
                product_support[item] = support
            else:
                product_support[item] = max(product_support[item], support)

    # Add nodes
    for product, support in product_support.items():
        # Node size proportional to support (popularity)
        size = 100 + support * 2000
        G.add_node(product, size=size, support=support, label=product)

    # Add edges with lift as weight
    for _, row in filtered_rules.iterrows():
        antecedent = row['Antecedent (If)']
        consequent = row['Consequent (Then)']
        lift = row['Lift']
        confidence = row['Confidence']
        support = row['Support']

        ant_items = [item.strip() for item in antecedent.split(',')]
        cons_items = [item.strip() for item in consequent.split(',')]

        # Create edges between all antecedent and consequent items
        for a in ant_items:
            for c in cons_items:
                if G.has_edge(a, c):
                    # Update with max lift if edge already exists
                    if G[a][c]['lift'] < lift:
                        G[a][c]['lift'] = lift
                        G[a][c]['confidence'] = confidence
                        G[a][c]['support'] = support
                else:
                    G.add_edge(a, c, lift=lift, confidence=confidence, support=support)

    print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G


def plot_static_network(G, output_path='network_graph.png'):
    """Create a static matplotlib visualization."""
    fig, ax = plt.subplots(figsize=(16, 12))

    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Node sizes based on support
    node_sizes = [G.nodes[node]['size'] for node in G.nodes()]

    # Node colors based on support (popularity)
    node_supports = [G.nodes[node]['support'] for node in G.nodes()]
    node_colors = plt.cm.YlOrRd([s / max(node_supports) for s in node_supports])

    # Edge widths based on lift
    edge_widths = [G[u][v]['lift'] * 0.5 for u, v in G.edges()]
    edge_lifts = [G[u][v]['lift'] for u, v in G.edges()]
    edge_colors = plt.cm.Blues([l / max(edge_lifts) for l in edge_lifts])

    # Draw edges
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.6, ax=ax)

    # Draw nodes
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.9, ax=ax)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)

    # Add colorbar for node popularity
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(vmin=min(node_supports), vmax=max(node_supports)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, aspect=20)
    cbar.set_label('Product Popularity (Support)', fontsize=12)

    # Add colorbar for edge lift
    sm2 = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin=min(edge_lifts), vmax=max(edge_lifts)))
    sm2.set_array([])
    cbar2 = plt.colorbar(sm2, ax=ax, shrink=0.5, aspect=20)
    cbar2.set_label('Association Strength (Lift)', fontsize=12)

    ax.set_title('Market Basket Analysis - Product Association Network\n'
                 'Node Size = Popularity | Edge Thickness = Lift', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Static network graph saved to {output_path}")


def create_interactive_network(G, output_path='network_interactive.html'):
    """Create an interactive PyVis network visualization."""
    # Create PyVis network
    net = Network(height='800px', width='100%', bgcolor='#ffffff', font_color='#333333')

    # Configure physics
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200, spring_strength=0.001, damping=0.09)

    # Add nodes
    for node in G.nodes():
        support = G.nodes[node]['support']
        size = G.nodes[node]['size']

        # Color based on support
        if support >= 0.25:
            color = '#d73027'  # Red for very popular
        elif support >= 0.15:
            color = '#fc8d59'  # Orange
        elif support >= 0.10:
            color = '#fee08b'  # Yellow
        else:
            color = '#e0f3f8'  # Light blue

        title = f"{node}<br>Support: {support:.3f}"
        net.add_node(node, label=node, title=title, size=size/10, color=color, font={'size': 12})

    # Add edges
    for u, v in G.edges():
        lift = G[u][v]['lift']
        confidence = G[u][v]['confidence']
        support = G[u][v]['support']

        # Width based on lift
        width = lift * 0.5

        # Color based on lift
        if lift >= 5:
            color = '#d73027'
        elif lift >= 2:
            color = '#fc8d59'
        else:
            color = '#91bfdb'

        title = f"Lift: {lift:.2f}<br>Confidence: {confidence:.2f}<br>Support: {support:.3f}"
        net.add_edge(u, v, title=title, width=width, color=color, arrows='')

    # Add legend
    net.show_buttons(filter_=['physics'])

    # Save
    net.save_graph(output_path)
    print(f"Interactive network saved to {output_path}")


def create_cluster_visualization(rules, output_path='cluster_analysis.png'):
    """Create a visualization showing product clusters."""
    # Filter high-lift rules
    high_lift = rules[rules['Lift'] >= 2.0].copy()

    # Build co-occurrence matrix for clustering
    all_items = set()
    for _, row in high_lift.iterrows():
        ant_items = [item.strip() for item in row['Antecedent (If)'].split(',')]
        cons_items = [item.strip() for item in row['Consequent (Then)'].split(',')]
        all_items.update(ant_items)
        all_items.update(cons_items)

    all_items = sorted(list(all_items))
    n_items = len(all_items)

    if n_items == 0:
        print("No high-lift rules for clustering")
        return

    # Create co-occurrence matrix
    co_matrix = pd.DataFrame(0, index=all_items, columns=all_items, dtype=float)

    for _, row in high_lift.iterrows():
        ant_items = [item.strip() for item in row['Antecedent (If)'].split(',')]
        cons_items = [item.strip() for item in row['Consequent (Then)'].split(',')]
        lift = row['Lift']

        for a in ant_items:
            for c in cons_items:
                co_matrix.loc[a, c] += lift
                co_matrix.loc[c, a] += lift

    # Plot heatmap
    plt.figure(figsize=(14, 12))

    # Mask diagonal
    mask = np.eye(n_items, dtype=bool)

    # Use a diverging colormap
    im = plt.imshow(co_matrix.values, cmap='RdYlBu_r', aspect='auto', interpolation='nearest')
    plt.colorbar(im, label='Association Strength (Sum of Lift)')

    plt.xticks(range(n_items), all_items, rotation=90, fontsize=8)
    plt.yticks(range(n_items), all_items, fontsize=8)
    plt.title('Product Co-occurrence Clusters (High Lift Rules)', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Cluster heatmap saved to {output_path}")


def print_network_statistics(G):
    """Print network statistics."""
    print("\n" + "=" * 60)
    print("NETWORK STATISTICS")
    print("=" * 60)
    print(f"Nodes (Products): {G.number_of_nodes()}")
    print(f"Edges (Associations): {G.number_of_edges()}")
    print(f"Density: {nx.density(G):.4f}")

    # Degree centrality (popularity in network)
    degree_cent = nx.degree_centrality(G)
    top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 Products by Network Degree Centrality:")
    for product, cent in top_degree:
        print(f"  {product}: {cent:.4f}")

    # Betweenness centrality (bridge products)
    betweenness = nx.betweenness_centrality(G)
    top_between = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 Bridge Products (Betweenness Centrality):")
    for product, cent in top_between:
        print(f"  {product}: {cent:.4f}")

    # Find connected components (clusters)
    components = list(nx.connected_components(G))
    print(f"\nNumber of Connected Components (Clusters): {len(components)}")
    for i, comp in enumerate(components):
        if len(comp) > 1:
            print(f"  Cluster {i+1} ({len(comp)} products): {', '.join(sorted(comp))}")


def main():
    """Main visualization pipeline."""
    print("\n" + "#" * 60)
    print("# MARKET BASKET ANALYSIS - NETWORK VISUALIZATION")
    print("#" * 60)

    # Load rules
    rules = load_rules()

    # Create network graph
    G = create_networkx_graph(rules, min_lift=1.5, top_n_edges=60)

    # Print statistics
    print_network_statistics(G)

    # Create static visualization
    plot_static_network(G, 'network_graph.png')

    # Create interactive visualization
    create_interactive_network(G, 'network_interactive.html')

    # Create cluster heatmap
    create_cluster_visualization(rules, 'cluster_analysis.png')

    print("\n" + "#" * 60)
    print("# VISUALIZATION COMPLETE")
    print("#" * 60)


if __name__ == "__main__":
    main()