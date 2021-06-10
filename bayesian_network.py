from itertools import product
from re import match, search


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
        self._asignarTablasDeProbabilidades(tablasDeProbabilidades)
        self._inferirNodos()
        self._generarDependencias()
        self._inferirRegistrosDeTablasDeProbabilidades()

    def _asignarTablasDeProbabilidades(self, tablasDeProbabilidades):
        if type(tablasDeProbabilidades) == dict:
            self.tablasDeProbabilidades = tablasDeProbabilidades
        elif type(tablasDeProbabilidades) == str:
            self.tablasDeProbabilidades = self._tablasDeProbabilidadesFromString(
                tablasDeProbabilidades)
        else:
            raise TypeError(
                "Los tipos soportados para la variable tablasDeProbabilidades son dict y string")

    def _inferirNodos(self):
        self.nodos = set()
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            for nodo, _ in inputVariablesConValores + ((outputVariable, _),):
                self.nodos.add(nodo)

    def _inferirRegistrosDeTablasDeProbabilidades(self):
        for (inputVariablesConValores, (outputVariable, outputValor)), probabilidad in list(self.tablasDeProbabilidades.items()):
            self.tablasDeProbabilidades[(
                inputVariablesConValores, (outputVariable, not outputValor))] = 1 - probabilidad

    def _generarDependencias(self):
        self.dependencias = {}
        for inputVariablesConValores, (outputVariable, _) in self.tablasDeProbabilidades:
            inputVariables = tuple(variable for variable,
                                   _ in inputVariablesConValores)

            if outputVariable in self.dependencias:
                assert(self.dependencias[outputVariable] == inputVariables)
            else:
                self.dependencias[outputVariable] = inputVariables

    def _tablasDeProbabilidadesFromString(self, string):
        tablasDeProbabilidades = {}
        renglones = string.split('\n')
        for renglon in renglones:
            if not renglon.strip():
                continue
            renglonSplitted = [input.strip() for input in renglon.split(',')]
            probabilidad = float(renglonSplitted[-1])
            outputVariableConValor = self._variableConValorFromString(
                renglonSplitted[-2])

            inputVariablesConValor = tuple(self._variableConValorFromString(
                inputVariableConValor) for inputVariableConValor in renglonSplitted[:-2])

            tablasDeProbabilidades[(
                inputVariablesConValor, outputVariableConValor)] = probabilidad

        return tablasDeProbabilidades

    def _variableConValorFromString(self, string):
        if match('^no ', string):
            return (string[3:], False)
        else:
            return (string, True)

    def _probabilidadDeInstanciaCompleta(self, instancia):
        """
        instancia: 
            ejemplo: {'a': 1, 'b': 0, ...]
        """
        resultado = 1
        conjuncion = 'P(' + ', '.join(
            [f'{nodo} = {bool(valor)}' for nodo, valor in instancia.items()]) + ')'
        logPrevio = ''
        logPosterior = ''

        for nodo, valor in list(instancia.items()):
            dependencias = self.dependencias[nodo]
            dependenciasConValores = tuple(
                (nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))

            logPrevio += f' * P({nodo} = {bool(valor)}' + (' | ' + ', '.join(
                [f'{nodo} = {bool(valor)}' for nodo, valor in dependenciasConValores]) if dependenciasConValores else '') + ')'
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad
            logPosterior += f' * {probabildad}'

        log = '\n='.join([conjuncion, logPrevio[3:],
                         logPosterior[3:], str(resultado)])
        print(log, end='\n'*2)

        return resultado

    def probabilidadDeInstancia(self, instancia):
        nodosNoInstanciados = [
            nodo for nodo in self.nodos if nodo not in instancia]

        tablaDeVerdad = list(
            product([False, True], repeat=len(nodosNoInstanciados)))

        print('P(' + ', '.join(
            [f'{nodo} = {bool(valor)}' for nodo, valor in instancia.items()]) + ')')
        log = []
        instanciasCompletas = []
        for registroDeVerdad in tablaDeVerdad:
            instanciaCompleta = instancia.copy()
            for nodo, valor in zip(nodosNoInstanciados, registroDeVerdad):
                instanciaCompleta[nodo] = valor

            instanciasCompletas.append(instanciaCompleta)
            conjuncion = 'P(' + ', '.join(
                [f'{nodo} = {bool(valor)}' for nodo, valor in instanciaCompleta.items()]) + ')'
            log.append(conjuncion)

        print('= ' + ' + '.join(log), end='\n'*3)
        print('Cálculos auxiliares:')

        resultado = 0
        for instanciaCompleta in instanciasCompletas:
            resultado += self._probabilidadDeInstanciaCompleta(
                instanciaCompleta)

        return resultado

    def probabilidadCondicional(self, output, inputs):
        # P(x|y) = P(x, y) / P(y)
        Py = self.probabilidadDeInstancia(inputs)
        inputs.update(output)
        Pxy = self.probabilidadDeInstancia(inputs)
        return Pxy / Py

    def calcular(self, string):
        cleaned = search('\s*P\s*\(\s*(.*)\s*\)\s*', string).groups()[0]
        splitted = cleaned.split('|')
        if len(splitted) == 1: 
            inputsDict = {}
            for variableConValorString in cleaned.split(','):
                variableConValorString = variableConValorString.strip()
                variable, valor = self._variableConValorFromString(variableConValorString)
                inputsDict[variable] = valor
            
            return self.probabilidadDeInstancia(inputsDict)

        elif len(splitted) == 2:
            output = splitted[0].strip()
            inputs = splitted[1]

            inputsDict = {}
            for variableConValorString in inputs.split(','):
                variableConValorString = variableConValorString.strip()
                variable, valor = self._variableConValorFromString(variableConValorString)
                inputsDict[variable] = valor
            
            outputVariable, outputValor = self._variableConValorFromString(output)
            outputDict = {outputVariable : outputValor}

            return self.probabilidadCondicional(outputDict , inputsDict)

        else:
            raise ValueError('Qué metiste?')

def aprox(value, expected):
    decimalPlacesLength = len(str(expected).split('.')[1])
    epsilon = 10**-decimalPlacesLength
    return abs(value - expected) < epsilon


if __name__ == '__main__':
    tablas = """        d1, 0.002
                        d2, 0.001
    d1,                 s1, 0.7
    no d1,              s1, 0.05
    d1,     d2,         r,  0.5
    d1,     no d2,      r,  0.5
    no d1,  d2,         r,  0.5
    no d1,  no d2,      r,  0
    d1,     d2,         s2, 0.95
    d1,     no d2,      s2, 0.2
    no d1,  d2,         s2, 0.8
    no d1,  no d2,      s2, 0.05"""
    
    red = BayesianNetwork(tablas)

    resultado = red.calcular('P(d1, no d2, s1, r, no s2)')
    print(resultado)
    assert(aprox(resultado, 0.00055944))

    resultado = red.calcular('P(d2 | no s1, r, s2)')
    print(resultado)
    assert(aprox(resultado, 0.863606886))

    resultado = red.calcular(' P ( d1 | no s1,      r,      s2 )')
    print(resultado)
    assert(aprox(resultado, 0.1370416302))

    print('Pasaron todos los tests!')
