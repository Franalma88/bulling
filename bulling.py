import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Configuración
num_alumnos = 100
num_tutores = 5
director_id = "D105"


# 1. Crear grafo de Alumnos
G = nx.Graph()
for i in range(num_alumnos):
    G.add_node(f"A{i}", tipo="alumno")

# 2. Asignar amistades aleatorias
amistades = set()
for i in range(num_alumnos):
    amigos = np.random.choice([j for j in range(num_alumnos) if j != i], size=5, replace=False)
    # utilizamos 5 relaciones de amistad ya que con tres no es tan grafico 
    for j in amigos:
        a, b = sorted((i, j))
        if (a, b) not in amistades:
            amistades.add((a, b))
            G.add_edge(f"A{a}", f"A{b}", weight=1)

# 3. Añadir Grafo de tutores y director
for t in range(num_tutores):
    G.add_node(f"T{t}", tipo="tutor")
G.add_node(director_id, tipo="director")

# 4. Calcular distancias
distancias = dict(nx.floyd_warshall(G, weight="weight"))
# utilizando la funcion del algoritmo floyd_warshall de la libreria networkx calculamos la distancias

# 5. Elegir alumno que sufre bullying de forma aleatoria
origen = f"A{np.random.randint(0, num_alumnos)}"
# importante el alumno que es origen del bulling no puede avisar
print(f"\n🎯 El caso de bullying ocurre en el alumno {origen} (pero no puede avisar directamente).\n")

# 6. Simular propagación desde origen
propagacion = []
for alumno in G.nodes:
    if alumno.startswith("A") and alumno != origen and alumno in distancias[origen]:
        # Buscando en los nodos a los alumnos por la palabra de inicio A y obiamos el original
        tiempo = distancias[origen][alumno]
        propagacion.append((alumno, int(tiempo)))

# 7. Alumnos que se enteran
df = pd.DataFrame(sorted(propagacion, key=lambda x: x[1]), columns=["Alumno", "Hora en que se entera"])
hora_minima = df["Hora en que se entera"].min()
# indicamos la hora minima conseguida en el dataframe
tiempo_total_director = hora_minima + 1 + 1
# creamos un dataframe ( Listado ) de alumnos y el tiempo en el que se enteran 


avisadores = df[df["Hora en que se entera"] == hora_minima].copy()
# filtramos nuestro dataframe por hora minima
avisadores["Tiempo total hasta director"] = tiempo_total_director
# sumamos dos horas hasta el tiempo al director

print("\n--- PROPAGACIÓN DEL CASO ---")
print(df.head(12))  # primeros 12 alumnos en enterarse ya que provando no pasa de 10

print("\n--- AVISO MÁS RÁPIDO AL DIRECTOR ---")
print(avisadores)

# 8. Asignar tutores por clase
tutores = {f"A{i}": f"T{i // 20}" for i in range(num_alumnos)}

# 9. Crear subgrafo para visualización
nodos_informados = [alumno for alumno, _ in propagacion]
nodos_informados.extend(tutores[alumno] for alumno in avisadores["Alumno"])
nodos_informados.append(director_id)
G_sub = G.subgraph(set(nodos_informados)).copy()

# 10. Añadir avisos alumno → tutor → director
for alumno in avisadores["Alumno"]:
    tutor = tutores[alumno]
    G_sub.add_node(tutor, tipo="tutor")
    G_sub.add_edge(alumno, tutor, tipo="aviso")
for tutor in set(tutores[alumno] for alumno in avisadores["Alumno"]):
    G_sub.add_edge(tutor, director_id, tipo="aviso")

# 11. Posiciones para graficar
pos = {}
layer_y = {"alumno": 0, "tutor": 1, "director": 2}
for node in G_sub.nodes:
    if node.startswith("A"):
        pos[node] = (int(node[1:]), layer_y["alumno"])
    elif node.startswith("T"):
        pos[node] = (int(node[1:]) * 2, layer_y["tutor"])
    else:
        pos[node] = (50, layer_y["director"])

# 12. Colores por tiempo
color_map = []
tiempo_dict = dict(propagacion)
max_tiempo = max(tiempo_dict.values()) + 1
for node in G_sub.nodes:
    if node.startswith("A"):
        tiempo = tiempo_dict.get(node, 0)
        color_map.append(plt.cm.viridis(tiempo / max_tiempo))
    elif node.startswith("T"):
        color_map.append("lightblue")
    else:
        color_map.append("red")

# 13. Dibujar grafo
plt.figure(figsize=(15, 6))
nx.draw_networkx_nodes(G_sub, pos, node_color=color_map, node_size=300)
nx.draw_networkx_labels(G_sub, pos, font_size=8)

amistades_edges = [(u, v) for u, v in G_sub.edges if G_sub[u][v].get("weight") == 1]
aviso_edges = [(u, v) for u, v in G_sub.edges if G_sub[u][v].get("tipo") == "aviso"]

nx.draw_networkx_edges(G_sub, pos, edgelist=amistades_edges, edge_color="gray", width=1, alpha=0.5)
nx.draw_networkx_edges(G_sub, pos, edgelist=aviso_edges, edge_color="red", width=2, arrows=True)

plt.title("Propagación del bullying con aviso a tutores correspondientes", fontsize=12)
plt.axis("off")
plt.tight_layout()
plt.show()


