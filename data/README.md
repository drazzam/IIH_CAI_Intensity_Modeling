# Data Documentation

This directory contains all data used in the CAI intensity modeling analysis.

---

## Directory Structure

```
data/
├── raw/                          # Original data extractions from literature
│   ├── Section_A_Clinical_Trials.md
│   ├── Section_B_Human_Observational.md
│   ├── Section_C_Animal_Mechanistic.md
│   ├── Section_D_In_Vitro.md
│   ├── Section_E1_Physiological.md
│   └── Section_E2_E3_Endocrine.md
├── processed/                    # Integrated and processed datasets
│   └── iih_integrated_data.pkl
├── data_dictionary.json          # Variable definitions and metadata
└── data_schema.json              # Dataset structure documentation
```

---

## Data Sources

### Section A: Clinical Trials (N=165 patients)
**Primary source:** IIHTT (Idiopathic Intracranial Hypertension Treatment Trial)
- Wall et al. JAMA 2014;311(16):1641-1651
- Randomized, double-masked, placebo-controlled trial
- Intervention: Acetazolamide (up to 4g/day) + weight loss vs placebo + weight loss
- Duration: 6 months
- Primary outcome: Perimetric mean deviation (PMD)

**Additional trials:**
- AZD4017 (11β-HSD1 inhibitor): O'Reilly et al. Brain 2019
- Topiramate studies: Çelebisoy et al. Acta Neurol Scand 2007
- Various smaller trials and case series

### Section B: Human Observational Studies
- Retrospective cohort studies of IIH treatment outcomes
- Dose-response observations from clinical practice
- Long-term follow-up data (>12 months)
- Real-world effectiveness data

### Section C: Animal Mechanistic Studies (N=42 studies)
**Key preclinical data:**
- Scotton et al. Cephalalgia 2019 (TPM vs ACZ ICP reduction in rats)
- Westgate et al. Br J Pharmacol 2024 (acute vs chronic CAI dosing)
- Barbuskaite et al. Fluids Barriers CNS 2022 (ACZ mechanism)
- Choroid plexus carbonic anhydrase expression studies

### Section D: In Vitro Studies
- Carbonic anhydrase isoform specificity (CA II, IV, VA, XII)
- IC50 values for ACZ and TPM
- Transporter-level effects (NKA, NKCC1, AQP1)
- CSF secretion apparatus mechanisms

### Section E1: Physiological Parameters
- CSF production rates (0.35 mL/min baseline)
- CSF outflow resistance (Rcsf: 10-12 mmHg/mL/min)
- Intracranial compliance parameters
- ICP-volume relationships

### Section E2-E3: Endocrine and Metabolic Data
- Testosterone effects on choroid plexus NKA/CA
- 11β-HSD1 cortisol amplification pathways
- GLP-1 receptor agonist effects on ICP
- Weight loss impact on ICP (0.3 mmHg/kg)

---

## Integrated Dataset

**File:** `processed/iih_integrated_data.pkl`

**Total data points:** 3,941 rows across 6 sections

**Structure:**
```python
{
    'section_a_clinical_trials': pd.DataFrame,
    'section_b_human_observational': pd.DataFrame,
    'section_c_animal_mechanistic': pd.DataFrame,
    'section_d_in_vitro': pd.DataFrame,
    'section_e1_physiological': pd.DataFrame,
    'section_e2_endocrine': pd.DataFrame
}
```

**Loading example:**
```python
import pickle

with open('data/processed/iih_integrated_data.pkl', 'rb') as f:
    data = pickle.load(f)

clinical_trials = data['section_a_clinical_trials']
```

---

## Key Variables

### Clinical Outcomes
- **ICP (mmHg):** Intracranial pressure measured by lumbar puncture opening pressure
- **PMD (dB):** Perimetric mean deviation (visual field metric, negative = worse)
- **Papilledema grade:** Frisén scale 0-5 (0=none, 5=severe)
- **Visual acuity:** LogMAR or Snellen
- **Headache severity:** HIT-6 score or VAS

### Treatment Variables
- **ACZ dose (mg/day):** Acetazolamide 0-4000 mg
- **TPM dose (mg/day):** Topiramate 0-400 mg
- **Weight loss (kg):** Change from baseline
- **Treatment duration (months):** Follow-up period

### Patient Characteristics
- **Age (years)**
- **BMI (kg/m²)**
- **Sex:** M/F
- **Baseline ICP (mmHg)**
- **Disease duration (months)**

### Mechanistic Parameters
- **CSF production rate (mL/min)**
- **Rcsf (mmHg/mL/min):** CSF outflow resistance
- **CA inhibition (%):** Carbonic anhydrase inhibition percentage
- **NKA activity (%):** Na-K-ATPase activity
- **Testosterone level (ng/dL)**
- **11β-HSD1 activity (%):** Cortisol amplification

---

## Data Quality

### Validation
- All clinical trial data cross-referenced with original publications
- Animal study parameters verified against reported values
- Physiological parameters within known biological ranges
- Missing data explicitly coded as NaN

### Limitations
- **Heterogeneity:** Data from multiple sources with varying methodologies
- **Missing values:** Not all studies report all variables
- **Temporal coverage:** Studies span 1974-2024 with evolving methodologies
- **Population diversity:** Limited pediatric and male patient data

---

## Data Dictionary

Full variable definitions available in `data_dictionary.json`:

```python
import json

with open('data/data_dictionary.json', 'r') as f:
    data_dict = json.load(f)

print(json.dumps(data_dict, indent=2))
```

---

## Usage Guidelines

1. **Citation:** Always cite original data sources when using this dataset
2. **Assumptions:** Understand data integration assumptions (see methodology docs)
3. **Validation:** Results should be validated against independent datasets
4. **Updates:** Data may be updated as new studies are published

---

## Contact

For questions about data sources, integration methodology, or access to raw extraction files:

**Ahmed Y. Azzam, MD, MEng, DSc(h.c.), FRCP**  
WVU Medicine, Department of Neuroradiology

---

**Last Updated:** 17th November 2025  
**Version:** 1.0.0
