import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

def generate_random_graph():
    """Generate a random graph with 10 nodes and 10-14 edges"""
    G = nx.Graph()
    nodes = list(range(10))
    G.add_nodes_from(nodes)
    
    # Add random edges
    edges_to_add = random.randint(10, 14)
    while G.number_of_edges() < edges_to_add:
        n1, n2 = random.sample(nodes, 2)
        G.add_edge(n1, n2)
    
    return G

def create_adjacency_dictionary(G):
    """Create adjacency dictionary from the graph"""
    adj_dict = {}
    for node in G.nodes():
        adj_dict[node] = list(G.neighbors(node))
    
    # Print the adjacency dictionary
    print("Adjacency Dictionary:")
    for node, neighbors in adj_dict.items():
        print(f"Node {node} -> {neighbors}")
    
    return adj_dict

class GraphTraversal:
    """Class implementing different graph traversal algorithms"""
    
    def __init__(self, adj_dict):
        self.adj_dict = adj_dict
    
    def dfs_iterative(self, start):
        """Depth-First Search using an iterative approach with a stack"""
        visited = []
        stack = [start]
        
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.append(node)
                # Add neighbors in reverse to maintain a similar order to recursive DFS
                neighbors = sorted(self.adj_dict[node], reverse=True)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return visited
    
    def bfs(self, start):
        """Breadth-First Search (Level-Order traversal)"""
        visited = []
        queue = [start]
        
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.append(node)
                for neighbor in self.adj_dict[node]:
                    if neighbor not in visited and neighbor not in queue:
                        queue.append(neighbor)
        
        return visited

def visualize_graph(G):
    """Visualize the graph"""
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    # Add edge labels showing the edge index
    edge_labels = {(u, v): f"{i}" for i, (u, v) in enumerate(G.edges())}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    plt.title("Random Graph with 10 Nodes", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('graph_visualization.png')
    plt.close()

def solve_economic_network(G, total_budget=10):
    """
    Solve the economic network optimization problem
    Maximize the aggregate welfare function sum(log(1/d_i + x_i))
    subject to sum(x_i) = B_t and x_i >= 0
    """
    # Get degrees of all nodes
    degrees = {node: G.degree(node) for node in G.nodes()}
    
    # Calculate inverse degree sum
    inverse_degree_sum = sum(1/degree for degree in degrees.values())
    
    # Calculate lambda (Lagrange multiplier)
    n = len(G.nodes())
    lambda_value = n / (total_budget + inverse_degree_sum)
    
    # Calculate optimal allocation
    allocations = {}
    for node, degree in degrees.items():
        allocation = max(0, 1/lambda_value - 1/degree)
        allocations[node] = allocation
    
    print(f"\nOptimal Budget Allocation (Total Budget = {total_budget}):")
    for node, allocation in allocations.items():
        print(f"Node {node} (degree {degrees[node]}): {allocation:.4f}")
    
    # Verify that the allocations sum to the total budget
    allocation_sum = sum(allocations.values())
    print(f"Sum of allocations: {allocation_sum:.4f} (should be close to {total_budget})")
    
    # Create a bar plot of allocations
    plt.figure(figsize=(12, 6))
    nodes = list(allocations.keys())
    values = list(allocations.values())
    
    # Sort by node ID for clearer presentation
    sorted_indices = sorted(range(len(nodes)), key=lambda i: nodes[i])
    sorted_nodes = [nodes[i] for i in sorted_indices]
    sorted_values = [values[i] for i in sorted_indices]
    sorted_degrees = [degrees[node] for node in sorted_nodes]
    
    # Create the bar chart
    bars = plt.bar(range(len(sorted_nodes)), sorted_values, tick_label=sorted_nodes)
    
    # Add degree labels on top of bars
    for i, (bar, degree) in enumerate(zip(bars, sorted_degrees)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f"d={degree}", ha='center', fontsize=10)
    
    plt.xlabel('Node', fontsize=12)
    plt.ylabel('Budget Allocation', fontsize=12)
    plt.title('Optimal Budget Allocation by Node with Degree Indicators', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('budget_allocation.png')
    
    return allocations, lambda_value, degrees

def modified_optimization_problem():
    """
    Describe the modified optimization problem with minimum payoff constraint
    max ∑ log(1/d_i + x_i)
    subject to:
    - ∑ x_i = B_t
    - x_i ≥ 0 for all i
    - log(1/d_i + x_i) ≥ ϕ_min for all i
    """
    print("\nModified Optimization Problem with Minimum Payoff Constraint:")
    print("Maximize: ∑ log(1/d_i + x_i)")
    print("Subject to:")
    print("- ∑ x_i = B_t")
    print("- x_i ≥ 0 for all i")
    print("- log(1/d_i + x_i) ≥ ϕ_min for all i")
    print("\nThe last constraint can be rewritten as:")
    print("- x_i ≥ max(0, e^ϕ_min - 1/d_i) for all i")
    print("\nThis ensures every node receives sufficient budget to achieve at least")
    print("the minimum required payoff ϕ_min, while still optimizing overall welfare.")

def main():
    # Generate random graph
    G = generate_random_graph()
    
    # Create adjacency dictionary
    adj_dict = create_adjacency_dictionary(G)
    
    # Visualize the graph
    visualize_graph(G)
    
    # Create graph traversal object
    traversal = GraphTraversal(adj_dict)
    
    # Run DFS and BFS from node 0
    start_node = 0
    dfs_result = traversal.dfs_iterative(start_node)
    bfs_result = traversal.bfs(start_node)
    
    print(f"\nDFS Traversal from node {start_node}: {dfs_result}")
    print(f"BFS Traversal from node {start_node}: {bfs_result}")
    
    print("\nObservations:")
    print("DFS explores deeply into branches before backtracking, which tends to find paths to far nodes first.")
    print("BFS explores all nodes at the current depth before moving deeper, finding shortest paths first.")
    
    # Solve the economic network optimization problem
    allocations, lambda_value, degrees = solve_economic_network(G)
    
    # Describe the modified optimization problem
    modified_optimization_problem()

if __name__ == "__main__":
    main()