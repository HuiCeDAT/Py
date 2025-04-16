def max_subarray_sum(nums):
    if not nums:
        return 0
    current_sum = max_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum


nums1 = [1, -2, 3, 5, -1]
nums2 = [1, -2, 3, -8, 5, 1]
nums3 = [1, -2, 3, -2, 5, 1]
print(max_subarray_sum(nums1))
print(max_subarray_sum(nums2))
print(max_subarray_sum(nums3))
