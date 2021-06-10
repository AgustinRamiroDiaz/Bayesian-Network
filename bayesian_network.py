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
            raise TypeError(
                "Los tipos soportados para la variable tablasDeProbabilidades son dict y string")

    def inferirNodos(self):
        self.nodos = set()
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            for nodo, _ in inputVariablesConValores + ((outputVariable, _),):
                self.nodos.add(nodo)

    def inferirRegistrosDeTablasDeProbabilidades(self):
        for (inputVariablesConValores, (outputVariable, outputValor)), probabilidad in list(self.tablasDeProbabilidades.items()):
            self.tablasDeProbabilidades[(
                inputVariablesConValores, (outputVariable, not outputValor))] = 1 - probabilidad

    def generarDependencias(self):
        self.dependencias = {}
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            inputVariables = tuple(variable for variable,
                                   _ in inputVariablesConValores)

            if outputVariable in self.dependencias:
                assert(self.dependencias[outputVariable] == inputVariables)
            else:
                self.dependencias[outputVariable] = inputVariables

    def tablasDeProbabilidadesFromString(self, string):
        tablasDeProbabilidades = {}
        renglones = string.split('\n')
        for renglon in renglones:
            if not renglon.strip():
                continue
            renglonSplitted = [input.strip() for input in renglon.split(',')]
            probabilidad = float(renglonSplitted[-1])
            outputVariableConValor = self.variableConValorFromString(
                renglonSplitted[-2])

            inputVariablesConValor = tuple(self.variableConValorFromString(
                inputVariableConValor) for inputVariableConValor in renglonSplitted[:-2])

            tablasDeProbabilidades[(
                inputVariablesConValor, outputVariableConValor)] = probabilidad

        return tablasDeProbabilidades

    def variableConValorFromString(self, string):
        if match('^no ', string):
            return (string[3:], False)
        else:
            return (string, True)

    def probabilidadDeInstanciaCompleta(self, instancia):
        """
        instancia: 
            ejemplo: {'a': 1, 'b': 0, ...]
        """
        resultado = 1
        conjuncion = 'P(' + ', '.join([f'{nodo} = {bool(valor)}' for nodo, valor in instancia.items()]) + ')'
        logPrevio = ''
        logPosterior = ''

        for nodo, valor in list(instancia.items()):
            dependencias = self.dependencias[nodo]
            dependenciasConValores = tuple(
                (nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))

            
            logPrevio += f' * P({nodo} = {bool(valor)}' + (' | '+ ', '.join([f'{nodo} = {bool(valor)}' for nodo, valor in dependenciasConValores]) if dependenciasConValores else '') + ')'
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad
            logPosterior += f' * {probabildad}'

        log = '\n='.join([conjuncion, logPrevio[3:], logPosterior[3:], str(resultado)])
        print(log)

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
