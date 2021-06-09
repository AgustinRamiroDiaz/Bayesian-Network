class BayesianNetwork:
    def __init__(self, nodos, tablasDeProbabilidades) -> None:
        """
        nodos: [str] 
            lista de nombres de nodos 
            
                                   
        tablasDeProbabilidades: 
            P(J/x_0,...,x_n)
            "x_0...x_n"      "J"  "probabilidad"
            lista de tuplas que representan arista y probabilidad
            ejemplo: 
                    {
                        ((('a', True), ('b', False)), ('c', True)) : 0.4, 
                        ((('a', False)), ('c', True)) : 0.7,
                        ((), ('a', False)) : 0,4
                    }
        """
        self.nodos = nodos
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
        
        for nodo, valor in instancia.values():
            dependencias = self.dependencias[nodo] 
            dependenciasConValores = ((nodoDependencia, instancia[nodoDependencia]) for nodoDependencia in dependencias)
            query = (dependenciasConValores, (nodo, valor))
            probabildad = self.tablasDeProbabilidades[query]
            resultado *= probabildad

        return resultado