def add(a, b):
    return a + b

# 2つの整数の減算を行う
def subtract(a, b):
    return a - b

# 2つの整数の乗算を行う
def multiply(a, b):
    return a * b

# 2つの整数の除算を行う
def divide(a, b):
    if b == 0:
        raise ValueError("0で除算された")
    return a / b