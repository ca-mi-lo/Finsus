import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gamma, poisson

# Seed for reproducibility
np.random.seed(42)

# Simulate some Poisson-distributed data
true_lambda = 5  # True rate parameter
data = np.random.poisson(true_lambda, size=100)  # Simulate 100 observations

# Prior parameters for the Gamma distribution
alpha_prior = 2  # Shape parameter
beta_prior = 1   # Rate parameter

# Posterior parameters
alpha_posterior = alpha_prior + np.sum(data)  # Update shape parameter
beta_posterior = beta_prior + len(data)  # Update rate parameter

# Generate posterior distribution
lambda_values = np.linspace(0, 15, 100)
posterior_distribution = gamma.pdf(lambda_values, a=alpha_posterior, scale=1/beta_posterior)

# Plotting
plt.figure(figsize=(12, 6))
sns.histplot(data, bins=30, stat="density", kde=True, label='Observed Data', color='lightblue')
plt.plot(lambda_values, posterior_distribution, label='Posterior Distribution', color='orange')
plt.axvline(x=true_lambda, color='red', linestyle='--', label='True λ')
plt.title("Bayesian Inference with Poisson Data")
plt.xlabel("Rate Parameter (λ)")
plt.ylabel("Density")
plt.legend()
plt.grid()
plt.show()

# Print posterior parameters
print(f"Posterior Alpha: {alpha_posterior}, Posterior Beta: {beta_posterior}")