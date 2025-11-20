"""
Machine Learning Experiment - Bayesian A/B Testing

This script implements a Bayesian approach to A/B testing for conversion rate optimization.
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def bayesian_ab_test(conversions_a, trials_a, conversions_b, trials_b, prior_alpha=1, prior_beta=1):
    """
    Perform Bayesian A/B test using Beta distributions.

    Args:
        conversions_a: Number of conversions in variant A
        trials_a: Number of trials in variant A
        conversions_b: Number of conversions in variant B
        trials_b: Number of trials in variant B
        prior_alpha: Alpha parameter for Beta prior
        prior_beta: Beta parameter for Beta prior

    Returns:
        Dictionary with test results
    """
    # Posterior distributions
    posterior_a = stats.beta(prior_alpha + conversions_a, prior_beta + trials_a - conversions_a)
    posterior_b = stats.beta(prior_alpha + conversions_b, prior_beta + trials_b - conversions_b)

    # Sample from posteriors
    samples_a = posterior_a.rvs(10000)
    samples_b = posterior_b.rvs(10000)

    # Calculate probability that B > A
    prob_b_better = (samples_b > samples_a).mean()

    # Expected loss
    expected_loss_a = (np.maximum(samples_b - samples_a, 0)).mean()
    expected_loss_b = (np.maximum(samples_a - samples_b, 0)).mean()

    return {
        'prob_b_better': prob_b_better,
        'prob_a_better': 1 - prob_b_better,
        'expected_loss_a': expected_loss_a,
        'expected_loss_b': expected_loss_b,
        'posterior_a_mean': posterior_a.mean(),
        'posterior_b_mean': posterior_b.mean()
    }


if __name__ == "__main__":
    # Example usage
    results = bayesian_ab_test(
        conversions_a=120,
        trials_a=1000,
        conversions_b=140,
        trials_b=1000
    )

    print("Bayesian A/B Test Results:")
    print(f"Probability B is better: {results['prob_b_better']:.2%}")
    print(f"Expected loss if choosing A: {results['expected_loss_a']:.4f}")
    print(f"Expected loss if choosing B: {results['expected_loss_b']:.4f}")
