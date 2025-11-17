"""
Dose-Response Modeling for Carbonic Anhydrase Inhibitors in IIH

This module implements Hill equation dose-response curves for acetazolamide (ACZ)
and topiramate (TPM), including synergistic combination effects.

Author: Ahmed Y. Azzam, MD, MEng, DSc(h.c.), FRCP
Institution: WVU Medicine, Department of Neuroradiology
Date: November 2024
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple

# ============================================================================
# DOSE-RESPONSE PARAMETERS (from literature calibration)
# ============================================================================

ACZ_PARAMS = {
    'name': 'Acetazolamide',
    'icp_emax': -8.5,      # Maximum ICP reduction (mmHg) at infinite dose
    'icp_ed50': 1200,      # Dose for 50% max effect (mg/day)
    'icp_hill': 1.2,       # Hill coefficient (slight cooperativity)
    'pmd_emax': 2.5,       # Maximum PMD improvement (dB)
    'pmd_ed50': 1400,      # Dose for 50% max effect (mg/day)
    'pmd_hill': 1.1,       # Hill coefficient
}

TPM_PARAMS = {
    'name': 'Topiramate',
    'icp_emax': -9.5,      # Maximum ICP reduction (mmHg)
    'icp_ed50': 150,       # Dose for 50% max effect (mg/day) - 8× more potent
    'icp_hill': 1.3,       # Hill coefficient (steeper response)
    'pmd_emax': 2.8,       # Maximum PMD improvement (dB)
    'pmd_ed50': 180,       # Dose for 50% max effect (mg/day)
    'pmd_hill': 1.2,       # Hill coefficient
}

SYNERGY_PARAMS = {
    'icp_synergy': 1.15,   # 15% synergistic enhancement for ICP
    'pmd_synergy': 1.10,   # 10% synergistic enhancement for PMD
}

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def hill_equation(dose: float, emax: float, ed50: float, hill_coef: float) -> float:
    """
    Hill equation for dose-response relationship.
    
    E = Emax × D^n / (ED50^n + D^n)
    
    Args:
        dose: Drug dose (mg)
        emax: Maximum achievable effect
        ed50: Dose producing 50% of maximum effect
        hill_coef: Hill coefficient (cooperativity)
    
    Returns:
        Effect magnitude
    """
    if dose == 0:
        return 0.0
    
    return emax * (dose ** hill_coef) / (ed50 ** hill_coef + dose ** hill_coef)


def calculate_acz_response(dose_mg: float) -> Dict[str, float]:
    """
    Calculate acetazolamide dose-response.
    
    Args:
        dose_mg: ACZ dose in mg/day
    
    Returns:
        Dictionary with ICP and PMD effects
    """
    icp_effect = hill_equation(dose_mg, ACZ_PARAMS['icp_emax'],
                               ACZ_PARAMS['icp_ed50'], ACZ_PARAMS['icp_hill'])
    
    pmd_effect = hill_equation(dose_mg, ACZ_PARAMS['pmd_emax'],
                               ACZ_PARAMS['pmd_ed50'], ACZ_PARAMS['pmd_hill'])
    
    return {
        'dose_mg': dose_mg,
        'icp_reduction': icp_effect,
        'pmd_improvement': pmd_effect,
        'pct_max_icp': abs(icp_effect / ACZ_PARAMS['icp_emax'] * 100),
        'pct_max_pmd': abs(pmd_effect / ACZ_PARAMS['pmd_emax'] * 100)
    }


def calculate_tpm_response(dose_mg: float) -> Dict[str, float]:
    """
    Calculate topiramate dose-response.
    
    Args:
        dose_mg: TPM dose in mg/day
    
    Returns:
        Dictionary with ICP and PMD effects
    """
    icp_effect = hill_equation(dose_mg, TPM_PARAMS['icp_emax'],
                               TPM_PARAMS['icp_ed50'], TPM_PARAMS['icp_hill'])
    
    pmd_effect = hill_equation(dose_mg, TPM_PARAMS['pmd_emax'],
                               TPM_PARAMS['pmd_ed50'], TPM_PARAMS['pmd_hill'])
    
    return {
        'dose_mg': dose_mg,
        'icp_reduction': icp_effect,
        'pmd_improvement': pmd_effect,
        'pct_max_icp': abs(icp_effect / TPM_PARAMS['icp_emax'] * 100),
        'pct_max_pmd': abs(pmd_effect / TPM_PARAMS['pmd_emax'] * 100)
    }


def calculate_combination_response(acz_dose: float, tpm_dose: float) -> Dict[str, float]:
    """
    Calculate combination therapy response with synergy.
    
    Args:
        acz_dose: Acetazolamide dose (mg/day)
        tpm_dose: Topiramate dose (mg/day)
    
    Returns:
        Dictionary with combined effects including synergy
    """
    # Individual effects
    acz_icp = hill_equation(acz_dose, ACZ_PARAMS['icp_emax'],
                           ACZ_PARAMS['icp_ed50'], ACZ_PARAMS['icp_hill'])
    acz_pmd = hill_equation(acz_dose, ACZ_PARAMS['pmd_emax'],
                           ACZ_PARAMS['pmd_ed50'], ACZ_PARAMS['pmd_hill'])
    
    tpm_icp = hill_equation(tpm_dose, TPM_PARAMS['icp_emax'],
                           TPM_PARAMS['icp_ed50'], TPM_PARAMS['icp_hill'])
    tpm_pmd = hill_equation(tpm_dose, TPM_PARAMS['pmd_emax'],
                           TPM_PARAMS['pmd_ed50'], TPM_PARAMS['pmd_hill'])
    
    # Synergistic combination
    combo_icp = (acz_icp + tpm_icp) * SYNERGY_PARAMS['icp_synergy']
    combo_pmd = (acz_pmd + tpm_pmd) * SYNERGY_PARAMS['pmd_synergy']
    
    return {
        'acz_dose_mg': acz_dose,
        'tpm_dose_mg': tpm_dose,
        'total_dose_mg': acz_dose + tpm_dose,
        'icp_reduction': combo_icp,
        'pmd_improvement': combo_pmd,
        'synergy_icp': abs(combo_icp / (acz_icp + tpm_icp)) if (acz_icp + tpm_icp) != 0 else 1.0,
        'synergy_pmd': abs(combo_pmd / (acz_pmd + tpm_pmd)) if (acz_pmd + tpm_pmd) != 0 else 1.0
    }


def generate_dose_response_curves() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate complete dose-response curves for ACZ, TPM, and combinations.
    
    Returns:
        Three DataFrames: (acz_results, tpm_results, combination_results)
    """
    # ACZ dose range (0-4000 mg)
    acz_doses = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
    acz_results = [calculate_acz_response(dose) for dose in acz_doses]
    
    # TPM dose range (0-400 mg)
    tpm_doses = [0, 25, 50, 100, 150, 200, 250, 300, 400]
    tpm_results = [calculate_tpm_response(dose) for dose in tpm_doses]
    
    # Combination therapy (clinically relevant combinations)
    combinations = [
        (1000, 100),   # ACZ 1g + TPM 100mg
        (1000, 200),   # ACZ 1g + TPM 200mg
        (2000, 100),   # ACZ 2g + TPM 100mg (optimal)
        (2000, 200),   # ACZ 2g + TPM 200mg (high-dose)
        (3000, 200),   # ACZ 3g + TPM 200mg (intensive)
    ]
    combo_results = [calculate_combination_response(acz, tpm) for acz, tpm in combinations]
    
    return (pd.DataFrame(acz_results), 
            pd.DataFrame(tpm_results), 
            pd.DataFrame(combo_results))


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate and save dose-response curves."""
    
    print("="*80)
    print("GENERATING DOSE-RESPONSE CURVES")
    print("="*80)
    
    # Generate curves
    df_acz, df_tpm, df_combo = generate_dose_response_curves()
    
    # Display results
    print("\n[1/3] Acetazolamide Dose-Response:")
    print(df_acz.to_string(index=False))
    
    print("\n[2/3] Topiramate Dose-Response:")
    print(df_tpm.to_string(index=False))
    
    print("\n[3/3] Combination Therapy:")
    print(df_combo.to_string(index=False))
    
    # Save results
    output_dir = '../../results/dose_response/'
    df_acz.to_csv(f'{output_dir}acz_dose_response.csv', index=False)
    df_tpm.to_csv(f'{output_dir}tpm_dose_response.csv', index=False)
    df_combo.to_csv(f'{output_dir}combination_dose_response.csv', index=False)
    
    print("\n✓ Dose-response curves saved to results/dose_response/")


if __name__ == '__main__':
    main()
