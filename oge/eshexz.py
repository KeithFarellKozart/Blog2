def f(x, i):
    x = int(str(x), i)
    return x
print(min(f(14, 16), f(17, 8), f(10011, 2)))
print(f(1011101,2))