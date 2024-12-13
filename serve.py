from livereload import Server
from flask import Flask, send_file, make_response

# Create Flask app first
app = Flask(__name__)
app.debug = True

# Initialize the server with the Flask app
server = Server(app.wsgi_app)


@app.route("/index.css")
def serve_index_css():
    return send_file("index.css")


# Add custom route to the Flask app, not the server
@app.route("/<color>")
def serve_red(color: str):
    response = make_response(send_file(f"action_graph_{color}.html"))
    response.headers["Content-Type"] = "text/html"
    return response


@app.route("/")
def serve_index():
    return send_file("index.html")


# Watch the specified HTML files for changes
server.watch("index.html")
server.watch("action_graph_red.html")
server.watch("action_graph_orange.html")
server.watch("action_graph_white.html")
server.watch("action_graph_blue.html")

# Serve files from the current directory on port 5500
server.serve(root=".", port=5500)
