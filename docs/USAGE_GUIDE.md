# Usage Guide: IIH CAI Intensity Modeling

This guide provides step-by-step instructions for using the CAI intensity modeling framework.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Loading Data](#loading-data)
3. [Running Dose-Response Analysis](#running-dose-response-analysis)
4. [Running DTR Simulations](#running-dtr-simulations)
5. [Analyzing Results](#analyzing-results)
6. [Customization](#customization)

---

## 1. Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/IIH_CAI_Intensity_Modeling.git
cd IIH_CAI_Intensity_Modeling

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```python
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

print("All dependencies installed successfully!")
```

---

## 2. Loading Data

### Load Integrated Dataset

```python
import pickle

# Load the processed integrated dataset
with open('data/processed/iih_integrated_data.pkl', 'rb') as f:
    data = pickle.load(f)

# Available sections
print(data.keys())
# dict_keys(['section_a_clinical_trials', 'section_b_human_observational', ...])

# Access specific sections
clinical_trials = data['section_a_clinical_trials']
print(clinical_trials.head())
```

### Load Data Dictionary

```python
import json

# Load variable definitions
with open('data/data_dictionary.json', 'r') as f:
    data_dict = json.load(f)

# View variable descriptions
print(json.dumps(data_dict, indent=2))
```

---

## 3. Running Dose-Response Analysis

### View Pre-Computed Dose-Response Curves

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load ACZ dose-response
acz_dr = pd.read_csv('results/dose_response/acz_dose_response.csv')

# Plot ICP reduction vs dose
plt.figure(figsize=(10, 6))
plt.plot(acz_dr['dose_mg'], acz_dr['icp_reduction'], marker='o', linewidth=2)
plt.xlabel('Acetazolamide Dose (mg)', fontsize=12)
plt.ylabel('ICP Reduction (mmHg)', fontsize=12)
plt.title('ACZ Dose-Response Curve', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.show()

# View numerical results
print(acz_dr)
```

### Compare ACZ vs TPM Potency

```python
# Load TPM dose-response
tpm_dr = pd.read_csv('results/dose_response/tpm_dose_response.csv')

# Plot comparison
plt.figure(figsize=(12, 6))
plt.plot(acz_dr['dose_mg'], acz_dr['pct_max_icp'], 
         marker='o', label='ACZ', linewidth=2)
plt.plot(tpm_dr['dose_mg'], tpm_dr['pct_max_icp'], 
         marker='s', label='TPM', linewidth=2)
plt.xlabel('Dose (mg)', fontsize=12)
plt.ylabel('% of Maximum ICP Effect', fontsize=12)
plt.title('ACZ vs TPM Dose-Response Comparison', fontsize=14, fontweight='bold')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.show()

# Compare ED50 values
print(f"ACZ reaches 50% effect at: ~1200 mg")
print(f"TPM reaches 50% effect at: ~150 mg")
print(f"TPM is {1200/150:.1f}x more potent per mg")
```

### Analyze Combination Therapy

```python
# Load combination therapy results
combo_dr = pd.read_csv('results/dose_response/combination_dose_response.csv')

# View synergy factors
print("\nCombination Therapy Synergy:")
print(combo_dr[['acz_dose_mg', 'tpm_dose_mg', 'icp_reduction', 
                'synergy_icp', 'synergy_pmd']])
```

---

## 4. Running DTR Simulations

### Load Pre-Computed DTR Results

```python
# Load complete DTR trajectories (1,200 patients × 12 policies)
dtr_results = pd.read_csv('results/dtr_outcomes/dtr_cai_intensity_complete.csv')

print(f"Total trajectories: {len(dtr_results)}")
print(f"Unique policies: {dtr_results['policy_id'].nunique()}")
print(f"Patients per policy: {len(dtr_results) // dtr_results['policy_id'].nunique()}")
```

### Compare Policy Outcomes

```python
# Load policy summary
policy_summary = pd.read_csv('results/dtr_outcomes/cai_intensity_policy_summary.csv')

# Sort by ICP normalization rate
best_policies = policy_summary.sort_values('icp_normalized_<lambda>', ascending=False)
print("\nTop 5 Policies by ICP Normalization:")
print(best_policies[['policy_name', 'total_cai_dose', 
                     'icp_reduction_mean', 'icp_normalized_<lambda>']].head())
```

### Analyze Individual Patient Variability

```python
# Select a specific policy
policy_data = dtr_results[dtr_results['policy_id'] == 'P10_Combo_Standard']

# Plot distribution of outcomes
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ICP reduction distribution
sns.histplot(policy_data['icp_reduction'], bins=20, ax=axes[0], kde=True)
axes[0].set_xlabel('ICP Reduction (mmHg)', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)
axes[0].set_title('Distribution of ICP Reduction\n(ACZ 2g + TPM 100mg)', 
                  fontsize=12, fontweight='bold')
axes[0].axvline(policy_data['icp_reduction'].mean(), color='red', 
                linestyle='--', linewidth=2, label=f'Mean: {policy_data["icp_reduction"].mean():.1f}')
axes[0].legend()

# PMD improvement distribution
sns.histplot(policy_data['pmd_improvement'], bins=20, ax=axes[1], kde=True, color='orange')
axes[1].set_xlabel('PMD Improvement (dB)', fontsize=11)
axes[1].set_ylabel('Frequency', fontsize=11)
axes[1].set_title('Distribution of PMD Improvement\n(ACZ 2g + TPM 100mg)', 
                  fontsize=12, fontweight='bold')
axes[1].axvline(policy_data['pmd_improvement'].mean(), color='red', 
                linestyle='--', linewidth=2, label=f'Mean: {policy_data["pmd_improvement"].mean():.1f}')
axes[1].legend()

plt.tight_layout()
plt.show()
```

---

## 5. Analyzing Results

### Statistical Comparisons

```python
# Load statistical comparisons vs ACZ 2g reference
comparisons = pd.read_csv('results/statistical_analyses/cai_intensity_statistical_comparisons.csv')

# Filter significant results (p < 0.05)
significant = comparisons[comparisons['icp_pvalue'] < 0.05]

print("\nStatistically Significant Improvements over ACZ 2g:")
print(significant[['policy_name', 'icp_diff', 'icp_pvalue', 'icp_cohens_d']])
```

### Sensitivity Analysis by Baseline Severity

```python
# Load severity-stratified results
sensitivity = pd.read_csv('results/statistical_analyses/sensitivity_baseline_severity.csv')

# Compare outcomes by severity
for severity in sensitivity['baseline_severity'].unique():
    print(f"\n=== {severity} ===")
    subset = sensitivity[sensitivity['baseline_severity'] == severity]
    print(subset[['policy', 'icp_reduction', 'icp_normalized_pct', 'surgery_rate_pct']])
```

### Load Bayesian Posterior

```python
import arviz as az

# Load MCMC posterior samples
trace = az.from_netcdf('models/bayesian/posterior_samples.nc')

# View parameter estimates
summary = az.summary(trace, var_names=['acz_ca_inhibition', 'testosterone_nka_effect',
                                       'acz_icp_change', 'azd_icp_change'])
print(summary)

# Check convergence diagnostics
print(f"\nR-hat range: {summary['r_hat'].min():.4f} - {summary['r_hat'].max():.4f}")
print(f"ESS range: {summary['ess_bulk'].min():.0f} - {summary['ess_bulk'].max():.0f}")
```

---

## 6. Customization

### Modify Dose-Response Parameters

If you want to test different dose-response assumptions, you can modify the parameters in `config/`:

```python
import json

# Load model priors
with open('config/model_priors.json', 'r') as f:
    priors = json.load(f)

# View ACZ dose-response parameters
print("Current ACZ parameters:")
print(json.dumps(priors.get('acz_dose_response', {}), indent=2))

# Modify (example only - would need to re-run simulation)
# priors['acz_dose_response']['ed50'] = 1500  # Change ED50
# with open('config/model_priors.json', 'w') as f:
#     json.dump(priors, f, indent=2)
```

### Add New Treatment Policies

To test additional CAI intensity strategies:

1. Define new policy in DTR simulation code
2. Specify ACZ dose, TPM dose, weight loss target
3. Re-run simulation
4. Compare results

---

## Common Analysis Workflows

### Workflow 1: Compare Monotherapy vs Combination

```python
# Extract monotherapy results
acz_2g = dtr_results[dtr_results['policy_id'] == 'P04_ACZ_High']
combo = dtr_results[dtr_results['policy_id'] == 'P10_Combo_Standard']

# Compare outcomes
from scipy import stats

# ICP reduction comparison
t_stat, p_val = stats.ttest_ind(combo['icp_reduction'], acz_2g['icp_reduction'])
print(f"ICP Reduction Comparison:")
print(f"  ACZ 2g: {acz_2g['icp_reduction'].mean():.2f} ± {acz_2g['icp_reduction'].std():.2f} mmHg")
print(f"  Combo:  {combo['icp_reduction'].mean():.2f} ± {combo['icp_reduction'].std():.2f} mmHg")
print(f"  p-value: {p_val:.4f}")
print(f"  Difference: {combo['icp_reduction'].mean() - acz_2g['icp_reduction'].mean():.2f} mmHg")
```

### Workflow 2: Identify Optimal Dose for Your Patient

```python
def recommend_dose(baseline_icp, has_migraine=False):
    """
    Recommend optimal CAI dosing based on baseline ICP and comorbidities
    
    Args:
        baseline_icp: Baseline ICP in mmHg
        has_migraine: Boolean indicating migraine comorbidity
    
    Returns:
        dict: Recommended treatment strategy
    """
    if baseline_icp < 26:
        # Mild IIH
        if has_migraine:
            return {'drug': 'TPM', 'dose': '100mg', 'rationale': 'Addresses both IIH and migraines'}
        else:
            return {'drug': 'ACZ', 'dose': '1g', 'rationale': '97% normalization rate, lower cost'}
    
    elif baseline_icp < 30:
        # Moderate IIH
        return {'drug': 'ACZ', 'dose': '2g', 'rationale': 'IIHTT standard, escalate to combo if needed'}
    
    else:
        # Severe IIH
        return {'drug': 'ACZ + TPM', 'dose': '2g + 100mg', 
                'rationale': 'Combination essential (65% vs 15% normalization)'}

# Example usage
patient1 = recommend_dose(baseline_icp=24, has_migraine=True)
print(f"Patient 1 (ICP 24, migraines): {patient1}")

patient2 = recommend_dose(baseline_icp=32, has_migraine=False)
print(f"Patient 2 (ICP 32, no migraines): {patient2}")
```

---

## Troubleshooting

### Issue: Data file not found
**Solution:** Ensure you're running from repository root and paths are correct

### Issue: Import errors
**Solution:** Activate virtual environment and reinstall requirements
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Memory errors loading large files
**Solution:** Load data in chunks or use data subsets for exploration

---

## Additional Resources

- **Methodology Documentation:** See `docs/methodology/`
- **Data Dictionary:** `data/data_dictionary.json`
- **Comprehensive Findings:** `results/COMPREHENSIVE_FINDINGS.json`

---

**For questions or issues:** Open an issue on GitHub or contact the author.
