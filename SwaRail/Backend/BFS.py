# Major TODO :- Use async BFS to find connectivity for each node to all other nodes
# To speed up the process and reduce some processing time

from queue import Queue
from SwaRail import Database


def connectivity_BFS(source : str, direction: str, key_nodes: set[str]):
    queue = Queue(maxsize=0)
    queue.put(source)
    visited = {source}

    while not queue.empty():
        node_id = queue.get()

        if node_id in key_nodes:
            Database.add_connectivity(source, node_id)

        for neighbour_id in Database.get_node(node_id).get_neighbours(direction):
            if not neighbour_id in visited:
                queue.put(neighbour_id)
                visited.add(neighbour_id)