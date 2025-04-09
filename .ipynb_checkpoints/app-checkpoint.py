from flask import Flask, request, Response, render_template_string
from rdflib import Graph
import matplotlib.pyplot as plt
import networkx as nx
import io

app = Flask(__name__)

# Load RDF graph once
rdf_graph = Graph()
rdf_graph.parse("FraudDetection.rdf", format="turtle")

# Get a list of unique subjects (entities)
entities = sorted(set(str(s) for s in rdf_graph.subjects()))

def generate_kg_image(entity_uri):
    G = nx.DiGraph()

    # Add triples involving the selected entity
    for s, p, o in rdf_graph:
        if str(s) == entity_uri or str(o) == entity_uri:
            G.add_edge(str(s), str(o), label=str(p))

    # Draw the graph
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', ax=ax, node_size=2500, font_size=8)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    plt.axis('off')

    # Return image in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

@app.route("/")
def index():
    return render_template_string('''
        <html>
            <head><title>🧠 Knowledge Graph Viewer</title></head>
            <body style="background:#1E1E2C; color:white; text-align:center;">
                <h2>Fraud Knowledge Graph Explorer</h2>
                <form onsubmit="event.preventDefault(); updateGraph();">
                    <select id="entity" name="entity">
                        {% for entity in entities %}
                            <option value="{{ entity }}">{{ entity }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">Show</button>
                </form>
                <br>
                <img id="graphImage" src="/graph?entity={{ entities[0] }}" width="800" />
                <script>
                    function updateGraph() {
                        const selected = document.getElementById('entity').value;
                        document.getElementById('graphImage').src = '/graph?entity=' + encodeURIComponent(selected) + '&t=' + new Date().getTime();
                    }
                </script>
            </body>
        </html>
    ''', entities=entities)

@app.route("/graph")
def graph():
    entity = request.args.get("entity", "")
    buf = generate_kg_image(entity)
    return Response(buf.getvalue(), mimetype='image/png')

if __name__ == "__main__":
    app.run(port=5050)
