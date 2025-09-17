from HandyMath import midpoint, squareroot, exponent, max, min, apply2

a = float(input("Enter first number: "))
b = float(input("Enter second number: "))

print(f"Midpoint: {midpoint(a, b)}")
print(f"Square root of {a}: {squareroot(a)}")
print(f"{a} to the power of {b}: {exponent(a, b)}")
print(f"Max: {max(a, b)}")
print(f"Min: {min(a, b)}")
print(apply2(a, b, midpoint))

