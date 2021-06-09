from itertools import product
from re import match


class BayesianNetwork:
    def __init__(self, tablasDeProbabilidades) -> None:
        """         
        tablasDeProbabilidades: 
            diccionario tal que:
                claves = (tuplas verdad input, tupla verdad output)
                valores = output probabilidad
            ejemplo: 
                    {
                        ((('a', 1), ('b', 0)), ('c', 1)) : 0.4, 
                        ((('a', 0)), ('b', 1)) : 0.7,
                        ((), ('a', 0)) : 0,4
                    }
        """
        self.asignarTablasDeProbabilidades(tablasDeProbabilidades)
        self.inferirNodos()
        self.generarDependencias()
        self.inferirRegistrosDeTablasDeProbabilidades()

    def asignarTablasDeProbabilidades(self, tablasDeProbabilidades):
        if type(tablasDeProbabilidades) == dict:
            self.tablasDeProbabilidades = tablasDeProbabilidades
        elif type(tablasDeProbabilidades) == str:
            self.tablasDeProbabilidades = self.tablasDeProbabilidadesFromString(
                tablasDeProbabilidades)
        else:
            raise TypeError

    def inferirNodos(self):
        self.nodos = []
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            for nodo, _ in inputVariablesConValores + ((outputVariable, None),):
                if nodo not in self.nodos:
                    self.nodos.append(nodo)

    def inferirRegistrosDeTablasDeProbabilidades(self):
        for (inputVariablesConValores, (outputVariable, outputValor)), probabilidad in list(self.tablasDeProbabilidades.items()):
            self.tablasDeProbabilidades[(
                inputVariablesConValores, (outputVariable, not outputValor))] = 1 - probabilidad

    def generarDependencias(self):
        self.dependencias = {}
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            inputVariables = [variable for variable,
                              _ in inputVariablesConValores]

            if outputVariable in self.dependencias:
                assert(self.dependencias[outputVariable] == inputVariables)
            else:
                self.dependencias[outputVariable] = inputVariables

    def tablasDeProbabilidadesFromString(self, string):
        renglones = string.split('\n')
        tablasDeProbabilidades = {}
        for renglon in renglones:
            if not renglon.strip():
                continue
            temp = [t.strip() for t in renglon.split(',')]
            probabilidad = float(temp[-1])
            outputVariableConValor = self.variableConValorFromString(temp[-2])

            inputVariablesConValor = tuple(self.variableConValorFromString(
                inputVariableConValor) for inputVariableConValor in temp[:-2])

            tablasDeProbabilidades[(
                inputVariablesConValor, outputVariableConValor)] = probabilidad

        return tablasDeProbabilidades

    def variableConValorFromString(self, string):
        if match('no ', string):
            return (string[3:], False)
        else:
            return (string, True)

    def probabilidadDeInstanciaCompleta(self, instancia):
        """
        instancia: 
            ejemplo: {'a': 1, 'b': 0, ...]
        """
        resultado = 1

        for nodo, valor in list(instancia.items()):
            dependencias = self.dependencias[nodo]
            dependenciasConValores = tuple(
                (nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad

        return resultado

    def probabilidadDeInstancia(self, instancia):
        nodosNoInstanciados = [
            nodo for nodo in self.nodos if nodo not in instancia]

        tablaDeVerdad = list(
            product([False, True], repeat=len(nodosNoInstanciados)))

        instanciasCompletas = []
        for registroDeVerdad in tablaDeVerdad:
            instanciaCompleta = instancia.copy()
            for nodo, valor in zip(nodosNoInstanciados, registroDeVerdad):
                instanciaCompleta[nodo] = valor

            instanciasCompletas.append(instanciaCompleta)

        resultado = 0
        for instanciaCompleta in instanciasCompletas:
            resultado += self.probabilidadDeInstanciaCompleta(
                instanciaCompleta)

        return resultado


def aprox(numero1, numero2, epsilon):
    return abs(numero1 - numero2) < epsilon


if __name__ == '__main__':
    tablaAlarma = {
        # Robo
        (
            (),
            ('r', 1)): 0.001,
        (
            (),
            ('r', 0)): 0.999,
        # Temblor
        (
            (),
            ('t', 1)): 0.002,
        (
            (),
            ('t', 0)): 0.998,
        # Alarma
        (
            (('r', 1), ('t', 1)),
            ('a', 1)): 0.95,
        (
            (('r', 1), ('t', 0)),
            ('a', 1)): 0.94,
        (
            (('r', 0), ('t', 1)),
            ('a', 1)): 0.290,
        (
            (('r', 0), ('t', 0)),
            ('a', 1)): 0.001,
        (
            (('r', 1), ('t', 1)),
            ('a', 0)): 0.050,
        (
            (('r', 1), ('t', 0)),
            ('a', 0)): 0.051,
        (
            (('r', 0), ('t', 1)),
            ('a', 0)): 0.71,
        (
            (('r', 0), ('t', 0)),
            ('a', 0)): 0.999,
        # Juan
        (
            (('a', 1),),
            ('j', 1)): 0.90,
        (
            (('a', 0),),
            ('j', 1)): 0.05,
        (
            (('a', 1),),
            ('j', 0)): 0.10,
        (
            (('a', 0),),
            ('j', 0)): 0.95,
        # Maria
        (
            (('a', 1),),
            ('m', 1)): 0.70,
        (
            (('a', 0),),
            ('m', 1)): 0.01,
        (
            (('a', 1),),
            ('m', 0)): 0.30,
        (
            (('a', 0),),
            ('m', 0)): 0.99,
    }

    red = BayesianNetwork(tablaAlarma)
    assert(aprox(red.probabilidadDeInstancia({'j': 1}), 0.0521, 0.0001))

    nombreArchivo = 'red.txt'
    with open(nombreArchivo, 'r') as archivo:
        redString = archivo.read()

    red = BayesianNetwork(redString)

    assert(aprox(red.probabilidadDeInstancia({'j': 1}), 0.0521, 0.0001))