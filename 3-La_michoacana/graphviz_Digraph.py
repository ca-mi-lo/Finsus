from graphviz import Digraph

# Create a new directed graph
dot = Digraph()

# Set the background color for the entire graph
dot.attr(bgcolor='#D3D3D3')  # Set the background color to pale gray

# Define nodes with an even lighter yellow background for the optimization problem
dot.node('A', 'Recolección de Datos', style='filled', fillcolor='#FAE3B0', fontcolor='#333333')  # Light yellow
dot.node('B', 'Modelo Predictivo', style='filled', fillcolor='#FAE3B0', fontcolor='#333333')  # Highlighted '#ffd966ff'
dot.node('D', 'Algoritmo de Optimización', style='filled', fillcolor='#64ffda', fontcolor='#333333')  # Light yellow
dot.node('G', 'Recomendaciones Diarias', style='filled', fillcolor='#FAE3B0', fontcolor='#333333')  # Light yellow

# Define edges
dot.edge('A', 'B')
dot.edge('B', 'D')  # Connect to optimization
dot.edge('D', 'G')

# Add a dotted line between G and A to represent dynamic adaptation
dot.edge('G', 'A', style='dotted', label='Sistema dinámico', color='black')  # Dotted line with label

# Render the graph
dot.render('flowchart', format='png', cleanup=True)
dot.view()  # This will open the generated image
