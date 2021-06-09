class BayesianNetwork:
    def __init__(self, tablasDeProbabilidades) -> None:
        """         
        tablasDeProbabilidades: 
            P(J/x_0,...,x_n)
            "x_0...x_n"      "J"  "probabilidad"
            lista de tuplas que representan arista y probabilidad
            ejemplo: 
                    {
                        ((('a', True), ('b', False)), ('c', True)) : 0.4, 
                        ((('a', False)), ('b', True)) : 0.7,
                        ((), ('a', False)) : 0,4
                    }
        """
        self.tablasDeProbabilidades = tablasDeProbabilidades
        self.dependencias = {}
        for inputVariablesConValores, (outputVariable, _) in tablasDeProbabilidades:
            inputVariables = [variable for variable, valor in inputVariablesConValores]

            if outputVariable in self.dependencias:
                assert(self.dependencias[outputVariable] == inputVariables)

            else:
                self.dependencias[outputVariable] = inputVariables


    def probabilidadDeInstanciaCompleta(self, instancia):
        """
        instancia: 
            ejemplo: {'a': True, 'b': False, ...]
        """
        resultado = 1
        
        for nodo, valor in list(instancia.items()):
            dependencias = self.dependencias[nodo] 
            dependenciasConValores = tuple((nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad

        return resultado

tablaAlarma = {
    # Robo
    (
        (), 
        ('r', True)) : 0.001,
    (
        (), 
        ('r', False)) : 0.999,
    # Temblor
    (
        (), 
        ('t', True)) : 0.002,
    (
        (), 
        ('t', False)) : 0.998,
    # Alarma
    (
        (('r', True), ('t', True)), 
        ('a', True))   : 0.950,
    (
        (('r', True), ('t', False)), 
        ('a', True))  : 0.950,
    (
        (('r', False), ('t', True)), 
        ('a', True))  : 0.290,
    (
        (('r', False), ('t', False)), 
        ('a', True)) : 0.001,
    (
        (('r', True), ('t', True)), 
        ('a', False))   : 0.050,
    (
        (('r', True), ('t', False)), 
        ('a', False))  : 0.050,
    (
        (('r', False), ('t', True)), 
        ('a', False))  : 0.710,
    (
        (('r', False), ('t', False)), 
        ('a', False)) : 0.999,
    # Juan
    (
        (('a', True),), 
        ('j', True)) : 0.90,
    (
        (('a', False),), 
        ('j', True)) : 0.05,
    (
        (('a', True),),
         ('j', False)) : 0.10,
    (
        (('a', False),), 
        ('j', False)) : 0.95,
    # Maria
    (
        (('a', True),), 
        ('m', True)) : 0.70,
    (
        (('a', False),), 
        ('m', True)) : 0.01,
    (
        (('a', True),),
         ('m', False)) : 0.30,
    (
        (('a', False),), 
        ('m', False)) : 0.99,
}

red = BayesianNetwork(tablaAlarma)

print(red.probabilidadDeInstanciaCompleta({'r': True, 't': True, 'a': True, 'j': True, 'm': True}))
