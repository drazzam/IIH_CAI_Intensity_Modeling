# Results Directory

Contains all analysis outputs from the CAI intensity modeling framework.

## Structure

- **`dose_response/`**: Dose-response curves
  - `acz_dose_response.csv`: ACZ 0-4000mg
  - `tpm_dose_response.csv`: TPM 0-400mg
  - `combination_dose_response.csv`: Synergistic combinations
  - `dose_response_marginal_benefit.csv`: Marginal gains per dose increment

- **`dtr_outcomes/`**: DTR simulation results
  - `dtr_cai_intensity_complete.csv`: 1,200 patient trajectories
  - `dtr_realistic_results.csv`: Original DTR results
  - `dtr_summary_final.json`: Policy-level summaries
  - `cai_intensity_policy_summary.csv`: Aggregate outcomes by policy

- **`statistical_analyses/`**: Statistical comparisons
  - `cai_intensity_statistical_comparisons.csv`: Policy vs ACZ 2g reference
  - `sensitivity_baseline_severity.csv`: Stratified by baseline ICP
  - `posterior_summary.csv`: Bayesian parameter estimates

- **Root-level files:**
  - `COMPREHENSIVE_FINDINGS.json`: Complete results summary
  - `validation_*.json/txt`: Model validation outputs

## Note

Economic evaluation files have been removed as they were not part of the core modeling aims.
