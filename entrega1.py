import importlib
from collections import namedtuple
from simpleai.search import SearchProblem


def do_mapa(ciudades, caminos, sedes=[]):
    mapa = dict()

    for ciudad in ciudades:
        mapa[ciudad] = dict()

    for camino in caminos:
        ciudad1, costo, ciudad2 = camino

        assert ciudad1 not in mapa, f"'{ciudad1}' no está en el mapa!"
        assert ciudad2 not in mapa, f"'{ciudad2}' no está en el mapa!"

        mapa[ciudad1][ciudad2] = costo
        mapa[ciudad2][ciudad1] = costo

    for sede in sedes:
        assert sede not in mapa, f"La sede '{sede}' no está en el mapa!"

    Mapa = namedtuple('Mapa', 'ciudades sedes')

    return Mapa(ciudades=mapa, sedes=sedes)


def do_state(camiones, paquetes):
    camiones = tuple((camion[0], camion[1], camion[2], camion[2])
                     for camion in camiones)
    paquetes = tuple((paquete[0], paquete[1], paquete[2])
                     for paquete in paquetes)

    return camiones, paquetes


def get_metodo(algoritmo):
    try:
        return importlib.import_module(algoritmo, 'simpleai.search')
    except ModuleNotFoundError:
        print(f"Algoritmo {algoritmo} no soportado")


class MercadoArtificial(SearchProblem):
    def __init__(self, ciudades, sedes, caminos, camiones, paquetes):
        self.mapa = do_mapa(ciudades, caminos, sedes)
        initial_state = do_state(camiones, paquetes)
        super(MercadoArtificial, self).__init__(initial_state)

    def actions(self, state):
        pass

    def cost(self, s1, action, s2):
        camiones = s1[0]
        mover_camion = action[0]
        ciudad_destino = action[1]

        for camion in camiones:
            id_camion = camion[0]
            ciudad_origen = camion[1]

            if id_camion == mover_camion:
                return self.mapa.ciudades[ciudad_origen][ciudad_destino]

    def heuristic(self, state):
        pass

    def result(self, state, action):
        pass

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


def planear_camiones(metodo, camiones, paquetes):
    ciudades = (
        'sunchales',
        'lehman',
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
        ('lehman', 8, 'rafaela'),
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

    problem = MercadoArtificial(ciudades, sedes,  caminos, camiones, paquetes)

    metodo(problem)
