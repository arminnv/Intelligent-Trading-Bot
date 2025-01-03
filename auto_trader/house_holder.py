import math

import numpy as np

def my_QR(A):
    """
    inputs:
        A (numpy ndarray): input matrix
    outputs:
        Q (numpy ndarray): orthonormal matrix
        R (numpy ndarray): upper triangular matrix

    """
    ### To Do ###
    m, n = A.shape
    Q = np.eye(m)
    R = A.copy()

    for i in range(min(m, n)):
        x = R[i:, i]    # target column for zeroing elements except 1st
        v1 = x[0] + np.sign(x[0]) * np.linalg.norm(x)
        v = x / v1
        v[0] = 1
        beta = 2 / sum(v**2)    # calculating beta

        R[i:, :] = R[i:, :] - beta * np.outer(v, v) @ R[i:, :]  # (I - 2b * vvT)R
        Q[:, i:] = Q[:, i:] - beta * Q[:, i:] @ np.outer(v, v)

    return Q, R


# time and correctness test
numpy_test = {'upper-triangular and  orthogonal test error': 0.0, 'correctness test error': 0.0}
yours_test = {'upper-triangular and  orthogonal test error': 0.0, 'correctness test error': 0.0}

num_test = 50
for i in range(num_test):
    m, n = np.random.randint(40, 50), np.random.randint(40, 50)
    A = np.random.randn(m, n)

    # numpy code
    Q, R = np.linalg.qr(A.copy(), mode='complete')
    numpy_test['upper-triangular and  orthogonal test error'] += np.linalg.norm(np.tril(R, -1)) + np.linalg.norm(
        np.eye(m) - Q @ Q.T)
    numpy_test['correctness test error'] += np.linalg.norm(A - Q @ R)

    ### To Do ###

    my_Q, my_R = my_QR(A.copy())
    yours_test['upper-triangular and  orthogonal test error'] += np.linalg.norm(np.tril(my_R, -1)) + np.linalg.norm(
        np.eye(m) - my_Q @ my_Q.T)
    yours_test['correctness test error'] += np.linalg.norm(A - my_Q @ my_R)

for name in numpy_test:
    numpy_test[name] /= num_test
    yours_test[name] /= num_test

yours_check = {
    'upper-triangular and  orthogonal test error': yours_test['upper-triangular and  orthogonal test error'] <= 1e-5,
    'correctness test error': yours_test['correctness test error'] <= 1e-5}

print(f'numpy| test ---> {numpy_test}')
print(f'yours| test ---> {yours_test}')
print(f'yours| check ---> {yours_check}')