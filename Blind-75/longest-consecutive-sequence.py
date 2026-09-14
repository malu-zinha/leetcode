# 128. Longest Consecutive Sequence

class Solution(object):
    def longestConsecutive(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """

        resultado = 0
        visitados = set()
        tabela = set(nums)

        for numero in tabela:
            if numero not in visitados:
                saida = 1
                while numero + 1 in tabela: 
                    saida+=1
                    numero+=1
                    visitados.add(numero)
                if saida > resultado:
                    resultado = saida
            
        return resultado

        