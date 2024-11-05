import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Colores personalizados
color_background = '#333333'  # Gris oscuro
color_inventory = '#F2D094'    # Amarillo claro
color_income = '#000000'        # Negro
color_reorder_point = '#F2D094'  # Amarillo claro
color_storage_cost = '#FFC107'   # Amarillo para los costos de almacenamiento
color_order_cost = '#28A745'      # Verde para los costos de pedidos
color_backlog_cost = '#DC3545'    # Rojo para los costos de atrasos

# Clase para el modelo de la cadena de suministro
class SupplyChain:
    def __init__(self, env, initial_inventory, reorder_point, order_quantity, storage_cost, order_cost, backlog_cost, price_per_palet):
        self.env = env
        self.inventory = initial_inventory
        self.reorder_point = reorder_point
        self.order_quantity = order_quantity
        self.storage_cost = storage_cost
        self.order_cost = order_cost
        self.backlog_cost = backlog_cost
        self.price_per_palet = price_per_palet

        # Listas para almacenar resultados a lo largo del tiempo
        self.inventory_history = []
        self.income_history = []
        self.total_storage_cost = 0
        self.total_order_cost = 0
        self.total_backlog_cost = 0
        self.total_income = 0
        self.demand_pattern = [1/6, 1/3, 1/3, 1/6]  # Distribución de demanda
        
    def demand(self):
        # Simula la demanda diaria
        demand_size = np.random.choice(range(1, 5), p=self.demand_pattern)
        self.inventory -= demand_size
        
        # Cálculo de ingresos
        if demand_size <= self.inventory:
            self.total_income += demand_size * self.price_per_palet
        else:
            self.total_income += self.inventory * self.price_per_palet
            
        # Costos por falta de inventario
        if self.inventory < 0:
            self.total_backlog_cost += abs(self.inventory) * self.backlog_cost
            self.inventory = 0  # No se puede tener inventario negativo

        # Verifica si se necesita reabastecimiento
        if self.inventory < self.reorder_point:
            self.env.process(self.order())

        # Almacena el estado actual
        self.inventory_history.append(self.inventory)
        self.income_history.append(self.total_income)

    def order(self):
        # Realiza un pedido
        self.total_order_cost += self.order_cost
        yield self.env.timeout(np.random.uniform(0.5, 1))  # Tiempo de llegada del pedido
        self.inventory += self.order_quantity
        self.total_storage_cost += self.inventory * self.storage_cost

    def run(self, duration):
        for _ in range(duration):
            yield self.env.timeout(1)  # Avanza un día
            self.demand()  # Simula la demanda diaria

# Clase para los perfiles de simulación
class Profile:
    def __init__(self, initial_inventory, reorder_point, order_quantity, storage_cost, order_cost, backlog_cost, price_per_palet):
        self.initial_inventory = initial_inventory
        self.reorder_point = reorder_point
        self.order_quantity = order_quantity
        self.storage_cost = storage_cost
        self.order_cost = order_cost
        self.backlog_cost = backlog_cost
        self.price_per_palet = price_per_palet

# Definición de perfiles de simulación
profiles = [
    Profile(60, 20, 40, 1, 32, 5, 15),
    Profile(80, 30, 50, 1.5, 40, 10, 20),
    Profile(50, 15, 30, 0.8, 30, 4, 12),
    Profile(70, 25, 45, 1.2, 35, 8, 18)
]

# Ejecutar simulaciones para cada perfil
results = []

for i, profile in enumerate(profiles):
    env = simpy.Environment()
    supply_chain = SupplyChain(env, profile.initial_inventory, profile.reorder_point, profile.order_quantity,
                               profile.storage_cost, profile.order_cost, profile.backlog_cost, profile.price_per_palet)

    # Ejecutar la simulación
    env.process(supply_chain.run(duration=120))  # Simulamos por 120 días
    env.run()

    # Almacenar resultados
    results.append({
        'profile': i + 1,
        'inventory_history': supply_chain.inventory_history,
        'income_history': supply_chain.income_history,
        'total_storage_cost': supply_chain.total_storage_cost,
        'total_order_cost': supply_chain.total_order_cost,
        'total_backlog_cost': supply_chain.total_backlog_cost,
        'total_income': supply_chain.total_income,
        'parameters': {
            'Initial Inventory': profile.initial_inventory,
            'Reorder Point': profile.reorder_point,
            'Order Quantity': profile.order_quantity,
            'Storage Cost': profile.storage_cost,
            'Order Cost': profile.order_cost,
            'Backlog Cost': profile.backlog_cost,
            'Price per Pallet': profile.price_per_palet
        }
    })

# Graficar la evolución de cada perfil
plt.figure(figsize=(14, 15))

for i, result in enumerate(results):
    days = np.arange(1, 121)  # Días de simulación
    ax = plt.subplot(5, 1, i + 1)
    
    # Gráfica de inventario
    ax.plot(days, result['inventory_history'], label='Inventario', color=color_inventory)
    ax.set_ylabel('Nivel de Inventario', color=color_income)
    ax.axhline(y=result['parameters']['Reorder Point'], color=color_reorder_point, linestyle='--', label='Punto de Reorden')
    
    # Agregar parámetros al título de la gráfica
    ax.set_title(f'Evolución del Perfil {result["profile"]}:\n' +
                 f'Inventario Inicial: {result["parameters"]["Initial Inventory"]}, ' +
                 f'Punto de Reorden: {result["parameters"]["Reorder Point"]}, ' +
                 f'Cantidad de Pedido: {result["parameters"]["Order Quantity"]}, ' +
                 f'Costo Almacenamiento: {result["parameters"]["Storage Cost"]}, ' +
                 f'Costo Pedido: {result["parameters"]["Order Cost"]}, ' +
                 f'Costo Atraso: {result["parameters"]["Backlog Cost"]}, ' +
                 f'Precio por Paleta: {result["parameters"]["Price per Pallet"]}', color=color_income)
    
    # Crear eje secundario para ingresos
    ax2 = ax.twinx()
    ax2.plot(days, result['income_history'], label='Ingresos', color=color_income, linestyle='--')
    ax2.set_ylabel('Ingresos (moneda)', color=color_income)

    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.grid()

# Gráfica total agregada
plt.subplot(5, 1, 5)

# Sumar las historias de todos los perfiles
total_inventory_history = np.sum([result['inventory_history'] for result in results], axis=0) / len(results)
total_income_history = np.sum([result['income_history'] for result in results], axis=0) / len(results)

# Gráfica de inventario promedio
ax = plt.gca()
ax.plot(days, total_inventory_history, label='Inventario Promedio', color=color_inventory)
ax.set_ylabel('Nivel de Inventario Promedio', color=color_income)

# Crear eje secundario para ingresos promedio
ax2 = ax.twinx()
ax2.plot(days, total_income_history, label='Ingresos Promedio', color=color_income, linestyle='--')
ax2.set_ylabel('Ingresos Promedio (moneda)', color=color_income)

# Agregar título y leyendas
ax.axhline(y=np.mean([profile.reorder_point for profile in profiles]), color=color_reorder_point, linestyle='--', label='Punto de Reorden Promedio')
ax.set_title('Evolución Total Promedio de Todos los Perfiles', color=color_income)
ax.set_xlabel('Día', color=color_income)
ax.legend(loc='upper left')
ax2.legend(loc='upper right')
ax.grid()

# Gráfica de resultados
plt.figure(figsize=(10, 6))

# Gráfica de costos y ganancias
labels = ['Almacenamiento', 'Pedidos', 'Atrasos', 'Ingresos']
values = [
    sum(result['total_storage_cost'] for result in results), 
    sum(result['total_order_cost'] for result in results), 
    sum(result['total_backlog_cost'] for result in results), 
    sum(result['total_income'] for result in results)
]

plt.bar(labels, values, color=[color_storage_cost, color_order_cost, color_backlog_cost, color_income])
plt.title('Resultados Financieros del Abastecimiento de Paletas (Acumulados)', color=color_income)
plt.ylabel('Monto (moneda)', color=color_income)
plt.grid(axis='y')
plt.tight_layout()
plt.show()