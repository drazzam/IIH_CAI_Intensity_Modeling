# Methodology Documentation

## Overview

This document describes the mechanistic Bayesian evidence synthesis and dynamic treatment regime (DTR) simulation methodology used to quantify CAI intensity effects in IIH.

---

## 1. Data Integration

### Sources
- **IIHTT RCT** (N=165): Primary calibration data
- **Preclinical studies** (N=42): Dose-response parameters
- **Mechanistic literature**: CSF dynamics, CA pharmacology
- **Total**: 3,941 integrated data points

### Integration Method
- Bayesian hierarchical framework
- Multi-level evidence synthesis
- Literature-based prior elicitation
- Cross-study harmonization

---

## 2. Dose-Response Modeling

### Hill Equation

E = E_max × D^n / (ED50^n + D^n)

Where:
- E = Effect (ICP reduction or PMD improvement)
- E_max = Maximum achievable effect
- D = Dose (mg/day)
- ED50 = Dose producing 50% of maximum effect
- n = Hill coefficient (cooperativity)

### Parameter Calibration

**Acetazolamide (ACZ):**
- ICP ED50: 1200 mg (from IIHTT dose titration)
- ICP E_max: -8.5 mmHg (from maximal observed effects)
- PMD ED50: 1400 mg
- PMD E_max: 2.5 dB

**Topiramate (TPM):**
- ICP ED50: 150 mg (8× more potent, Scotton 2019)
- ICP E_max: -9.5 mmHg (slightly higher lipophilicity)
- PMD ED50: 180 mg
- PMD E_max: 2.8 dB

**Combination Synergy:**
- ICP synergy factor: 1.15 (15% enhancement)
- PMD synergy factor: 1.10 (10% enhancement)
- Based on: Loewe additivity + mechanistic reasoning

---

## 3. Bayesian Hierarchical Model

### Structure

Level 1: Physiological Parameters
- CSF production rate (0.35 ± 0.10 mL/min)
- CSF outflow resistance (10.6 ± 2.8 mmHg/mL/min)
- Choroid plexus CA activity

Level 2: Treatment Effects
- CAI dose → CA inhibition → CSF reduction → ICP reduction
- Weight loss → mechanical effects → ICP reduction

Level 3: Endocrine Pathways
- Testosterone → NKA/CA upregulation
- 11β-HSD1 → cortisol amplification

Level 4: Clinical Outcomes
- ICP → PMD (perimetric mean deviation)
- ICP → Papilledema grade
- ICP → Headache severity

### MCMC Sampling

- **Algorithm:** NUTS (No-U-Turn Sampler)
- **Chains:** 4 independent
- **Draws per chain:** 1,500 (after 1,000 tuning)
- **Total samples:** 6,000
- **Convergence:** R-hat = 1.003, ESS = 3,717

### Validation

| Trial | Outcome | Predicted | Observed | Error |
|-------|---------|-----------|----------|-------|
| IIHTT | ACZ PMD | 1.65 dB | 1.43 dB | 15% |
| IIHTT | Placebo PMD | 0.59 dB | 0.71 dB | 17% |
| AZD4017 | ICP change | -2.38 mmHg | -2.30 mmHg | 3% |

---

## 4. DTR Simulation

### Patient Heterogeneity

- **Biological response:** Log-normal(0, 0.3) → 0.5-1.5× effect
- **Adherence:** Beta(8, 2) → 30-100% typical
- **Baseline ICP:** N(28, 4) mmHg

### Realistic Features

1. **Drug tolerance:** 10% efficacy reduction per 6 months
2. **Adherence variability:** Monthly fluctuations (85-100% of baseline)
3. **Weight loss dynamics:** Exponential approach to target
4. **Stochastic noise:** ±2-4 mmHg ICP, ±1-2 dB PMD

### Simulation Parameters

- **N patients:** 100 per policy
- **N policies:** 12 (ACZ monotherapy, TPM monotherapy, combinations)
- **Duration:** 12 months
- **Time step:** Monthly
- **Total trajectories:** 1,200

---

## 5. Statistical Analysis

### Primary Outcomes
- ICP reduction (mmHg)
- PMD improvement (dB)
- ICP normalization rate (ICP <25 mmHg)
- Vision preservation
- Surgery avoidance

### Comparisons
- Two-sample t-tests (policy vs ACZ 2g reference)
- Cohen's d effect sizes
- Bonferroni correction for multiple comparisons
- Sensitivity analyses by baseline severity

### Reporting
- Mean ± SD for continuous outcomes
- Percentages for binary outcomes
- 95% confidence intervals
- p-values and effect sizes

---

## 6. Limitations

### Model-Based Evidence
- Simulated outcomes, not prospective RCT
- Assumptions about synergy magnitude
- Simplified patient heterogeneity

### Data Limitations
- Limited head-to-head TPM vs ACZ trials
- 12-month follow-up (extrapolation beyond)
- Moderate-severity IIH bias (ICP 22-35 mmHg)

### Generalizability
- Adult female population primarily
- Excluded pediatric, fulminant, pregnancy
- Single-ethnicity studies overrepresented

---

## 7. Software & Reproducibility

### Core Libraries
- **PyMC:** Bayesian inference (v5.0+)
- **ArviZ:** Convergence diagnostics
- **NumPy/Pandas:** Data manipulation
- **SciPy:** Statistical tests

### Random Seeds
- Dose-response: N/A (deterministic)
- DTR simulation: seed=42
- Bayesian sampling: seed=42

### Hardware
- Standard CPU (no GPU required)
- RAM: 8GB minimum
- Runtime: around 2 hours for complete analysis

---

**Author:** Ahmed Y. Azzam, MD, MEng, DSc(h.c.), FRCP  
**Last Updated:** 17th November 2025 
