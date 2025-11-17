# Changelog

All notable changes to the IIH CAI Intensity Modeling project.

## [1.0.0] - 2024-11-17

### Added
- Complete dose-response modeling framework for ACZ and TPM
- Hill equation parameterization from literature calibration
- Bayesian hierarchical model (6,000 MCMC samples)
- DTR simulator with 1,200 patient trajectories across 12 policies
- Comprehensive statistical analyses and comparisons
- Severity-stratified outcome analyses
- Full documentation and usage guides
- Publication-ready tables and figures

### Key Findings
- ACZ dose-response plateau at 2-3g (80-81% of maximum)
- TPM 8× more potent than ACZ per mg (ED50: 150mg vs 1200mg)
- Combination therapy synergy: 15% ICP, 10% PMD enhancement
- Optimal strategy: ACZ 2g + TPM 100mg (89% ICP normalization)
- Severity-stratified precision dosing algorithms

### Validated Against
- IIHTT trial data (ACZ 2g, N=165)
- AZD4017 trial (11β-HSD1 inhibitor)
- Preclinical dose-response studies (Scotton 2019, Westgate 2024)

### Repository Structure
- `/data`: Raw and processed datasets (3,941 data points)
- `/models`: Bayesian and dose-response models
- `/results`: All analysis outputs
- `/config`: Model parameters and calibration data
- `/docs`: Comprehensive documentation

---

**Version:** 1.0.0  
**Author:** Ahmed Y. Azzam, MD, MEng, DSc(h.c.), FRCP  
**Institution:** WVU Medicine, Department of Neuroradiology  
**Date:** November 17, 2024
