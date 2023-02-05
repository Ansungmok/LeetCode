class Solution(object):
    def fizzBuzz(self, n):
        """
        :type n: int
        :rtype: List[str]
        """
        return ['Fizz'*(d%3==0)+'Buzz'*(d%5==0) or str(d) for d in range(1,n+1)]