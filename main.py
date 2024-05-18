import numpy as np
import pyvista as pv
import networkx as nx
import re

def parse_cif_to_graph(filename):
    """ Parses a CIF file and creates a graph representation with layer information. """
    graph = nx.Graph()
    current_layer = None
    node_id = 0
    
    with open(filename, 'r') as file:
        for line in file:
            # print("Processing line:", line.strip()) # Debug
            line = line.strip()
            if line.startswith('L '):
                # print("Current layer set to:", current_layer) # Debug
                current_layer = line.split()[1].replace(';', '')
            elif line.startswith('P '):
                points = tuple(map(int, re.findall(r'-?\d+', line)))
                # print("Points found:", points) # Debug
                if len(points) >= 6 and len(set(points)) > 1:
                    graph.add_node(node_id, layer=current_layer, points=points)
                    # print("Node added:", node_id, "Layer:", current_layer, "Points:", points) # Debug
                    node_id += 1
                    
            elif line.startswith('4N '):
                parts = line.split()
                layer = re.sub(r'\d+', '', parts[1])  # Remove digits from the layer
                points = tuple(map(int, [part.replace(';', '') for part in parts[2:]]))
                # print("4N Points found:", points)  # Debug
                graph.add_node(node_id, layer=layer, points=points)
                # print("4N Node added:", node_id, "Layer:", layer, "Points:", points)  # Debug
                node_id += 1
                
    return graph

def create_3d_plot(graph):
    plotter = pv.Plotter(notebook=False)
    
    layer_order = [ 'KN', 'CM1', 'CM2', 'CSI', 'P', 'NA', 'NE', 'PE', 'CPA', 'CNA', 'CPE', 'CNE',  'SP',  "SN", 'SI', 'M1', 'M2', 'C', 'E', 'S', 'TN', 'TP', 'X', 'Y', 'ZERO']
    layer_thickness = 50  # Thickness of each layer to create the appearance of a brick
    spike_thickness = 500  # Thickness for spikes
    spike_width = 20  # Width for the spike
    layer_z_coordinates = {layer: i * len(layer_order) for i, layer in enumerate(layer_order)}
    layer_colors = {
        # L:
        'KN': [200, 0, 0],
        'CM1': 'black',
        'CM2': 'cyan',
        'CSI': 'orange',
        'P': 'blue',
        'NA': 'red',
        'NE': 'lightblue',
        'PE': 'yellow',
        'CPA': 'yellow',
        'CNA': 'pink',
        'CPE': 'brown',
        'CNE': 'lightgreen',
        'SP': 'grey',
        'SN': 'grey',
        'SI': 'green',
        'M1': 'magenta',
        'M2': 'cyan',
        # 4N:
        'C': 'violet',
        'E': 'teal',
        'S': 'olive',
        'TN': 'maroon',
        'TP': 'navy',
        'X': 'turquoise',
        'Y': 'lime',
        'ZERO': 'indigo'
    }

    max_size_threshold = 15000  # threshold - filter out large elements

    for node, data in graph.nodes(data=True):
        x, y = data['points'][::2], data['points'][1::2]
        layer = data.get('layer')
        base_z = layer_z_coordinates.get(layer, 0)
        x = np.array(x, dtype=np.float32)
        y = np.array(y, dtype=np.float32)
        if len(x) == 1 and len(y) == 1:
            x = np.append(x, x)
            y = np.append(y, y)
        if np.ptp(x) <= max_size_threshold and np.ptp(y) <= max_size_threshold and layer in layer_order:
            if len(x) == 2 and len(y) == 2:
                # Create a small rectangle around the points to make it visually thicker
                bottom_points = [
                    (x[0] - spike_width, y[0] - spike_width, base_z),
                    (x[0] + spike_width, y[0] - spike_width, base_z),
                    (x[0] + spike_width, y[0] + spike_width, base_z),
                    (x[0] - spike_width, y[0] + spike_width, base_z),
                    (x[1] - spike_width, y[1] - spike_width, base_z),
                    (x[1] + spike_width, y[1] - spike_width, base_z),
                    (x[1] + spike_width, y[1] + spike_width, base_z),
                    (x[1] - spike_width, y[1] + spike_width, base_z),
                ]
                top_points = [(p[0], p[1], base_z + spike_thickness) for p in bottom_points]
            else:
                bottom_points = [(x[i], y[i], base_z) for i in range(len(x))]
                top_points = [(x[i], y[i], base_z + layer_thickness) for i in range(len(x))]
            all_points = np.array(bottom_points + top_points)
            num_points = len(bottom_points)
            cells = np.array([num_points] + list(range(num_points)) + [num_points] + list(range(num_points, 2*num_points)))
            for i in range(num_points):
                next_i = (i + 1) % num_points
                cells = np.concatenate((cells, [4, i, next_i, next_i + num_points, i + num_points]))
            poly = pv.PolyData(all_points)
            poly.faces = cells
            color = layer_colors.get(layer, 'white')
            plotter.add_mesh(poly, color=color, show_edges=True, edge_color='black')
        else:
            print(f"Skipping large element at node {node} due to size threshold")
    
    
    camera = plotter.camera
    camera.position = (0, -1, 0)
    camera.focal_point = (0, 0, 0)
    camera.view_up = (0, 1, 0)
    plotter.camera = camera
    plotter.view_xy()
    plotter.camera.roll += 0
    
    plotter.add_axes()    
    plotter.show()

cif_filename = 'adder2.cif'
graph = parse_cif_to_graph(cif_filename)
create_3d_plot(graph)
