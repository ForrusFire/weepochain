from urllib.parse import urlparse


class NodeNetwork():
    def __init__(self):
        # Node list
        self.nodes = set()


    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        # Check for valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
