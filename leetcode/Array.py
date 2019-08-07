class Solution:
    """ leetcode array  """
    def __init__(self, nums):
        self.nums = nums

    # @return a tuple, (index1, index2)
    def twoSum(self, num, target):
        sign = {}
        for idx, val in enumerate(num):
                sign[val] = idx

        for idx, val in enumerate(num):
            gap = target - val
            if gap in sign and sign[gap] > idx :
                return idx+1, sign[gap]+1

        return ()

    # @return length
    def removeDuplicatesFromSortedArray(self):
        """
        remove duplicates from sorted array
        """
        
        length = len(self.nums)
        lastIndex =  length - 1
        while lastIndex > 0:
            if self.nums[lastIndex] == self.nums[lastIndex - 1]:
                del(self.nums[lastIndex])
                lastIndex -= 2
                length -= 1
            else:
                lastIndex -= 1
        return length

if __name__ == '__main__':
    so = Solution([1, 1, 3, 4, 5, 6, 6, 8, 10])
    # print so.twoSum([0,3,4,0], 0)
    print so.removeDuplicatesFromSortedArray()
    print so.nums
