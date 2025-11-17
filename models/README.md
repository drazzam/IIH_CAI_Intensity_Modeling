# Models Directory

This directory contains all modeling code for the CAI intensity analysis.

## Structure

- **`bayesian/`**: Bayesian hierarchical models
  - `csf_dynamics_model.py`: CSF/ICP mechanistic model
  - `endocrine_pathways.py`: Testosterone/cortisol pathways
  - `clinical_outcomes.py`: ICP→PMD mappings
  - `posterior_samples.nc`: 6,000 MCMC samples (NetCDF format)

- **`dose_response/`**: Hill equation dose-response models
  - `dose_response_model.py`: ACZ, TPM, combination curves

- **`dtr_simulation/`**: Dynamic treatment regime simulator
  - `dtr_simulator.py`: Patient trajectory simulation

## Usage

See main repository README and docs/USAGE_GUIDE.md for detailed usage instructions.
