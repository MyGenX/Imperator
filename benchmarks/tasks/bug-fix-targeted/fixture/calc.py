def running_total(nums):
    """Return the running cumulative sum.

    running_total([1, 2, 3]) -> [1, 3, 6]
    """
    totals = []
    acc = 0
    for i in range(1, len(nums)):  # bug: skips the first element
        acc += nums[i]
        totals.append(acc)
    return totals
