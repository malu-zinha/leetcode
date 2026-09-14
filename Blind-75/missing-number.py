# 268. Missing Number

class Solution(object):
    def missingNumber(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        s = set(nums)
        
        if 0 in nums:

            for n in s:
                if n+1 not in s:
                    return n+1

        else:

            return 0