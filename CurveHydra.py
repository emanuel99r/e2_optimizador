# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 18:05:43 2022

@author: e2_Amorris
"""

import pandas as pd
import sklearn as sk
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import math
import joblib

#--FUNCIÓN CORRECCIÓN CURVAS POR VISCOSIDAD Y GE--
#--------------------------------------------------------------------------------------------------------------------   
def Visc_Change(f_name,end_name,Real_Visc,Real_GE):
    
#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Proceso de corrección por viscosidad-
#--------------------------------------------------------------------------------------------------------------------
    K_Visc=16.5    
    if Real_Visc<20:
        Real_Visc=30
    Real_GE=Real_GE*1e3
    ##Encontrar el TDH y Flujo con la eficiencia más alta de los datos base.
    max_value=max(CurvDat["EFFb (%)"])
    HBEP_m=CurvDat["DP (m)"][CurvDat[CurvDat["EFFb (%)"]==max_value].index.values[0]]
    QBEP_m3h=CurvDat["BLS/h"][CurvDat[CurvDat["EFFb (%)"]==max_value].index.values[0]]/6.28
    ##Conversión de Flujo de BPH a m3/h
    Q_m3h=CurvDat["BLS/h"]/6.28
    ##RPM de las Bombas tomado de archivo base
    N_Visc=float(Curve_DF["Unnamed: 1"][4])
    ##Coeficiente de corrección calculado
    B_Visc=K_Visc*(((Real_Visc**0.5)*(HBEP_m)**0.0625)/((QBEP_m3h**0.375)*N_Visc**0.25))
    Cq_Visc=pow(math.e,-0.165*pow(math.log10(B_Visc),3.15))
    Ch_Visc=1-(1-Cq_Visc)*(Q_m3h/QBEP_m3h)**0.75
    Ceff_Visc=pow(B_Visc,-0.0547*pow(B_Visc,0.69))
    ##Reemplazar todas las columnas del archivo csv
    CurvDat["DP (m)"]=CurvDat["DP (m)"]*Ch_Visc
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]/(1/((Real_GE*9.81/1e3)*0.1450377))
    CurvDat["BLS/h"]=Q_m3h*Cq_Visc*6.28
    CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
    CurvDat["EFFb (%)"]=CurvDat["EFFb (%)"]*Ceff_Visc
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    ##Introducir los datos al CSV y actualizarlo
    Curve_DF[10:]=CurvDat
    Curve_DF["Unnamed: 1"][2]=Real_Visc
    Curve_DF["Unnamed: 1"][3]=Real_GE
    Dir_Final=os.path.join(endir,end_name)
    Curve_DF.to_csv(Dir_Final,sep=";",decimal=',',index=False)

#--FUNCIÓN PARA CORREGIR EL TDH DEPENDIENDO DE GE--
# #--------------------------------------------------------------------------------------------------------------------
def ge_Change(f_name,end_name,Real_GE):

#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Proceso de corrección por GE-
#--------------------------------------------------------------------------------------------------------------------
    Curve_DF=Curve_DF.replace(',','.',regex=True)
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]*Real_GE/2.31*0.3048
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    ##Introducir los datos al CSV y actualizarlo
    Curve_DF[10:]=CurvDat
    Curve_DF["Unnamed: 1"][3]=Real_GE*1000
    Dir_Final=os.path.join(endir,end_name)
    Curve_DF.to_csv(Dir_Final,sep=";",decimal=',',index=False)    


#--FUNCIÓN PARA CORREGIR EL DIÁMETRO DEL IMPELLER DE LAS CURVAS DE BOMBAS--
# #--------------------------------------------------------------------------------------------------------------------
def Impeller_Change(f_name,end_name,Real_Impeller,Real_Medida="mm"):

#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Proceso de corrección por diámetro del impeller-
#--------------------------------------------------------------------------------------------------------------------
    if Real_Medida=="in":
        Real_Impeller=Real_Impeller*25.4
    Curve_DF=Curve_DF.replace(',','.',regex=True)
    Actual_Impeller=float(Curve_DF["Unnamed: 1"][8])*25.4
    CurvDat["BLS/h"]=CurvDat["BLS/h"]*(Real_Impeller/Actual_Impeller)
    CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
    FC=(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
    CurvDat["DP (m)"]=CurvDat["DP (m)"]*pow(Real_Impeller/Actual_Impeller,2)
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]*FC
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    ##Introducir los datos al CSV y actualizarlo
    Curve_DF[10:]=CurvDat
    Curve_DF["Unnamed: 1"][8]=Real_Impeller/25.4
    Dir_Final=os.path.join(endir,end_name)
    Curve_DF.to_csv(Dir_Final,sep=";",decimal=',',index=False)    

#--FUNCIÓN PARA CORREGIR EL DIÁMETRO DEL IMPELLER DE LAS CURVAS DE BOMBAS--
# #--------------------------------------------------------------------------------------------------------------------
def Stage_Change(f_name,end_name,Real_Stage):

#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)
    
#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    Curve_DF=Curve_DF.replace(',','.',regex=True)
    Actual_Stage=float(Curve_DF["Unnamed: 1"][7])
    FC=(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
    CurvDat["DP (m)"]=CurvDat["DP (m)"]*(Real_Stage/Actual_Stage)
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]*FC
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    ##Introducir los datos al CSV y actualizarlo
    Curve_DF[10:]=CurvDat
    Curve_DF["Unnamed: 1"][7]=Real_Stage
    Dir_Final=os.path.join(endir,end_name)
    Curve_DF.to_csv(Dir_Final,sep=";",decimal=',',index=False)

#--FUNCIÓN PARA CORREGIR LA CURVA CON CAMBIO DE RPM--
#--------------------------------------------------------------------------------------------------------------------   
def RPM_Change(f_name,end_name,Real_RPM):
    
#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)
    
#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------    
    Actual_RPM=float(Curve_DF["Unnamed: 1"][4])
    
#Corregir curvas por RPM de las Bombas
#--------------------------------------------------------------------------------------------------------------------
    CurvDat["BLS/h"]=CurvDat["BLS/h"]*(Real_RPM/Actual_RPM)
    CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
    CurvDat["DP (m)"]=CurvDat["DP (m)"]*pow(Real_RPM/Actual_RPM,2)
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]*(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    ##Introducir los datos al CSV y actualizarlo
    Curve_DF[10:]=CurvDat
    Curve_DF["Unnamed: 1"][4]=Real_RPM
    Dir_Final=os.path.join(endir,end_name)
    Curve_DF.to_csv(Dir_Final,sep=";",decimal=',',index=False)

#--FUNCIÓN CÁLCULO DE VARIABLES DE BOMBAS--
#--------------------------------------------------------------------------------------------------------------------   
def curve_calc(f_name,Real_Flujo,Real_RPM="N",Medida="psi"):

#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------    
    Real_Flujo=np.array([Real_Flujo])
    Actual_RPM=float(Curve_DF["Unnamed: 1"][4])
    if Real_RPM=="N":
        Real_RPM=Actual_RPM
#Corregir curvas por RPM de las Bombas
#--------------------------------------------------------------------------------------------------------------------
    CurvDat["BLS/h"]=CurvDat["BLS/h"]*(Real_RPM/Actual_RPM)
    CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
    FC=(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
    CurvDat["DP (m)"]=CurvDat["DP (m)"]*pow(Real_RPM/Actual_RPM,2)
    CurvDat["DP (psi)"]=CurvDat["DP (m)"]*FC
    CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
    CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
    CurvDat.fillna(0)
    
#Identificar BEP
#--------------------------------------------------------------------------------------------------------------------
    max_value=max(CurvDat["EFFb (%)"])
    QBEP=CurvDat["BLS/h"][CurvDat[CurvDat["EFFb (%)"]==max_value].index.values[0]]
    BEP_Percent=Real_Flujo/QBEP
#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    x_Flux=CurvDat["BLS/h"].to_numpy()
    if Medida=="psi":
        y_TDH=CurvDat["DP (psi)"].to_numpy()
    else:
        y_TDH=CurvDat["DP (m)"].to_numpy()
        FC=float((CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10])
    y_Eff=CurvDat["EFFb (%)"].to_numpy()
#-Construir Modelos de regresión lineal polinómica para TDH-
#--------------------------------------------------------------------------------------------------------------------
    poly=sk.preprocessing.PolynomialFeatures(degree=2,include_bias=False)
    poly_features=poly.fit_transform(x_Flux.reshape(-1,1))
    poly_reg_model=LinearRegression()
    poly_reg_model.fit(poly_features,y_TDH)
#-Construir Modelos de regresión lineal polinómica para TDH-
#--------------------------------------------------------------------------------------------------------------------
    poly_Eff=sk.preprocessing.PolynomialFeatures(degree=2,include_bias=False)
    poly_features_Eff=poly_Eff.fit_transform(x_Flux.reshape(-1,1))
    poly_reg_model_Eff=LinearRegression()
    poly_reg_model_Eff.fit(poly_features_Eff,y_Eff)
#-Calcular valores estimados de TDH, Eficiencia, PH, Peje-
#--------------------------------------------------------------------------------------------------------------------
    poly_TDH=poly.fit_transform(Real_Flujo.reshape(-1,1))
    poly_Eff=poly_Eff.fit_transform(Real_Flujo.reshape(-1,1))
    
    Predicted_TDH=poly_reg_model.predict(poly_TDH)
    Predicted_Eff=poly_reg_model_Eff.predict(poly_Eff)
    if Medida=="psi":
        Predicted_PH=Predicted_TDH*Real_Flujo*6.891*0.16/3600
    else:
        Predicted_PH=Predicted_TDH*Real_Flujo*6.891*0.16/3600*FC
    Predicted_Peje=Predicted_PH/Predicted_Eff
    if Medida=="psi":
        Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
    else:
        Name_columns=['Flujo (BPH)','TDH (m)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
    Results=[[float(Real_Flujo),float(Predicted_TDH),Real_RPM,float(Predicted_PH),float(Predicted_Eff),float(Predicted_Peje),float(BEP_Percent)]]
    Results=pd.DataFrame(Results,columns=Name_columns)
    return Results

#--FUNCIÓN CÁLCULO VARIABLES RELEVANTES PARA BPT--
#--------------------------------------------------------------------------------------------------------------------   
def bpt_calc(f_name,Real_Visc,Real_GE,Real_Ps,Real_Pd):
    
    #-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)
    
    #Se toma las RPM del archivo
#--------------------------------------------------------------------------------------------------------------------   
    Curve_DF=Curve_DF.replace(',','.',regex=True)    
    Real_RPM=float(Curve_DF["Unnamed: 1"][4])
    
    #Se calculan las variables relevantes
#--------------------------------------------------------------------------------------------------------------------   
    Flujo_BPT=Real_RPM*CurvDat["a"][10]+Real_GE*CurvDat["d"][10]+Real_Ps*CurvDat["b"][10]+\
        Real_Pd*CurvDat["c"][10]+CurvDat["e"][10]+(CurvDat["b1"][10]*(pow(Real_Visc,2)+CurvDat["b2"][10]*Real_Visc)/(pow(Real_Visc,2)+CurvDat["b3"][10]*Real_Visc+CurvDat["b4"][10]))       
    Eff_v=Real_RPM*CurvDat["a"][11]+\
        (CurvDat["d"][11]*(pow(Real_Visc,2)+CurvDat["e"][11]*Real_Visc)/(pow(Real_Visc, 2)+CurvDat["b1"][11]*Real_Visc+CurvDat["b2"][11])+Flujo_BPT*CurvDat["b"][11]+CurvDat["c"][11])       
    Eff_m=CurvDat["a"][12]*pow(Eff_v,4)+CurvDat["b"][12]*pow(Eff_v,3)+CurvDat["c"][12]*pow(Eff_v,2)+CurvDat["d"][12]*Eff_v+CurvDat["e"][12]   
    Eff_total=Eff_v*Eff_m
    TDH_BPT=(Real_Pd-Real_Ps)
    PH_BPT=(Real_Pd-Real_Ps)*Flujo_BPT*6.891*0.16/3600
    Peje_BPT=PH_BPT/Eff_total
    
    #Se guardan en dataframes
#--------------------------------------------------------------------------------------------------------------------   
    Results=[[float(Flujo_BPT),float(TDH_BPT),float(Real_RPM),float(PH_BPT),float(Eff_total),float(Peje_BPT)]]
    Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)']
    Results=pd.DataFrame(Results,columns=Name_columns)
    return Results

#--FUNCIÓN CALCULO DE PROPIEDADES DE MOTORES ELÉCTRICOS--
#--------------------------------------------------------------------------------------------------------------------   
def melec_calc(f_name,p_in,V_in=6550,Medida="kW"):
    
    #-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')
    Curve_DF=Curve_DF.replace(',','.',regex=True)
    
#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#Se ajustan las mediciones si son dadas en kW
#--------------------------------------------------------------------------------------------------------------------   
    if Medida!="kW":
        p_in=p_in*0.745
    
#Se calculan el factor de carga
#--------------------------------------------------------------------------------------------------------------------   
    
    P_nominal=float(Curve_DF["Unnamed: 1"][5])*0.745
    Factor_V=float(Curve_DF["Unnamed: 1"][7])
    
    F_Carga=p_in/P_nominal
    
#Se calculan las variables principales de motores eléctricos
#--------------------------------------------------------------------------------------------------------------------   

    Eff_Motor=CurvDat["a"][10]*(F_Carga**2+CurvDat["b"][10]*F_Carga)/(F_Carga**2+CurvDat["c"][10]*F_Carga+CurvDat["d"][10])
    FP_Motor=CurvDat["a"][11]*(F_Carga**2+CurvDat["b"][11]*F_Carga)/(F_Carga**2+CurvDat["c"][11]*F_Carga+CurvDat["d"][11])
    P_Salida_Motor=p_in/Eff_Motor
    Corr_Salida=P_Salida_Motor*1e3/(math.sqrt(3)*FP_Motor*V_in*Factor_V)

    #Se guardan en dataframes
#--------------------------------------------------------------------------------------------------------------------   

    Results=[[F_Carga,p_in,Eff_Motor,P_Salida_Motor,FP_Motor,Corr_Salida]]
    Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
    Results=pd.DataFrame(Results,columns=Name_columns)
    
    return Results

#--FUNCIÓN CALCULO DE PROPIEDADES DE VARIADORES DE VELOCIDAD MECÁNICOS--
#--------------------------------------------------------------------------------------------------------------------   
def varmec_calc(f_name,rpm_in):
    
    #-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')
    
#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Se aislan los puntos de las variables dependientes e independientes-
#--------------------------------------------------------------------------------------------------------------------
    rpm_nominal=float(Curve_DF["Unnamed: 1"][4])
    y_Eff=CurvDat["EFFcentrifugas"].to_numpy()
    x_speed=CurvDat["% speed"].to_numpy()
    
#-Se generan los modelos de regresión lineal para el cálclo aproxiumado de eficiencias-
#--------------------------------------------------------------------------------------------------------------------
    poly_reg_model=LinearRegression()
    poly_reg_model.fit(x_speed.reshape(-1,1),y_Eff)
    
#-Se calculan los estimados de eficiencia para estos variadores de velocidad-
#--------------------------------------------------------------------------------------------------------------------
    
    F_vel=np.array(rpm_in/rpm_nominal)
    F_vel=F_vel.reshape(-1,1)
    predicted_Eff=float(poly_reg_model.predict(F_vel))
    F_vel=float(F_vel)
    
    #Se guardan en dataframes
#--------------------------------------------------------------------------------------------------------------------   
    Results=[[F_vel,rpm_in,predicted_Eff]]
    Name_columns=['FCarga (%)','rpm_in','Eff_Var(%)']
    Results=pd.DataFrame(Results,columns=Name_columns)
    return Results
    
#--FUNCIÓN ESTIMACIÓN DE RPM BPC--
#--------------------------------------------------------------------------------------------------------------------   
def rpmvar_predicted(f_name,Real_Flujo,Real_TDH):
    
    #-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------    
    # Real_Flujo=np.array([Real_Flujo])
    Nominal_RPM=float(Curve_DF["Unnamed: 1"][4])
    
    #-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    x_Flux=CurvDat["BLS/h"].to_numpy()
    y_TDH=CurvDat["DP (psi)"].to_numpy()
     
    #-Construir Modelos de regresión lineal polinómica para TDH-
#--------------------------------------------------------------------------------------------------------------------
    poly=sk.preprocessing.PolynomialFeatures(degree=2,include_bias=False)
    poly_features=poly.fit_transform(x_Flux.reshape(-1,1))
    poly_reg_model=LinearRegression()
    poly_reg_model.fit(poly_features,y_TDH)
    
    #-cálculo de estimadores para calculadora rpm-
#--------------------------------------------------------------------------------------------------------------------    
    alpha=poly_reg_model.coef_[1]*(Real_Flujo**2)-Real_TDH
    betha=poly_reg_model.coef_[0]*Real_Flujo
    zetha=poly_reg_model.intercept_
    
    FC=(-betha-math.sqrt(betha**2-4*alpha*zetha))/(2*alpha)
    RPM_Real=float(Nominal_RPM/FC)

#     #-cálculo de variables de energía-
# #--------------------------------------------------------------------------------------------------------------------    
    
    Results=curve_calc(f_name,Real_Flujo,RPM_Real)
    
 
    #Se guardan en dataframes
#--------------------------------------------------------------------------------------------------------------------   
    return Results
    
#--FUNCIÓN ESTIMACIÓN DE DELTA P BB BPC-- SE SUGIERE CAMBIAR POR MODELOS DE ML Y GENERALIZAR MÁS LA FUNCIÓN
#--------------------------------------------------------------------------------------------------------------------   
def Covena_dp_bb(f_name,NBPT,NBPC,Real_Visc,Real_GE,Real_Flujo):
#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Delta_P")
    Curve_DF=pd.read_csv(os.path.join(endir,f_name),sep=";",decimal=',')

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)
    
#Se calcula el DP entre BB y BPC, teniendo en cuenta esta diferencia
#--------------------------------------------------------------------------------------------------------------------   
    DP_BB_BPC=CurvDat["N° BPT"][10]*NBPT+CurvDat["N° BPC"][10]*NBPC+CurvDat["Viscosidad"][10]*Real_Visc+CurvDat["GE (API)"][10]*Real_GE+CurvDat["Flujo"][10]*Real_Flujo+CurvDat["Intercepto"][10]
    
    return DP_BB_BPC

#--FUNCIÓN GENERACIÓN DE GRÁFICAS DE CURVAS DE BOMBAS--
#--------------------------------------------------------------------------------------------------------------------   
def Covena_Graph(Ub_fija,Num_fija,Ub_var,Num_var,Ub_Tor,Num_Tor,real_ps=102,BEP_min=0.74,BEP_max=1.14,rpm_min=3100,rpm_max=3560):
    #-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Curves")
    Curve_fija=pd.read_csv(os.path.join(endir,Ub_fija),sep=";",decimal=',')
    Curve_var=pd.read_csv(os.path.join(endir,Ub_var),sep=";",decimal=',')
    Curve_fija=Curve_fija.replace(',','.',regex=True)
    Curve_var=Curve_var.replace(',','.',regex=True)
    

#-Aislar puntos de curva fija-
#--------------------------------------------------------------------------------------------------------------------
    CurvFija=Curve_fija.iloc[9:]
    Col_Name=CurvFija.iloc[0]
    CurvFija.columns=Col_Name
    CurvFija=CurvFija.iloc[1:]
    CurvFija=CurvFija.astype(float)
    
    CurvVar=Curve_var.iloc[9:]
    Col_Name=CurvVar.iloc[0]
    CurvVar.columns=Col_Name
    CurvVar=CurvVar.iloc[1:]
    CurvVar=CurvVar.astype(float)
    
#-Encontrar BEP de cada una de las curvas-
#--------------------------------------------------------------------------------------------------------------------
    max_value=max(CurvFija["EFFb (%)"])
    QBEP_fija=CurvFija["BLS/h"][CurvFija[CurvFija["EFFb (%)"]==max_value].index.values[0]]
    min_flux_fija=QBEP_fija*BEP_min*Num_fija
    max_flux_fija=QBEP_fija*BEP_max *Num_fija   
    
    max_value=max(CurvVar["EFFb (%)"])
    QBEP_var=CurvVar["BLS/h"][CurvVar[CurvVar["EFFb (%)"]==max_value].index.values[0]]
    min_flux_var=QBEP_var*BEP_min*Num_var
    max_flux_var=QBEP_var*BEP_max*Num_var   
    
    min_flux_abs=max(min_flux_fija,min_flux_var)
    max_flux_abs=min(max_flux_fija,max_flux_var)
    
#-Definir la viscosidad y la GE de la operación-
#--------------------------------------------------------------------------------------------------------------------
    Real_Visc=float(Curve_fija["Unnamed: 1"][2])
    Real_GE=float(Curve_var["Unnamed: 1"][3])/1e3

#Crear matrices de cálculo dependiendo de tipo de arreglo.
#--------------------------------------------------------------------------------------------------------------------
#Operan todos los tipos de BP 

#--CASO FIJAS + VARIABLES--#
#--------------------------------------------------------------------------------------------------------------------            
    if (Num_fija>0 and Num_var>0):
        step_lateral=(max_flux_abs-min_flux_abs)/99
        Flux_Graph=np.arange(min_flux_abs,max_flux_abs+step_lateral,step_lateral)
        RPM_Graph=np.ones(len(Flux_Graph))*rpm_max
        step_lateral=(rpm_max-rpm_min)/48
        Aux_RPM=-np.sort(-np.arange(rpm_min,rpm_max,step_lateral))
        Aux_Flux_1=np.zeros(len(Aux_RPM))
        for x in range(len(Aux_RPM)):
            Aux_Flux_1[x]=Aux_RPM[x]/rpm_max*max_flux_abs
        RPM_Graph=np.append(RPM_Graph,Aux_RPM)
        Aux_RPM=np.ones(len(Flux_Graph))*rpm_min
        RPM_Graph=np.append(RPM_Graph,Aux_RPM)
        step_lateral=(rpm_max-rpm_min)/48
        Aux_RPM=np.arange(rpm_min,rpm_max,step_lateral)
        Aux_Flux_2=np.zeros(len(Aux_RPM))
        for x in range(len(Aux_RPM)):
            Aux_Flux_2[x]=Aux_RPM[x]/rpm_max*min_flux_abs
        RPM_Graph=np.append(RPM_Graph,Aux_RPM) 
        
        Aux_Flux_3=np.ones(len(Flux_Graph))*rpm_min/rpm_max
        Aux_Flux_3=Aux_Flux_3*Flux_Graph
        Aux_Flux_3=-np.sort(-Aux_Flux_3)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_1)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_3)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_2)
        
        PSI_Graph=np.zeros(len(Flux_Graph))
        
        for x in range(len(PSI_Graph)):
            calc_fija=curve_calc(Ub_fija,Flux_Graph[x]/Num_fija,RPM_Graph[x])
            calc_var=curve_calc(Ub_var,Flux_Graph[x]/Num_var,RPM_Graph[x])
            PSI_Graph[x]=calc_fija["TDH (psi)"][0]+calc_var["TDH (psi)"][0]+real_ps
            if Num_Tor>0:
                calc_tor=bpt_calc(Ub_Tor,Real_Visc,Real_GE,real_ps,float(PSI_Graph[x]))
                Flux_Graph[x]=Flux_Graph[x]+calc_tor["Flujo (BPH)"][0]*Num_Tor

#--CASO SOLO VARIABLES--#
#--------------------------------------------------------------------------------------------------------------------                            
    if (Num_fija==0 and Num_var>0):
        step_lateral=(max_flux_var-min_flux_var)/99
        Flux_Graph=np.arange(min_flux_var,max_flux_var+step_lateral,step_lateral)
        RPM_Graph=np.ones(len(Flux_Graph))*rpm_max
        step_lateral=(rpm_max-rpm_min)/48
        Aux_RPM=-np.sort(-np.arange(rpm_min,rpm_max,step_lateral))
        Aux_Flux_1=np.zeros(len(Aux_RPM))
        for x in range(len(Aux_RPM)):
            Aux_Flux_1[x]=Aux_RPM[x]/rpm_max*max_flux_var
        RPM_Graph=np.append(RPM_Graph,Aux_RPM)
        Aux_RPM=np.ones(len(Flux_Graph))*rpm_min
        RPM_Graph=np.append(RPM_Graph,Aux_RPM)
        step_lateral=(rpm_max-rpm_min)/48
        Aux_RPM=np.arange(rpm_min,rpm_max,step_lateral)
        Aux_Flux_2=np.zeros(len(Aux_RPM))
        for x in range(len(Aux_RPM)):
            Aux_Flux_2[x]=Aux_RPM[x]/rpm_max*min_flux_var
        RPM_Graph=np.append(RPM_Graph,Aux_RPM) 
        
        Aux_Flux_3=np.ones(len(Flux_Graph))*rpm_min/rpm_max
        Aux_Flux_3=Aux_Flux_3*Flux_Graph
        Aux_Flux_3=-np.sort(-Aux_Flux_3)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_1)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_3)
        Flux_Graph=np.append(Flux_Graph,Aux_Flux_2)
        
        PSI_Graph=np.zeros(len(Flux_Graph))
        
        for x in range(len(PSI_Graph)):
            calc_var=curve_calc(Ub_var,Flux_Graph[x]/Num_var,RPM_Graph[x])
            PSI_Graph[x]=calc_var["TDH (psi)"][0]+real_ps
            if Num_Tor>0:
                calc_tor=bpt_calc(Ub_Tor,Real_Visc,Real_GE,real_ps,float(PSI_Graph[x]))
                Flux_Graph[x]=Flux_Graph[x]+calc_tor["Flujo (BPH)"][0]*Num_Tor
        
#--CASO SOLO FIJAS--#
#--------------------------------------------------------------------------------------------------------------------
    if (Num_fija>0 and Num_var==0):
        RPM_Graph=np.ones(100)*rpm_max    
        step_lateral=(max_flux_fija-min_flux_fija)/99
        Flux_Graph=np.arange(min_flux_fija,max_flux_fija+step_lateral,step_lateral)        
        PSI_Graph=np.zeros(100)
        
        for x in range(len(PSI_Graph)):
            calc_fija=curve_calc(Ub_fija,Flux_Graph[x]/Num_fija,RPM_Graph[x])
            PSI_Graph[x]=calc_fija["TDH (psi)"][0]+real_ps
            if Num_Tor>0:
                calc_tor=bpt_calc(Ub_Tor,Real_Visc,Real_GE,real_ps,float(PSI_Graph[x]))
                Flux_Graph[x]=Flux_Graph[x]+calc_tor["Flujo (BPH)"][0]*Num_Tor
            
#--CASO SOLO TORNILLOS--#
#--------------------------------------------------------------------------------------------------------------------
    if (Num_fija==0 and Num_var==0 and Num_Tor>0):

        PSI_Graph=np.arange(real_ps,1640,10)
        Flux_Graph=np.zeros(len(PSI_Graph))
        RPM_Graph=np.ones(len(PSI_Graph))
        
        for x in range(len(PSI_Graph)):
            calc_tor=bpt_calc(Ub_Tor,Real_Visc,Real_GE,real_ps,float(PSI_Graph[x]))
            Flux_Graph[x]=Flux_Graph[x]+calc_tor["Flujo (BPH)"][0]*Num_Tor
            RPM_Graph[x]=calc_tor["Vel (RPM)"][0]

#--CASO ERROR--#
#--------------------------------------------------------------------------------------------------------------------            
    if (Num_fija==0 and Num_var==0 and Num_Tor==0):
            print("CÁLCULO NO POSIBLE")
            Flux_Graph=0
            PSI_Graph=0
            RPM_Graph=0
        
    return Flux_Graph, PSI_Graph, RPM_Graph

#--FUNCIÓN PARA DEFINIR NUMERO MÍNIMO DE BOMBAS PARA OPERAR EN UN RANGO DE FLUJO--
#--------------------------------------------------------------------------------------------------------------------   
def Num_CP(f_name,flux_B,RPM="N",BEP_min=0.74,BEP_max=1.14):
    Info_B=curve_calc(f_name,flux_B,RPM)
    flujo_min_B=(Info_B["Flujo (BPH)"][0]/Info_B["%BEP"][0])*BEP_min
    flujo_max_B=(Info_B["Flujo (BPH)"][0]/Info_B["%BEP"][0])*BEP_max
    if flux_B>=flujo_min_B:
        Num_B_max=math.floor(flux_B/flujo_min_B)
        Num_B_min=math.ceil(flux_B/flujo_max_B)
    else:
        Num_B_max=0
        Num_B_min=0
    
    return Num_B_max, Num_B_min, flujo_min_B, flujo_max_B


#--FUNCIÓN PARA CALCULAR LA CORRECCIÓN DE DP--
#--------------------------------------------------------------------------------------------------------------------   
def corr_dra(dp,ppm_act,ppm_proyec,m,b):
    if ppm_act==0:
        red_act=0
    else:
        red_act=1/(m*(1/ppm_act)+b)
    
    if ppm_proyec==0:
        red_proyec=0
    else:
        red_proyec=1/(m*(1/ppm_proyec)+b)
        
    if red_act==0:
        dp_base=dp
    else:
        dp_base=dp/(1-red_act/1e2)
        
    if red_proyec==0:
        dp_proyec=dp_base
    else:
        dp_proyec=dp_base*(1-red_proyec/1e2)
        
    return dp_proyec


#--FUNCIÓN PARA CORRECCIÓN DE COEFICIENTE M DEL DRA--
#--------------------------------------------------------------------------------------------------------------------   
def coef_adj_dra(v_in,ppm_in,dp_in,ppm_fin,dp_fin,calct="m"):
        
    dp_coef=dp_in/dp_fin
    
    if calct=="m":
        
        a_cor=pow(100,2)*(1/ppm_in)*(1/ppm_fin)*(dp_coef-1)
        b_cor=dp_coef*(pow(100,2)*v_in*(1/ppm_in+1/ppm_fin)-100*1/ppm_in)-(pow(100,2)*v_in*(1/ppm_in+1/ppm_fin)-100*1/ppm_fin)
        c_cor=100*v_in*(100*v_in-1)*(dp_coef-1)
        try:
            r1=(-b_cor+math.sqrt(b_cor**2-4*a_cor*c_cor))/(2*a_cor)
        except:
            r1=0
        try:
            r2=(-b_cor-math.sqrt(b_cor**2-4*a_cor*c_cor))/(2*a_cor)
        except:
            r2=0
        result=max(r1,r2)
    
    else:
        
        a_cor=pow(100,2)*(dp_coef-1)
        b_cor=100*(100*v_in*(1/ppm_in+1/ppm_fin)-1)*(dp_coef-1)
        c_cor=100*v_in*(1/ppm_in)*dp_coef*(100*v_in*(1/ppm_fin)-1)-100*v_in*(1/ppm_fin)*(100*v_in*(1/ppm_in)-1)
        
        try:
            r1=(-b_cor+math.sqrt(b_cor**2-4*a_cor*c_cor))/(2*a_cor)
        except:
            r1=0
        try:
            r2=(-b_cor-math.sqrt(b_cor**2-4*a_cor*c_cor))/(2*a_cor)
        except:
            r2=0
        result=max(r1,r2)            
    
    return result


#--FUNCIÓN PARA ENTRENAR MODELOS DE MACHINE LEARNING DE MANERA RÁPIDA--
#--------------------------------------------------------------------------------------------------------------------   

def save_rf_model(data_name,file_name,n_est=100):
    #-Llamar la curva al código-
    #--------------------------------------------------------------------------------------------------------------------    
    dir_path = os.getcwd()
    endir=os.path.join(dir_path,"Varios")
    Curve_DF=pd.read_csv(os.path.join(endir,data_name),sep=";",decimal=',')
    savedir=os.path.join(dir_path,"Delta_P")
    savedir=os.path.join(savedir,file_name)
    
    #-Aislar puntos de curva-
    #--------------------------------------------------------------------------------------------------------------------
    CurvDat=Curve_DF.iloc[9:]
    Col_Name=CurvDat.iloc[0]
    CurvDat.columns=Col_Name
    CurvDat=CurvDat.iloc[1:]
    CurvDat=CurvDat.set_index(CurvDat.columns[0])
    CurvDat=CurvDat.replace(',','.',regex=True)
    CurvDat=CurvDat.astype(float)
    
    
    x_regressor=CurvDat.iloc[:,1:].to_numpy()
    y_regressor=CurvDat.iloc[:,0].to_numpy()
    
    regressor = RandomForestRegressor(n_estimators = n_est, random_state = 0)
    
    # fit the regressor with x and y data
    regressor.fit(x_regressor, y_regressor)
    
    #Save file
    joblib.dump(regressor,savedir,compress=3)
    
#--FUNCIÓN PARA PREDECIR FUNCIONES DE MACHINE LEARNING PREVIAMENTE ENTRENADAS--
#--------------------------------------------------------------------------------------------------------------------   
def pred_rf_model(file_name,in_arra):
    
    dir_path = os.getcwd()
    savedir=os.path.join(dir_path,"Delta_P")
    savedir=os.path.join(savedir,file_name)
    
    rf=joblib.load(savedir)
    result=rf.predict(np.array(in_arra))
    
    return result

#--FUNCIÓN PARA GRAFICAR CURVA DE RENDIMIENTO DE DRA M Y B--
#--------------------------------------------------------------------------------------------------------------------   
def dra_graph(ppm_dra,m_dra,b_dra):
    
    red_act=np.zeros(50)
    for ppm_proyec in range(0,50):
        if ppm_proyec==0:
            red_act[ppm_proyec]=0
        else:
            red_act[ppm_proyec]=1/(m_dra*(1/ppm_proyec)+b_dra)/1e2
            
    ppm_proyec=np.array(range(50))
    if ppm_dra==0:
        red_real=0
    else:
        red_real=1/(m_dra*(1/ppm_dra)+b_dra)/1e2
        
    return ppm_proyec, red_act,red_real
    
    