import numpy as np
import pulp
import matplotlib.pyplot as plt

# Parámetros
C_storage = 1   # Costo de almacenamiento por paleta
C_order = 100   # Costo fijo por pedido
C_backlog = 5   # Costo por falta de inventario
D = [10, 30, 25, 15]  # Demandas esperadas para 4 períodos
initial_inventory = 0  # Inventario inicial
T = len(D)  # Número de períodos

# Definición del problema
problem = pulp.LpProblem("Maximizar_Ingresos", pulp.LpMaximize)

# Variables de decisión
Q = pulp.LpVariable.dicts("Q", range(T), lowBound=0, cat='Continuous')  # Cantidad a pedir
I = pulp.LpVariable.dicts("I", range(T), lowBound=0, cat='Continuous')  # Inventario
B = pulp.LpVariable.dicts("B", range(T), lowBound=0, cat='Continuous')  # Atrasos
OrderPlaced = pulp.LpVariable.dicts("OrderPlaced", range(T), cat='Binary')  # Variable binaria para indicar si se hace un pedido

# Precio de venta por paleta
P = 15  # Precio por paleta

# Función objetivo: Maximizar ingresos menos costos totales
problem += pulp.lpSum([P * D[t] - C_storage * I[t] - C_order * OrderPlaced[t] - C_backlog * B[t] for t in range(T)]), "Ingresos_Netos"

# Restricciones
for t in range(T):
    # Restricción de inventario
    if t == 0:
        problem += I[t] == initial_inventory + Q[t] - D[t], f"Inventario_balance_{t}"
    else:
        problem += I[t] == I[t-1] + Q[t] - D[t], f"Inventario_balance_{t}"
    
    # Restricción de atrasos
    problem += B[t] >= D[t] - I[t], f"Atrasos_{t}"

    # Restricción de inventario no negativo
    problem += I[t] >= 0, f"No_inventario_negativo_{t}"

    # Relación entre la cantidad pedida y la variable binaria
    problem += Q[t] <= 1000 * OrderPlaced[t], f"OrderPlaced_{t}"  # Arbitrary large number to allow enough volume

# Resolver el problema
problem.solve()

# Resultados
print("Estado del problema:", pulp.LpStatus[problem.status])
for t in range(T):
    print(f"Cantidad a pedir en período {t+1}: {Q[t].varValue}")
    print(f"Inventario en período {t+1}: {I[t].varValue}")
    print(f"Atrasos en período {t+1}: {B[t].varValue}")
    print(f"Pedido realizado en período {t+1}: {OrderPlaced[t].varValue}")

print("Ingreso neto total: ", pulp.value(problem.objective))

# Visualización de resultados
Q_values = [Q[t].varValue for t in range(T)]
I_values = [I[t].varValue for t in range(T)]
B_values = [B[t].varValue for t in range(T)]

# Colores de la plantilla
color_order = '#cacacaff'      # Color para cantidad pedida
color_inventory = '#F2D094'     # Amarillo claro para inventario
color_backlog = '#64ffda'       # Menta para atrasos
color_demand = '#FFC107'        # Amarillo para demanda

# Gráfica de resultados
labels = ['Cantidad Pedida', 'Inventario', 'Atrasos', 'Demanda']
data = [Q_values, I_values, B_values, D]

# Crear la gráfica
x = np.arange(T)  # la ubicación de las etiquetas
width = 0.2  # el ancho de las barras

fig, ax = plt.subplots(figsize=(12, 6))

# Graficar cada conjunto de datos
ax.bar(x, Q_values, width, label='Cantidad Pedida', color=color_order)
ax.bar(x + width, I_values, width, label='Inventario', color=color_inventory)
ax.bar(x + 2 * width, B_values, width, label='Atrasos', color=color_backlog)
ax.bar(x + 3 * width, D, width, label='Demanda', color=color_demand)

# Añadir etiquetas y título
ax.set_ylabel('Cantidad')
ax.set_title('Resultados por Período', color='#333333')
ax.set_xticks(x + width / 2)
ax.set_xticklabels([f'Período {i+1}' for i in range(T)], color='#333333')
ax.legend()

# Agregar los parámetros en la esquina superior izquierda
params_text = (f"Costo de almacenamiento: {C_storage}\n"
               f"Costo de pedido: {C_order}\n"
               f"Costo de atraso: {C_backlog}\n"
               f"Demandas: {D}")
plt.gcf().text(0.05, 0.95, params_text, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

plt.grid(axis='y')
plt.tight_layout()
plt.show()