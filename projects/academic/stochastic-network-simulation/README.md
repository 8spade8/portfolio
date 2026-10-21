# 📈 Stochastic Network Simulation

> Network traffic simulated from first principles: random variates are generated with classical methods (inversion and rejection) rather than library samplers, then plotted to check them against the theory.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square)

| | |
|---|---|
| **Context** | Stochastic processes coursework |
| **Focus** | Random-variate generation and simulation of a packet network |

---

## What it models

| Phenomenon | Distribution | Generation method |
|---|---|---|
| **Packets arriving per second** | Poisson | **Inversion** for discrete variables: build the cumulative distribution iteratively, draw a uniform and return the first index it falls below |
| **Time between two successive packets** | Exponential | **Acceptance–rejection**: propose from a simple distribution, accept with probability proportional to the target density |
| **Gaussian variability** | Normal | Generated from uniform variates |

```mermaid
flowchart LR
    U["Uniform random source"] --> I["Inversion<br/>discrete CDF"] --> P["Poisson counts per second"]
    U --> R["Acceptance and rejection"] --> E["Exponential inter-arrival times"]
    U --> G["Gaussian generator"] --> N["Gaussian variability"]
    P --> V["Histograms vs theoretical law"]
    E --> V
    N --> V
```

## Why it's interesting

- Implements the algorithms **from the definition**, which shows what a library call hides.
- **Validates by simulation**: empirical histograms are compared with the theoretical densities.
- Provides the building blocks for a queueing or network-load model.
