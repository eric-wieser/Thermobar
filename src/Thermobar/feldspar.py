import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import inspect
import warnings as w
import numbers
import pandas as pd
from Thermobar.core import *


## Equations: Plag-Liquid thermometers
def T_Put2008_eq23(P, *, An_Plag, SiO2_Liq_cat_frac,
                   Al2O3_Liq_cat_frac, CaO_Liq_cat_frac, Ab_Plag, H2O_Liq):
    '''
    Plagioclase-Liquid thermometer of Putirka (2008) eq. 23
    SEE=+-43C
    '''
    return ((10**4 / (6.12 + 0.257 * np.log(An_Plag / (SiO2_Liq_cat_frac**2 * Al2O3_Liq_cat_frac**2 * CaO_Liq_cat_frac))
                      - 3.166 * CaO_Liq_cat_frac - 3.137 *
                      (Al2O3_Liq_cat_frac / (Al2O3_Liq_cat_frac + SiO2_Liq_cat_frac))
                      + 1.216 * Ab_Plag**2 - 2.475 * 10**-2 * (P / 10) * 10 + 0.2166 * H2O_Liq)))




def T_Put2008_eq24a(P, *, An_Plag, SiO2_Liq_cat_frac, Al2O3_Liq_cat_frac,
                    CaO_Liq_cat_frac, K2O_Liq_cat_frac, Ab_Plag, H2O_Liq):
    '''
    Plagioclase-Liquid thermometer of Putirka (2008) eq. 24a
    Global regression, improves equation 23 SEE by  6C
    SEE=+-36C
    '''
    return ((10**4 / (6.4706 + 0.3128 * (np.log(An_Plag / (SiO2_Liq_cat_frac**2 * Al2O3_Liq_cat_frac**2 * CaO_Liq_cat_frac)))
                      - 8.103 * SiO2_Liq_cat_frac + 4.872 *
                      K2O_Liq_cat_frac + 8.661 * SiO2_Liq_cat_frac**2
                      + 1.5346 * Ab_Plag**2 - 3.341 * 10**-2 * (P / 10) * 10 + 0.18047 * H2O_Liq)))


## Equation: Plag-Liquid barometer

def P_Put2008_eq25(T, *, Ab_Plag, Al2O3_Liq_cat_frac, CaO_Liq_cat_frac,
                   Na2O_Liq_cat_frac, SiO2_Liq_cat_frac, An_Plag, K2O_Liq_cat_frac):
    '''
    Plagioclase-Liquid barometer of Putirka (2008) eq. 26.
    SEE=+-2.2 kbar *But in spreadsheet, Putirka warns plag is not a good barometer*
    '''
    return (-42.2 + (4.94 * (10**-2) * T) + (1.16 * (10**-2) * T) *
    (np.log((Ab_Plag * Al2O3_Liq_cat_frac * CaO_Liq_cat_frac) / (Na2O_Liq_cat_frac * SiO2_Liq_cat_frac * An_Plag)))
            - 19.6 * np.log(Ab_Plag) - 382.3 * SiO2_Liq_cat_frac**2 +
            514.2 * SiO2_Liq_cat_frac**3 - 139.8 * CaO_Liq_cat_frac
            + 287.2 * Na2O_Liq_cat_frac + 163.9 * K2O_Liq_cat_frac)

## Equations - Kspar-Liquid thermometry

def T_Put2008_eq24b(P, *, Ab_Kspar, Al2O3_Liq_cat_frac, Na2O_Liq_cat_frac,
                  K2O_Liq_cat_frac, SiO2_Liq_cat_frac, CaO_Liq_cat_frac):
    '''
    Alkali Felspar-Liquid thermometer of Putirka (2008) eq. 24b.
    SEE=+-23 C (Calibration data)
    SEE=+-25 C (All data)

    '''
    return (10**4 / (17.3 - 1.03 * np.log(Ab_Kspar / (Na2O_Liq_cat_frac * Al2O3_Liq_cat_frac * SiO2_Liq_cat_frac**3))
    - 200 * CaO_Liq_cat_frac - 2.42 * Na2O_Liq_cat_frac -29.8 * K2O_Liq_cat_frac + 13500 * (CaO_Liq_cat_frac - 0.0037)**2
    - 550 * (K2O_Liq_cat_frac - 0.056) * (Na2O_Liq_cat_frac - 0.089) - 0.078 * (P / 10) / 10))





## Function: Fspar-Liquid temperature (works for alkali and plag feldspars)

plag_liq_T_funcs = {T_Put2008_eq23, T_Put2008_eq24a}
plag_liq_T_funcs_by_name = {p.__name__: p for p in plag_liq_T_funcs}

Kspar_Liq_T_funcs = {T_Put2008_eq24b}
Kspar_Liq_T_funcs_by_name = {p.__name__: p for p in Kspar_Liq_T_funcs}


def calculate_fspar_liq_temp(*, plag_comps=None, kspar_comps=None,
    liq_comps=None, equationT=None, P=None, H2O_Liq=None, eq_tests=False):
    '''
    Liquid-Feldspar thermometery (same function for Plag and Kspar),
    returns temperature in Kelvin.

    Parameters
    -------

    liq_comps: DataFrame
        liquid compositions with column headings SiO2_Liq, MgO_Liq etc.

    kspar_comps or plag_comps (DataFrame)
        Specify kspar_comps=... for Kspar-Liquid thermometry (with column headings SiO2_Kspar, MgO_Kspar) etc
        Specify plag_comps=... for Plag-Liquid thermometry (with column headings SiO2_Plag, MgO_Plag) etc

    EquationT: str
        Equation choices:
            |   T_Put2008_eq24b (Kspar-Liq, P-dependent, H2O-independent

            |   T_Put2008_eq23 (Plag-Liq, P-dependent, H2O-dependent)
            |   T_Put2008_eq24a (Plag-Liq, P-dependent, H2O-dependent)

    P: float, int, series, str  ("Solve")
        Pressure in kbar
        Only needed for P-sensitive thermometers.
        If enter P="Solve", returns a partial function
        Else, enter an integer, float, or panda series

    H2O_Liq: optional.
        If None, uses H2O_Liq column from input.
        If int, float, series, uses this instead of H2O_Liq Column

    Returns
    -------
    Panda series
        Temperatures in Kelvin

    '''
    liq_comps_c = liq_comps.copy()
    if H2O_Liq is not None:
        liq_comps_c['H2O_Liq'] = H2O_Liq


    if plag_comps is not None:
        try:
            func = plag_liq_T_funcs_by_name[equationT]
        except KeyError:
            raise ValueError(f'{equationT} is not a valid equation for Plag-Liquid') from None
        sig=inspect.signature(func)

        cat_plags = calculate_cat_fractions_plagioclase(plag_comps=plag_comps)
        cat_liqs = calculate_anhydrous_cat_fractions_liquid(liq_comps_c)
        combo_fspar_Liq = pd.concat([cat_plags, cat_liqs], axis=1)

        Kd_Ab_An = (combo_fspar_Liq['Ab_Plag'] * combo_fspar_Liq['Al2O3_Liq_cat_frac'] * combo_fspar_Liq['CaO_Liq_cat_frac'] /
                    (combo_fspar_Liq['An_Plag'] * combo_fspar_Liq['Na2O_Liq_cat_frac'] * combo_fspar_Liq['SiO2_Liq_cat_frac']))
        combo_fspar_Liq['Kd_Ab_An'] = Kd_Ab_An

        if np.min(combo_fspar_Liq['An_Plag'] < 0.05):
            w.warn('Some inputted feldspars have An<0.05, but you have selected a plagioclase-liquid thermometer'
            '. If these are actually alkali felspars, please use T_P2008_eq24b or T_P2008_24c instead', stacklevel=2)

    if kspar_comps is not None:
        try:
            func = Kspar_Liq_T_funcs_by_name[equationT]
        except KeyError:
            raise ValueError(f'{equationT} is not a valid equation for Kspar-Liquid') from None
        sig=inspect.signature(func)

        cat_kspars = calculate_cat_fractions_kspar(kspar_comps=kspar_comps)
        cat_liqs = calculate_anhydrous_cat_fractions_liquid(liq_comps_c)
        combo_fspar_Liq = pd.concat([cat_kspars, cat_liqs], axis=1)

        Kd_Ab_An = (combo_fspar_Liq['Ab_Kspar'] * combo_fspar_Liq['Al2O3_Liq_cat_frac'] * combo_fspar_Liq['CaO_Liq_cat_frac'] /
                    (combo_fspar_Liq['An_Kspar'] * combo_fspar_Liq['Na2O_Liq_cat_frac'] * combo_fspar_Liq['SiO2_Liq_cat_frac']))
        combo_fspar_Liq['Kd_Ab_An'] = Kd_Ab_An

        if np.min(combo_fspar_Liq['An_Kspar'] > 0.05):
            w.warn('Some inputted feldspars have An>0.05, but you have selected a Kspar-liquid thermometer'
            '. If these are actually Plagioclase feldspars, please use T_P2008_eq23 or _eq24a instead', stacklevel=2)

    if sig.parameters['P'].default is not None:
        if P is None:
            raise ValueError(f'{equationT} requires you to enter P, or specify P="Solve"')
    else:
        if P is not None:
            print('Youve selected a P-independent function')



    kwargs = {name: combo_fspar_Liq[name] for name, p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}

    if isinstance(P, str) or P is None:
        if P == "Solve":
            T_K = partial(func, **kwargs)
        if P is None:
            T_K=func(**kwargs)

    else:
        T_K=func(P, **kwargs)

    if eq_tests is False:
        return T_K
    if eq_tests is True:
        if kspar_comps is not None:
            print('Sorry, no equilibrium tests implemented for Kspar-Liquid')
            return T_K
        if plag_comps is not None:
            eq_tests=calculate_plag_liq_eq_tests(liq_comps=liq_comps,
            plag_comps=plag_comps, P=P, T=T_K)
            eq_tests.insert(1, "T_K_calc", T_K)
            return eq_tests


## Function: Fspar-Liq pressure
plag_liq_P_funcs = {P_Put2008_eq25}
plag_liq_P_funcs_by_name = {p.__name__: p for p in plag_liq_P_funcs}

Kspar_Liq_P_funcs = {}
Kspar_Liq_P_funcs_by_name = {p.__name__: p for p in Kspar_Liq_P_funcs}

def calculate_fspar_liq_press(*, plag_comps=None, kspar_comps=None, liq_comps=None, equationP=None,
                              T=None, H2O_Liq=None, eq_tests=False):

    '''
    Liquid-Feldspar barometer (at the moment, only options for Plag).
    Note, Putirka warns that plagioclase is not a reliable barometer!
    For a user-selected equation returns a pressure in kbar.

    Parameters
    -------

    liq_comps: DataFrame
        liquid compositions with column headings SiO2_Liq, MgO_Liq etc.

    plag_comps (DataFrame)
        Specify plag_comps=... (with column headings SiO2_Plag, MgO_Plag) etc

    EquationP: str
        Equation choices:
            |   P_Put2008_eq25 (Kspar-Liq, P-dependent, H2O-independent

    T: float, int, series, str  ("Solve")
        Temperature in Kelvin
        Only needed for T-sensitive barometers.
        If enter T="Solve", returns a partial function
        Else, enter an integer, float, or panda series

    H2O_Liq: optional.
        If None, uses H2O_Liq column from input.
        If int, float, series, uses this instead of H2O_Liq Column

    Returns
    -------
    Panda series
        Temperature in Kelvin

    '''
    if kspar_comps is not None:
        raise TypeError('Sorry, this tool doesnt contain any alkali-fspar-liquid barometers,'
        ' this option is here as a place holder incase a great one comes along!')

    try:
        func = plag_liq_P_funcs_by_name[equationP]
    except KeyError:
        raise ValueError(f'{equationP} is not a valid equation') from None
    sig=inspect.signature(func)



    liq_comps_c = liq_comps.copy()
    if H2O_Liq is not None:
        liq_comps_c['H2O_Liq'] = H2O_Liq


    cat_plags = calculate_cat_fractions_plagioclase(plag_comps=plag_comps)
    cat_liqs = calculate_anhydrous_cat_fractions_liquid(liq_comps)
    combo_plag_liq = pd.concat([cat_plags, cat_liqs], axis=1)

    Kd_Ab_An = (combo_plag_liq['Ab_Plag'] * combo_plag_liq['Al2O3_Liq_cat_frac'] * combo_plag_liq['CaO_Liq_cat_frac'] /
                (combo_plag_liq['An_Plag'] * combo_plag_liq['Na2O_Liq_cat_frac'] * combo_plag_liq['SiO2_Liq_cat_frac']))

    combo_plag_liq['Kd_Ab_An'] = Kd_Ab_An


    kwargs = {name: combo_plag_liq[name] for name, p in sig.parameters.items() \
    if p.kind == inspect.Parameter.KEYWORD_ONLY}

    if sig.parameters['T'].default is not None:
        if T is None:
            raise ValueError(f'{equationP} requires you to enter T')
    else:
        if T is not None:
            print('Youve selected a T-independent function')


    kwargs = {name: combo_plag_liq[name] for name, p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
    if isinstance(T, str) or T is None:
        if T == "Solve":
            P_kbar = partial(func, **kwargs)
        if T is None:
            P_kbar=func(**kwargs)

    else:
        P_kbar=func(T, **kwargs)

    if eq_tests is False:
        return P_kbar
    if eq_tests is True:

        eq_tests=calculate_plag_liq_eq_tests(liq_comps=liq_comps,
        plag_comps=plag_comps, P=P_kbar, T=T)
        eq_tests.insert(1, "P_kbar_calc", P_kbar)
        return eq_tests
    return P_kbar

## Function for iterating pressure and temperature - (probably not recomended)

def calculate_fspar_liq_press_temp(*, liq_comps=None, plag_comps=None, kspar_comps=None,
                                meltmatch=None, equationP=None, equationT=None, iterations=30, T_K_guess=1300,
                                H2O_Liq=None):
    '''
    Solves simultaneous equations for temperature and pressure using
    plagioclase-liquid thermometers and barometers.

   Parameters
    -------

    plag_comps: DataFrame
        Feldspar compositions with column headings SiO2_Fspar, MgO_Fspar etc.

    liq_comps: DataFrame (not required for P_Put2008_eq29c)
        Liquid compositions with column headings SiO2_Liq, MgO_Liq etc.

    Or:

    meltmatch: DataFrame
        Combined dataframe of fspar-Liquid compositions (headings SiO2_Liq, SiO2_Plag etc.).
        means a plag-liq matching algorithm could be added (not implemented currently due
        to lack of equilibrium test consensus).

    EquationP: str
        Barometer
        |  P_Put2008_eq25 (Plagioclase)

    EquationT: str
        Thermometer
        |  T_Put2008_eq23 (Plagioclase)
        |  T_Put2008_eq24a (Plagioclase)


     iterations: int. Default=30
         Number of iterations used to converge to solution.

     T_K_guess: int or float  (optional). Default = 1300K
         Initial guess of temperature.

    Returns:
    -------
    panda.dataframe: Pressure in kbar, Temperature in K + fspar+liq comps (if eq_tests=True)


    '''
    # Gives users flexibility to reduce or increase iterations
    liq_comps_c=liq_comps.copy()
    if H2O_Liq is not None:
        liq_comps_c['H2O_Liq']=H2O_Liq
    if kspar_comps is not None:
        raise Exception(
            'Sorry, we currently dont have any kspar barometers coded up, so you cant iteratively solve for Kspars')


    if meltmatch is None:
        T_func = calculate_fspar_liq_temp(
            plag_comps=plag_comps, liq_comps=liq_comps_c, equationT=equationT, P="Solve")
        P_func = calculate_fspar_liq_press(
            plag_comps=plag_comps, liq_comps=liq_comps_c, equationP=equationP,  T="Solve")
    if meltmatch is not None:
        T_func = calculate_fspar_liq_temp(
            meltmatch=meltmatch, equationT=equationT)
        P_func = calculate_fspar_liq_press(
            meltmatch=meltmatch, equationP=equationP)

 # This bit checks if temperature is already a series - e.g., equations
 # with no pressure dependence
    if isinstance(T_func, pd.Series) and isinstance(P_func, pd.Series):
        P_guess = P_func
        T_K_guess = T_func

    if isinstance(T_func, pd.Series) and isinstance(P_func, partial):
        P_guess = P_func(T_func)
        T_K_guess = T_func

    if isinstance(P_func, pd.Series) and isinstance(T_func, partial):
        T_K_guess = T_func(P_func)
        P_guess = P_func

    if isinstance(P_func, partial) and isinstance(T_func, partial):
        with w.catch_warnings():
            w.simplefilter('ignore')

        # Gives users flexibility to add a different guess temperature

            for _ in range(iterations):
                P_guess = P_func(T_K_guess)
                T_K_guess = T_func(P_guess)

    # calculates Kd Fe-Mg if eq_tests="True"

    PT_out = pd.DataFrame(data={'P_kbar_calc': P_guess, 'T_K_calc': T_K_guess})
    return PT_out

## Equations: Plag-Liquid hygrometry

def H_Put2008_eq25b(T, *, P, An_Plag, SiO2_Liq_cat_frac,
                    Al2O3_Liq_cat_frac, CaO_Liq_cat_frac, K2O_Liq_cat_frac, MgO_Liq_cat_frac):
    '''
    Plagioclase-Hygrometer of  Putirka (2008) eq. 25b
    Global calibration improving estimate of Putirka (2005) eq H
    SEE=+-1.1 wt%
    '''
    LnKAn=np.log((An_Plag)/((SiO2_Liq_cat_frac**2)*(Al2O3_Liq_cat_frac**2) * CaO_Liq_cat_frac))
    return (25.95-0.0032*(T-273.15)*LnKAn-18.9*K2O_Liq_cat_frac+14.5*MgO_Liq_cat_frac-40.3*CaO_Liq_cat_frac+5.7*An_Plag**2+0.108*(P))


def H_Put2005_eqH(T, *, An_Plag, SiO2_Liq_cat_frac, Al2O3_Liq_cat_frac, Na2O_Liq_cat_frac,
                  CaO_Liq_cat_frac, Pred_Ab_EqF, Pred_An_EqE, K2O_Liq_cat_frac, MgO_Liq_cat_frac):
    '''
    Plagioclase-Hygrometer of  Putirka (2005) eq. H
    Tends to overpredict water in global datasets
    '''

    return (24.757 - 2.26 * 10**(-3) * (T) * (np.log(An_Plag / (SiO2_Liq_cat_frac**2 * Al2O3_Liq_cat_frac**2 * CaO_Liq_cat_frac)))
            - 3.847 * Pred_Ab_EqF + 1.927 * Pred_An_EqE / (CaO_Liq_cat_frac / (CaO_Liq_cat_frac + Na2O_Liq_cat_frac)))


def H_Waters2015(T, *, liq_comps=None, plag_comps=None,
                 P, XAn=None, XAb=None):
    '''
    Plagioclase-Hygrometer of  Waters and Lange (2015)
    Update of Lange et al. (2009) model.
    SEE=+-0.35 wt%
    '''
    # 1st bit calculates mole fractions in the same way as Waters and Lange.
    # Note, to match excel, all Fe is considered as FeOT.
    mol_prop = calculate_anhydrous_mol_proportions_liquid(liq_comps=liq_comps)
    mol_prop['Al2O3_Liq_mol_prop_v2'] = mol_prop['Al2O3_Liq_mol_prop'] - \
        mol_prop['K2O_Liq_mol_prop']
    # These are set to zero, so the sum of molar proportions is the same as in
    # the Waters and Lange Matlab script
    mol_prop['Al2O3_Liq_mol_prop'] = 0
    mol_prop['P2O5_Liq_mol_prop'] = 0
    mol_prop['Cr2O3_Liq_mol_prop'] = 0
    mol_prop['MnO_Liq_mol_prop'] = 0
    # This sums the remaining non-zero columns
    mol_prop['sum'] = mol_prop.sum(axis='columns')
    Liq_anhyd_mol_frac = mol_prop.div(mol_prop['sum'], axis='rows')
    Liq_anhyd_mol_frac.drop(['sum'], axis='columns', inplace=True)
    Liq_anhyd_mol_frac.columns = [str(col).replace(
        'prop', 'frac') for col in Liq_anhyd_mol_frac.columns]

    if XAn is not None and XAb is not None:
        XAn_Plag = XAn
        XAb_Plag = XAb
    if isinstance(plag_comps, pd.DataFrame):
        feld_cat_frac = calculate_cat_fractions_plagioclase(
            plag_comps=plag_comps)
        XAn_Plag = feld_cat_frac['An_Plag']
        XAb_Plag = feld_cat_frac['Ab_Plag']

    # The other option is they just enter Xan and Xab: Then we use the
    # existing functions to calculate plag cat fractions, which are then used
    # to calculate An and Ab.

    # Returns warning

    Al2O3_Liq_mol_frac_v2 = Liq_anhyd_mol_frac['Al2O3_Liq_mol_frac_v2']
    FeOt_Liq_mol_frac = Liq_anhyd_mol_frac['FeOt_Liq_mol_frac']
    Na2O_Liq_mol_frac = Liq_anhyd_mol_frac['Na2O_Liq_mol_frac']
    CaO_Liq_mol_frac = Liq_anhyd_mol_frac['CaO_Liq_mol_frac']
    SiO2_Liq_mol_frac = Liq_anhyd_mol_frac['SiO2_Liq_mol_frac']
    TiO2_Liq_mol_frac = Liq_anhyd_mol_frac['TiO2_Liq_mol_frac']
    MgO_Liq_mol_frac = Liq_anhyd_mol_frac['MgO_Liq_mol_frac']
    K2O_Liq_mol_frac = Liq_anhyd_mol_frac['K2O_Liq_mol_frac']

    AnTerm1 =( (-0.000000000010696 * ((T - 273.15)**4)) + (0.00000004945054 * ((T - 273.15)**3))
    - (0.00008207491 * ((T - 273.15)**2)) + (0.05275448 * (T - 273.15)) - 7.914622)

    AnTerm2 = ((0.000000000000219441 * ((T - 273.15)**5)) - (0.00000000106298 * ((T - 273.15)**4)) +
        (0.00000200317 * ((T - 273.15)**3)) - (0.00182716 *((T - 273.15)**2)) + (0.811309 * (T - 273.15)) - 146.951)

    AnTerm3 = ((-0.0000000000000002443527 * ((T - 273.15)**6)) + (0.0000000000013185282 * ((T - 273.15)**5))
    - (0.0000000028995878 *((T - 273.15)**4)) + (0.0000033377181 * ((T - 273.15)**3))
    - (0.0021408319 * ((T - 273.15)**2)) + (0.73454132 * (T - 273.15)) - 104.25573)

    AnTerm4 = ((0.00000000000000009642821 * ((T - 273.15)**6)) - (0.0000000000005482202 * ((T - 273.15)**5))
    + (0.000000001280331 *((T - 273.15)**4)) - (0.00000157613 * ((T - 273.15)**3))
    + (0.001084872 * ((T - 273.15)**2)) - (0.3997902 * (T - 273.15)) + 63.39784)


    AnConstant = ((-0.000000000000000006798238 * ((T - 273.15)**6)) + (0.00000000000004008407 * ((T - 273.15)**5))
    - (0.0000000000972437 *((T - 273.15)**4)) + (0.0000001242399 * ((T - 273.15)**3))
    - (0.00008824071 * ((T - 273.15)**2)) + (0.03310392 * (T - 273.15)) - 5.136283)
    #
    AbTerm1 = ((0.0000000000311852 * ((T - 273.15)**4)) - (0.000000124156 * ((T - 273.15)**3))
    + (0.000181664 * ((T - 273.15)**2)) - (0.110128 * (T - 273.15)) + 19.9603)

    AbTerm2 = ((-0.00000000006683324 * ((T - 273.15)**4)) + (0.000000264682 * ((T - 273.15)**3))
    - (0.0003813719 * ((T - 273.15)**2)) + (0.2230349 * (T - 273.15)) - 35.75847)

    AbTerm3 = ((0.000000000045560722 * ((T - 273.15)**4)) - (0.00000017904633 * ((T - 273.15)**3))
    + (0.00025203154 * ((T - 273.15)**2)) - (0.13902056 * (T - 273.15)) + 17.479424)

    AbTerm4 = ((-0.00000000001038026 * ((T - 273.15)**4)) + (0.00000004046137 * ((T - 273.15)**3))
     - (0.00005510837 * ((T - 273.15)**2)) + (0.02766904 * (T - 273.15)) - 0.9465208)

    AbConstant = ((0.00000000000000003664241 * ((T - 273.15)**6)) - (0.0000000000002106807 * ((T - 273.15)**5))
    + (0.0000000004975989 *((T - 273.15)**4)) - (0.0000006178773 * ((T - 273.15)**3))
    + (0.0004252932 * ((T - 273.15)**2)) - (0.1537074 * (T - 273.15)) + 22.74359)

    Aab = (AbTerm1 * (XAb_Plag**4)) + (AbTerm2 * (XAb_Plag**3)) + \
        (AbTerm3 * (XAb_Plag**2)) + (AbTerm4 * XAb_Plag) + AbConstant
    Aan = (AnTerm1 * (XAn_Plag**4)) + (AnTerm2 * (XAn_Plag**3)) + \
        (AnTerm3 * (XAn_Plag**2)) + (AnTerm4 * XAn_Plag) + AnConstant

    # volume of albite crystal
    VolAbxtal = 100.570 * np.exp(0.0000268 * (T - 298))
    # volume of anorthite crystal
    VolAnxtal = 100.610 * np.exp(0.0000141 * (T - 298))
    VliqAb = 112.715 + (0.00382 * (T - 1373))  # volume of liquid at 1 bar
    VliqAn = 106.300 + (0.003708 * (T - 1673))  # volume of liquid at 1 bar
    dVdPliqAb = (0.75 * (-1.843) + 0.125 * (0.685 + 0.0024 * (T - 1673)) + 0.125 * (-2.384 -
                 0.0035 * (T - 1673))) * 4 / 10000  # Change in volume of albite liquid with temperature
    # Change in volume of anorthite liquid with temperature
    dVdPliqAn = (0.50 * (-1.906) + 0.250 * (-1.665) + 0.25 *
                 (0.295 - (0.00101 * (T - 1673)))) * 4 / 10000
    # 1st part of solution to the pressure integral for albite AKA
    # deltaV(P-1)albite(J)
    deltaValbite_J = 0.1 * (VliqAb - VolAbxtal) * ((P * 1000) - 1)
    # 2nd part of the solution to the pressure integral for albite AKA
    # dV/dP**2albite(J)
    deltaValbite2_J = 0.1 * ((dVdPliqAb - 0.0000167) / 2) * ((P * 1000)**2)
    # 1st part of the solution to the pressure integral for anorthite AKA
    # deltaV(P-1)anorth(J)
    deltaVanorthite_J = 0.1 * (VliqAn - VolAnxtal) * ((P * 1000) - 1)
    # second part of the solution to the pressure integral for anorthiteAKA
    # dV/dP**2anorthtie(J)
    deltaVanorthite2_J = 0.1 * ((dVdPliqAn - 0.0000116) / 2) * ((P * 1000)**2)
    # the volume change between anorthite liquid and cyrstal at temperature
    # and pressure
    intdeltaVAn = deltaVanorthite_J + deltaVanorthite2_J
    # the volume change between albite liquid and cyrstal at temperature and
    # pressure
    intdeltaVAb = deltaValbite_J + deltaValbite2_J
    # the total change in volume between anorthite and albite crystal and
    # liquid
    intdeltaV = - deltaValbite_J - deltaValbite2_J + \
        deltaVanorthite_J + deltaVanorthite2_J

    XAbliq = ((Na2O_Liq_mol_frac**0.5) * (Al2O3_Liq_mol_frac_v2**0.5) *
              (SiO2_Liq_mol_frac**3)) * 18.963     # mol fraction of albite in the liquid
    # mol fraction of anorthite in the liquid
    XAnliq = (CaO_Liq_mol_frac * Al2O3_Liq_mol_frac_v2 *
              (SiO2_Liq_mol_frac**2)) * 64
    XAn_AnAb_liquid = XAnliq / (XAbliq + XAnliq) * 100  # liquid An #
    lnK = (np.log(Aab) - np.log(Aan)) + \
        (np.log(XAnliq) - np.log(XAbliq))  # equilibrium constant
    # overall change in volume considering the effects of temperature and
    # pressure divided by the constant R and T in kelvin
    volterm = intdeltaV / (8.3144 * T)

    intdeltaCp_An = ((-5.77) * (T - 1830)) - ((-3734 / 0.5) * (T**0.5 - 1830**0.5)) - ((317020000 / -2)
     * (T**-2 - 1830**-2))  # AKA the integral of the heat capacity of anorthite crystal
    deltaHfus_An = 142406 + intdeltaCp_An
    intdeltaCp_Ab = ((-35.64) * (T - 1373)) - ((-2415.5 / 0.5) * (T**0.5 - 1373**0.5)) - \
        ((789280) * ((T**-1) - (1373**-1))) - \
        ((1070640000 / -2) * ((T**-2) - (1373**-2)))
    deltaHfus_Ab = 64500 + intdeltaCp_Ab
    Cap_deltaH_AnAb = deltaHfus_An - deltaHfus_Ab
    Cap_deltaH_RT = Cap_deltaH_AnAb / (8.3144 * T)
    intCp_divdedTfus_An = (-5.77 * (np.log(T) - np.log(1830)) + (3734 / -0.5) * ((T**-0.5) - (
        1830**-0.5)) + (0 / -2) * ((T**-2) - (1830**-2)) - (317020000 / -3) * ((T**-3) - (1830**-3)))
    deltaSfus_An = 77.82 + intCp_divdedTfus_An
    intCp_divdedTfus_Ab = -35.64 * (np.log(T) - np.log(1373)) + (2415.5 / -0.5) * ((T**-0.5) - (
        1373**-0.5)) + (7892800 / -2) * (T**-2 - 1373**-2) - (1070640000 / -3) * ((T**-3) - (1373**-3))
    deltaSfus_Ab = 47 + intCp_divdedTfus_Ab
    CapDeltaS_R = (deltaSfus_An - deltaSfus_Ab) / 8.3144
    H_TdeltaS_An = (deltaHfus_An - (T * deltaSfus_An)) / 1000
    H_TdeltaS_Ab = (deltaHfus_Ab - (T * deltaSfus_Ab)) / 1000
    Gibbs_exchange = H_TdeltaS_An - H_TdeltaS_Ab
    Gibbs_exchange_RT = 1000 * Gibbs_exchange / (8.31441 * T)
    P_T = (P * 1000) / T
    H_RTminusS_R = Cap_deltaH_RT - CapDeltaS_R
    neglnK_V_G = -1 * (lnK + volterm + Gibbs_exchange_RT)
    T_term = 10000 / T
    negSiO2_Liq_mol_frac = -1 * SiO2_Liq_mol_frac
    negTiO2_Liq_mol_frac = -1 * TiO2_Liq_mol_frac
    negAl2O3_Liq_mol_frac_v2 = -1 * Al2O3_Liq_mol_frac_v2
    negFeOt_Liq_mol_frac = -1 * FeOt_Liq_mol_frac
    negMgO_Liq_mol_frac = -1 * MgO_Liq_mol_frac
    negCaO_Liq_mol_frac = -1 * CaO_Liq_mol_frac
    negNa2O_Liq_mol_frac = -1 * Na2O_Liq_mol_frac
    negK2O_Liq_mol_frac = -1 * K2O_Liq_mol_frac

    wtH2Ocalc = (- 17.3204203938587 + (0.389218669342048 * neglnK_V_G) + (2.98588693659695 * T_term)
    + (7.8289140199477 * negSiO2_Liq_mol_frac) - (50.1063951084878 * negAl2O3_Liq_mol_frac_v2) +
     (14.114740308799 * negFeOt_Liq_mol_frac) + (23.9996276026497 * negMgO_Liq_mol_frac)
     - (15.9003801663855 * negCaO_Liq_mol_frac) + (18.6326909831708 * negNa2O_Liq_mol_frac)
     + (24.0180473651546 * negK2O_Liq_mol_frac))

    if XAn is not None and XAb is not None and plag_comps is None:
        Combo_Out = pd.DataFrame(
            data={'H2O_calc': wtH2Ocalc, 'An': XAn, 'Ab': XAb})
        return Combo_Out
    else:
        Combo_Out = pd.concat(
            [feld_cat_frac, liq_comps, Liq_anhyd_mol_frac], axis=1)
        cols_to_move = ['An_Plag', 'Ab_Plag']
        Combo_Out = Combo_Out[cols_to_move +
                              [col for col in Combo_Out.columns if col not in cols_to_move]]
        Combo_Out.insert(0, "H2O_calc", wtH2Ocalc)
    return Combo_Out

## Function for Plag-Liq hygrometry

plag_liq_H_funcs = {H_Put2008_eq25b, H_Put2005_eqH, H_Waters2015}
plag_liq_H_funcs_by_name = {p.__name__: p for p in plag_liq_H_funcs}



def calculate_fspar_liq_hygr(*, liq_comps, plag_comps=None, kspar_comps=None,
                            equationH=None, P=None, T=None, XAn=None, XAb=None, XOr=0):

    '''calculates H2O content (wt%) from composition of equilibrium plagioclase
     and liquid.

   Parameters
    -------
    liq_comps: DataFrame
        liquids compositions with column headings SiO2_Liq, MgO_Liq etc.

    One of:

    1) plag_comps: DataFrame (optional)
        Plag compositions with column headings SiO2_Plag, MgO_Plag etc.


    2) XAn, XAb, XOr, float, int, series
        If plag_comps is None, enter XAn and XAb for plagioclases instead.
        XOr is set to zero by default, but can be overwritten for equilibrium tests

    equation: str

        |  H_Waters2015 (T-dependent, P-dependent)
        |  H_Put2005_eqH (T-dependent, P-independent)
        |  H_Put2008_eq25b (T-dependent, P-dependent)

    P: float, int, series
        Pressure (kbar)

    T: float, int, series
        Temperature (K)

    eq_tests: bool
        If True, also calculatse equilibrum tests of Putirka (2008).

    Returns:
    Pandas DataFrame
        DataFrame with calculated H2O, along with calculated plag and liq parameters


    '''
    if kspar_comps is not None:
        raise ValueError('Sorry, no k-fspar hygrometers implemented in this tool. You must enter plag_comps=')
    try:
        func = plag_liq_H_funcs_by_name[equationH]
    except KeyError:
        raise ValueError(f'{equationH} is not a valid equation') from None
    sig=inspect.signature(func)

    if equationH=="H_Put2008_eq25b" or equationH=="H_Waters2015":
        if P is None:
            raise ValueError(f'{equationH} requires you to enter P. If you dont know this'
            ' Waters and Lange (2015) suggesting entering P=1')

    if sig.parameters['T'].default is not None:
        if T is None:
            raise ValueError(f'{equationH} requires you to enter T')
    else:
        if T is not None:
            print('Youve selected a T-independent function')


    # Then, warn if enter contradicting inputs;
    if plag_comps is not None and XAn is not None:
        raise Exception(
            'You have entered both a plag composition, and an XAn value'
            ', so the code doesnt know which to use. Either enter a full feld composition,'
            ' OR XAn and XAb values')
    if plag_comps is not None and XAb is not None:
        raise Exception(
            'You have entered both a feld composition, and an XAb value,'
            ' so the code doesnt know what to use. Either enter a full feld composition,'
            ' OR XAn and XAb values')

    if plag_comps is None and XAb is None:
        raise Exception('You must enter either plag_comps=, or an XAb and XAn content')

    if equationH == "H_Waters2015":
        if XAn is not None and XAb is not None and plag_comps is None:
            Combo_Out = H_Waters2015(
                liq_comps=liq_comps, P=P, T=T, XAn=XAn, XAb=XAb)
            eq_tests=calculate_plag_liq_eq_tests(liq_comps=liq_comps, XAn=XAn, XAb=XAb,
                P=P, T=T)



        if plag_comps is not None:

            Combo_Out = H_Waters2015(
                liq_comps=liq_comps, plag_comps=plag_comps, P=P, T=T)
            eq_tests=calculate_plag_liq_eq_tests(plag_comps=plag_comps,
                liq_comps=liq_comps, P=P, T=T)

        Combo_Out.insert(0, "Pass An-Ab Eq Test Put2008?", eq_tests['Pass An-Ab Eq Test Put2008?'])

        Combo_Out.insert(2, 'Delta_An', eq_tests['Delta_An'])
        Combo_Out.insert(3, 'Delta_Ab', eq_tests['Delta_Ab'])
        Combo_Out.insert(4, 'Delta_Or', eq_tests['Delta_Or'])
        Combo_Out.insert(5, 'Pred_An_EqE', eq_tests['Pred_An_EqE'])
        Combo_Out.insert(6, 'Pred_Ab_EqF', eq_tests['Pred_Ab_EqF'])
        Combo_Out.insert(7, 'Pred_Or_EqG', eq_tests['Pred_Or_EqG'])
        Combo_Out.insert(8, 'Obs_Kd_Ab_An', eq_tests['Obs_Kd_Ab_An'])
        return Combo_Out


    if equationH == "H_Put2008_eq25b" or equationH == "H_Put2005_eqH":
        if P is None:
            raise TypeError('even if the equation doesnt require a P to be entered'
            ' because you have selected eq tests, you need to enter a P')
        if plag_comps is not None:
            combo_plag_liq = calculate_plag_liq_eq_tests(
                liq_comps=liq_comps, plag_comps=plag_comps, T=T, P=P)
        if plag_comps is None:
            combo_plag_liq = calculate_plag_liq_eq_tests(
                liq_comps=liq_comps, T=T, P=P)
            combo_plag_liq['An_Plag'] = XAn
            combo_plag_liq['Ab_Plag'] = XAb

        kwargs = {name: combo_plag_liq[name] for name,
        p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}

        H2O_out = func(T, **kwargs)
        combo_plag_liq.insert(0, "H2O_calc", H2O_out)
        return combo_plag_liq




## Equations: Two feldspar thermometers


def T_Put2008_eq27a(P, *, K_Barth, SiO2_Kspar_cat_frac,
                    CaO_Kspar_cat_frac, An_Kspar, An_Plag, Ab_Plag):
    '''
    Two feldspar thermometer: Equation 27a of Putirka (2008).
    SEE±23°C for calibration
    SEE±44°C for test data
    '''

    return (273.15 + 10**4 / (9.8 - 0.0976 * P - 2.46 * np.log(K_Barth) - 14.2 * SiO2_Kspar_cat_frac +
            423.4 * CaO_Kspar_cat_frac - 2.42 * np.log(An_Kspar) - 11.4 * An_Plag * Ab_Plag))


def T_Put2008_eq27b(P, *, K_Barth, SiO2_Kspar_cat_frac,
                    CaO_Kspar_cat_frac, An_Kspar, An_Plag, Ab_Plag):
    '''
    Two feldspar thermometer: Equation 27b of Putirka (2008).
    Putirka recomends using this thermometer over 27a, with preference
    being 27b>global>27a
    Global calibration (unlike 27a, which is calibrated on a smaller dataset)
    SEE±30°C for calibration
    '''
    return (273.15 + (-442 - 3.72 * P) / (-0.11 + 0.1 * np.log(K_Barth) -
            3.27 * An_Kspar + 0.098 * np.log(An_Kspar) + 0.52 * An_Plag * Ab_Plag))


def T_Put_Global_2Fspar(P, *, K_Barth, SiO2_Kspar_cat_frac, CaO_Kspar_cat_frac,
Ab_Kspar, Or_Kspar, Na2O_Plag_cat_frac, An_Kspar, An_Plag, Ab_Plag):
    '''
    Two feldspar thermometer from supporting spreadsheet of Putirka (2008)
    Global calibration
    '''
    return (273.15 + 10**4 / (100.638 - 0.0975 * P - 4.9825 * An_Plag
    - 115.03 * Ab_Kspar - 95.745 * Or_Kspar
    + 45.68 * Na2O_Plag_cat_frac - 2.5182 * np.log(An_Kspar)
    + 3.7522 * np.log(K_Barth) - 15.503 * (Ab_Kspar - 0.3136) * (Or_Kspar - 0.6625)))




## Function for calculating 2 feldspar temperatures
Plag_Kspar_T_funcs = {T_Put2008_eq27a, T_Put2008_eq27b, T_Put_Global_2Fspar}

Plag_Kspar_T_funcs_by_name = {p.__name__: p for p in Plag_Kspar_T_funcs}


def calculate_plag_kspar_temp(*, plag_comps=None, kspar_comps=None, Two_Fspar_Match=None, equationT=None, P=None, eq_tests=False):
    '''
    Two feldspar thermometer (Kspar-Plag)
    Returns temperature in Kelvin

    Parameters
    -------

    plag_comps: DataFrame
        Plag compositions with column headings SiO2_Plag, MgO_Plag etc.

    kspar_comps: DataFrame
        Kspar compositions with column headings SiO2_Kspar, MgO_Kspar etc.

    or:
    Two_Fspar_Match: Pandas dataframe from mineral matching algorithm

    EquationT: str
        Equation choices:
            |   T_Put2008_eq27a (P-dependent, H2O-independent)
            |   T_Put2008_eq27b (P-dependent, H2O-independent)
            |   T_Put_Global_2Fspar (P-dependent, H2O-independent)


    P: float, int, series, str  ("Solve")
        Pressure in kbar
        Only needed for P-sensitive thermometers.
        If enter P="Solve", returns a partial function
        Else, enter an integer, float, or panda series


    Returns
    -------
    Panda series
        Temperatures in Kelvin

    '''
# These are checks that our inputs are okay
    try:
        func = Plag_Kspar_T_funcs_by_name[equationT]
    except KeyError:
        raise ValueError(f'{equationT} is not a valid equation') from None
    sig=inspect.signature(func)

    if Two_Fspar_Match is None:
        if isinstance(P, pd.Series):
            if len(P) != len(plag_comps):
                raise ValueError('The panda series entered for pressure isnt the same length '
                'as the dataframe of Plag compositions')
            if len(plag_comps) != len(kspar_comps):
                raise ValueError('The panda series entered for Plag isnt the same length as for KSpar')



        cat_plag = calculate_cat_fractions_plagioclase(plag_comps=plag_comps)
        cat_kspar = calculate_cat_fractions_kspar(kspar_comps=kspar_comps)
        combo_fspars = pd.concat([cat_plag, cat_kspar], axis=1)
        combo_fspars['K_Barth'] = combo_fspars['Ab_Kspar'] / \
        combo_fspars['Ab_Plag']

    else:
        combo_fspars=Two_Fspar_Match

    if sig.parameters['P'].default is not None:
        if P is None:
            raise ValueError(f'{equationT} requires you to enter P, or specify P="Solve"')
    else:
        if P is not None:
            print('Youve selected a P-independent function')


    kwargs = {name: combo_fspars[name] for name, p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
    if isinstance(P, str) or P is None:
        if P == "Solve":
            T_K = partial(func, **kwargs)
        if P is None:
            T_K=func(**kwargs)

    else:
        T_K=func(P, **kwargs)

    if eq_tests is False:
        return T_K
    if eq_tests is True:
        func=calculate_fspar_activity_components
        combo_fspars['T']=T_K
        combo_fspars['P']=P
        kwargs = {name: combo_fspars[name] for name, p in inspect.signature(func).parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
        print('got to Kwargs')
        Eq_Test=func(**kwargs)

        Eq_Test.insert(0, "T_K_calc", T_K)
        return Eq_Test


## Plag Kspar matching

def calculate_plag_kspar_temp_matching(*, kspar_comps, plag_comps, equationT=None,
                                 P=None):
    '''Evaluates all possible Plag-Kspar pairs,
    returns T (K) and equilibrium tests

   Parameters
    -------

    plag_comps: DataFrame
        Panda DataFrame of plag compositions with column headings SiO2_Plag, CaO_Plag etc.

    kspar_comps: DataFrame
        Panda DataFrame of kspar compositions with column headings SiO2_Kspar etc.

    EquationT: str
            |   T_Put2008_eq27a (P-dependent, H2O-independent)
            |   T_Put2008_eq27b (P-dependent, H2O-independent)
            |   T_Put_Global_2Fspar (P-dependent, H2O-independent)


    Or: User sets one of P or T
        pressure in kbar or temperature in Kelvin. Doesn't need to iterate,
        e.g., if set pressure, calculates temperature for that pressure,
        and returns temperature for equilibrium pairs.



   Returns
    -------
    DataFrame
        dataframe of calculated equilibrium tests, temperature,
        as well as user-entered oxides
        and component calculations.
    '''


    # calculating Plag and plag components. Do before duplication to save
    # computation time
    cat_plag = calculate_cat_fractions_plagioclase(plag_comps=plag_comps)
    cat_kspar = calculate_cat_fractions_kspar(kspar_comps=kspar_comps)

    # Adding an ID label to help with melt-kspar rematching later
    cat_plag['ID_Plag'] = cat_plag.index
    cat_kspar['ID_Kspar'] = cat_kspar.index.astype('float64')
    if "Sample_ID_Plag" not in cat_plag:
        cat_plag['Sample_ID_Plag'] = cat_plag.index.astype('float64')
    if "Sample_ID_Kspar" not in cat_kspar:
        cat_kspar['Sample_ID_Kspar'] = cat_kspar.index.astype('float64')
    # Duplicate kspars and liquids so end up with panda of all possible liq-kspar
    # matches

    # This duplicates Plags, repeats kspar1-kspar1*N, kspar2-kspar2*N etc.
    DupPlags = pd.DataFrame(np.repeat(cat_plag.values, np.shape(
        cat_kspar)[0], axis=0))  # .astype('float64')
    DupPlags.columns = cat_plag.columns

    # This duplicates liquids like liq1-liq2-liq3 for kspar1, liq1-liq2-liq3 for
    # kspar2 etc.
    DupKspars = pd.concat([cat_kspar] * np.shape(cat_plag)[0]).reset_index(drop=True)
    # Combines these merged liquids and kspar dataframes
    Combo_plags_kspars = pd.concat([DupKspars, DupPlags], axis=1)

    Combo_plags_kspars_1 = Combo_plags_kspars.copy()
    Combo_plags_kspars_1['K_Barth'] = Combo_plags_kspars_1['Ab_Kspar'] / \
        Combo_plags_kspars_1['Ab_Plag']
    LenCombo = str(np.shape(Combo_plags_kspars)[0])
    print("Considering " + LenCombo +
          " Kspar-Plag pairs, be patient if this is >>1 million!")

    T_K_calc=calculate_plag_kspar_temp(Two_Fspar_Match=Combo_plags_kspars_1.astype(float),
    equationT=equationT, P=P)
    Combo_plags_kspars_1.insert(0, "T_K_calc", T_K_calc)

    func=calculate_fspar_activity_components
    Combo_plags_kspars_1['T']=T_K_calc
    Combo_plags_kspars_1['P']=P
    kwargs = {name: Combo_plags_kspars_1[name].astype('float64') for name, p in inspect.signature(func).parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
    print('got to Kwargs')
    Eq_Test=func(**kwargs)
    out=pd.concat([Eq_Test, Combo_plags_kspars_1], axis=1)

    return out# Combo_plags_kspars_1

