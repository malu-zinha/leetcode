class Solution(object):
    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        
        string = []
        saida = []
        maior = []

        for i in range(len(s)):
            for j in range(i, len(s)):
                if s[i] == s[j]:
                    string = s[i:j+1]
                    if string == string[::-1]:
                        saida = string
    
                if len(saida) > len(maior):
                    maior = saida

        return maior

