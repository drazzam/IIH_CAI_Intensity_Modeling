"""
CSF/ICP Mechanistic Model
Compartmental ODE model with transporter-level parameterization
"""

import numpy as np
from scipy.integrate import solve_ivp

class CSFModel:
    """
    Multi-compartment CSF/ICP dynamics model
    
    Compartments:
    - Arterial blood
    - Venous blood (with sinus)
    - Intracranial CSF
    - (Optional) Spinal CSF
    
    Key processes:
    - CSF production (choroid plexus, transporter-mediated)
    - CSF outflow (resistance-based)
    - Compliance/elastance
    - Venous pressure coupling
    """
    
    def __init__(self, params):
        """
        Parameters:
        -----------
        params : dict
            Model parameters including:
            - csf_production_baseline: mL/min
            - rcsf: mmHg/(mL/min) outflow resistance
            - compliance: mL/mmHg
            - venous_pressure: mmHg
            - cp_fraction: fraction of CSF from CP (vs extrachoroidal)
            - nka_activity: multiplier for NKA contribution (default 1.0)
            - nkcc1_activity: multiplier for NKCC1 (default 1.0)
            - aqp1_activity: multiplier for AQP1 (default 1.0)
            - ca_activity: multiplier for CA (default 1.0)
            - nka_fraction: baseline NKA contribution to CP secretion
            - nkcc1_fraction: baseline NKCC1 contribution
            - aqp1_fraction: baseline AQP1 contribution
            - ca_fraction: baseline CA contribution
        """
        self.params = params
        
        # Set defaults
        self.params.setdefault('nka_activity', 1.0)
        self.params.setdefault('nkcc1_activity', 1.0)
        self.params.setdefault('aqp1_activity', 1.0)
        self.params.setdefault('ca_activity', 1.0)
        
    def csf_production_rate(self, t):
        """
        Calculate CSF production rate at time t
        
        Production = Baseline * CP_fraction * Transporter_effect + Extrachoroidal
        
        Transporter effect = weighted sum of individual transporter activities
        """
        baseline = self.params['csf_production_baseline']
        cp_frac = self.params['cp_fraction']
        
        # Transporter contributions (fractions should sum to ~1)
        nka_contrib = self.params['nka_fraction'] * self.params['nka_activity']
        nkcc1_contrib = self.params['nkcc1_fraction'] * self.params['nkcc1_activity']
        aqp1_contrib = self.params['aqp1_fraction'] * self.params['aqp1_activity']
        ca_contrib = self.params['ca_fraction'] * self.params['ca_activity']
        
        # Total transporter effect (multiplicative)
        transporter_effect = nka_contrib + nkcc1_contrib + aqp1_contrib + ca_contrib
        
        # CP production + extrachoroidal
        cp_production = baseline * cp_frac * transporter_effect
        extrachoroidal_production = baseline * (1 - cp_frac)
        
        total_production = cp_production + extrachoroidal_production
        
        return total_production
    
    def csf_outflow_rate(self, icp):
        """
        CSF outflow via resistance
        
        Q_out = (ICP - P_venous) / R_csf
        """
        p_venous = self.params['venous_pressure']
        rcsf = self.params['rcsf']
        
        pressure_gradient = max(0, icp - p_venous)  # No backflow
        q_out = pressure_gradient / rcsf
        
        return q_out
    
    def icp_from_volume(self, csf_volume):
        """
        ICP-volume relationship via compliance
        
        Simple model: ICP = P0 + (V - V0) / C
        where C is compliance
        """
        baseline_volume = self.params.get('baseline_csf_volume', 150)  # mL
        baseline_icp = self.params.get('baseline_icp', 12)  # mmHg
        compliance = self.params['compliance']
        
        icp = baseline_icp + (csf_volume - baseline_volume) / compliance
        
        return icp
    
    def derivatives(self, t, state):
        """
        ODE system: dV/dt = Q_in - Q_out
        
        State variables:
        [0] csf_volume (mL)
        """
        csf_volume = state[0]
        
        # Calculate current ICP
        icp = self.icp_from_volume(csf_volume)
        
        # Production and outflow
        q_in = self.csf_production_rate(t)
        q_out = self.csf_outflow_rate(icp)
        
        # Volume change
        dV_dt = q_in - q_out
        
        return [dV_dt]
    
    def simulate(self, t_span, initial_volume=None, n_points=100):
        """
        Simulate CSF dynamics
        
        Parameters:
        -----------
        t_span : tuple
            (t_start, t_end) in minutes
        initial_volume : float
            Initial CSF volume (mL), default is baseline
        n_points : int
            Number of time points
            
        Returns:
        --------
        dict with keys: 't', 'csf_volume', 'icp', 'q_in', 'q_out'
        """
        if initial_volume is None:
            initial_volume = self.params.get('baseline_csf_volume', 150)
        
        # Solve ODE
        sol = solve_ivp(
            self.derivatives,
            t_span,
            [initial_volume],
            method='LSODA',
            t_eval=np.linspace(t_span[0], t_span[1], n_points)
        )
        
        # Extract results
        t = sol.t
        csf_volume = sol.y[0]
        
        # Calculate ICP, flows at each time point
        icp = np.array([self.icp_from_volume(v) for v in csf_volume])
        q_in = np.array([self.csf_production_rate(ti) for ti in t])
        q_out = np.array([self.csf_outflow_rate(p) for p in icp])
        
        return {
            't': t,
            'csf_volume': csf_volume,
            'icp': icp,
            'q_in': q_in,
            'q_out': q_out
        }


def create_baseline_model(priors):
    """
    Create baseline model with priors from literature
    """
    params = {
        'csf_production_baseline': priors['csf_production_rate']['mean'],
        'rcsf': priors['rcsf_outflow']['mean'],
        'compliance': priors['compliance']['mean'],
        'venous_pressure': priors['venous_pressure']['mean'],
        'baseline_icp': priors['mean_icp']['mean'],
        'baseline_csf_volume': 150.0,  # mL (standard)
        'cp_fraction': priors['cp_fraction']['mean'],
        'nka_fraction': priors['nka_fraction']['mean'],
        'nkcc1_fraction': priors['nkcc1_fraction']['mean'],
        'aqp1_fraction': priors['aqp1_fraction']['mean'],
        'ca_fraction': priors['ca_fraction']['mean']
    }
    
    return CSFModel(params)


def apply_treatment(model, treatment_name, intensity=1.0):
    """
    Apply treatment by modifying transporter activities
    
    Parameters:
    -----------
    model : CSFModel
    treatment_name : str
        'acetazolamide', 'topiramate', 'bumetanide', 'glp1ra', etc.
    intensity : float
        Treatment intensity (0-1 scale, or dose-dependent)
    
    Returns:
    --------
    Modified model parameters
    """
    params = model.params.copy()
    
    # Treatment effects on transporters (from literature)
    if treatment_name.lower() in ['acetazolamide', 'acz']:
        # ACZ inhibits CA, modest effect on NKA
        params['ca_activity'] = 1.0 - 0.6 * intensity  # 60% inhibition at full dose
        params['nka_activity'] = 1.0 - 0.15 * intensity  # 15% inhibition
        
    elif treatment_name.lower() in ['topiramate', 'tpm']:
        # TPM inhibits CA, different mechanism than ACZ
        params['ca_activity'] = 1.0 - 0.5 * intensity
        params['nka_activity'] = 1.0 - 0.10 * intensity
        
    elif treatment_name.lower() in ['bumetanide', 'bum']:
        # Bumetanide inhibits NKCC1
        params['nkcc1_activity'] = 1.0 - 0.7 * intensity
        
    elif treatment_name.lower() in ['glp1ra', 'glp-1']:
        # GLP-1RA inhibits NKA
        params['nka_activity'] = 1.0 - 0.25 * intensity
    
    return CSFModel(params)
