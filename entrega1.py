from collections import namedtuple
from simpleai.search import SearchProblem, astar, breadth_first, depth_first, uniform_cost, greedy, viewers

ALGORITMOS_VALIDOS = [astar, breadth_first, depth_first, uniform_cost, greedy]
CONSUME_1LITRO_CADA_KMS = 100

__all__ = ['planear_camiones']


def do_mapa(ciudades, caminos, sedes=[]):
    mapa = dict()
    menor_costo_camino = 0

    for ciudad in ciudades:
        mapa[ciudad] = dict()

    for camino in caminos:
        ciudad1, costo, ciudad2 = camino

        if (costo < menor_costo_camino) or (menor_costo_camino == 0):
            menor_costo_camino = costo

        assert ciudad1 in mapa, f"'{ciudad1}' no está en el mapa!"
        assert ciudad2 in mapa, f"'{ciudad2}' no está en el mapa!"

        mapa[ciudad1][ciudad2] = costo
        mapa[ciudad2][ciudad1] = costo

    for sede in sedes:
        assert sede in mapa, f"La sede '{sede}' no está en el mapa!"

    Mapa = namedtuple('Mapa', 'ciudades sedes menor_costo_camino')

    return Mapa(ciudades=mapa, sedes=sedes, menor_costo_camino=menor_costo_camino)


def do_state(camiones, paquetes):
    """
    El estado es una tupla de tuplas:
    - Un camion es una tupla (id, ciudad_donde_esta, capacidad_tanque, combustible_actual)
    - Un paquete es una tupla (id, ciudad_donde_esta, ciudad_destino_final)
    """
    camiones = tuple((camion + (camion[2],))
                     for camion in camiones)
    paquetes = tuple(paquetes)

    return camiones, paquetes


def get_metodo(algoritmo):
    usar = [solver for solver in ALGORITMOS_VALIDOS if solver.__name__ is algoritmo]

    if len(usar) == 0:
        raise ValueError(f"Algoritmo '{algoritmo}' no soportado")

    return usar[0]


def get_costo_litros(distancia_kms):
    return distancia_kms / CONSUME_1LITRO_CADA_KMS


class MercadoArtificial(SearchProblem):
    def __init__(self, ciudades, sedes, caminos, camiones, paquetes):
        self.mapa = do_mapa(ciudades, caminos, sedes)
        initial_state = do_state(camiones, paquetes)
        super(MercadoArtificial, self).__init__(initial_state)

    def actions(self, state):
        camiones, paquetes = state
        acciones = []

        for camion in camiones:
            camion_viaja, ciudad_actual, combustible = camion[0], camion[1], camion[3]
            lleva_paquetes = []

            for paquete in paquetes:
                # posicion es la ciudad donde esta el paquete
                paquete_id, posicion, paquete_destino = paquete
                entregado = posicion == paquete_destino
                puede_agarrar = posicion == ciudad_actual

                if not entregado and puede_agarrar:
                    lleva_paquetes.append(paquete_id)

            conectadas = tuple(
                ciudad for ciudad in self.mapa.ciudades[ciudad_actual].items())

            for ciudad_conectada in conectadas:
                a_destino, distancia = ciudad_conectada
                costo_a_destino = get_costo_litros(distancia)

                if combustible >= costo_a_destino:
                    acciones.append(
                        (camion_viaja, ciudad_actual, a_destino, costo_a_destino, tuple(lleva_paquetes)))

        return acciones

    def cost(self, s1, action, s2):
        desde_ciudad, a_destino = action[1], action[2]
        return get_costo_litros(self.mapa.ciudades[desde_ciudad][a_destino])

    def heuristic(self, state):
        paquetes = state[1]
        paquetes_sin_entregar = len(
            [paquete for paquete in paquetes if paquete[1] != paquete[2]])
        return paquetes_sin_entregar * get_costo_litros(self.mapa.menor_costo_camino)

    def result(self, state, action):
        costo = action[3]
        camiones, paquetes = state
        paquetes_transportados = action[4]
        mover_camion, a_ciudad = action[0], action[2]

        resultado_camiones = []

        for camion in camiones:
            id_camion, posicion, capacidad, combustible = camion

            if id_camion == mover_camion:
                posicion = a_ciudad

                if posicion in self.mapa.sedes:
                    combustible = capacidad
                else:
                    combustible -= costo

            resultado_camiones.append(
                (id_camion, posicion, capacidad, combustible))

        resultado_paquetes = []

        for paquete in paquetes:
            id_paquete, ciudad_actual, ciudad_final = paquete

            if id_paquete in paquetes_transportados:
                ciudad_actual = a_ciudad

            resultado_paquetes.append(
                (id_paquete, ciudad_actual, ciudad_final))

        return tuple(resultado_camiones), tuple(resultado_paquetes)

    def is_goal(self, state):
        camiones, paquetes = state

        for camion in camiones:
            ciudad = camion[1]

            if ciudad not in self.mapa.sedes:
                return False

        for paquete in paquetes:
            paquete_ciudad = paquete[1]
            paquete_destino = paquete[2]

            if paquete_ciudad != paquete_destino:
                return False

        return True


def itinerario(solution):
    viajes = []

    for viaje, estado in solution.path():
        if viaje:
            camion, origen, destino, costo, paquetes = viaje
            viajes.append((camion, destino, costo, paquetes))

    return viajes


def planear_camiones(metodo, camiones, paquetes, viewer=None):
    metodo = get_metodo(metodo)

    ciudades = (
        'sunchales',
        'lehmann',
        'rafaela',
        'susana',
        'angelica',
        'santa_clara_de_saguier',
        'san_vicente',
        'esperanza',
        'recreo',
        'santo_tome',
        'sauce_viejo',
        'santa_fe'
    )

    sedes = ['rafaela', 'santa_fe']

    caminos = (
        ('sunchales', 32, 'lehmann'),
        ('lehmann', 8, 'rafaela'),
        ('rafaela', 10, 'susana'),
        ('susana', 25, 'angelica'),
        ('angelica', 18, 'san_vicente'),
        ('angelica', 60, 'santa_clara_de_saguier'),
        ('rafaela', 70, 'esperanza'),
        ('angelica', 85, 'santo_tome'),
        ('esperanza', 20, 'recreo'),
        ('santo_tome', 5, 'santa_fe'),
        ('recreo', 10, 'santa_fe'),
        ('santo_tome', 15, 'sauce_viejo')
    )

    problem = MercadoArtificial(ciudades, sedes, caminos, camiones, paquetes)

    return itinerario(metodo(problem, graph_search=True, viewer=viewer))


if __name__ == "__main__":
    # Caso de juguete con viewer para revisar
    planear_camiones(
        metodo='breadth_first',
        camiones=[
            # id, ciudad de origen, y capacidad de combustible máxima (litros)
            ('c1', 'rafaela', 1.5),
        ],
        paquetes=[
            # id, ciudad de origen, y ciudad de destino
            ('p1', 'rafaela', 'angelica'),
        ],
        viewer=viewers.ConsoleViewer()
    )
