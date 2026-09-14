# 125. Valid Palindrome

class Solution(object):
    def isPalindrome(self, s):
        """
        :type s: str
        :rtype: bool
        """
        string = s.lower()
        string = re.sub(r'[^\w\s]', '', string)
        string = string.replace("_", "")
        string = string.replace(" ", "")
        
        if string == string[::-1]:
            return True

        else:
            return False