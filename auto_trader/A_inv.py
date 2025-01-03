import time

import numpy as np


def inverse(A):
    """
 Computes the inverse of the input matrix

 inputs:
 A (numpy ndarray): input matrix

 outputs:
 A_inv (numpy ndarray): inverse of the input matrix
 """

    # write your code here
    n = len(A)
    I = np.eye(n)
    D = np.concatenate((A, I), axis=1)

    for i in range(n):
        j = 1
        pivot = D[i][i]

        while pivot == 0 and i + j < n:
            D[[i, i + j]] = D[[i + j, i]]
            j += 1
            pivot = D[i][i]
        if pivot == 0:
            return D[:, n:]

        row = D[i]
        D[i] = row / pivot

        for j in [k for k in range(0, n) if k != i]:
            D[j] = D[j] - D[i] * D[j][i]

    A_inv = D[:, n:]

    return A_inv


# Evaluation Cell
n = 10
A = np.random.rand(n, n) + n * np.eye(n, n)
s = time.time()
A_inv = inverse(A.copy())
elapsed = time.time() - s
assert np.linalg.norm(A @ A_inv - np.eye(n, n)) < 1e-10, "A_inv does not satisfy A @ A_inv = I"
print(f'status: successful, time elapsed: {np.round(elapsed, 5)}seconds')
