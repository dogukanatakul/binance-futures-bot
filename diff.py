def get_diff(previous, current):
    try:
        if previous == current:
            percentage = 0
        elif previous < 0 and current < 0:
            percentage = ((previous - current) / min(previous, current)) * 100
        elif previous < 0 and current > 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100)
        elif previous > 0 and current < 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100) * -1
        elif previous > current:
            percentage = (((previous - current) / previous) * 100) * -1
        else:
            percentage = ((current - previous) / current) * 100
    except ZeroDivisionError:
        percentage = float('inf')
    return percentage


print(get_diff(-10, -100))  # -90
print(get_diff(100, 10))  # -90
print(get_diff(100, -10))  # -110
print(get_diff(-100, -10))  # 90
print(get_diff(-10, 100))  # 110
print(get_diff(10, 100)) # 90
