import plotly.graph_objects as go
import pandas as pd
from pyvis.network import Network

# ==========================================
# 1. MOCK DATA SETUP
# This section mimics the exact data structure 
# your project generates from reports.
# ==========================================
class Entity:
    def __init__(self, label, value):
        self.label = label
        self.value = value

class Triplet:
    def __init__(self, subject_label, subject_value, relation, object_label, object_value):
        self.subject = Entity(subject_label, subject_value)
        self.relation = relation
        self.object = Entity(object_label, object_value)

class ExtractionResult:
    def __init__(self, triplets):
        self.triplets = triplets

# Sample Data (Based exactly on your APT-44 Neo4j Graph in Screenshot 2026-05-02 at 01.12.15.jpg)
mock_triplets = [
    Triplet("ThreatActor", "APT-44", "USES", "Malware", "CrypTox"),
    Triplet("ThreatActor", "APT-44", "EXPLOITS", "Vulnerability", "CVE-2026-9901"),
    Triplet("ThreatActor", "APT-44", "TARGETS", "Organization", "Solar Winds"),
    Triplet("ThreatActor", "APT-44", "TARGETS", "Geolocation", "Eastern Europe"),
    Triplet("ThreatActor", "APT-44", "TARGETS", "Geolocation", "North America"),
    Triplet("Malware", "CrypTox", "HAS_HASH", "FileHash", "d41d8cd98f00b204"),
    Triplet("Malware", "CrypTox", "COMMUNICATES_WITH", "C2Server", "update-check.xyz"),
    Triplet("Organization", "Solar Winds", "OWNED_BY", "Organization", "Thoma Bravo") # Added relationship for depth
]
mock_result = ExtractionResult(mock_triplets)

# Helper function to assign consistent colors per node label
def get_node_color(label):
    color_map = {
        "ThreatActor": "#FF9999",  # Red-ish
        "Malware": "#FFCC99",       # Orange-ish
        "Vulnerability": "#99FFFF", # Cyan
        "Organization": "#CCFF99",   # Light Green
        "Geolocation": "#99FF99",   # Green
        "FileHash": "#FF99FF",      # Magenta
        "C2Server": "#FFFF99"       # Yellow-ish
    }
    return color_map.get(label, "#CCCCCC") # Default Grey

# ==========================================
# OPTION 1: SANKEY DIAGRAM (Flow Layout)
# (Like the SecureClaw example in Screenshot 2026-05-02 at 01.13.37.jpg)
# ==========================================
def generate_sankey_diagram(results, filename='sankey_graph.html'):
    """
    Shows flow from left to right.
    Best for visualizing attack vectors and impact.
    """
    print(f"Generating Sankey Diagram: {filename}...")
    
    # 1. Convert to simple DataFrame
    data_list = []
    for t in results.triplets:
        data_list.append({
            'source': t.subject.value,
            'source_label': t.subject.label,
            'link_label': t.relation,
            'target': t.object.value,
            'target_label': t.object.label,
            'value': 1 # Sankeys need numerical weight, we just use 1
        })
    df = pd.DataFrame(data_list)

    # 2. Get unique nodes and map colors
    unique_source_targets = pd.unique(df[['source', 'target']].values.ravel('K'))
    node_mapping = {label: i for i, label in enumerate(unique_source_targets)}
    
    node_labels_dict = {}
    for _, row in df.iterrows():
        node_labels_dict[row['source']] = row['source_label']
        node_labels_dict[row['target']] = row['target_label']
    
    node_colors = [get_node_color(node_labels_dict.get(n_val)) for n_val in unique_source_targets]

    # 3. Create the Sankey object
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = unique_source_targets,
          color = node_colors
        ),
        link = dict(
          source = df['source'].map(node_mapping), 
          target = df['target'].map(node_mapping),
          value = df['value'],
          label = df['link_label'] # Relationship shown on hover
      ))])

    fig.update_layout(title_text="APT-44 Incident Flow Analysis (Sankey)", font_size=10)
    fig.write_html(filename)
    print("Complete. Open the file in your browser.")


# ==========================================
# OPTION 2: HIERARCHICAL TREE (Top-Down)
# (Like a Root-Cause Analysis tree)
# ==========================================
def generate_tree_graph(results, filename='tree_graph.html'):
    """
    Enforces a strict parent-child tree structure.
    Best for showing how everything stems from the root actor.
    """
    print(f"Generating Hierarchical Tree: {filename}...")
    net = Network(height='100vh', width='100%', bgcolor='#222222', font_color='white', directed=True)
    
    # Enable the specific tree algorithm
    net.set_options("""
        var options = {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "levelSeparation": 150,
              "nodeSpacing": 150,
              "treeSpacing": 200,
              "sortMethod": "directed"
            }
          },
          "physics": {
            "enabled": false
          }
        }
    """)

    for t in results.triplets:
        # Add Nodes with custom colors and labels
        net.add_node(t.subject.value, title=t.subject.label, color=get_node_color(t.subject.label), label_highlight_bold=True)
        net.add_node(t.object.value, title=t.object.label, color=get_node_color(t.object.label))
        
        # Add Directed Relationship with label
        net.add_edge(t.subject.value, t.object.value, label=t.relation, color='#aaaaaa')
    
    net.save_graph(filename)
    print("Complete. Open the file in your browser.")


# ==========================================
# OPTION 3: TARGET-CENTRIC (Circular)
# (Like spokes on a wheel)
# ==========================================
def generate_circular_graph(results, center_node_value, filename='circular_graph.html'):
    """
    Arranges nodes in a circle around a central pivot point.
    Best for profiling a specific asset (e.g., Solar Winds).
    """
    print(f"Generating Circular Graph around {center_node_value}: {filename}...")
    net = Network(height='100vh', width='100%', bgcolor='#ffffff', font_color='black', directed=True)
    
    central_pivot = center_node_value

    # Identify connections to the central pivot
    for t in results.triplets:
        involved = False
        if t.subject.value == central_pivot or t.object.value == central_pivot:
            involved = True
        
        if involved:
            # Highlight the central pivot
            net.add_node(t.subject.value, color=get_node_color(t.subject.label), shape='box' if t.subject.value == central_pivot else 'dot', size=30 if t.subject.value == central_pivot else 10)
            net.add_node(t.object.value, color=get_node_color(t.object.label), shape='box' if t.object.value == central_pivot else 'dot', size=30 if t.object.value == central_pivot else 10)
            net.add_edge(t.subject.value, t.object.value, label=t.relation, color='#aaaaaa')
            
    # Set circular layout options
    net.set_options("""
        var options = {
          "layout": {
            "improvedLayout": true
          },
          "physics": {
            "solver": "repulsion",
            "repulsion": {
                "nodeDistance": 200
            }
          }
        }
    """)
    
    net.save_graph(filename)
    print("Complete. Open the file in your browser.")

# ==========================================
# 5. EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    # Choose which graphs to generate by commenting/uncommenting below
    
    # OPTION 1: Flows from left to right
    generate_sankey_diagram(mock_result, '1_sankey_flow.html')
    
    # OPTION 2: Flows from top (APT-44) down
    generate_tree_graph(mock_result, '2_tree_hierarchy.html')
    
    # OPTION 3: Circular around a specific target (e.g., Solar Winds)
    generate_circular_graph(mock_result, center_node_value="APT-44", filename='3_circular_apt_profile.html')