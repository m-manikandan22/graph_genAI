import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

def build_graph(entities, relations):
    G = nx.DiGraph()
    entity_map = {ent["text"].lower(): ent for ent in entities}

    # Add all named entities
    for ent in entities:
        G.add_node(ent["text"], label=ent["text"], tooltip=ent["label"])

    # Add relations (even if not in named entities)
    for rel in relations:
        src = rel["source"]
        tgt = rel["target"]

        if src.lower() not in entity_map:
            G.add_node(src, label=src, tooltip="GENERIC")
        if tgt.lower() not in entity_map:
            G.add_node(tgt, label=tgt, tooltip="GENERIC")

        G.add_edge(src, tgt, label=rel["relation"], confidence=rel.get("confidence", 0.8))

    return G


def draw_graph(G):
    net = Network(height="850px", width="100%", directed=True)
    pos = nx.spring_layout(G, seed=42, k=3.0, iterations=200)

    color_map = {
        "PERSON": "#66c2a5",
        "ORG": "#fc8d62",
        "GPE": "#8da0cb",
        "PRODUCT": "#e78ac3",
        "EVENT": "#a6d854"
    }

    for node, data in G.nodes(data=True):
        x, y = pos[node]
        label = data.get("label", node)
        tooltip = data.get("tooltip", "")
        color = color_map.get(tooltip.upper(), "#a6cee3")
        node_size = max(400, min(1000, len(label) * 150))

        node_size = max(200, min(600, len(label) * 80))  # tighter size

        net.add_node(
    node,
    label=label,
    title=tooltip,
    shape="ellipse",
    size=node_size,
    color={"background": color, "border": "#1f78b4"},
    font={"size": 20, "color": "#000000", "face": "Arial"},
    widthConstraint={"minimum": 100, "maximum": 400},
    physics=True
)



    for src, dst, data in G.edges(data=True):
        label = data.get("label", "related_to")
        confidence = data.get("confidence", 0.8)
        relation = f"{label} ({confidence:.2f})"

        net.add_edge(
    src, dst,
    label=relation,
    title=relation,
    arrows="to",
    font={"align": "top", "size": 25, "face": "Arial"},
    color="#333",
    width=4,
    smooth={"enabled": True, "type": "curvedCW"}
)

        net.set_edge_smooth("dynamic")


    net.set_options("""
{
  "layout": {
    "improvedLayout": true
  },
  "physics": {
    "enabled": true,
    "stabilization": {
      "enabled": true,
      "iterations": 200
    },
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -150,
      "centralGravity": 0.01,
      "springLength": 250,
      "springConstant": 0.05
    }
  },
  "edges": {
    "smooth": {
      "enabled": true,
      "type": "dynamic"
    },
    "color": {
      "inherit": false
    }
  },
  "interaction": {
    "dragNodes": true,
    "dragView": true,
    "zoomView": true,
    "navigationButtons": true,
    "hover": true
  }
}
""")


    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("</script>", """
    network.fit();

    // Prevent zooming out too far or in too close
    network.on("zoom", function () {
      const MIN_ZOOM = 0.3;
      const MAX_ZOOM = 2.0;
      const scale = network.getScale();

      if (scale < MIN_ZOOM) {
        network.moveTo({ scale: MIN_ZOOM });
      } else if (scale > MAX_ZOOM) {
        network.moveTo({ scale: MAX_ZOOM });
      }
    });
</script>""")



    components.html(html, height=850, scrolling=True)
