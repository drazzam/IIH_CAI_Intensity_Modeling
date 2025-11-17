"""
Dynamic Treatment Regime (DTR) Simulator for CAI Intensity in IIH

Simulates patient trajectories under different CAI dosing strategies with
realistic heterogeneity, adherence variability, and drug tolerance.

Author: Ahmed Y. Azzam, MD, MEng, DSc(h.c.), FRCP
Institution: WVU Medicine, Department of Neuroradiology
Date: November 2024
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import sys
sys.path.append('../dose_response')
from dose_response_model import calculate_combination_response

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

N_PATIENTS = 100
N_MONTHS = 12
RANDOM_SEED = 42

# Baseline ICP distribution (typical IIH)
BASELINE_ICP_MEAN = 28.0
BASELINE_ICP_STD = 4.0
BASELINE_PMD_MEAN = -8.0

# ============================================================================
# CAI TREATMENT POLICIES
# ============================================================================

CAI_POLICIES = {
    'P01_ACZ_Low': {'acz': 500, 'tpm': 0, 'wl': 2},
    'P02_ACZ_Standard': {'acz': 1000, 'tpm': 0, 'wl': 3},
    'P03_ACZ_Moderate': {'acz': 1500, 'tpm': 0, 'wl': 3},
    'P04_ACZ_High': {'acz': 2000, 'tpm': 0, 'wl': 3},
    'P05_ACZ_VeryHigh': {'acz': 3000, 'tpm': 0, 'wl': 3},
    'P06_ACZ_Max': {'acz': 4000, 'tpm': 0, 'wl': 3},
    'P07_TPM_Standard': {'acz': 0, 'tpm': 100, 'wl': 4},
    'P08_TPM_High': {'acz': 0, 'tpm': 200, 'wl': 5},
    'P09_Combo_Low': {'acz': 1000, 'tpm': 100, 'wl': 4},
    'P10_Combo_Standard': {'acz': 2000, 'tpm': 100, 'wl': 4},
    'P11_Combo_High': {'acz': 2000, 'tpm': 200, 'wl': 5},
    'P12_Combo_Intensive': {'acz': 3000, 'tpm': 200, 'wl': 6}
}

# ============================================================================
# PATIENT SIMULATOR
# ============================================================================

def simulate_patient(patient_id: int, policy: Dict, months: int = 12) -> Dict:
    """
    Simulate individual patient trajectory under treatment policy.
    
    Args:
        patient_id: Unique patient identifier
        policy: Treatment policy dict with 'acz', 'tpm', 'wl'
        months: Simulation duration in months
    
    Returns:
        Dictionary with baseline, final, and trajectory outcomes
    """
    # Baseline characteristics
    baseline_icp = np.random.normal(BASELINE_ICP_MEAN, BASELINE_ICP_STD)
    baseline_icp = np.clip(baseline_icp, 22, 40)
    baseline_pmd = BASELINE_PMD_MEAN
    
    # Patient heterogeneity
    icp_response_factor = np.clip(np.random.lognormal(0, 0.3), 0.5, 1.5)
    pmd_response_factor = np.clip(np.random.lognormal(0, 0.25), 0.6, 1.4)
    
    # Adherence
    base_adherence = np.random.beta(8, 2)
    if policy['acz'] + policy['tpm'] > 2000:
        base_adherence *= 0.90
    
    # Initialize
    icp_current = baseline_icp
    pmd_current = baseline_pmd
    
    # Simulate monthly evolution
    for month in range(1, months + 1):
        # Monthly adherence fluctuation
        adherence = base_adherence * np.random.uniform(0.85, 1.0)
        
        # Get drug effects from dose-response model
        response = calculate_combination_response(
            policy['acz'] * adherence,
            policy['tpm'] * adherence
        )
        
        # Apply heterogeneity
        drug_icp_effect = response['icp_reduction'] * icp_response_factor
        drug_pmd_effect = response['pmd_improvement'] * pmd_response_factor
        
        # Drug tolerance (10% reduction per 6 months)
        tolerance = 1.0 - (month / 60.0)
        drug_icp_effect *= tolerance
        drug_pmd_effect *= tolerance
        
        # Weight loss effect
        wl_achieved = policy['wl'] * (1 - np.exp(-month / 4.0))
        wl_icp_effect = wl_achieved * -0.3
        wl_pmd_effect = wl_achieved * 0.05
        
        # Total effects with noise
        total_icp_effect = drug_icp_effect + wl_icp_effect + np.random.normal(0, 2.0)
        total_pmd_effect = drug_pmd_effect + wl_pmd_effect + np.random.normal(0, 1.0)
        
        # Update state
        icp_current = np.clip(baseline_icp + total_icp_effect, 8, 45)
        pmd_current = np.clip(baseline_pmd - total_pmd_effect, -15, 0)
    
    # Outcomes
    icp_reduction = baseline_icp - icp_current
    pmd_improvement = pmd_current - baseline_pmd
    icp_normalized = 1 if icp_current < 25 else 0
    vision_preserved = 1 if pmd_improvement > -2 else 0
    surgery_needed = 1 if icp_current > 30 or pmd_improvement < -3 else 0
    
    return {
        'patient_id': patient_id,
        'baseline_icp': baseline_icp,
        'final_icp': icp_current,
        'icp_reduction': icp_reduction,
        'baseline_pmd': baseline_pmd,
        'final_pmd': pmd_current,
        'pmd_improvement': pmd_improvement,
        'icp_normalized': icp_normalized,
        'vision_preserved': vision_preserved,
        'surgery_needed': surgery_needed,
        'adherence': base_adherence
    }

# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_dtr_simulation() -> pd.DataFrame:
    """Run complete DTR simulation across all policies."""
    
    np.random.seed(RANDOM_SEED)
    results = []
    
    print(f"Simulating {len(CAI_POLICIES)} policies × {N_PATIENTS} patients...")
    
    for policy_id, policy_params in CAI_POLICIES.items():
        for patient_id in range(N_PATIENTS):
            outcome = simulate_patient(patient_id, policy_params, N_MONTHS)
            outcome['policy_id'] = policy_id
            outcome['acz_dose'] = policy_params['acz']
            outcome['tpm_dose'] = policy_params['tpm']
            outcome['total_cai_dose'] = policy_params['acz'] + policy_params['tpm']
            results.append(outcome)
    
    return pd.DataFrame(results)

def main():
    """Execute DTR simulation and save results."""
    
    print("="*80)
    print("DTR SIMULATION: CAI INTENSITY COMPARISON")
    print("="*80)
    
    df_results = run_dtr_simulation()
    
    # Save
    output_path = '../../results/dtr_outcomes/dtr_cai_intensity_complete.csv'
    df_results.to_csv(output_path, index=False)
    
    # Summary
    summary = df_results.groupby('policy_id').agg({
        'icp_reduction': 'mean',
        'pmd_improvement': 'mean',
        'icp_normalized': lambda x: x.mean() * 100
    }).round(2)
    
    print(f"\n✓ Simulated {len(df_results)} trajectories")
    print("\nPolicy Summary (ICP Normalization %):")
    print(summary['icp_normalized'].sort_values(ascending=False))

if __name__ == '__main__':
    main()
