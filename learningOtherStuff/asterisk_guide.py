numbers = (10, 20, 30, (25, 23, 10))

def add(a, b, c):
    return a + b + c

print(numbers)
print(*numbers)

# basically the asterisk means to pass the numbers arguments as separate entities rather than passing it as a tuple
#print(add(*numbers))