from calc import running_total

assert running_total([1, 2, 3]) == [1, 3, 6], running_total([1, 2, 3])
assert running_total([]) == [], running_total([])
assert running_total([5]) == [5], running_total([5])
assert running_total([2, -2, 4]) == [2, 0, 4], running_total([2, -2, 4])
print("ok")
