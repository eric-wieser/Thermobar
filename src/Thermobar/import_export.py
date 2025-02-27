
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import inspect
import warnings as w
import numbers
import pandas as pd


from Thermobar.core import *

def import_lepr_file(filename):
    """
    Reads in data from the outputs from the Caltech LEPR site (where oxides are followed by the word "value")
    Splits the data into phases, as for the read_excel function.

   Parameters
    -------
    filename: str
        Excel filename from LEPR

    Returns
    -------
    pandas DataFrames stored in a dictionary. E.g., Access Cpxs using output.Cpxs
        my_input = pandas dataframe of the entire spreadsheet
        mylabels = sample labels
        Experimental_press_temp = User-entered PT
        Fluid=pandas dataframe of fluid compositions
        Liqs=pandas dataframe of liquid oxides
        Ols=pandas dataframe of olivine oxides
        Cpxs=pandas dataframe of cpx oxides
        Plags=pandas dataframe of plagioclase oxides
        Kspars=pandas dataframe of kspar oxides
        Opxs=pandas dataframe of opx oxides
        Amps=pandas dataframe of amphibole oxides
        Sps=pandas dataframe of spinel oxides


    """

    my_input = pd.ExcelFile(filename)
    sheet_names = my_input.sheet_names

    if "Experiment" in sheet_names:
        my_input_Exp = pd.read_excel(filename, sheet_name="Experiment")
        myExp = pd.DataFrame(data={'Citation': my_input_Exp['Citation'], 'Experiment': my_input_Exp['Experiment'],
                                   'T_K': my_input_Exp['T (C)'] + 273.15, 'P_kbar': 10 * my_input_Exp['P (GPa)']}
                             )
    if "Experiment" not in sheet_names:
        myExp = pd.DataFrame()

    if "Fluid" in sheet_names:
        my_input_Fluid = pd.read_excel(filename, sheet_name="Fluid").fillna(0)
        myFluid = pd.DataFrame(data={'Experiment': my_input_Fluid['Experiment'],
                                     'H2O_Val': my_input_Fluid['H2O value'],
                                     'CO2_Val': my_input_Fluid['CO2 value']})
        myFluid_Exp = pd.merge(myFluid, myExp, on="Experiment")

    if "Fluid" not in sheet_names:
        myFluid = pd.DataFrame()
        myFluid_Exp = pd.DataFrame()

    if "Plagioclase" in sheet_names:
        my_input_Plag = pd.read_excel(
            filename, sheet_name="Plagioclase").fillna(0)
        my_input_Plag['FeOT value'] = my_input_Plag['FeO value'] + \
            0.89998 * my_input_Plag['Fe2O3 value']
        myPlag = pd.DataFrame(data={'Experiment': my_input_Plag['Experiment'],
                                    'SiO2_Plag': my_input_Plag['SiO2 value'],
                                    'TiO2_Plag': my_input_Plag['TiO2 value'],
                                    'Al2O3_Plag': my_input_Plag['Al2O3 value'],
                                    'FeOt_Plag': my_input_Plag['FeOT value'],
                                    'MnO_Plag': my_input_Plag['MnO value'],
                                    'MgO_Plag': my_input_Plag['MgO value'],
                                    'CaO_Plag': my_input_Plag['CaO value'],
                                    'Na2O_Plag': my_input_Plag['Na2O value'],
                                    'K2O_Plag': my_input_Plag['K2O value'],
                                    'Cr2O3_Plag': my_input_Plag['Cr2O3 value'],
                                    'P2O5_Plag': my_input_Plag['P2O5 value']})
        myPlag_Exp = pd.merge(myPlag, myExp, on="Experiment")

    if "Plagioclase" not in sheet_names:
        myPlag = pd.DataFrame()
        myPlag_Exp = pd.DataFrame()
    if "Clinopyroxene" in sheet_names:
        my_input_Cpx = pd.read_excel(
            filename, sheet_name="Clinopyroxene").fillna(0)
        my_input_Cpx['FeOT value'] = my_input_Cpx['FeO value'] + \
            0.89998 * my_input_Cpx['Fe2O3 value']
        myCpx = pd.DataFrame(data={'Experiment': my_input_Cpx['Experiment'],
                                   'SiO2_Cpx': my_input_Cpx['SiO2 value'],
                                   'TiO2_Cpx': my_input_Cpx['TiO2 value'],
                                   'Al2O3_Cpx': my_input_Cpx['Al2O3 value'],
                                   'FeOt_Cpx': my_input_Cpx['FeOT value'],
                                   'MnO_Cpx': my_input_Cpx['MnO value'],
                                   'MgO_Cpx': my_input_Cpx['MgO value'],
                                   'CaO_Cpx': my_input_Cpx['CaO value'],
                                   'Na2O_Cpx': my_input_Cpx['Na2O value'],
                                   'K2O_Cpx': my_input_Cpx['K2O value'],
                                   'Cr2O3_Cpx': my_input_Cpx['Cr2O3 value'],
                                   'P2O5_Cpx': my_input_Cpx['P2O5 value']})
        myCpx_Exp = pd.merge(myCpx, myExp, on="Experiment")

    if "Clinopyroxene" not in sheet_names:
        myCpx = pd.DataFrame()
        myCpx_Exp = pd.DataFrame()

    if "Orthopyroxene" in sheet_names:
        my_input_Opx = pd.read_excel(
            filename, sheet_name="Orthopyroxene").fillna(0)
        my_input_Opx['FeOT value'] = my_input_Opx['FeO value'] + \
            0.89998 * my_input_Opx['Fe2O3 value']
        myOpx = pd.DataFrame(data={'Experiment': my_input_Opx['Experiment'],
                                   'SiO2_Opx': my_input_Opx['SiO2 value'],
                                   'TiO2_Opx': my_input_Opx['TiO2 value'],
                                   'Al2O3_Opx': my_input_Opx['Al2O3 value'],
                                   'FeOt_Opx': my_input_Opx['FeOT value'],
                                   'MnO_Opx': my_input_Opx['MnO value'],
                                   'MgO_Opx': my_input_Opx['MgO value'],
                                   'CaO_Opx': my_input_Opx['CaO value'],
                                   'Na2O_Opx': my_input_Opx['Na2O value'],
                                   'K2O_Opx': my_input_Opx['K2O value'],
                                   'Cr2O3_Opx': my_input_Opx['Cr2O3 value'],
                                   'P2O5_Opx': my_input_Opx['P2O5 value']})
        myOpx_Exp = pd.merge(myOpx, myExp, on="Experiment")

    if "Orthopyroxene" not in sheet_names:
        myOpx = pd.DataFrame()
        myOpx_Exp = pd.DataFrame()
    if "Liquid" in sheet_names:
        my_input_Liq = pd.read_excel(filename, sheet_name="Liquid").fillna(0)
        my_input_Liq['FeOT value'] = my_input_Liq['FeO value'] + \
            0.89998 * my_input_Liq['Fe2O3 value']
        myLiq = pd.DataFrame(data={'Experiment': my_input_Liq['Experiment'],
                                   'SiO2_Liq': my_input_Liq['SiO2 value'],
                                   'TiO2_Liq': my_input_Liq['TiO2 value'],
                                   'Al2O3_Liq': my_input_Liq['Al2O3 value'],
                                   'FeOt_Liq': my_input_Liq['FeOT value'],
                                   'MnO_Liq': my_input_Liq['MnO value'],
                                   'MgO_Liq': my_input_Liq['MgO value'],
                                   'CaO_Liq': my_input_Liq['CaO value'],
                                   'Na2O_Liq': my_input_Liq['Na2O value'],
                                   'K2O_Liq': my_input_Liq['K2O value'],
                                   'Cr2O3_Liq': my_input_Liq['Cr2O3 value'],
                                   'P2O5_Liq': my_input_Liq['P2O5 value'],
                                   'H2O_Liq': my_input_Liq['H2O value']})
        myLiq_Exp = pd.merge(myLiq, myExp, on="Experiment")
    if "Liquid" not in sheet_names:
        myLiq = pd.DataFrame()
        myLiq_Exp = pd.DataFrame()
    if "Amphibole" in sheet_names:
        my_input_Amp = pd.read_excel(
            filename, sheet_name="Amphibole").fillna(0)
        my_input_Amp['FeOT value'] = my_input_Amp['FeO value'] + \
            0.89998 * my_input_Amp['Fe2O3 value']
        myAmp = pd.DataFrame(data={'Experiment': my_input_Amp['Experiment'],
                                   'SiO2_Amp': my_input_Amp['SiO2 value'],
                                   'TiO2_Amp': my_input_Amp['TiO2 value'],
                                   'Al2O3_Amp': my_input_Amp['Al2O3 value'],
                                   'FeOt_Amp': my_input_Amp['FeOT value'],
                                   'MnO_Amp': my_input_Amp['MnO value'],
                                   'MgO_Amp': my_input_Amp['MgO value'],
                                   'CaO_Amp': my_input_Amp['CaO value'],
                                   'Na2O_Amp': my_input_Amp['Na2O value'],
                                   'K2O_Amp': my_input_Amp['K2O value'],
                                   'Cr2O3_Amp': my_input_Amp['Cr2O3 value'],
                                   'P2O5_Amp': my_input_Amp['P2O5 value']})
        myAmp_Exp = pd.merge(myAmp, myExp, on="Experiment")

    if "Amphibole" not in sheet_names:
        myAmp = pd.DataFrame()
        myAmp_Exp = pd.DataFrame()

    if "Olivine" in sheet_names:
        my_input_Ol = pd.read_excel(filename, sheet_name="Olivine").fillna(0)
        my_input_Ol['FeOT value'] = my_input_Ol['FeO value'] + \
            0.89998 * my_input_Ol['Fe2O3 value']
        myOl = pd.DataFrame(data={'Experiment': my_input_Ol['Experiment'],
                            'SiO2_Ol': my_input_Ol['SiO2 value'],
                                  'TiO2_Ol': my_input_Ol['TiO2 value'],
                                  'Al2O3_Ol': my_input_Ol['Al2O3 value'],
                                  'FeOt_Ol': my_input_Ol['FeOT value'],
                                  'MnO_Ol': my_input_Ol['MnO value'],
                                  'MgO_Ol': my_input_Ol['MgO value'],
                                  'CaO_Ol': my_input_Ol['CaO value'],
                                  'Na2O_Ol': my_input_Ol['Na2O value'],
                                  'K2O_Ol': my_input_Ol['K2O value'],
                                  'Cr2O3_Ol': my_input_Ol['Cr2O3 value'],
                                  'P2O5_Ol': my_input_Ol['P2O5 value']})
        myOl_Exp = pd.merge(myOl, myExp, on="Experiment")

    if "Olivine" not in sheet_names:
        myOl = pd.DataFrame()
        myOl_Exp = pd.DataFrame()

    return {'Experimental_press_temp': myExp, 'Liquids': myLiq, 'Liqs_Exp': myLiq_Exp, 'Fluids': myFluid, 'Fluids_Exp': myFluid_Exp, 'Plags': myPlag, 'Plags_Exp': myPlag_Exp,
            'Cpxs': myCpx, 'Cpxs_Exp': myCpx_Exp, 'Opxs': myOpx, 'Opxs_Exp': myOpx_Exp, 'Amps': myAmp, 'Amps_Exp': myAmp_Exp, 'Ols_Exp': myOl_Exp}
    # 'Experimental_press_temp':Experimental_press_temp1, 'Cpxs': myCPXs1, 'Opxs': myOPXs1, 'Liqs':myLiquids1, 'Plags': myPlags1, 'Kspars': myKspars1,'Amps': myAmphs1, 'Ols': myOls1, 'Sps': mySps1}#,


# Loading Excel, returns a disctionry
def import_excel(filename, sheet_name, sample_label=None, GEOROC=False):
    '''
    Import excel sheet of oxides in wt%, headings should be of the form SiO2_Liq (for the melt/liquid), SiO2_Ol (for olivine comps), SiO2_Cpx (for clinopyroxene compositions). Order doesn't matter


   Parameters
    -------

    filename: pExcel file
        Excel file of oxides in wt% with columns labelled SiO2_Liq, SiO2_Ol, SiO2_Cpx etc.

    filename: str
        specifies the file name (e.g., Python_OlLiq_Thermometers_Test.xlsx)

    Returns
    -------
    pandas DataFrames stored in a dictionary. E.g., Access Cpxs using output.Cpxs
        my_input = pandas dataframe of the entire spreadsheet
        mylabels = sample labels
        Experimental_press_temp = User-entered PT
        Liqs=pandas dataframe of liquid oxides
        Ols=pandas dataframe of olivine oxides
        Cpxs=pandas dataframe of cpx oxides
        Plags=pandas dataframe of plagioclase oxides
        Kspars=pandas dataframe of kspar oxides
        Opxs=pandas dataframe of opx oxides
        Amps=pandas dataframe of amphibole oxides
        Sps=pandas dataframe of spinel oxides
    '''
    if 'csv' in filename:
        my_input = pd.read_csv(filename)

    elif 'xls' in filename:
        if sheet_name is not None:
            my_input = pd.read_excel(filename, sheet_name=sheet_name)
            #my_input[my_input < 0] = 0
        else:
            my_input = pd.read_excel(filename)
            #my_input[my_input < 0] = 0

    my_input_c = my_input.copy()

    if any(my_input.columns.str.contains("_cpx")):
        w.warn("You've got a column heading with a lower case _cpx, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Cpx)" )

    if any(my_input.columns.str.contains("_opx")):
        w.warn("You've got a column heading with a lower case _opx, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Opx)" )

    if any(my_input.columns.str.contains("_plag")):
        w.warn("You've got a column heading with a lower case _plag, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Plag)" )

    if any(my_input.columns.str.contains("_kspar")):
       w.warn("You've got a column heading with a lower case _kspar, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Kspar)" )

    if any(my_input.columns.str.contains("_sp")):
        w.warn("You've got a column heading with a lower case _sp, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Sp)" )

    if any(my_input.columns.str.contains("_ol")):
        w.warn("You've got a column heading with a lower case _ol, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Ol)" )

    if any(my_input.columns.str.contains("_amp")):
        w.warn("You've got a column heading with a lower case _amp, this is okay if this campumn is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Amp)" )

    if any(my_input.columns.str.contains("_liq")):
        w.warn("You've got a column heading with a lower case _liq, this is okay if this column is for your"
        " own use, but if its an input to Thermobar, it needs to be capitalized (_Liq)" )

    if any(my_input.columns.str.contains("FeO_")) and (all(my_input.columns.str.contains("FeOt_")==False)):
        raise ValueError("No FeOt found. You've got a column heading with FeO. To avoid errors based on common EPMA outputs"
        " thermobar only recognises columns with FeOt for all phases except liquid"
        " where you can also enter a Fe3Fet_Liq heading used for equilibrium tests")

    if any(my_input.columns.str.contains("Fe2O3_")) and (all(my_input.columns.str.contains("FeOt_")==False)):
         raise ValueError("No FeOt column found. You've got a column heading with Fe2O3. To avoid errors based on common EPMA outputs"
        " thermobar only recognises columns with FeOt for all phases except liquid"
        " where you can also enter a Fe3Fet_Liq heading used for equilibrium tests")




 #   myLabels=my_input.Sample_ID

    Experimental_press_temp1 = my_input.reindex(df_ideal_exp.columns, axis=1)
# This deals with the fact almost everyone will enter as FeO, but the code uses FeOt for these minerals.
# E.g., if users only enter FeO (not FeOt and Fe2O3), allocates a FeOt
# column. If enter FeO and Fe2O3, put a FeOt column


    if GEOROC is True:
        my_input_c.loc[np.isnan(my_input_c['FeOt_Liq']) is True, 'FeOt_Liq'] = my_input_c.loc[np.isnan(
            my_input_c['FeOt_Liq']) is True, 'FeO_Liq'] + my_input_c.loc[np.isnan(my_input_c['FeOt_Liq']) is True, 'Fe2O3_Liq'] * 0.8999998

    myLiquids1 = my_input_c.reindex(df_ideal_liq.columns, axis=1).fillna(0)
    myLiquids1 = myLiquids1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myLiquids1[myLiquids1 < 0] = 0

    myCPXs1 = my_input_c.reindex(df_ideal_cpx.columns, axis=1).fillna(0)
    myCPXs1 = myCPXs1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myCPXs1[myCPXs1 < 0] = 0

    myOls1 = my_input_c.reindex(df_ideal_ol.columns, axis=1).fillna(0)
    myOls1 = myOls1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myOls1[myOls1 < 0] = 0

    myPlags1 = my_input_c.reindex(df_ideal_plag.columns, axis=1).fillna(0)
    myPlags1 = myPlags1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myPlags1[myPlags1 < 0] = 0

    myKspars1 = my_input_c.reindex(df_ideal_kspar.columns, axis=1).fillna(0)
    myKspars1 = myKspars1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myKspars1[myKspars1 < 0] = 0

    myOPXs1 = my_input_c.reindex(df_ideal_opx.columns, axis=1).fillna(0)
    myOPXs1 = myOPXs1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myOPXs1[myOPXs1 < 0] = 0

    mySps1 = my_input_c.reindex(df_ideal_sp.columns, axis=1).fillna(0)
    mySps1 = mySps1.apply(pd.to_numeric, errors='coerce').fillna(0)
    mySps1[mySps1 < 0] = 0

    myAmphs1 = my_input_c.reindex(df_ideal_amp.columns, axis=1).fillna(0)
    myAmphs1 = myAmphs1.apply(pd.to_numeric, errors='coerce').fillna(0)
    myAmphs1[myAmphs1 < 0] = 0
    # Adding sample Names
    if "Sample_ID_Cpx" in my_input:
        myCPXs1['Sample_ID_Cpx'] = my_input['Sample_ID_Cpx']
    else:
        myCPXs1['Sample_ID_Cpx'] = my_input.index

    if "Sample_ID_Opx" in my_input:
        myOPXs1['Sample_ID_Opx'] = my_input['Sample_ID_Opx']
    else:
        myOPXs1['Sample_ID_Opx'] = my_input.index

    if "Sample_ID_Liq" in my_input:
        myLiquids1['Sample_ID_Liq'] = my_input['Sample_ID_Liq']
    else:
        myLiquids1['Sample_ID_Liq'] = my_input.index

    if "Sample_ID_Plag" in my_input:
        myPlags1['Sample_ID_Plag'] = my_input['Sample_ID_Plag']
    else:
        myPlags1['Sample_ID_Plag'] = my_input.index

    if "Sample_ID_Amp" in my_input:
        myAmphs1['Sample_ID_Amp'] = my_input['Sample_ID_Amp']
    else:
        myAmphs1['Sample_ID_Amp'] = my_input.index

    # if "P_kbar" in my_input:
    #     myAmphs1['P_kbar'] = my_input['P_kbar']
    #     myPlags1['P_kbar'] = my_input['P_kbar']
    #     myOls1['P_kbar'] = my_input['P_kbar']
    #     myCPXs1['P_kbar'] = my_input['P_kbar']
    #     myOPXs1['P_kbar'] = my_input['P_kbar']
    #     mySps1['P_kbar'] = my_input['P_kbar']
    #     myLiquids1['P_kbar'] = my_input['P_kbar']
    #
    # if "T_K" in my_input:
    #     myAmphs1['T_K'] = my_input['T_K']
    #     myPlags1['T_K'] = my_input['T_K']
    #     myOls1['T_K'] = my_input['T_K']
    #     myCPXs1['T_K'] = my_input['T_K']
    #     myOPXs1['T_K'] = my_input['T_K']
    #     mySps1['T_K'] = my_input['T_K']
    #     myLiquids1['T_K'] = my_input['T_K']

    return {'my_input': my_input, 'Experimental_press_temp': Experimental_press_temp1, 'Cpxs': myCPXs1, 'Opxs': myOPXs1, 'Liqs': myLiquids1,
            'Plags': myPlags1, 'Kspars': myKspars1, 'Amps': myAmphs1, 'Ols': myOls1, 'Sps': mySps1}  # , 'y1': y1 ,'y2': y2}


def import_excel_errors(filename, sheet_name, GEOROC=False):
    '''
    Import excel sheet of oxide errors in wt%, headings should be of the form SiO2_Liq_Err (for the melt/liquid), SiO2_Ol_Err (for olivine comps), SiO2_Cpx_Err (for clinopyroxene compositions).


   Parameters
    -------

    filename: pExcel file
                Excel file of oxides in wt% with columns labelled SiO2_Liq, SiO2_Ol, SiO2_Cpx etc.

    filename: str
        specifies the file name (e.g., Python_OlLiq_Thermometers_Test.xlsx)

    Returns
    -------
    pandas DataFrames stored in a dictionary. E.g., Access Cpxs using output.Cpxs
        my_input_Err = pandas dataframe of the entire spreadsheet
        Experimental_press_temp_Err = User-entered PT errors.
        Liqs_Err=pandas dataframe of liquid oxide errors
        Ols_Err=pandas dataframe of olivine oxide errors
        Cpxs_Err=pandas dataframe of cpx oxide  errors
        Plags_Err=pandas dataframe of plagioclase oxide errors
        Kspars_Err=pandas dataframe of kspar oxide errors
        Opxs_Err=pandas dataframe of opx oxide errors
        Amps_Err=pandas dataframe of amphibole oxide errors
        Sps_Err=pandas dataframe of spinel oxide errors
    '''
    if 'csv' in filename:
        my_input = pd.read_csv(filename)
        #my_input[my_input < 0] = 0
    elif 'xls' in filename:
        if sheet_name is not None:
            my_input = pd.read_excel(filename, sheet_name=sheet_name)
            #my_input[my_input < 0] = 0
        else:
            my_input = pd.read_excel(filename)
            #my_input[my_input < 0] = 0

    my_input_c = my_input.copy()

 #   myLabels=my_input.Sample_ID
    my_input.fillna(0)
    Experimental_press_temp1 = my_input.reindex(df_ideal_exp_Err.columns)
# This deals with the fact almost everyone will enter as FeO, but the code uses FeOt for these minerals.
# E.g., if users only enter FeO (not FeOt and Fe2O3), allocates a FeOt
# column. If enter FeO and Fe2O3, put a FeOt column

    if "FeO_Cpx_Err" in my_input and "FeOt_Cpx" not in my_input and "Fe2O3_Cpx" not in my_input:
        my_input_c['FeOt_Cpx_Err'] = my_input_c['FeO_Cpx_Err']
        print('Only FeO_Cpx found in input, the code has allocated this to FeOt_Cpx')
    if "FeO_Cpx_Err" in my_input and "Fe2O3_Cpx_Err" in my_input and 'FeOt_Cpx' not in my_input:
        my_input_c['FeOt_Cpx_Err'] = my_input_c['FeO_Cpx_Err'] + \
            0.8998 * my_input_c['Fe2O3_Cpx_Err']

    if "FeO_Opx_Err" in my_input and "FeOt_Opx" not in my_input and "Fe2O3_Opx" not in my_input:
        my_input_c['FeOt_Opx_Err'] = my_input_c['FeO_Opx_Err']
        print('Only FeO_Opx found in input, the code has allocated this to FeOt_Opx')
    if "FeO_Opx_Err" in my_input and "Fe2O3_Opx_Err" in my_input and 'FeOt_Opx' not in my_input:
        my_input_c['FeOt_Opx_Err'] = my_input_c['FeO_Opx_Err'] + \
            0.8998 * my_input_c['Fe2O3_Opx_Err']

    if "FeO_Plag_Err" in my_input and "FeOt_Plag" not in my_input and "Fe2O3_Plag" not in my_input:
        my_input_c['FeOt_Plag_Err'] = my_input_c['FeO_Plag_Err']
        print('Only FeO_Plag found in input, the code has allocated this to FeOt_Plag')
    if "FeO_Plag_Err" in my_input and "Fe2O3_Plag_Err" in my_input and 'FeOt_Plag' not in my_input:
        my_input_c['FeOt_Plag_Err'] = my_input_c['FeO_Plag_Err'] + \
            0.8998 * my_input_c['Fe2O3_Plag_Err']

    if "FeO_Kspar_Err" in my_input and "FeOt_Kspar" not in my_input and "Fe2O3_Kspar" not in my_input:
        my_input_c['FeOt_Kspar_Err'] = my_input_c['FeO_Kspar_Err']
        print('Only FeO_Kspar found in input, the code has allocated this to FeOt_Kspar')
    if "FeO_Kspar_Err" in my_input and "Fe2O3_Kspar_Err" in my_input and 'FeOt_Kspar' not in my_input:
        my_input_c['FeOt_Kspar_Err'] = my_input_c['FeO_Kspar_Err'] + \
            0.8998 * my_input_c['Fe2O3_Kspar_Err']

    if "FeO_Amp_Err" in my_input and "FeOt_Amp" not in my_input and "Fe2O3_Amp" not in my_input:
        my_input_c['FeOt_Amp_Err'] = my_input_c['FeO_Amp_Err']
        print('Only FeO_Amp found in input, the code has allocated this to FeOt_Amp')
    if "FeO_Amp_Err" in my_input and "Fe2O3_Amp_Err" in my_input and 'FeOt_Amp' not in my_input:
        my_input_c['FeOt_Amp_Err'] = my_input_c['FeO_Amp_Err'] + \
            0.8998 * my_input_c['Fe2O3_Amp_Err']

    if "FeO_Sp_Err" in my_input and "FeOt_Sp" not in my_input and "Fe2O3_Sp" not in my_input:
        my_input_c['FeOt_Sp_Err'] = my_input_c['FeO_Sp_Err']
        print('Only FeO_Sp found in input, the code has allocated this to FeOt_Sp')
    if "FeO_Sp_Err" in my_input and "Fe2O3_Sp_Err" in my_input and 'FeOt_Sp' not in my_input:
        my_input_c['FeOt_Sp_Err'] = my_input_c['FeO_Sp_Err'] + \
            0.8998 * my_input_c['Fe2O3_Sp_Err']

    if "FeO_Ol_Err" in my_input and "FeOt_Ol" not in my_input and "Fe2O3_Ol" not in my_input:
        my_input_c['FeOt_Ol_Err'] = my_input_c['FeO_Ol_Err']
        print('Only FeO_Ol found in input, the code has allocated this to FeOt_Ol')
    if "FeO_Ol_Err" in my_input and "Fe2O3_Ol_Err" in my_input and 'FeOt_Ol' not in my_input:
        my_input_c['FeOt_Ol_Err'] = my_input_c['FeO_Ol_Err'] + \
            0.8998 * my_input_c['Fe2O3_Ol_Err']

    # For liquids, users have an option to specify Fe3Fet_Liq.
    # 1st scenario, users only enter FeOt, code sets Fe3FeT to 0.
    if "FeOt_Err_Liq_Err" in my_input and "Fe2O3_Err_Liq" not in my_input and "Fe3Fet_Err_Liq" not in my_input:
        my_input_c['Fe3Fet_Liq_Err'] = 0
        print('We have set Fe3Fet_Liq_Err to zero, as you only entered FeOt. You can input a Fe3Fet_Liq_Er column to specify this value instead')
    # 2nd scenario, user only enteres FeO. Code sets FeO=FeOt, sets Fe3FeT to 0
    if "FeO_Err_Liq_Err" in my_input and "Fe2O3_Err_Liq" not in my_input and 'FeOt_Liq' not in my_input and "Fe3Fet_Err_Liq" not in my_input:
        my_input_c['FeOt_Liq_Err'] = my_input_c['FeO_Liq_Err']
        my_input_c['Fe3Fet_Liq_Err'] = 0
        print('Only FeO_Ol found in input, the code has allocated this to FeOt_Ol')
    # 3rd scenario, user only enteres Fe2O3. code calculates FeOt
    if "Fe2O3_Err_Liq_Err" in my_input and "FeO_Err_Liq" not in my_input and 'FeOt_Liq' not in my_input and "Fe3Fet_Err_Liq" not in my_input:
        my_input_c['FeOt_Liq_Err'] = 0.8998 * my_input_c['Fe2O3_Liq_Err']
        my_input_c['Fe3Fet_Liq_Err'] = 1
        print('Only Fe2O3_Ol found in input, the code has allocated this to FeOt_Ol, and set Fe3Fet_Liq=1')

    # 4th scenario, users enter only FeO and Fe2O3
    if "Fe2O3_Err_Liq_Err" in my_input and "FeO_Err_Liq_Err" in my_input and 'FeOt_Liq' not in my_input and "Fe3Fet_Err_Liq" not in my_input:
        my_input_c['FeOt_Liq_Err'] = my_input_c['FeO_Liq_Err'] + \
            0.8998 * my_input_c['Fe2O3_Liq_Err']
        my_input_c['Fe3Fet_Liq_Err'] = (0.89998 * my_input_c['Fe2O3_Liq_Err']) / (
            (0.89998 * my_input_c['Fe2O3_Liq_Err'] + my_input_c['FeO_Liq_Err']))
    if "Fe2O3_Err_Liq_Err" in my_input and "FeO_Err_Liq_Err" in my_input and 'FeOt_Liq' in my_input:
        w.warn('You have entered FeO, Fe2O3, AND FeOt. The code uses FeO and Fe2O3 to recalculate FeOt and Fe3FeT ')
        my_input_c['FeOt_Liq_Err'] = my_input_c['FeO_Liq_Err'] + \
            0.8998 * my_input_c['Fe2O3_Liq_Err']
        my_input_c['Fe3Fet_Liq_Err'] = (0.89998 * my_input_c['Fe2O3_Liq_Err']) / (
            (0.89998 * my_input_c['Fe2O3_Liq_Err'] + my_input_c['FeO_Liq_Err']))


    myLiquids1 = my_input.reindex(df_ideal_liq_Err.columns, axis=1).fillna(0)
    myLiquids1 = myLiquids1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myCPXs1 = my_input_c.reindex(df_ideal_cpx_Err.columns, axis=1).fillna(0)
    myCPXs1 = myCPXs1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myOls1 = my_input_c.reindex(df_ideal_ol_Err.columns, axis=1).fillna(0)
    myOls1 = myOls1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myPlags1 = my_input_c.reindex(df_ideal_plag_Err.columns, axis=1).fillna(0)
    myPlags1 = myPlags1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myKspars1 = my_input_c.reindex(
        df_ideal_kspar_Err.columns, axis=1).fillna(0)
    myKspars1 = myKspars1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myOPXs1 = my_input_c.reindex(df_ideal_opx_Err.columns, axis=1).fillna(0)
    myOPXs1 = myOPXs1.apply(pd.to_numeric, errors='coerce').fillna(0)

    mySps1 = my_input_c.reindex(df_ideal_sp_Err.columns, axis=1).fillna(0)
    mySps1 = mySps1.apply(pd.to_numeric, errors='coerce').fillna(0)

    myAmphs1 = my_input_c.reindex(df_ideal_amp_Err.columns, axis=1).fillna(0)
    myAmphs1 = myAmphs1.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Adding sample Names
    if "Sample_ID_Cpx_Err" in my_input:
        myCPXs1['Sample_ID_Cpx_Err'] = my_input['Sample_ID_Cpx_Err']
    else:
        myCPXs1['Sample_ID_Cpx_Err'] = my_input.index

    if "Sample_ID_Opx_Err" in my_input:
        myOPXs1['Sample_ID_Opx_Err'] = my_input['Sample_ID_Opx_Err']
    else:
        myOPXs1['Sample_ID_Opx_Err'] = my_input.index

    if "Sample_ID_Err_Liq_Err" in my_input:
        myLiquids1['Sample_ID_Liq_Err'] = my_input['Sample_ID_Liq_Err']
    else:
        myLiquids1['Sample_ID_Liq_Err'] = my_input.index

    if "Sample_ID_Plag_Err" in my_input:
        myPlags1['Sample_ID_Plag_Err'] = my_input['Sample_ID_Plag_Err']
    else:
        myPlags1['Sample_ID_Plag_Err'] = my_input.index

    if "Sample_ID_Amp_Err" in my_input:
        myAmphs1['Sample_ID_Amp_Err'] = my_input['Sample_ID_Amp_Err']
    else:
        myAmphs1['Sample_ID_Amp_Err'] = my_input.index

    if "P_kbar_Err" in my_input:
        myAmphs1['P_kbar_Err'] = my_input['P_kbar_Err']
        myPlags1['P_kbar_Err'] = my_input['P_kbar_Err']
        myOls1['P_kbar_Err'] = my_input['P_kbar_Err']
        myCPXs1['P_kbar_Err'] = my_input['P_kbar_Err']
        myOPXs1['P_kbar_Err'] = my_input['P_kbar_Err']
        mySps1['P_kbar_Err'] = my_input['P_kbar_Err']
        myLiquids1['P_kbar_Err'] = my_input['P_kbar_Err']

    if "T_K_Err" in my_input:
        myAmphs1['T_K_Err'] = my_input['T_K_Err']
        myPlags1['T_K_Err'] = my_input['T_K_Err']
        myOls1['T_K_Err'] = my_input['T_K_Err']
        myCPXs1['T_K_Err'] = my_input['T_K_Err']
        myOPXs1['T_K_Err'] = my_input['T_K_Err']
        mySps1['T_K_Err'] = my_input['T_K_Err']
        myLiquids1['T_K_Err'] = my_input['T_K_Err']

    return {'my_input_Err': my_input, 'Experimental_press_temp_Err': Experimental_press_temp1, 'Cpxs_Err': myCPXs1,
            'Opxs_Err': myOPXs1, 'Liqs_Err': myLiquids1, 'Plags_Err': myPlags1, 'Kspars_Err': myKspars1, 'Amps_Err': myAmphs1, 'Ols_Err': myOls1, 'Sps_Err': mySps1}


# Gets liquid dataframe into a format that can be used in VESical. Have to
# have VESIcal installed for the final step, which we do in the script for
# simplicity
def convert_to_vesical(liq_comps, T1):
    ''' Takes liquid dataframe in the format used for PyMME, and strips the _Liq string so that it can be input into VESical. Also removes the Fe3FeTcolumn, and appends temperature (converted from Kevlin to celcius)


   Parameters
    -------
    liq_comps: DataFrame
        DataFrame of liquid compositions.

    T1: Panda series, int, float
        Temperature in Kelvin (e.g., from a thermometer of choice)

   Returns
    -------
    DataFrame formatted so that it can be inputted into VESIcal.

    '''
    df = liq_comps.copy()
    df['Temp'] = T1 - 273.15
    df.drop('Fe3Fet_Liq', inplace=True, axis=1)
    df.columns = [str(col).replace('_Liq', '') for col in df.columns]
    return df


def convert_from_vesical(data):
    '''
    Takes liquid compositions from VESIcal, and converts it into a panda dataframe that can be inputted into the thermobaromety functions in PyMME

   Parameters
    -------
    data:
    VESIcal data formatted, obtained from myfile.get_Data

   Returns
    -------
    pandas dataframe formatted wtih column headings suitable for PyMME
    '''
    df = data.copy()
    df = df.rename(columns={col: col + '_Liq' for col in df.columns if col in
                            ['SiO2', 'TiO2', 'Al2O3', 'FeO', 'Fe2O3', 'MnO', 'MgO', 'CaO',
                             'K2O', 'Na2O', 'Cr2O3', 'P2O5', 'H2O', 'NiO']})
    df['FeOt_Liq'] = df['FeO_Liq'] + 0.8999998 * df['Fe2O3_Liq']
    df['Fe3Fet_Liq'] = df['Fe2O3_Liq'] * 1.111111 / \
        (df['Fe2O3_Liq'] * 1.111111 + df['FeO_Liq'])
    df['Sample_ID_Liq'] = df.index
    return df

