# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 15:41:59 2022

@author: Usuario
"""

import pandas as pd
import sklearn as sk
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import math

dir_path = os.path.dirname(os.path.realpath(__file__))
endir=os.path.join(dir_path,"Curves")

## Nombre de la curva

f="BPT.csv"
obj_f="BPT_Corr.csv"

#-Llamar la curva al código-
#--------------------------------------------------------------------------------------------------------------------
Prueba=pd.read_csv(os.path.join(endir,f),sep=";",decimal=",")

#-Aislar puntos de curva-
#--------------------------------------------------------------------------------------------------------------------
CurvDat=Prueba.iloc[9:]
Col_Name=CurvDat.iloc[0]
CurvDat.columns=Col_Name
CurvDat=CurvDat.iloc[1:]
CurvDat=CurvDat.replace(',','.',regex=True)
CurvDat=CurvDat.astype(float)
# x_Flux=CurvDat["BLS/h"].to_numpy()
# y_TDH_m=CurvDat["DP (m)"].to_numpy()

# #-Construir Modelos de regresión lineal polinómica-
# #--------------------------------------------------------------------------------------------------------------------
# poly=sk.preprocessing.PolynomialFeatures(degree=2,include_bias=False)
# poly_features=poly.fit_transform(x_Flux.reshape(-1,1))
# poly_reg_model=LinearRegression()
# poly_reg_model.fit(poly_features,y_TDH_m)

# #-Crear array con data para suavizado de modelos entrenados-
# #--------------------------------------------------------------------------------------------------------------------
# Min_Flux= getattr(x_Flux[0], "tolist", lambda: x_Flux[0])()
# Max_Flux= getattr(x_Flux[-1], "tolist", lambda: x_Flux[0])()
# step_Flux=(Max_Flux-Min_Flux)/1000
# x_Flux_plot=np.arange(Min_Flux,Max_Flux,step_Flux)
# poly_plot=poly.fit_transform(x_Flux_plot.reshape(-1,1))
# y_predicted=poly_reg_model.predict(poly_plot)
# y_predicted_change=poly_reg_model.predict(poly_features)

# #-Graficar Información Obtenida-
# #--------------------------------------------------------------------------------------------------------------------
# plt.figure(figsize=(10,6))
# plt.title("Prueba Gráfica Ventana Operativa",size=16)
# plt.xlabel("Flujo [BPH]", size="16")
# plt.ylabel("TDH [m]", size="16")
# plt.xlim(0,7000)
# plt.ylim(0,900)
# plt.scatter(x_Flux,y_TDH_m)
# plt.plot(x_Flux_plot,y_predicted, c="red")

# #-Proceso de corrección por viscosidad- Convertir en Función
# #--------------------------------------------------------------------------------------------------------------------
# K_Visc=16.5
# ##Tiene que ser un Input
# Real_Visc=50
# if Real_Visc<20:
#     Real_Vis=30
# Real_GE=0.92
# Real_GE=Real_GE*1e3

# ##Encontrar el TDH y Flujo con la eficiencia más alta de los datos base.
# max_value=max(CurvDat["EFFb (%)"])
# HBEP_m=CurvDat["DP (m)"][CurvDat[CurvDat["EFFb (%)"]==max_value].index.values[0]]
# QBEP_m3h=CurvDat["BLS/h"][CurvDat[CurvDat["EFFb (%)"]==max_value].index.values[0]]/6.28
# ##Conversión de Flujo de BPH a m3/h
# Q_m3h=CurvDat["BLS/h"]/6.28
# ##RPM de las Bombas tomado de archivo base
# N_Visc=float(Prueba["Unnamed: 1"][4])
# ##Coeficiente de corrección calculado
# B_Visc=K_Visc*(((Real_Visc**0.5)*(HBEP_m)**0.0625)/((QBEP_m3h**0.375)*N_Visc**0.25))
# Cq_Visc=pow(math.e,-0.165*pow(math.log10(B_Visc),3.15))
# Ch_Visc=1-(1-Cq_Visc)*(Q_m3h/QBEP_m3h)**0.75
# Ceff_Visc=pow(B_Visc,-0.0547*pow(B_Visc,0.69))
# ##Reemplazar todas las columnas del archivo csv
# CurvDat["DP (m)"]=CurvDat["DP (m)"]*Ch_Visc
# CurvDat["DP (psi)"]=CurvDat["DP (m)"]*Real_GE*9.81/1e3
# CurvDat["BLS/h"]=Q_m3h*Cq_Visc*6.28
# CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
# CurvDat["EFFb (%)"]=CurvDat["EFFb (%)"]*Ceff_Visc
# CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
# CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
# CurvDat.fillna(0)
# ##Introducir los datos al CSV y actualizarlo
# Prueba[10:]=CurvDat
# Prueba["Unnamed: 1"][2]=Real_Visc
# Prueba["Unnamed: 1"][3]=Real_GE
# Dir_Final=os.path.join(endir,obj_f)
# Prueba.to_csv(Dir_Final,sep=";",decimal=",",index=False)

# # #-Proceso de corrección por Diámetro del Impeller- Convertir en Función
# # #--------------------------------------------------------------------------------------------------------------------
# Real_Impeller=311.15
# Medida="mm"
# if Medida=="in":
#     Real_Impeller=Real_Impeller*25.4
# Prueba=Prueba.replace(',','.',regex=True)
# Actual_Impeller=float(Prueba["Unnamed: 1"][8])*25.4
# CurvDat["BLS/h"]=CurvDat["BLS/h"]*(Real_Impeller/Actual_Impeller)
# CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
# CurvDat["DP (m)"]=CurvDat["DP (m)"]*pow(Real_Impeller/Actual_Impeller,2)
# CurvDat["DP (psi)"]=CurvDat["DP (m)"]*(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
# CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
# CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
# CurvDat.fillna(0)
# ##Introducir los datos al CSV y actualizarlo
# Prueba[10:]=CurvDat
# Prueba["Unnamed: 1"][8]=Real_Impeller/25.4
# Dir_Final=os.path.join(endir,obj_f)
# Prueba.to_csv(Dir_Final,sep=";",decimal=",",index=False)

# # #-Proceso de corrección por Número de etapas- Convertir en Función
# # #--------------------------------------------------------------------------------------------------------------------
# Real_Stage=3
# Prueba=Prueba.replace(',','.',regex=True)
# Actual_Stage=float(Prueba["Unnamed: 1"][7])
# FC=(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
# CurvDat["DP (m)"]=CurvDat["DP (m)"]*(Real_Stage/Actual_Stage)
# CurvDat["DP (psi)"]=CurvDat["DP (m)"]*FC
# CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
# CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
# CurvDat.fillna(0)
# ##Introducir los datos al CSV y actualizarlo
# Prueba[10:]=CurvDat
# Prueba["Unnamed: 1"][7]=Real_Stage
# Dir_Final=os.path.join(endir,obj_f)
# Prueba.to_csv(Dir_Final,sep=";",decimal=",",index=False)

# # # #-Proceso de Cálculo de Variables par curvas de Bombas
# # # #--------------------------------------------------------------------------------------------------------------------
# Real_RPM= 3500
# Real_Flujo=4500
# Real_Flujo=np.array([Real_Flujo])
# Medida="psi"
# Actual_RPM=float(Prueba["Unnamed: 1"][4])
# #Corregir curvas por RPM de las Bombas
# CurvDat["BLS/h"]=CurvDat["BLS/h"]*(Real_RPM/Actual_RPM)
# CurvDat["BLS/día"]=CurvDat["BLS/h"]*24
# CurvDat["DP (m)"]=CurvDat["DP (m)"]*pow(Real_RPM/Actual_RPM,2)
# CurvDat["DP (psi)"]=CurvDat["DP (m)"]*(CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10]
# CurvDat["Ph (kW)"]=CurvDat["BLS/h"]*CurvDat["DP (psi)"]*6.891*0.16/3600
# CurvDat["Peje (kW)"]=CurvDat["Ph (kW)"]/CurvDat["EFFb (%)"]
# CurvDat.fillna(0)
# #-Aislar puntos de curva-
# #--------------------------------------------------------------------------------------------------------------------
# x_Flux=CurvDat["BLS/h"].to_numpy()
# if Medida=="psi":
#     y_TDH=CurvDat["DP (psi)"].to_numpy()
# else:
#     y_TDH=CurvDat["DP (m)"].to_numpy()
#     FC=float((CurvDat["DP (psi)"]/CurvDat["DP (m)"])[10])
# y_Eff=CurvDat["EFFb (%)"].to_numpy()
# #-Construir Modelos de regresión lineal polinómica para TDH-
# #--------------------------------------------------------------------------------------------------------------------
# poly=sk.preprocessing.PolynomialFeatures(degree=2,include_bias=False)
# poly_features=poly.fit_transform(x_Flux.reshape(-1,1))
# poly_reg_model=LinearRegression()
# poly_reg_model.fit(poly_features,y_TDH)
# #-Construir Modelos de regresión lineal polinómica para TDH-
# #--------------------------------------------------------------------------------------------------------------------
# poly_Eff=sk.preprocessing.PolynomialFeatures(degree=6,include_bias=False)
# poly_features_Eff=poly_Eff.fit_transform(x_Flux.reshape(-1,1))
# poly_reg_model_Eff=LinearRegression()
# poly_reg_model_Eff.fit(poly_features_Eff,y_Eff)
# #-Calcular valores estimados de TDH, Eficiencia, PH, Peje-
# #--------------------------------------------------------------------------------------------------------------------
# poly_TDH=poly.fit_transform(Real_Flujo.reshape(-1,1))
# poly_Eff=poly_Eff.fit_transform(Real_Flujo.reshape(-1,1))

# Predicted_TDH=poly_reg_model.predict(poly_TDH)
# Predicted_Eff=poly_reg_model_Eff.predict(poly_Eff)
# if Medida=="psi":
#     Predicted_PH=Predicted_TDH*Real_Flujo*6.891*0.16/3600
# else:
#     Predicted_PH=Predicted_TDH*Real_Flujo*6.891*0.16/3600*FC
# Predicted_Peje=Predicted_PH/Predicted_Eff
# Name_columns=['Flujo (BPH)','TDH (psi)','PH (kW)','Eff (%)','Peje (kW)']
# Results=[[float(Real_Flujo),float(Predicted_TDH),float(Predicted_PH),float(Predicted_Eff),float(Predicted_Peje)]]
# Results=pd.DataFrame(Results,columns=Name_columns)

##Función para calcular variables relevanetes para las BPT
# #--------------------------------------------------------------------------------------------------------------------

# #Se definen las variables de entrada para calcular cada una de las variables.
# Prueba=Prueba.replace(',','.',regex=True)
# Real_RPM=float(Prueba["Unnamed: 1"][4])
# Real_Visc=50
# Real_GE=0.92
# Real_Ps=102
# Real_Pd=1600

# Flujo_BPT=Real_RPM*CurvDat["a"][10]+Real_GE*CurvDat["d"][10]+Real_Ps*CurvDat["b"][10]+\
#     Real_Pd*CurvDat["c"][10]+CurvDat["e"][10]+(CurvDat["b1"][10]*(pow(Real_Visc,2)+CurvDat["b2"][10]*Real_Visc)/(pow(Real_Visc,2)+CurvDat["b3"][10]*Real_Visc+CurvDat["b4"][10]))
    
# Eff_v=Real_RPM*CurvDat["a"][11]+\
#     (CurvDat["d"][11]*(pow(Real_Visc,2)+CurvDat["e"][11]*Real_Visc)/(pow(Real_Visc, 2)+CurvDat["b1"][11]*Real_Visc+CurvDat["b2"][11])+Flujo_BPT*CurvDat["b"][11]+CurvDat["c"][11])
    
# Eff_m=CurvDat["a"][12]*pow(Eff_v,4)+CurvDat["b"][12]*pow(Eff_v,3)+CurvDat["c"][12]*pow(Eff_v,2)+CurvDat["d"][12]*Eff_v+CurvDat["e"][12]

# Eff_total=Eff_v*Eff_m