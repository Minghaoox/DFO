import numpy as np
from time import perf_counter
import multiprocessing as mp
from multiprocessing import pool
import concurrent.futures
import os
import sys

open('MultiFitness.txt', 'w').close()

def scientific(x, n):
    n = int(n)
    x = float(x)
    if n < 1: raise ValueError("1+ significant digits required.")
    return ''.join(('{:.', str(n - 1), 'e}')).format(x)


# FITNESS FUNCTION (SPHERE FUNCTION)
def sphere(x):  # x IS A VECTOR REPRESENTING ONE FLY. SPHERE FUNCTION with bounds ∈ [-100, 100]
    sums = 0.0
    for i in range(len(x)):
        sums = sums + np.power(x[i], 2)
    return sums


def rastrigin(x):  # Rastrigin Function, ∈ [-5.12, 5.12]
    sums = 0.0
    for i in range(len(x)):
        sums += x[i] ** 2 - (10 * np.cos(2 * np.pi * x[i])) + 10
    return sums


def schwefel_1_2(x):  # Schwefel 1.2 Function, ∈ [−100,100]
    # x = np.array(x)
    sums = 0.0
    for i in range(len(x)):
        sums = sums + (sums + x[i] ** 2)
    return sums


def rosenbrock(x):  # Rosenbrock Function, ∈ [-5, 10] but may be restricted to [-2.048, 2.048]
    sums = 0.0
    for i in range(len(x) - 1):
        xn = x[i + 1]
        new = 100 * np.power(xn - np.power(x[i], 2), 2) + np.power(x[i] - 1, 2)
        sums = sums + new
    return sums


def ackley(x):  # Ackley Function, ∈ [-32.768, 32.768]
    sum = 0.0
    sum2 = 0.0
    for c in x:
        sum += c ** 2.0
        sum2 += np.cos(2.0 * np.pi * c)
    n = float(len(x))
    return -20.0 * np.exp(-0.2 * np.sqrt(sum / n)) - np.exp(sum2 / n) + 20 + np.exp(1)


def griewank(x):  # Griewank Function, ∈ [-600, 600]
    p1 = 0
    for i in range(len(x)):
        p1 += x[i] ** 2
        p2 = 1
    for i in range(len(x)):
        p2 *= np.cos(float(x[i] / np.sqrt(i + 1)))
    return 1 + (float(p1) / 4000.0) - float(p2)


def goldstein(x):  # Goldstein Function, ∈ [-2, 2]
    if len(x) <= 2:
        return goldsteinAid(0, x)
    else:
        total = 0
        for i in range(len(x)):
            total += x[i] * \
                     goldsteinAid(i, x)
    return total


def goldsteinAid(i, x):  # Main component of the Goldstein Function
    x1 = x[i]
    x2 = x[(i + 1) % len(x)]  # Two flies are taken to be used
    eq1a = np.power(x1 + x2 + 1, 2)
    eq1b = 19 - 14 * x1 + 3 * np.power(x1, 2) - 14 * x2 + 6 * x1 * x2 + 3 * np.power(x2, 2)
    eq1 = 1 + eq1a * eq1b
    eq2a = np.power(2 * x1 - 3 * x2, 2)
    eq2b = 18 - 32 * x1 + 12 * np.power(x1, 2) + 48 * x2 - 36 * x1 * x2 + 27 * np.power(x2, 2)
    eq2 = 30 + eq2a * eq2b
    return eq1 * eq2


def camel6(x):  # Six-Hump Camel-Back Function, x1 ∈ [-3, 3] and x2 ∈ [-2, 2] so decided to use ∈ [-5, 5]
    if len(x) <= 2:
        return camel6Aid(0, x)
    else:
        total = 0
        for i in range(len(x)):
            total += x[i] * \
                     camel6Aid(i, x)
        return total


def camel6Aid(i, x):  # Main component of the Camel-Back Function
    x1 = x[i]
    x2 = x[(i + 1) % len(x)]  # Two flies are also needed
    part1 = (4 - 2.1 * np.power(x1, 2) + (np.power(x1, 4) / 3)) * np.power(x1, 2)
    part2 = x1 * x2
    part3 = (- 4 + 4 * np.power(x2, 2))
    return part1 + part2 + part3


def lunaceksBiRastrigin(x):  # Lunaceks Bi-Rastrigin Function ∈ [-5.12,5.12]
    sum = 0.0
    sum1 = 0.0
    sum2 = 0.0
    s = 1 - (1 / (2 * np.sqrt(len(x) + 20) - 8.2))
    d = 1
    mu = 2.5
    mu1 = - np.sqrt(abs((mu ** 2 - d) / s))
    for i in range(len(x)):
        sum += (x[i] - mu) ** 2
        sum1 += (x[i] - mu1) ** 2
        sum2 += 1 - np.cos(2 * np.pi * (x[i] - mu))
    return min(sum, d * len(x) + s * sum1) + 10 * sum2


def schafferN06(x):  # Schaffer N0 6 Function ∈ [-100,100]
    if len(x) <= 2:
        return schafferAid(0, x)
    else:
        total = 0
        for i in range(len(x)):
            total += x[i] * \
                     schafferAid(i, x)
        return total


def schafferAid(i, x):  # Main component of Schaffer N06 Function
    x1 = x[i]
    y1 = x[(i + 1) % len(x)]  # Uses two flies
    xysqrd = x1 ** 2 + y1 ** 2
    return 0.5 + (np.sin(np.sqrt(xysqrd)) - 0.5) / (1 + 0.001 * xysqrd) ** 2


def shiftedRastrigin(x):  # Shifted Rastrigin Function, ∈ [-5, 5]
    summ = 0.0
    sum1 = 0.0
    fopt = 100
    for i in range(len(x)):
        summ = summ + (np.power(x[i], 2) - 10 * np.cos(2 * np.pi * x[i]) + 10)  # The original Rastrgin function is -
        # used to get the optimal fly, so it can be used for shifting the function

        xopt = 0.0512 * (summ - x[i])  # The optimal fly is stored and ready to be used again
    return sum1 + (np.power(xopt, 2) - 10 * np.cos(2 * np.pi * xopt) + 10 + fopt)  # Shifted Rastrign function is -
    # executed on return here


def shiftedRosenbrock(x):  # Shifted Rosenbrock Function, ∈ [-2, 2]
    sums = 0.0
    sums1 = 0.0
    fopt = 100
    for i in range(len(x) - 1):
        xn = x[i + 1]
        new = 100 * np.power(np.power(x[i], 2) - xn, 2) + np.power(x[i] - 1, 2)  # The original Rosenbrock function is
        # used to get the optimal fly, so it can later be used for shifting

        sums = sums + new
        xopt = 0.02048 * (sums - x[i]) + 1
    return sums1 + 100 * np.power(np.power(xopt, 2) - xopt, 2) + np.power(xopt - 1, 2)  # Shifted Rosenbrock function is
    # executed on return here


t0 = perf_counter()
# file = open("MultiFitness.txt", "r+")

N = 100  # POPULATION SIZE
D = 30  # DIMENSIONALITY
delta = 0.001  # DISTURBANCE THRESHOLD
maxIterations = 3100  # ITERATIONS ALLOWED
lowerB = [-100] * D  # LOWER BOUND (IN ALL DIMENSIONS)
upperB = [100] * D  # UPPER BOUND (IN ALL DIMENSIONS)


def multi():
    lis = []
    # INITIALISATION PHASE
    X = np.empty([N, D])  # EMPTY FLIES ARRAY OF SIZE: (N,D)
    fitness = [None] * N  # EMPTY FITNESS ARRAY OF SIZE N

    # INITIALISE FLIES WITHIN BOUNDS
    for i in range(N):
        for d in range(D):
            X[i, d] = np.random.uniform(lowerB[d], upperB[d])

    # MAIN DFO LOOP
    for itr in range(maxIterations):
        for i in range(N):  # EVALUATION
            fitness[i] = sphere(X[i,])
        s = np.argmin(fitness)  # FIND BEST FLY

        if itr % 100 == 0:  # PRINT BEST FLY EVERY 100 ITERATIONS
            print("Iteration:", itr, "\tBest fly index:", s,
                  "\tFitness value:", fitness[s])

        # TAKE EACH FLY INDIVIDUALLY
        for i in range(N):
            if i == s: continue  # ELITIST STRATEGY

            # FIND BEST NEIGHBOUR
            left = (i - 1) % N
            right = (i + 1) % N
            bNeighbour = right if fitness[right] < fitness[left] else left

            for d in range(D):  # UPDATE EACH DIMENSION SEPARATELY
                if np.random.rand() < delta:
                    X[i, d] = np.random.uniform(lowerB[d], upperB[d])
                    continue

                u = np.random.rand()
                X[i, d] = X[bNeighbour, d] + u * (X[s, d] - X[i, d])

                # OUT OF BOUND CONTROL
                if X[i, d] < lowerB[d] or X[i, d] > upperB[d]:
                    X[i, d] = np.random.uniform(lowerB[d], upperB[d])

    for i in range(N): fitness[i] = sphere(X[i,])  # EVALUATION
    s = np.argmin(fitness)  # FIND BEST FLY
    lis.append(fitness[s])

    with open("MultiFitness.txt", "a+") as f:
        f.write(f"{fitness[s]}\n")  # :.50f}\n")
        f.close()

    print("\nFinal best fitness:\t", fitness[s])
    print("\nBest fly position:\n", X[s,])
    minimum = X[s,].min()
    maximum = X[s,].max()
    Fmean = X[s,].mean()
    standardDev = X[s,].std()
    print("The min is: ", minimum, "\nThe Max is: ", maximum, "\nThe Mean is: ", Fmean, "\nThe Standard Deviation is: ",
          standardDev)


if __name__ == "__main__":
    processes = []
    tStart = perf_counter()
    for _ in range(30):
        p1 = mp.Process(target=multi, )
        p1.start()
        processes.append(p1)

    for process in processes:
        process.join()
    tEnd = perf_counter()
    newLis = np.loadtxt('MultiFitness.txt', delimiter="\n")

    print(newLis)
    print("These are the best fies after 30 trials:", newLis, f"\nMin = ", min(newLis),
          "\nMax = ", max(newLis), "\nMedian = ", np.median(newLis), "\nMean = ", np.mean(newLis),
          "\nStandard deviation = ", np.std(newLis), "\nCounter says ")

    print("Time elapsed: ", tEnd - tStart)
    fMean = np.mean(newLis)
    standardDev = np.std(newLis)
    print("Mean: ", scientific(fMean, 3), "Standard deviation: ", scientific(standardDev, 3))
