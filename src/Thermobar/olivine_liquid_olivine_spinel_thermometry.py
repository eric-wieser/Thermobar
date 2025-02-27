import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import inspect
import warnings as w
import numbers
import pandas as pd


from Thermobar.core import *
from Thermobar.mineral_equilibrium import *

## Functions for olivine-liquid hygrometry
def H_Gavr2016(*, CaO_Liq, MgO_Liq, CaO_Ol):
    '''
    Olivine-Liquid hygrometer of Gavrilenko et al. (2016).
    '''
    DCa_dry_HighMgO=0.00042*MgO_Liq+0.0196
    DCa_dry_LowMgO=-0.0043*MgO_Liq+0.072
    DCa_dry_calc=np.empty(len(MgO_Liq), dtype=float)
    DeltaCa=np.empty(len(MgO_Liq), dtype=float)

    H2O_Calc=np.empty(len(MgO_Liq), dtype=float)

    DCa_Meas=CaO_Ol/CaO_Liq
    DCa_Divider=0.00462*MgO_Liq-0.027
    for i in range(0, len(MgO_Liq)):
        if DCa_Meas[i]<=DCa_Divider[i]:
            DCa_dry_calc[i]=DCa_dry_HighMgO[i]
            DeltaCa[i]=DCa_dry_calc[i]-DCa_Meas[i]
            H2O_Calc[i]=397*DeltaCa[i]
        else:
            DCa_dry_calc[i]=DCa_dry_LowMgO[i]
            DeltaCa[i]=DCa_dry_calc[i]-DCa_Meas[i]
            H2O_Calc[i]=188*DeltaCa[i]
    H2O_Calc[CaO_Ol==0]=np.nan
    return H2O_Calc

Liquid_olivine_hygr_funcs = {H_Gavr2016}
Liquid_olivine_hygr_funcs_by_name = {p.__name__: p for p in Liquid_olivine_hygr_funcs}


def calculate_ol_liq_hygr(*, liq_comps, ol_comps, equationH, eq_tests=False,
P=None, T=None, equationT=None, Fe3Fet_Liq=None):
    '''
    Olivine-liquid hygrometer. Returns the estimated H2O content
    in wt%

   Parameters
    -------

    liq_comps: DataFrame
        liquid compositions with column headings SiO2_Liq, MgO_Liq etc.

    ol_comps: DataFrame
        Olivine compositions with column headings SiO2_Ol, MgO_Ol etc.

    equationH: str
        H_Gavr2016 (P-independent, H2O_independent)

    eq_tests: bool
        if true, calculates Kd for olivine-liquid pairs.
        Other inputs for these tests:

        P: int, flt, Series (needed for Toplis Kd calculation).
        If nothing inputted, P set to 1 kbar

        T: int, flt, Series (needed for Toplis KD calculation).
        Can also specify equationT="" to calculate temperature
        using an olivine-liquid thermometer, using the calculated H2O content
        from the hygrometer

        Fe3Fet_Liq: int, flt, Series. As Kd calculated using only Fe2 in the Liq.


    Returns
    -------
    pandas.core.series.Series
        H2O content in wt%.
 '''
# These are checks that our inputs are okay
    ol_comps_c=ol_comps.copy()
    liq_comps_c=liq_comps.copy()

    if Fe3Fet_Liq is not None:
        liq_comps_c['Fe3Fet_Liq'] = Fe3Fet_Liq

    try:
        func = Liquid_olivine_hygr_funcs_by_name[equationH]
    except KeyError:
        raise ValueError(f'{equationH} is not a valid equation') from None
    sig=inspect.signature(func)

    anhyd_cat_frac = calculate_anhydrous_cat_fractions_liquid(liq_comps=liq_comps_c)
    ol_cat_frac = calculate_cat_fractions_olivine(ol_comps=ol_comps_c)
    Liq_Ols = pd.concat([ol_comps_c, anhyd_cat_frac, ol_cat_frac], axis=1)



    if len(liq_comps) != len(ol_comps):
        raise ValueError('The panda series entered for olivine isnt the same length as for liquids')

    kwargs = {name: Liq_Ols[name] for name, p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
    H2O_Calc_np=func(**kwargs)
    H2O_Calc=pd.Series(H2O_Calc_np)

    if eq_tests is False and ol_comps is not None:
         return H2O_Calc

    if eq_tests is True:
        if P is None:
            P = 1
            print(
                'You have not selected a pressure, so we have calculated Toplis Kd at 1kbar')
        if T is None and equationT is None:
            raise ValueError('Temperature needed to calculate Delta Kd using Toplis.'
             'Either enter T, or specify equationT=""')
        if equationT is not None:
            T=calculate_ol_liq_temp(ol_comps=ol_comps, liq_comps=liq_comps,
            equationT=equationT, H2O_Liq=H2O_Calc, P=P).T_K_calc
        ol_fo = (ol_comps_c['MgO_Ol'] / 40.3044) / \
            ((ol_comps_c['MgO_Ol'] / 40.3044) + ol_comps_c['FeOt_Ol'] / 71.844)
        KdFeMg_Meas = (
            ((ol_comps_c['FeOt_Ol'] / 71.844) / (ol_comps_c['MgO_Ol'] / 40.3044)) /
            ((liq_comps_c['FeOt_Liq'] * (1 - liq_comps_c['Fe3Fet_Liq']
                                         ) / 71.844) / (liq_comps_c['MgO_Liq'] / 40.3044))
        )
        Kd_func = partial(calculate_toplis2005_kd, SiO2_mol=Liq_Ols['SiO2_Liq_mol_frac'],
        Na2O_mol=Liq_Ols['Na2O_Liq_mol_frac'], K2O_mol=Liq_Ols['Na2O_Liq_mol_frac'],
        P=P, H2O=Liq_Ols['H2O_Liq'], T=T)
        Kd_Toplis_calc = Kd_func(ol_fo)

        DeltaKd_Toplis = abs(KdFeMg_Meas - Kd_Toplis_calc)
        DeltaKd_Roeder = abs(KdFeMg_Meas - 0.3)
        DeltaKd_Matzen = abs(KdFeMg_Meas - 0.34)
        df = pd.DataFrame(data={'H2O_calc': H2O_Calc, 'Temp used for calcs': T, 'P used for calcs': P, 'Kd Meas': KdFeMg_Meas, 'Kd calc (Toplis)': Kd_Toplis_calc,
                                'ΔKd, Toplis': DeltaKd_Toplis, 'ΔKd, Roeder': DeltaKd_Roeder, 'ΔKd, Matzen': DeltaKd_Matzen})
        df_out = pd.concat([df, Liq_Ols], axis=1)

        return df_out

## Functions for olivine-Liquid thermometry
# Defining functions where DMg is measured.
def T_Beatt93_ol(P, *, Den_Beat93):
    '''
    Olivine-Liquid thermometer: Beattie (1993). Putirka (2008) suggest this is the best olivine-liquid thermometer for anhydrous conditions at relatively low pressures.
    '''
    return (((113.1 * 1000) / 8.3144 + (0.1 * P * 10**9 - 10**5)
            * 4.11 * (10**(-6)) / 8.3144) / Den_Beat93)
# This is equation 19 from Putirka 2008


def T_Beatt93_ol_HerzCorr(P, *, Den_Beat93):
    '''
    Olivine-Liquid thermometer: Beattie (1993) with correction of Herzberg and O'Hara (2002), eliminating systematic error at higher pressures
    Anhydrous SEE=±44°C
    Hydrous SEE=±53°C
    '''

    return (((113.1 * 1000 / 8.3144 + (0.0001 * (10**9) - 10**5) * 4.11 *
            (10**(-6)) / 8.3144) / Den_Beat93) + 54 * (0.1 * P) + 2 * (0.1 * P)**2)


def T_Put2008_eq19(P, *, DMg_Meas, CNML, CSiO2L, NF):
    '''
    Olivine-Liquid thermometer originally from Beattie, (1993), form from Putirka (2008)

    '''
    return ((13603) + (4.943 * 10**(-7)) * ((0.1 * P)*10**9 - 10**(-5))) / (6.26 + 2 *
            np.log(DMg_Meas) + 2 * np.log(1.5 * CNML) + 2 * np.log(3 * CSiO2L) - NF)



def T_Put2008_eq21(P, *, DMg_Meas, Na2O_Liq, K2O_Liq, H2O_Liq):
    '''
    Olivine-Liquid thermometer: Putirka (2008), equation 21 (originally Putirka et al., 2007,  Eq 2). Recalibration of Beattie (1993) to account for the pressures sensitivity noted by Herzberg and O'Hara (2002), and esliminates the systematic error of Beattie (1993) for hydrous compositions.
    Anhydrous SEE=±53°C
    Hydrous SEE=±36°C
    '''
    return (1 / ((np.log(DMg_Meas) + 2.158 - 5.115 * 10**(-2) * (Na2O_Liq +
            K2O_Liq) + 6.213 * 10**(-2) * H2O_Liq) / (55.09 * 0.1 * P + 4430)) + 273.15)


def T_Put2008_eq22(P, *, DMg_Meas, CNML, CSiO2L, NF, H2O_Liq):
    '''
    Olivine-Liquid thermometer: Putirka (2008), equation 22 (originally Putirka et al., 2007,  Eq 4). Recalibration of Beattie (1993) to account for the pressures sensitivity noted by Herzberg and O'Hara (2002), and esliminates the systematic error of Beattie (1993) for hydrous compositions. Putirka (2008) suggest this is the best olivine-liquid thermometer for hydrous melts.
    Anhydrous SEE±45°C
    Hydrous SEE±29°C
    '''
    return ((15294.6 + 1318.8 * 0.1 * P + 2.48348 * ((0.1 * P)**2)) / (8.048 + 2.8352 * np.log(DMg_Meas) + 2.097 *
            np.log(1.5 * CNML) + 2.575 * np.log(3 * CSiO2L) - 1.41 * NF + 0.222 * H2O_Liq + 0.5 * (0.1 * P)) + 273.15)


def T_Sisson1992(P, *, KdMg_TSG1992):
    '''
    Olivine-Liquid thermometer: Sisson and Grove (1992). Putirka (2008) suggests this thermometer is best in peridotitic systems containing 2-25 wt% CO2.
    '''
    return ((4129 + 0.0146 * (P*1000-1)) /
            (np.log10(KdMg_TSG1992) + 2.082))


def T_Pu2017(P=None, *, NiO_Ol_mol_frac, FeOt_Liq_mol_frac, MnO_Liq_mol_frac, MgO_Liq_mol_frac,
             CaO_Liq_mol_frac, NiO_Liq_mol_frac, Al2O3_Liq_mol_frac, TiO2_Liq_mol_frac, SiO2_Liq_mol_frac):
    '''
    Olivine-Liquid thermometer: Pu et al. (2017). Uses D Ni (ol-melt) rather than D Mg (ol-melt),
    meaning this thermometer has far less sensitivity to H2O or pressure at 0-1 GPa.
    SEE=±29°C
    '''
    D_Ni_Mol = NiO_Ol_mol_frac / NiO_Liq_mol_frac
    XNm = FeOt_Liq_mol_frac + MnO_Liq_mol_frac + \
        MgO_Liq_mol_frac + CaO_Liq_mol_frac + NiO_Liq_mol_frac
    NFX = 3.5 * np.log(1 - Al2O3_Liq_mol_frac) + 7 * \
        np.log(1 - TiO2_Liq_mol_frac)
    return 9416 / (np.log(D_Ni_Mol) + 0.71 * np.log(XNm) -
                   0.349 * NFX - 0.532 * np.log(SiO2_Liq_mol_frac) + 4.319)


def T_Pu2021(P, *, NiO_Ol_mol_frac, FeOt_Liq_mol_frac, MnO_Liq_mol_frac, MgO_Liq_mol_frac,
             CaO_Liq_mol_frac, NiO_Liq_mol_frac, Al2O3_Liq_mol_frac, TiO2_Liq_mol_frac, SiO2_Liq_mol_frac):
    '''
    Olivine-Liquid thermometer: Pu et al. (2017), with the pressure correction of Pu et al. (2021).
    Uses D Ni (ol-melt) rather than D Mg (ol-melt), meaning this thermometer has far less sensitivity to melt H2O than other olivine-liquid thermometers.
    SEE=±45°C (for the 2017 expression).
    '''
    D_Ni_Mol = NiO_Ol_mol_frac / NiO_Liq_mol_frac
    XNm = FeOt_Liq_mol_frac + MnO_Liq_mol_frac + \
        MgO_Liq_mol_frac + CaO_Liq_mol_frac + NiO_Liq_mol_frac
    NFX = 3.5 * np.log(1 - Al2O3_Liq_mol_frac) + 7 * \
        np.log(1 - TiO2_Liq_mol_frac)
    return (9416 / (np.log(D_Ni_Mol) + 0.71 * np.log(XNm) - 0.349 * NFX - 0.532 *
            np.log(SiO2_Liq_mol_frac) + 4.319)) - 70 + 110 * (P * 0.1) - 18 * (P * 0.1)**2

## Listing all equation options
Liquid_olivine_funcs = {T_Beatt93_ol, T_Beatt93_ol_HerzCorr, T_Put2008_eq19, T_Put2008_eq21,
T_Put2008_eq22, T_Sisson1992, T_Pu2017, T_Pu2021}

Liquid_olivine_funcs_by_name = {p.__name__: p for p in Liquid_olivine_funcs}


## Function for calculating olivine-liquid temperature using various equations.

def calculate_ol_liq_temp(*, liq_comps, equationT, ol_comps=None, P=None,
                          NiO_Ol_Mol=None, H2O_Liq=None, Fe3Fet_Liq=None, eq_tests=False):
    '''
    Olivine-liquid thermometers. Returns the temperature in Kelvin,
    along with calculations of Kd-Fe-Mg equilibrium tests.

   Parameters
    -------

    liq_comps: DataFrame
        liquid compositions with column headings SiO2_Liq, MgO_Liq etc.

    ol_comps: DataFrame
        Olivine compositions with column headings SiO2_Ol, MgO_Ol etc.

    equationT: str
        T_Beatt93_ol (P-dependent, H2O_independent)
        T_Beatt93_ol_HerzCorr (P-dependent, H2O_independent)
        T_Put2008_eq21 (P-dependent, H2O-dependent)
        T_Put2008_eq22 (P-dependent, H2O-dependent)
        T_Sisson1992 (P-dependent, H2O_independent)
        T_Pu2017 (P-independent, H2O_independent)
        T_Pu2021 (P-dependent, H2O_independent)

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
    pandas.core.series.Series
        Temperatures in kelvin.


    '''
# These are checks that our inputs are okay
    try:
        func = Liquid_olivine_funcs_by_name[equationT]
    except KeyError:
        raise ValueError(f'{equationT} is not a valid equation') from None
    sig=inspect.signature(func)


    if isinstance(P, pd.Series):
        if len(P) != len(liq_comps):
            raise ValueError('The panda series entered for pressure isnt the same length '
             'as the dataframe of liquid compositions')
        if len(liq_comps) != len(ol_comps):
            raise ValueError('The panda series entered for olivine isnt the same length as for liquids')

# Replacing H2O and Fe3FeT if relevant
    liq_comps_c = liq_comps.copy()
    ol_comps_c=ol_comps.copy()

    if H2O_Liq is not None:
        liq_comps_c['H2O_Liq'] = H2O_Liq
    if Fe3Fet_Liq is not None:
        liq_comps_c['Fe3Fet_Liq'] = Fe3Fet_Liq

# Allows different calculation scheme for Ni-bearing equations
    if equationT == "T_Pu2017" or equationT == "T_Pu2021":
        anhyd_mol_frac_Ni = calculate_anhydrous_mol_fractions_liquid_Ni(
            liq_comps=liq_comps_c)
        if NiO_Ol_Mol is None:
            ol_mol_frac_Ni = calculate_mol_fractions_olivine_ni(
                ol_comps=ol_comps_c)
            Liq_Ols_Ni = pd.concat([anhyd_mol_frac_Ni, ol_mol_frac_Ni], axis=1)
            if eq_tests is True:
                anhyd_cat_frac = calculate_anhydrous_cat_fractions_liquid(
                    liq_comps=liq_comps_c)
                Liq_Ols = pd.concat([Liq_Ols_Ni, liq_comps_c], axis=1)
    # This means the equilibrium testwork
        if NiO_Ol_Mol is not None:
            if eq_tests is True and ol_comps is None:
                raise Exception(
                    'you dont have any ol compositions, so we cant calculate Kd values')

            NiO_Ol_Mol = NiO_Ol_Mol
            Liq_Ols_Ni = anhyd_mol_frac_Ni.copy()
            Liq_Ols_Ni['NiO_Ol_mol_frac'] = NiO_Ol_Mol
        if equationT == "T_Pu2017":
            func = T_Pu2017
            kwargs = {name: Liq_Ols_Ni[name] for name, p in inspect.signature(
                func).parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
            T_K=func(**kwargs)
        if equationT=="T_Pu2021":
            if P is None:
                raise ValueError(f'{equationT} requires you to enter P, or set P=Solve')
            func = T_Pu2021
            kwargs = {name: Liq_Ols_Ni[name] for name, p in inspect.signature(
                func).parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
            T_K=func(P, **kwargs)


    else:
    # Keiths spreadsheets dont use Cr2O3 and P2O5. So have set this to zero.
        liq_comps_c['Cr2O3_Liq']=0
        liq_comps_c['P2O5_Liq']=0
        ol_comps_c['Cr2O3_Ol']=0
        ol_comps_c['P2O5_Ol']=0
    # Now calculate cation fractions
        anhyd_cat_frac = calculate_anhydrous_cat_fractions_liquid(liq_comps=liq_comps_c)
        ol_cat_frac = calculate_cat_fractions_olivine(ol_comps=ol_comps_c)
        Liq_Ols = pd.concat([anhyd_cat_frac, ol_cat_frac], axis=1)

    # This performs extra calculation steps for Beattie equations
        if equationT == "T_Put2008_eq22" or equationT == "T_Put2008_eq21" or \
        equationT == "T_Beatt93_ol" or equationT == "T_Beatt93_ol_HerzCorr" or equationT=="T_Put2008_eq19":

                Liq_Ols['DMg_Meas'] = Liq_Ols['MgO_Ol_cat_frac'] / \
                    Liq_Ols['MgO_Liq_cat_frac']
                Liq_Ols['CNML'] = (Liq_Ols['MgO_Liq_cat_frac'] + Liq_Ols['FeOt_Liq_cat_frac'] +
                                   Liq_Ols['CaO_Liq_cat_frac'] + Liq_Ols['MnO_Liq_cat_frac'])
                Liq_Ols['CSiO2L'] = Liq_Ols['SiO2_Liq_cat_frac']
                Liq_Ols['NF'] = (7 / 2) * np.log(1 - Liq_Ols['Al2O3_Liq_cat_frac']
                                                 ) + 7 * np.log(1 - Liq_Ols['TiO2_Liq_cat_frac'])
                Liq_Ols['Den_Beat93'] = 52.05 / 8.3144 + 2 * np.log(Liq_Ols['DMg_Meas']) + 2 * np.log(
                    1.5 * Liq_Ols['CNML']) + 2 * np.log(3 * Liq_Ols['CSiO2L']) - Liq_Ols['NF']

        if equationT == "T_Sisson1992":
            Liq_Ols['KdMg_TSG1992'] = (Liq_Ols['MgO_Ol_cat_frac'] /
                (Liq_Ols['MgO_Liq_cat_frac'] *
                    (Liq_Ols['SiO2_Liq_cat_frac']**(0.5))))


    # Checks if P-dependent function you have entered a P
        if sig.parameters['P'].default is not None:
            if P is None:
                raise ValueError(f'{equationT} requires you to enter P')
        else:
            if P is not None:
                print('Youve selected a P-independent function')


        kwargs = {name: Liq_Ols[name] for name, p in sig.parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
        if isinstance(P, str) or P is None:
            if P == "Solve":
                T_K = partial(func, **kwargs)
            if P is None:
                T_K=func(**kwargs)

        else:
            T_K=func(P, **kwargs)

    if eq_tests is False and ol_comps is not None:
        KdFeMg_Meas = (
            ((ol_comps_c['FeOt_Ol'] / 71.844) / (ol_comps_c['MgO_Ol'] / 40.3044)) /
            ((liq_comps_c['FeOt_Liq'] * (1 - liq_comps_c['Fe3Fet_Liq']
                                         ) / 71.844) / (liq_comps_c['MgO_Liq'] / 40.3044))
        )
        df = pd.DataFrame(
            data={'T_K_calc': T_K, 'Kd (Fe-Mg) Meas': KdFeMg_Meas})
        return df

    if eq_tests is True:
        if NiO_Ol_Mol is not None:
            raise Exception(
                'No olivine composition, so cannot calculate equilibrium test. Set eq_tests=False')
        if P is None:
            P = 1
            print(
                'You have not selected a pressure, so we have calculated Toplis Kd at 1kbar')
        ol_fo = (ol_comps_c['MgO_Ol'] / 40.3044) / \
            ((ol_comps_c['MgO_Ol'] / 40.3044) + ol_comps_c['FeOt_Ol'] / 71.844)
        KdFeMg_Meas = (
            ((ol_comps_c['FeOt_Ol'] / 71.844) / (ol_comps_c['MgO_Ol'] / 40.3044)) /
            ((liq_comps_c['FeOt_Liq'] * (1 - liq_comps_c['Fe3Fet_Liq']
                                         ) / 71.844) / (liq_comps_c['MgO_Liq'] / 40.3044))
        )
        Kd_func = partial(calculate_toplis2005_kd, SiO2_mol=Liq_Ols['SiO2_Liq_mol_frac'], Na2O_mol=Liq_Ols[
                          'Na2O_Liq_mol_frac'], K2O_mol=Liq_Ols['Na2O_Liq_mol_frac'], P=P, H2O=Liq_Ols['H2O_Liq'], T=T_K)
        Kd_Toplis_calc = Kd_func(ol_fo)

        DeltaKd_Toplis = abs(KdFeMg_Meas - Kd_Toplis_calc)
        DeltaKd_Roeder = abs(KdFeMg_Meas - 0.3)
        DeltaKd_Matzen = abs(KdFeMg_Meas - 0.34)
        df = pd.DataFrame(data={'T_K_calc': T_K, 'Kd Meas': KdFeMg_Meas, 'Kd calc (Toplis)': Kd_Toplis_calc,
                                'ΔKd, Toplis': DeltaKd_Toplis, 'ΔKd, Roeder': DeltaKd_Roeder, 'ΔKd, Matzen': DeltaKd_Matzen})
        df_out = pd.concat([df, Liq_Ols], axis=1)

        return df_out

## Functions for olivine-spinel thermometry equations

def T_Coogan2014(P=None, *, Cr_No_sp, Al2O3_Ol, Al2O3_Sp):
    '''
    Aluminum-in-olivine thermometer from Coogan et al. 2014. doi: 10.1016/j.chemgeo.2014.01.004
    Uses the Al2O3 content in Olivine, Al2O3 content of Spinel, and the Cr number of the spinel
    '''

    return (10000 / ((0.575) + 0.884 * Cr_No_sp -
            0.897 * np.log(Al2O3_Ol / Al2O3_Sp)))


def T_Wan2008(P=None, *, Cr_No_sp, Al2O3_Ol, Al2O3_Sp):
    '''
    Aluminum-in-olivine thermometer from Wan et al. (2008)  - doi: 10.2138/am.2008.2758
    Uses the Al2O3 content in Olivine, Al2O3 content of Spinel, and the Cr number of the spinel
    '''

    return (10000 / ((0.512) + 0.873 * Cr_No_sp -
            0.91 * np.log(Al2O3_Ol / Al2O3_Sp)))

##  Olivine-spinel thermometry function

def calculate_ol_sp_temp(ol_comps, sp_comps, equationT):
    ''' calculates temperatures from olivine-spinel pairs.


   Parameters
    -------
    ol_comps: DataFrame
        liquid compositions with column headings SiO2_Ol, MgO_Ol etc

    sp_comps: DataFrame
        spinel compositions with column headings SiO2_Sp, MgO_Sp etc

    equationT: str
        Equation choices:
            |   T_Wan2008
            |   T_Coogan2014

    Returns
    -------
    pandas series
       Temperature in K

    '''
    combo = pd.concat([ol_comps, sp_comps], axis=1)
    Cr_No = (sp_comps['Cr2O3_Sp'] / 151.99) / \
        (sp_comps['Cr2O3_Sp'] / 151.9 + sp_comps['Al2O3_Sp'] / 101.96)
    combo.insert(1, "Cr_No_sp", Cr_No)
    if equationT == "T_Coogan2014":
        T_func = T_Coogan2014
    if equationT == "T_Wan2008":
        T_func = T_Wan2008
    kwargs = {name: combo[name] for name, p in inspect.signature(
        T_func).parameters.items() if p.kind == inspect.Parameter.KEYWORD_ONLY}
    T_K = T_func(**kwargs)
    df_T_K = pd.DataFrame(data={'T_K_calc' + str(equationT.strip('T_')): T_K})

    return T_K
