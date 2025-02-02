import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
import numpy as np
from pathlib import Path

def create_network_graph():
    """Create interactive network visualization of traffic intersections"""
    # Read traffic network data
    df = pd.read_csv('data/traffic_network.csv')
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes
    for _, row in df.iterrows():
        G.add_node(row['SCATS Number'], 
                  pos=(row['Longitude'], row['Latitude']),
                  desc=row['Site Description'])
        
        # Add edges from neighbours
        neighbours = str(row['Neighbours']).split(';')
        for neighbour in neighbours:
            if neighbour.isdigit():
                G.add_edge(row['SCATS Number'], int(neighbour))
    
    # Get node positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Create plotly figure
    fig = go.Figure()
    
    # Add edges as lines
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Connections'
    ))
    
    # Add nodes as points
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hovertext=[f"{node}\n{nx.get_node_attributes(G, 'desc')[node]}" for node in G.nodes()],
        text=[str(node) for node in G.nodes()],
        textposition="top center",
        marker=dict(
            size=10,
            color='#1f77b4',
            line_width=2
        ),
        name='Intersections'
    ))
    
    fig.update_layout(
        title='Traffic Network Graph',
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40)
    )
    
    fig.write_html('visualizations/traffic_network_interactive.html')

def create_connectivity_heatmap():
    """Create heatmap showing intersection connectivity patterns"""
    df = pd.read_csv('data/traffic_network.csv')
    
    # Create adjacency matrix
    nodes = df['SCATS Number'].tolist()
    n = len(nodes)
    adj_matrix = np.zeros((n, n))
    
    # Fill adjacency matrix
    for idx, row in df.iterrows():
        neighbours = str(row['Neighbours']).split(';')
        for neighbour in neighbours:
            if neighbour.isdigit():
                neighbour_idx = nodes.index(int(neighbour))
                adj_matrix[idx][neighbour_idx] = 1
                adj_matrix[neighbour_idx][idx] = 1
    
    # Create heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(adj_matrix, 
                xticklabels=nodes,
                yticklabels=nodes,
                cmap='YlOrRd')
    plt.title('Intersection Connectivity Matrix')
    plt.xlabel('Intersection ID')
    plt.ylabel('Intersection ID')
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('visualizations/connectivity_heatmap.png')
    plt.close()

def create_geographical_plot():
    """Create geographical scatter plot of intersections"""
    df = pd.read_csv('data/traffic_network.csv')
    
    fig = px.scatter_map(
        df,
        lat='Latitude', 
        lon='Longitude',
        hover_name='Site Description',
        hover_data=['SCATS Number', 'Site Type'],
        color='Site Type',
        zoom=12,
        title='Traffic Intersection Locations'
    )
    
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    fig.write_html('visualizations/geographical_plot.html')

def create_connectivity_analysis():
    """Create visualization showing connectivity statistics"""
    df = pd.read_csv('data/traffic_network.csv')
    
    # Calculate number of connections per intersection
    df['Connection_Count'] = df['Neighbours'].str.count(';') + 1
    
    plt.figure(figsize=(12, 6))
    
    # Plot distribution of connections
    sns.histplot(data=df, x='Connection_Count', bins=range(1, df['Connection_Count'].max()+2))
    plt.title('Distribution of Intersection Connections')
    plt.xlabel('Number of Connected Intersections')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('visualizations/connectivity_distribution.png')
    plt.close()

def main():
    # Create visualizations directory if it doesn't exist
    Path('visualizations').mkdir(exist_ok=True)
    
    # Generate all visualizations
    create_network_graph()
    create_connectivity_heatmap()
    create_geographical_plot()
    create_connectivity_analysis()

if __name__ == '__main__':
    main()
