from itertools import product
from pprint import pprint
from re import match

class BayesianNetwork:
    def __init__(self, nodos, tablasDeProbabilidades) -> None:
        """         
        tablasDeProbabilidades: 
            P(J/x_0,...,x_n)
            "x_0...x_n"      "J"  "probabilidad"
            lista de tuplas que representan arista y probabilidad
            ejemplo: 
                    {
                        ((('a', 1), ('b', 0)), ('c', 1)) : 0.4, 
                        ((('a', 0)), ('b', 1)) : 0.7,
                        ((), ('a', 0)) : 0,4
                    }
        """
        self.nodos = nodos
        if type(tablasDeProbabilidades) == dict:
            self.tablasDeProbabilidades = tablasDeProbabilidades
        elif type(tablasDeProbabilidades) == str:
            self.tablasDeProbabilidades = self.fromString(tablasDeProbabilidades)
        else:
            raise TypeError
        pprint(self.tablasDeProbabilidades)

        self.dependencias = {}
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            inputVariables = [variable for variable, valor in inputVariablesConValores]

            if outputVariable in self.dependencias:
                assert(self.dependencias[outputVariable] == inputVariables)

            else:
                self.dependencias[outputVariable] = inputVariables

    def fromString(self, string):
        renglones = string.split('\n')
        tablasDeProbabilidades = {}                         # x, no w, y, 0.5
        for renglon in renglones:                           # 0.5 
            temp = [t.strip() for t in renglon.split(',')]                    # y
            probabilidad = float(temp[-1])
            outputVariableConValor = self.variableConValorFromString(temp[-2])

            inputVariablesConValor = tuple(self.variableConValorFromString(inputVariableConValor) for inputVariableConValor in temp[:-2])

            tablasDeProbabilidades[(inputVariablesConValor, outputVariableConValor)] = probabilidad

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
            dependenciasConValores = tuple((nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad

        return resultado

    def probabilidadDeInstancia(self, instancia):
        nodosNoInstanciados = [nodo for nodo in self.nodos if nodo not in instancia]

        tablaDeVerdad = list(product([False, True], repeat=len(nodosNoInstanciados)))

        instanciasCompletas = []
        for registroDeVerdad in tablaDeVerdad:
            instanciaCompleta = instancia.copy()
            for nodo, valor in zip(nodosNoInstanciados, registroDeVerdad):
                instanciaCompleta[nodo] = valor

            instanciasCompletas.append(instanciaCompleta)

        resultado = 0
        for instanciaCompleta in instanciasCompletas:
            resultado += self.probabilidadDeInstanciaCompleta(instanciaCompleta)

        return resultado

tablaAlarma = {
    # Robo
    (
        (), 
        ('r', 1)) : 0.001,
    (
        (), 
        ('r', 0)) : 0.999,
    # Temblor
    (
        (), 
        ('t', 1)) : 0.002,
    (
        (), 
        ('t', 0)) : 0.998,
    # Alarma
    (
        (('r', 1), ('t', 1)), 
        ('a', 1))   : 0.95,
    (
        (('r', 1), ('t', 0)), 
        ('a', 1))  : 0.94,
    (
        (('r', 0), ('t', 1)), 
        ('a', 1))  : 0.290,
    (
        (('r', 0), ('t', 0)), 
        ('a', 1)) : 0.001,
    (
        (('r', 1), ('t', 1)), 
        ('a', 0))   : 0.050,
    (
        (('r', 1), ('t', 0)), 
        ('a', 0))  : 0.051,
    (
        (('r', 0), ('t', 1)), 
        ('a', 0))  : 0.71,
    (
        (('r', 0), ('t', 0)), 
        ('a', 0)) : 0.999,
    # Juan
    (
        (('a', 1),), 
        ('j', 1)) : 0.90,
    (
        (('a', 0),), 
        ('j', 1)) : 0.05,
    (
        (('a', 1),),
         ('j', 0)) : 0.10,
    (
        (('a', 0),), 
        ('j', 0)) : 0.95,
    # Maria
    (
        (('a', 1),), 
        ('m', 1)) : 0.70,
    (
        (('a', 0),), 
        ('m', 1)) : 0.01,
    (
        (('a', 1),),
         ('m', 0)) : 0.30,
    (
        (('a', 0),), 
        ('m', 0)) : 0.99,
}

#red = BayesianNetwork(['r', 't', 'a', 'j', 'm'], tablaAlarma)

nombreArchivo = 'red.txt' 
archivo = open(nombreArchivo, 'r')
redString = archivo.read()

red = BayesianNetwork(['r', 't', 'a', 'j', 'm'], redString)

print(red.probabilidadDeInstancia({'j': 1}))

# valor 0,521