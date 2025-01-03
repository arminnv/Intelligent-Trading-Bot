import time

import numpy as np


def LU_factorization(A):
    """
 Computes LU factorization for the given matrix

 inputs:
 A (numpy ndarray): input matrix

 outputs:
 L (numpy ndarray): a lower triangular matrix
 U (numpy ndarray): an upper triangular matrix
 """

    # write your code here

    n = len(A)
    I = np.eye(n)
    U = np.copy(A)
    x = []

    for k in range(n):
        v = U[:, k]
        t_k = np.zeros((n, 1))
        for i in range(k + 1, n):
            t_k[i, 0] = v[i] / v[k]
        T = t_k.dot(np.reshape(I[k, :], (1, n)))
        M = np.eye(n) - T
        M_inverse = np.eye(n) + T
        x.append(M_inverse)
        U = M.dot(U)
    L = I

    for i in range(len(x)):
        L = L.dot(x[i])

    return L, U


# Evaluation Cell
n = 10
A = np.random.randn(n, n)
s = time.time()
L, U = LU_factorization(A.copy())
elapsed = time.time() - s
assert np.linalg.norm(L - np.tril(L)) < 1e-10, "L is not lowertriangular"
assert np.linalg.norm(U - np.triu(U)) < 1e-10, "U is not uppertriangular"
assert np.linalg.norm(A - L @ U) < 1e-10, "L and U does not satisfy A= L @ U"
print(f'status: successful, time elapsed: {np.round(elapsed, 5)}seconds')
