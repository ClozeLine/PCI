import scipy.stats as stats
import numpy as np
import pandas as pd

# Observed counts in a contingency table
# Rows: k values (5, 10, 15)
# Columns: categories a, b, c
observed = np.array([
    [10, 3, 86],   # k = 5
    [67, 7, 26],   # k = 10
    [79, 12, 9]    # k = 15
])

# Perform Chi-Square Test
chi2, p, dof, expected = stats.chi2_contingency(observed)

# Display results
print("Chi-square statistic:", chi2)
print("Degrees of freedom:", dof)
print("P-value:", p)
print("\nExpected counts:")
print(pd.DataFrame(expected, columns=['a', 'b', 'c'], index=['k=5', 'k=10', 'k=15']))