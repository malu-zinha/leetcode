class Solution(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """

        if s:
            saida = 1
        else:
            return 0

        for i in range(len(s)):
            letras = set()
            inicio = 0
            resultado = 1

            while i + 1 < len(s) and s[i] != s[i + 1] and s[i+1] not in letras:
                letras.add(s[i])
                resultado += 1
                i += 1
                if resultado > saida:
                    saida = resultado

        return saida

