# server.py

from livereload import Server

# Initialize the server
server = Server()

# Watch the specified HTML files for changes
server.watch("index.html")
server.watch("action_graph.html")

# Serve files from the current directory on port 5500
server.serve(root=".", port=5500)
