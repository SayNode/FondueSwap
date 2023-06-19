from collections import deque

# Function to find the shortest path
def find_shortest_path(trading_pairs, start_crypto, target_crypto):
    # Create a graph using the trading pairs
    graph = {}
    for pair in trading_pairs:
        source, destination = pair.split("/")
        if source not in graph:
            graph[source] = []
        if destination not in graph:
            graph[destination] = []
        graph[source].append(destination)
        graph[destination].append(source)

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
    # Define the trading pairs
    trading_pairs = [
        "BTC/ETH",
        "ETH/LTC",
        "LTC/XRP",
        "BTC/XRP",
        "ETH/BCH",
        "XRP/BCH",
        "BCH/EOS",
        "EOS/XLM",
        "EOS/ADA",
        "ADA/XLM"
    ]

    # Define the start and target cryptocurrencies
    start_crypto = "BTC"
    target_crypto = "XLM"

    # Find the shortest path to exchange one crypto for another
    path = find_shortest_path(trading_pairs, start_crypto, target_crypto)

    if path is not None:
        print("Shortest path:", " -> ".join(path))
    else:
        print("No path found.")

        