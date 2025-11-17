"""
Clinical Outcome Mapping
Links CSF/ICP dynamics to clinical endpoints
"""

import numpy as np
from scipy.stats import norm

def predict_pmd_change(icp_change, weight_loss_pct, baseline_pmd, months=6):
    """
    Predict change in perimetric mean deviation
    
    Parameters:
    -----------
    icp_change : float
        Change in ICP (mmHg), negative = reduction
    weight_loss_pct : float
        % weight loss (positive = loss)
    baseline_pmd : float
        Baseline PMD (dB), negative values
    months : int
        Follow-up duration
        
    Returns:
    --------
    float : Expected PMD change (dB), positive = improvement
    """
    # Base improvement from ICP reduction
    icp_effect = 0.15 * abs(icp_change)  # More reduction = more improvement
    
    # Weight loss effect
    wl_effect = 0.08 * weight_loss_pct
    
    # Baseline severity interaction (ceiling effect)
    baseline_factor = 1.0 + 0.05 * (baseline_pmd / (-5.0))  # Normalize to typical baseline
    
    # Time scaling (diminishing returns)
    time_factor = min(1.0, months / 6)
    
    expected_change = (icp_effect + wl_effect) * baseline_factor * time_factor
    
    # Add realistic noise
    noise_sd = 0.8
    
    return expected_change, noise_sd


def predict_papilledema_change(icp_change, baseline_grade):
    """
    Predict change in Frisen papilledema grade
    
    Parameters:
    -----------
    icp_change : float
        Change in ICP (mmHg)
    baseline_grade : int
        Baseline Frisen grade (0-5)
        
    Returns:
    --------
    dict : Probabilities of grade changes
    """
    # Logistic model
    logit_score = -0.5 + 0.25 * abs(icp_change)
    
    # Ceiling effect for baseline grade
    if baseline_grade <= 1:
        logit_score *= 0.5  # Less room for improvement
    
    # Convert to probability of improvement (≥1 grade reduction)
    prob_improve = 1 / (1 + np.exp(-logit_score))
    
    # Grade distribution
    probs = {
        'improvement_2plus': prob_improve * 0.3,
        'improvement_1': prob_improve * 0.7,
        'no_change': 1 - prob_improve,
        'worsening': 0.05
    }
    
    return probs


def predict_headache_change(icp_change):
    """
    Predict change in HIT-6 headache score
    
    Parameters:
    -----------
    icp_change : float
        Change in ICP (mmHg)
        
    Returns:
    --------
    float : Expected HIT-6 change (negative = improvement)
    """
    # Linear relationship
    hit6_change = -1.2 * abs(icp_change) - 2.0
    
    noise_sd = 5.0
    
    return hit6_change, noise_sd


def predict_surgery_risk(icp, pmd, papilledema_grade, months=6):
    """
    Predict probability of requiring surgery
    
    Parameters:
    -----------
    icp : float
        Current ICP (mmHg)
    pmd : float
        Current PMD (dB)
    papilledema_grade : int
        Current Frisen grade
    months : int
        Time horizon
        
    Returns:
    --------
    float : Probability of surgery
    """
    # Logistic model
    logit_score = -6.0 + 0.15*icp - 0.20*pmd + 0.40*papilledema_grade
    
    # Time scaling
    time_factor = months / 6
    logit_score *= time_factor
    
    prob_surgery = 1 / (1 + np.exp(-logit_score))
    
    return prob_surgery


def simulate_clinical_trajectory(icp_trajectory, baseline_clinical, treatment_info):
    """
    Simulate full clinical trajectory given ICP time series
    
    Parameters:
    -----------
    icp_trajectory : array
        ICP values over time (mmHg)
    baseline_clinical : dict
        {'pmd': -3.5, 'papilledema_grade': 2, 'hit6': 65}
    treatment_info : dict
        {'weight_loss_pct': 5.0, 'duration_months': 6}
        
    Returns:
    --------
    dict : Predicted outcomes at final timepoint
    """
    icp_change = icp_trajectory[-1] - icp_trajectory[0]
    weight_loss = treatment_info.get('weight_loss_pct', 0)
    duration = treatment_info.get('duration_months', 6)
    
    # PMD
    pmd_change, _ = predict_pmd_change(
        icp_change, 
        weight_loss, 
        baseline_clinical['pmd'],
        duration
    )
    final_pmd = baseline_clinical['pmd'] + pmd_change
    
    # Papilledema
    papil_probs = predict_papilledema_change(
        icp_change,
        baseline_clinical['papilledema_grade']
    )
    # Expected grade change
    expected_grade_change = (
        -2 * papil_probs['improvement_2plus'] +
        -1 * papil_probs['improvement_1'] +
        0 * papil_probs['no_change'] +
        1 * papil_probs['worsening']
    )
    final_grade = max(0, baseline_clinical['papilledema_grade'] + expected_grade_change)
    
    # Headache
    hit6_change, _ = predict_headache_change(icp_change)
    final_hit6 = baseline_clinical['hit6'] + hit6_change
    
    # Surgery risk
    surgery_prob = predict_surgery_risk(
        icp_trajectory[-1],
        final_pmd,
        final_grade,
        duration
    )
    
    return {
        'final_pmd': final_pmd,
        'pmd_change': pmd_change,
        'final_papilledema_grade': final_grade,
        'papilledema_grade_change': expected_grade_change,
        'final_hit6': final_hit6,
        'hit6_change': hit6_change,
        'surgery_probability': surgery_prob,
        'final_icp': icp_trajectory[-1],
        'icp_change': icp_change
    }
