import streamlit as st
import io
import networkx as nx
from ner_module import extract_entities
from relation_module import extract_relations
from graph_module import build_graph, draw_graph
from utils import extract_text_from_file

st.set_page_config(page_title="Knowledge Graph Builder", layout="wide")
st.title("Knowledge Graph Builder")

# Tabs for input types
tab1, tab2 = st.tabs(["Text Input", "Upload File(s)"])
file_text = ""
texts = []

with tab1:
    user_text = st.text_area("Enter your text here:")

with tab2:
    uploaded_files = st.file_uploader("Upload TXT, PDF, or DOCX", type=["txt", "pdf", "docx"], accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        text = extract_text_from_file(uploaded_file)
        texts.append(text)
    if texts:
        file_text = "\n".join(texts)
        st.text_area("File Content", value=file_text, height=300)

final_text = user_text if user_text.strip() else file_text

if final_text and st.button("\U0001F50D Generate Knowledge Graph"):
    entities = extract_entities(final_text)
    relations = extract_relations(final_text)
    G = build_graph(entities, relations)
    draw_graph(G)

    st.subheader("\U0001F4CA Graph Metrics")
    st.write(f"Nodes: {G.number_of_nodes()}")
    st.write(f"Edges: {G.number_of_edges()}")
    st.write(f"Density: {nx.density(G):.4f}")

    relations = extract_relations(text)
    # GEXF (binary)
    gexf_io = io.BytesIO()
    nx.write_gexf(G, gexf_io)
    gexf_bytes = gexf_io.getvalue()
    st.download_button("⬇️ Download GEXF", data=gexf_bytes, file_name="graph.gexf", mime="application/xml")

# CSV (text)
    csv_io = io.BytesIO()
    nx.write_edgelist(G, csv_io, delimiter=",")
    csv_str = csv_io.getvalue().decode("utf-8")

    st.download_button("⬇️ Download CSV", data=csv_str, file_name="graph.csv", mime="text/csv")