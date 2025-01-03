import numpy as np
import matplotlib.pyplot as plt


def generate_x_y(n):
    e = np.random.normal(0, 1, n)
    x = np.linspace(0, 5, n)
    y = 2 * x + 3 + e
    return x, y


n = 10
x, y = generate_x_y(n)

"""
a = (n∑xy - ∑y∑x)/n∑x2 - (∑x)2
b = (∑y - a∑x)/n
"""
a = (n * sum(x * y) - sum(x) * sum(y)) / (n * sum(np.square(x)) - (sum(x)) ** 2)
b = (sum(y) - a * sum(x)) / n
print('y = ', a, 'x + ', b)
plt.plot(x, a * x + b, color='red')
plt.scatter(x, y)
plt.savefig('linear')
plt.show()
plt.close()

X = []
Y = []
for n in range(10, 50):
    x, y = generate_x_y(n)
    a = (n * sum(x * y) - sum(x) * sum(y)) / (n * sum(np.square(x)) - (sum(x)) ** 2)
    b = (sum(y) - a * sum(x)) / n
    e = sum((a*x+b-y) ** 2) / n
    X.append(n)
    Y.append(e)

plt.scatter(X, Y)
plt.show()
plt.savefig('error')
plt.close()

# part 2
n = 20
x = np.linspace(0, 5, n)
e = np.random.normal(0, 1, n)
y = x ** 2 + 2 * x + 3 + e
M = np.array([[sum(x ** 4), sum(x ** 3), sum(x ** 2)],
              [sum(x ** 3), sum(x ** 2), sum(x)],
              [sum(x ** 2), sum(x), n]])
S = np.array([sum(x ** 2 * y), sum(x * y), sum(y)])
M = np.matrix(M)
U = np.linalg.inv(M).dot(S)
a, b, c = U[0, 0], U[0, 1], U[0, 2]
print('y = ', a, 'x^2 + ', b, 'x + ', c)
plt.scatter(x, y)
plt.plot(x, a*x**2 + b*x + c, color='red')
plt.savefig('quadratic')
plt.show()
