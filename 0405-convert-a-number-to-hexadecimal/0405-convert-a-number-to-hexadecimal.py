class Solution(object):
    def toHex(self,num):
        """
        :type num: int
        :rtype: str
        """
        state=True if num>=0 else False
        a=[str(i) for i in range(10)]+[chr(i+97) for i in range(6)]
        hex=[]

        while abs(num)>15:
            hex.insert(0,a[num%16])
            num=num/16
        if state:
            return a[num]+''.join(hex)
        else:
            return ''.join(['f' for i in range(7-len(hex))])+a[num]+''.join(hex)
        

