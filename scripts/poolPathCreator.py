from collections import deque

# Function to find the shortest path
def find_shortest_path(trading_pairs, start_crypto, target_crypto):
    # Create a graph using the trading pairs and weights
    graph = {}
    weights = {}
    
    for pair in trading_pairs:
        source, destination, weight = pair.split("/")
        if source not in graph:
            graph[source] = []
        if destination not in graph:
            graph[destination] = []
        graph[source].append(destination)
        graph[destination].append(source)
        weights[(source, destination)] = float(weight)
        weights[(destination, source)] = float(weight)

    # Perform BFS to find the shortest path
    queue = deque([(start_crypto, [])])
    visited = set()

    while queue:
        current_crypto, path = queue.popleft()
        if current_crypto == target_crypto:
            return path + [current_crypto]

        if current_crypto in visited:
            continue

        visited.add(current_crypto)

        if current_crypto not in graph:
            continue

        for neighbor in graph[current_crypto]:
            queue.append((neighbor, path + [current_crypto]))

    return None


# Example usage
if __name__ == "__main__":
    # Define the trading pairs and their weights
    trading_pairs = [
        "ETH/USDT/3000",
        "USDC/USDT/100",
        "LINK/USDC/500",
        "ETH/USDC/500",
        "ETH/BCH/500",
    ]

    # Define the start and target cryptocurrencies
    start_crypto = "ETH"
    target_crypto = "LINK"

    # Find the shortest path to exchange one crypto for another
    path = find_shortest_path(trading_pairs, start_crypto, target_crypto)

    if path is not None:
        print("Shortest path:", " -> ".join(path))
    else:
        print("No path found.")


        