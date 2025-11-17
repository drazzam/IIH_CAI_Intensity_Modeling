"""
Endocrine-Metabolic Layer for CSF/ICP Model
Maps hormonal/metabolic state to transporter activity multipliers
"""

import numpy as np

def map_endocrine_to_transporters(endocrine_state, baseline_params=None):
    """
    Map endocrine/metabolic state to transporter activity multipliers
    
    Parameters:
    -----------
    endocrine_state : dict
        {
            'testosterone_nmol': serum testosterone (nmol/L),
            'testosterone_csf_nmol': CSF testosterone (optional),
            'androstenedione_nmol': serum A4 (nmol/L),
            'hsd11b1_activity': 11β-HSD1 activity (0-1 scale, 1=normal),
            'cortisol_nmol': serum cortisol (nmol/L),
            'bmi': body mass index,
            'trunk_fat_pct': trunk/android fat percentage,
            'leptin': leptin levels (ng/mL),
            'weight_loss_pct': % weight loss from baseline (negative = loss),
            'glp1ra_active': bool, GLP-1RA treatment,
            'glp1ra_dose_category': 'low'/'medium'/'high',
            'azd4017_active': bool, 11β-HSD1 inhibitor,
            'azd4017_dose_mg': dose in mg
        }
    
    baseline_params : dict (optional)
        Reference values for "normal" state
    
    Returns:
    --------
    dict of transporter activity multipliers:
        {
            'nka_activity': multiplier for NKA (1.0 = baseline),
            'nkcc1_activity': multiplier for NKCC1,
            'aqp1_activity': multiplier for AQP1,
            'ca_activity': multiplier for CA,
            'cp_fraction': multiplier for CP fraction of total CSF production
        }
    """
    
    # Set defaults
    if baseline_params is None:
        baseline_params = {
            'testosterone_nmol': 1.0,  # Normal female range
            'bmi': 25,
            'hsd11b1_activity': 1.0
        }
    
    # Initialize multipliers at baseline
    multipliers = {
        'nka_activity': 1.0,
        'nkcc1_activity': 1.0,
        'aqp1_activity': 1.0,
        'ca_activity': 1.0,
        'cp_fraction': 1.0
    }
    
    # ========================================================================
    # ANDROGEN EFFECTS
    # ========================================================================
    
    testosterone = endocrine_state.get('testosterone_nmol', baseline_params['testosterone_nmol'])
    baseline_t = baseline_params['testosterone_nmol']
    delta_t = testosterone - baseline_t
    
    # Testosterone → NKA (O'Reilly 2019)
    t_nka_effect = 1.0 + np.clip(0.35 * delta_t, -0.5, 1.0)  # Max 2x, min 0.5x
    multipliers['nka_activity'] *= t_nka_effect
    
    # Testosterone → CA (O'Reilly 2019)
    t_ca_effect = 1.0 + np.clip(0.25 * delta_t, -0.5, 0.8)  # Max 1.8x
    multipliers['ca_activity'] *= t_ca_effect
    
    # Testosterone → NKCC1 (inferred)
    t_nkcc1_effect = 1.0 + np.clip(0.20 * delta_t, -0.3, 0.5)
    multipliers['nkcc1_activity'] *= t_nkcc1_effect
    
    # ========================================================================
    # 11β-HSD1 / CORTISOL EFFECTS
    # ========================================================================
    
    hsd11b1_activity = endocrine_state.get('hsd11b1_activity', 1.0)
    
    # 11β-HSD1 amplifies cortisol → NKA
    # Higher activity = more cortisol conversion = more NKA stimulation
    hsd_nka_effect = 1.0 + 0.30 * (hsd11b1_activity - 1.0)
    multipliers['nka_activity'] *= hsd_nka_effect
    
    # AZD4017 inhibition
    if endocrine_state.get('azd4017_active', False):
        dose_mg = endocrine_state.get('azd4017_dose_mg', 400)
        inhibition_fraction = min(1.0, dose_mg / 400)  # 400mg = full dose
        # Reverse the 11β-HSD1 amplification
        multipliers['nka_activity'] /= (1.0 + 0.30 * inhibition_fraction)
    
    # ========================================================================
    # GLP-1RA EFFECTS
    # ========================================================================
    
    if endocrine_state.get('glp1ra_active', False):
        dose_cat = endocrine_state.get('glp1ra_dose_category', 'medium')
        
        dose_factors = {'low': 0.5, 'medium': 1.0, 'high': 1.5}
        dose_mult = dose_factors.get(dose_cat, 1.0)
        
        # GLP-1RA inhibits NKA (Botfield 2017)
        glp1_nka_inhibition = 0.25 * dose_mult
        multipliers['nka_activity'] *= (1.0 - glp1_nka_inhibition)
        
        # May also reduce 11β-HSD1 indirectly
        multipliers['nka_activity'] /= (1.0 + 0.10 * dose_mult)
    
    # ========================================================================
    # OBESITY / ADIPOSITY EFFECTS
    # ========================================================================
    
    bmi = endocrine_state.get('bmi', baseline_params['bmi'])
    trunk_fat = endocrine_state.get('trunk_fat_pct', None)
    
    # Obesity amplifies androgen dysregulation and 11β-HSD1
    if bmi > 30:
        obesity_factor = 1.0 + 0.05 * (bmi - 30)
        # This amplifies the testosterone and 11β-HSD1 effects already applied
        # Implemented as additional CP fraction increase (more CP CSF production)
        multipliers['cp_fraction'] *= min(1.3, obesity_factor)
    
    if trunk_fat is not None and trunk_fat > 40:
        trunk_factor = 1.0 + 0.03 * (trunk_fat - 40)
        multipliers['cp_fraction'] *= min(1.2, trunk_factor)
    
    # ========================================================================
    # WEIGHT LOSS EFFECTS
    # ========================================================================
    
    weight_loss_pct = endocrine_state.get('weight_loss_pct', 0)
    
    if weight_loss_pct < 0:  # Negative = weight loss
        # Weight loss reduces androgen excess and 11β-HSD1 activity
        loss_magnitude = abs(weight_loss_pct)
        
        # Reverse some of the obesity-related amplification
        # Assume 10% weight loss reverses ~50% of obesity effect
        reversal_fraction = min(1.0, loss_magnitude / 20)  # Full reversal at 20% loss
        
        # Reduce transporter activities toward baseline
        for key in ['nka_activity', 'ca_activity', 'nkcc1_activity']:
            if multipliers[key] > 1.0:
                excess = multipliers[key] - 1.0
                multipliers[key] = 1.0 + excess * (1.0 - 0.5 * reversal_fraction)
        
        # Reduce CP fraction toward baseline
        if multipliers['cp_fraction'] > 1.0:
            excess = multipliers['cp_fraction'] - 1.0
            multipliers['cp_fraction'] = 1.0 + excess * (1.0 - 0.6 * reversal_fraction)
    
    return multipliers


def create_iih_endocrine_state(testosterone=1.7, bmi=35, hsd11b1=1.3):
    """
    Create typical IIH patient endocrine state (from O'Reilly 2019)
    
    Default values from O'Reilly cohort:
    - Testosterone: 1.7 nmol/L (vs 1.0 in controls)
    - BMI: ~35
    - 11β-HSD1 activity: elevated ~1.3x normal
    """
    return {
        'testosterone_nmol': testosterone,
        'bmi': bmi,
        'hsd11b1_activity': hsd11b1,
        'glp1ra_active': False,
        'azd4017_active': False,
        'weight_loss_pct': 0
    }


def apply_treatment_to_endocrine_state(state, treatment):
    """
    Modify endocrine state based on treatment
    
    Parameters:
    -----------
    state : dict
        Current endocrine state
    treatment : dict
        {
            'type': 'glp1ra'/'azd4017'/'weight_loss'/'bariatric',
            'dose': dose/intensity parameter,
            'duration_weeks': treatment duration
        }
    
    Returns:
    --------
    Updated state
    """
    new_state = state.copy()
    
    if treatment['type'] == 'glp1ra':
        new_state['glp1ra_active'] = True
        new_state['glp1ra_dose_category'] = treatment.get('dose', 'medium')
        # GLP-1RA also induces weight loss over time
        duration = treatment.get('duration_weeks', 12)
        expected_loss = min(10, 0.5 * duration)  # ~0.5% per week, max 10%
        new_state['weight_loss_pct'] = new_state.get('weight_loss_pct', 0) - expected_loss
        
    elif treatment['type'] == 'azd4017':
        new_state['azd4017_active'] = True
        new_state['azd4017_dose_mg'] = treatment.get('dose', 400)
        
    elif treatment['type'] == 'weight_loss':
        target_loss = treatment.get('target_pct', 10)
        duration = treatment.get('duration_weeks', 24)
        achieved_loss = min(target_loss, target_loss * (duration / 24))
        new_state['weight_loss_pct'] = new_state.get('weight_loss_pct', 0) - achieved_loss
        # Update BMI
        current_bmi = new_state.get('bmi', 35)
        new_state['bmi'] = current_bmi * (1.0 - achieved_loss/100)
        
    elif treatment['type'] == 'bariatric':
        # Rapid, sustained weight loss
        duration = treatment.get('duration_weeks', 52)
        if duration < 12:
            loss = 10  # Early phase
        elif duration < 26:
            loss = 20  # Intermediate
        else:
            loss = 25  # Sustained
        new_state['weight_loss_pct'] = -loss
        current_bmi = new_state.get('bmi', 35)
        new_state['bmi'] = current_bmi * (1.0 - loss/100)
    
    return new_state
