# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, ctx
import dash_bootstrap_components as dbc
from suds.client import Client
import time
import pandas as pd
import plotly.graph_objects as go
import CurveHydra as e2
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pulp as p
from influxdb import InfluxDBClient
import os
import math
import dash_auth

date = time.strftime('%Y-%m-%d')

def trm(date):
    try:
        WSDL_URL = 'https://www.superfinanciera.gov.co/SuperfinancieraWebServiceTRM/TCRMServicesWebService/TCRMServicesWebService?WSDL'
        client = Client(WSDL_URL, location=WSDL_URL, faults=True)
        trm =  list(pd.DataFrame(client.service.queryTCRM(date))[1])[4]
    except Exception as e:
        return str(e)

    return trm

#_____________________________________
#        ENTRADAS DEL SIMULADOR

def Inputs(dbm):
    
        """
        
        *Los query vaciós reemplazar por 0
        
        -> 1 | Formato: ## | Flujo (BPC0000_COV_FI_1315Tbarril/h)
        -> 2 | Formato: ## | Visc  (BPC0000_COV_VMY_1650_cps)
        -> 3 | Formato: ## | API (BPC0000_COV_API60_1314)
        
        -> 4 | Formato: ## | NBB (NBB1 + NBB2 + NBB3 + NBB4 + NBB5 + NBB6 + NBB7)
        
        NBB1 = Si BPC0000_COV_BB_1401 = 1 y BPC0000_COV_PT_1401B_psi >= 75, 1, 0
        NBB2 = Si BPC0000_COV_BB_1402 = 1 y BPC0000_COV_PT_1402B_psi >= 75, 1, 0
        NBB3 = Si BPC0000_COV_BB_1403 = 1 y BPC0000_COV_PT_1403B_psi >= 75, 1, 0
        NBB4 = Si BPC0000_COV_BB_1404 = 1 y BPC0000_COV_PT_1404B_psi >= 75, 1, 0
        NBB5 = Si BPC0000_COV_BB_1405 = 1 y BPC0000_COV_PT_1405B_psi >= 75, 1, 0
        NBB6 = Si BPC0000_COV_BB_1406 = 1 y BPC0000_COV_PT_1406B_psi >= 75, 1, 0
        NBB7 = Si BPC0000_COV_BB_1407 = 1 y BPC0000_COV_PT_1407B_psi >= 75, 1, 0
        
        , last("BPC0000_COV_BB_1401") AS "BB_1401", last("BPC0000_COV_BB_1402") AS "BB_1402", last("BPC0000_COV_BB_1403") AS "BB_1403"
        , last("BPC0000_COV_BB_1404") AS "BB_1404", last("BPC0000_COV_BB_1405") AS "BB_1405", last("BPC0000_COV_BB_1406") AS "BB_1406"
        , last("BPC0000_COV_BB_1407") AS "BB_1407"
         
        "BB_1401"
        "BB_1404"
        "BB_1407"
        "BB_1402"
        "BB_1405"
        "BB_1403"
        "BB_1406"
        
        , last("BPC0000_COV_PT_1401B_psi") AS "PT_1401B_psi", last("BPC0000_COV_PT_1402B_psi") AS "PT_1402B_psi", last("BPC0000_COV_PT_1403B_psi") AS "PT_1403B_psi"
        , last("BPC0000_COV_PT_1404B_psi") AS "PT_1404B_psi", last("BPC0000_COV_PT_1405B_psi") AS "PT_1405B_psi", last("BPC0000_COV_PT_1406B_psi") AS "PT_1406B_psi"
        , last("BPC0000_COV_PT_1407B_psi") AS "PT_1407B_psi"
        
        "PT_1401B_psi"
        "PT_1404B_psi"
        "PT_1407B_psi"
        "PT_1402B_psi"
        "PT_1405B_psi"
        "PT_1403B_psi"
        "PT_1406B_psi"
        
        
        -> 5 | Formato: ## | NBPCV (NBPC1 + NBPCV2)
        
        NBPC1 = Si BPC0000_COV_BPC_14D0_ON = 1 y BPC0000_COV_ST_14D0_rpm > 2000, 1, 0 
        NBPC2 = Si BPC0000_COV_BPC_14E0_ON = 1 y BPC0000_COV_ST_14E0_rpm > 2000, 1, 0 
        
        , last("BPC0000_COV_BPC_14D0_ON") AS "BPC_14D0", last("BPC0000_COV_BPC_14E0_ON") AS "BPC_14E0"
        , last("BPC0000_COV_ST_14E0_rpm") AS "ST_14E0_rpm", last("BPC0000_COV_ST_14D0_rpm") AS "ST_14D0_rpm"
        
        "BPC_14D0"
        "BPC_14E0"
        "ST_14E0_rpm"
        "ST_14D0_rpm"
        
    
        -> 6 | Formato: ## | NBPCF
        
        NPCF =  Si Si BPC0000_COV_BPC_14B0_ON = 1 y (BPC0000_COV_PT_14B2_psi-BPC0000_COV_PI_1400A_psi)> 400, 1, 0
        
        , last("BPC0000_COV_BPC_14B0_ON") AS "BPC_14B0", last("BPC0000_COV_PT_14B2_psi") AS "PT_14B2_psi", last("BPC0000_COV_PI_1400A_psi") AS "PI_1400A_psi"
        
        "BPC_14B0"
        "PT_14B2_psi"
        "PI_1400A_psi"
    
        
        -> 7 | Formato: ## | NBPT (NBPT1 + NBPT2 + NBPT3 + NBPT4 + NBPT5 + NBPT6)
        
        NBPT1 = BPC0000_COV_MPE_1411 = 1 y BPC0000_COV_PT_1410B_psi > 400, 1, 0
        NBPT2 = BPC0000_COV_MPE_1421 = 1 y BPC0000_COV_PT_1420B_psi > 400, 1, 0
        NBPT3 = BPC0000_COV_MPE_1431 = 1 y BPC0000_COV_PT_1430B_psi > 400, 1, 0
        NBPT4 = BPC0000_COV_MPE_1441 = 1 y BPC0000_COV_PT_1440B_psi > 400, 1, 0
        NBPT5 = BPC0000_COV_MPE_1451 = 1 y BPC0000_COV_PT_1450B_psi > 400, 1, 0
        NBPT6 = BPC0000_COV_MPE_1461 = 1 y BPC0000_COV_PT_1460B_psi > 400, 1, 0
        
        , last("BPC0000_COV_MPE_1411") AS "MPE_1411", last("BPC0000_COV_MPE_1421") AS "MPE_1421", last("BPC0000_COV_MPE_1431") AS "MPE_1431"
        , last("BPC0000_COV_MPE_1441") AS "MPE_1441", last("BPC0000_COV_MPE_1451") AS "MPE_1451", last("BPC0000_COV_MPE_1461") AS "MPE_1461"
        
        "MPE_1411"
        "MPE_1441"
        "MPE_1421"
        "MPE_1451"
        "MPE_1431"
        "MPE_1461"
        
        
        , last("BPC0000_COV_PT_1410B_psi") AS "PT_1410B_psi", last("BPC0000_COV_PT_1420B_psi") AS "PT_1420B_psi", last("BPC0000_COV_PT_1430B_psi") AS "PT_1430B_psi"
        , last("BPC0000_COV_PT_1440B_psi") AS "PT_1440B_psi", last("BPC0000_COV_PT_1450B_psi") AS "PT_1450B_psi", last("BPC0000_COV_PT_1460B_psi") AS "PT_1460B_psi"
        
        "PT_1410B_psi"
        "PT_1440B_psi"
        "PT_1420B_psi"
        "PT_1450B_psi"
        "PT_1430B_psi"
        "PT_1460B_psi"
    
        
        -> 8 | Formato: ##,# | DRA_ppm (BPC0000_COV_FT_540_gal/h)
        -> 9 | Formato: ##,# | - (BPC0000_CTG_PIT_1502_psi)
        -> 10 | Formato: ##,# | Pd (BPC0000_COV_PI_1611_psi)
        -> 11 | Formato: $##,# | Tarifa_Elect
        -> 12 | Formato: $##,# | Tarifa_DRA
        -> 13 | Formato: ##,# | Ps_TK
        -> 14 | Formato: ##,# | -

        , last("BPC0000_COV_FT_540_gal/h") AS "draTotIN", last("BPC0000_CTG_PIT_1502_psi") AS "pRecIN", last("BPC0000_COV_PI_1611_psi") AS "pDesIN", last("Tarifa_Elect") AS "tarifaEleIN", last("Tarifa_DRA") AS "tarifaDRAIN", last("Ps_TK") AS "pBoosterIN"

        flujoIN=""
        viscocidadIN=""
        apiIN=""
        numUnidadesIN=""
        numEqpVarIN=""
        numEqpFijoIN=""
        numEqpParIN=""
        draTotIN=""
        pRecIN=""
        pDesIN=""
        tarifaEleIN=""
        tarifaDRAIN=""
        pBoosterIN=""
        vBPIN=""
        
        """
        
        dbname = dbm
        #Fecha='"2022-12-02T05:00:00.000Z" AND time <= "2022-12-02T04:59:59.000Z"'
        Fecha='now()-10m'
        queryVOP = f'SELECT last("BPC0000_COV_FT_540_gal/h") AS "draTotIN", last("BPC0000_CTG_PIT_1502_psi") AS "pRecIN", last("BPC0000_COV_PI_1611_psi") AS "pDesIN", last("Tarifa_Elect") AS "tarifaEleIN", last("Tarifa_DRA") AS "tarifaDRAIN", last("Ps_TK") AS "pBoosterIN", last("BPC0000_COV_FI_1315Tbarril/h") AS "flujoIN", last("BPC0000_COV_VMY_1650_cps") AS "viscocidadIN", last("BPC0000_COV_API60_1314") AS "apiIN" , last("BPC0000_COV_BB_1401") AS "BB_1401", last("BPC0000_COV_BB_1402") AS "BB_1402", last("BPC0000_COV_BB_1403") AS "BB_1403", last("BPC0000_COV_BB_1404") AS "BB_1404", last("BPC0000_COV_BB_1405") AS "BB_1405", last("BPC0000_COV_BB_1406") AS "BB_1406", last("BPC0000_COV_BB_1407") AS "BB_1407", last("BPC0000_COV_PT_1401B_psi") AS "PT_1401B_psi", last("BPC0000_COV_PT_1402B_psi") AS "PT_1402B_psi", last("BPC0000_COV_PT_1403B_psi") AS "PT_1403B_psi", last("BPC0000_COV_PT_1404B_psi") AS "PT_1404B_psi", last("BPC0000_COV_PT_1405B_psi") AS "PT_1405B_psi", last("BPC0000_COV_PT_1406B_psi") AS "PT_1406B_psi", last("BPC0000_COV_PT_1407B_psi") AS "PT_1407B_psi", last("BPC0000_COV_BPC_14D0_ON") AS "BPC_14D0", last("BPC0000_COV_BPC_14E0_ON") AS "BPC_14E0", last("BPC0000_COV_ST_14E0_rpm") AS "ST_14E0_rpm", last("BPC0000_COV_ST_14D0_rpm") AS "ST_14D0_rpm", last("BPC0000_COV_BPC_14B0_ON") AS "BPC_14B0", last("BPC0000_COV_PT_14B2_psi") AS "PT_14B2_psi", last("BPC0000_COV_PI_1400A_psi") AS "PI_1400A_psi", last("BPC0000_COV_MPE_1411") AS "MPE_1411", last("BPC0000_COV_MPE_1421") AS "MPE_1421", last("BPC0000_COV_MPE_1431") AS "MPE_1431", last("BPC0000_COV_MPE_1441") AS "MPE_1441", last("BPC0000_COV_MPE_1451") AS "MPE_1451", last("BPC0000_COV_MPE_1461") AS "MPE_1461", last("BPC0000_COV_PT_1410B_psi") AS "PT_1410B_psi", last("BPC0000_COV_PT_1420B_psi") AS "PT_1420B_psi", last("BPC0000_COV_PT_1430B_psi") AS "PT_1430B_psi", last("BPC0000_COV_PT_1440B_psi") AS "PT_1440B_psi", last("BPC0000_COV_PT_1450B_psi") AS "PT_1450B_psi", last("BPC0000_COV_PT_1460B_psi") AS "PT_1460B_psi" from "VOP" WHERE time >= {Fecha}' 
        client = InfluxDBClient(host="192.99.68.249", port="8086", database=dbname)
            
        resultVOP = client.query(queryVOP)
        #print(resultVOP)
        Input={}

        for item in resultVOP:
            
            Input["flujoIN"]=0 if item[0]["flujoIN"]==None else item[0]["flujoIN"]
            Input["viscocidadIN"]=0 if item[0]["viscocidadIN"]==None else item[0]["viscocidadIN"]
            Input["apiIN"]=0 if item[0]["apiIN"]==None else item[0]["apiIN"]
            
            #      BB

            NBB1=1 if item[0]["BB_1401"]==1 and item[0]["PT_1401B_psi"] >= 75 else 0
            NBB2=1 if item[0]["BB_1402"]==1 and item[0]["PT_1402B_psi"] >= 75 else 0
            NBB3=1 if item[0]["BB_1403"]==1 and item[0]["PT_1403B_psi"] >= 75 else 0
            NBB4=1 if item[0]["BB_1404"]==1 and item[0]["PT_1404B_psi"] >= 75 else 0
            NBB5=1 if item[0]["BB_1405"]==1 and item[0]["PT_1405B_psi"] >= 75 else 0
            NBB6=1 if item[0]["BB_1406"]==1 and item[0]["PT_1406B_psi"] >= 75 else 0
            NBB7=1 if item[0]["BB_1407"]==1 and item[0]["PT_1407B_psi"] >= 75 else 0
            
            NBB = NBB1+NBB2+NBB3+NBB4+NBB5+NBB6+NBB7
            Input["numUnidadesIN"]=NBB
            
            #      BPC Variable
            
            NBPC1=1 if item[0]["BPC_14D0"]==1 and item[0]["ST_14D0_rpm"] > 2000 else 0
            NBPC2=1 if item[0]["BPC_14E0"]==1 and item[0]["ST_14E0_rpm"] > 2000 else 0
            
            NBPCV=NBPC1 + NBPC2
            Input["numEqpVarIN"]=NBPCV
            
             #      BPC Fija
            
            NPCF=1 if item[0]["BPC_14B0"]==1 and (item[0]["PT_14B2_psi"]-item[0]["PI_1400A_psi"])>400 else 0
            Input["numEqpFijoIN"]=NPCF
            
             #      BPT
            
            NBPT1=1 if item[0]["MPE_1411"]==1 and item[0]["PT_1410B_psi"]>400 else 0
            NBPT2=1 if item[0]["MPE_1421"]==1 and item[0]["PT_1420B_psi"]>400 else 0
            NBPT3=1 if item[0]["MPE_1431"]==1 and item[0]["PT_1430B_psi"]>400 else 0
            NBPT4=1 if item[0]["MPE_1441"]==1 and item[0]["PT_1440B_psi"]>400 else 0
            NBPT5=1 if item[0]["MPE_1451"]==1 and item[0]["PT_1450B_psi"]>400 else 0
            NBPT6=1 if item[0]["MPE_1461"]==1 and item[0]["PT_1460B_psi"]>400 else 0
            
            NBPT=NBPT1+NBPT2+NBPT3+NBPT4+NBPT5+NBPT6
            Input["numEqpParIN"]=NBPT

            Input["draTotIN"]=0 if item[0]["draTotIN"]==None else item[0]["draTotIN"]
            Input["pRecIN"]=0 if item[0]["pRecIN"]==None else item[0]["pRecIN"]
            Input["pDesIN"]=0 if item[0]["pDesIN"]==None else item[0]["pDesIN"]
            Input["tarifaEleIN"]=0 if item[0]["tarifaEleIN"]==None else item[0]["tarifaEleIN"]
            Input["tarifaDRAIN"]=0 if item[0]["tarifaDRAIN"]==None else item[0]["tarifaDRAIN"]
            Input["pBoosterIN"]=0 if item[0]["pBoosterIN"]==None else item[0]["pBoosterIN"]
        
        
        print(Input)
            
        return Input


#---- (Ejecutas aquí la Inputs para actualizar al cargar :))-----------

Flujo_BHP=6800
Viscocidad_cSt=75
API=23
NumUndPar=7
CantEqpSerVar=1
CantEqpSerFij=1
CantEqpPar=3
DRAT=5
PREC=40
PRED=1597
TELE=547.7
TDRA=19.06
PSBOOSTER=12
VBP=6550

#--------------------------------------------------------------------------

app = Dash(__name__)
app.title = 'Optimizador - Simulador'


url='https://docs.google.com/spreadsheets/d/1kVNEr-0nzSIxBKyu2GpY_j4Un5OHjXCC0td1YGoCDFM/export?format=csv'
df=pd.read_csv(url)

Usuarios=df["Usuario"].tolist()
Contrasenas=df["Contraseña"].tolist()

VALID_USERNAME_PASSWORD_PAIRS={}

for i,usr in enumerate(Usuarios):
    VALID_USERNAME_PASSWORD_PAIRS[usr]=Contrasenas[i]


"""
VALID_USERNAME_PASSWORD_PAIRS = {
    'adminE2': 'adminE22022'
}
"""

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

fig1=go.Figure()
fig2=go.Figure()

#BG: #282D39
colors={
    'background':'#282D39',
    'text':'#D0CFCF',
    'titles':'White'
}

fig1.update_layout(

        showlegend=False,
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font_color=colors['titles'],
        title="Grafico 1"
)

fig1.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')
    
fig1.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')

fig1.update_layout(
             title={
                        'text': "Ventana Operativa",
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
            yaxis_title="Presión de Descarga [psi]",
            xaxis_title="Flujo [BPH]"
            )

fig2.update_layout(

        showlegend=False,
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font_color=colors['titles'],
        title="Grafico 2"
)

fig2.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')
    
fig2.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor='#8B8E95',
        gridcolor='#8B8E95')

fig2.update_layout(
             title={
                        'text': "Rendimiento DRA",
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
            yaxis_title="Rendimiento",
            xaxis_title="DRA (ppm)"
            )

Graficos=html.Div([

    dcc.Graph(id='Grafico1',figure=fig1,className="GraficoHijo", style={"visibility":"hidden"}),
    dcc.Graph(id='Grafico2',figure=fig2,className="GraficoHijo") #conflicto con la funcion de abajko de tarjetas

    ],className="GraficoPadre", id="Graficos")

Encabezados = html.Div(
                [
                html.Div(html.Img(src="https://cenit-transporte.com/wp-content/uploads/2017/07/cropped-cenit_logo-mob.png",className="icono3")),
                html.Div([html.Div("OPTIMIZADOR ENERGÉTICO", className="TituloMain", id="Titulo"),
                          html.Div("SISTEMA DE GESTIÓN ENERGÉTICA CENIT - E2 2022", className="SubTituloMain")]
                         ,className="Titulos"),
                
                dcc.Store(id='store-data', data=[], storage_type='memory'),
                dcc.Store(id='store-data2', data=[], storage_type='memory'),
                
                html.Div(html.Img(src="https://www.e2energiaeficiente.com/wp-content/uploads/2018/05/logo-e2-movil.png",className="icono3"))
                   
                ],className="Encabezados")
BPCFija=html.Div(
        [
            
    html.Div("BPC Fija",className="Result1"),
    html.Div(html.Img(src="/assets/Bomba.png",className="icono1")),
    html.Div("Variables de Interés",className="Result3"),
    
    html.Div([
        html.Div("#BPC F", className="textResult1"),
        html.Div(id='BPCF', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("BEP [%]", className="textResult1"),
        html.Div(id='BEP', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("FC Motor [%]", className="textResult1"),
        html.Div(id='FCMOTOR', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="EfiSelectedBPC",
    options={
             "EfEquipo":"Efi Equipo [%]",
             "EfMotor":"Efi Motor [%]",
             "EfVariador":"Efi Variador [%]",
             "EfConjunto":"Efi Conjunto [%]"
            },
        value="EfEquipo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='EFIEQP', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="ConsumoSelectedBPC",
    options={
             "Consumo":"Consumo [kWh]",
             "Corriente":"Corriente [A]"
            },
        value="Consumo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='CONEQP', className="textResul2")
            ],className="Result4")
    
        ],className="Result2")       
BPCVariable=html.Div(
        [
            
    html.Div("BPC Variable",className="Result1"),
    html.Div(html.Img(src="/assets/Bomba.png",className="icono1")),
    html.Div("Variables de Interés",className="Result3"),
    
    html.Div([
        html.Div("#BPC V", className="textResult1"),
        html.Div(id='BPCV', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("BEP [%]", className="textResult1"),
        html.Div(id='BEP2', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("FC Motor [%]", className="textResult1"),
        html.Div(id='FCMOTOR2', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("RPM", className="textResult1"),
        html.Div(id='RPM', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="EfiSelectedBPCVAR",
    options={
             "EfEquipo":"Efi Equipo [%]",
             "EfMotor":"Efi Motor [%]",
             "EfVariador":"Efi Variador [%]",
             "EfConjunto":"Efi Conjunto [%]"
            },
        value="EfEquipo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='EFIEQPVAR', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="ConsumoSelectedBPCVAR",
    options={
             "Consumo":"Consumo [kWh]",
             "Corriente":"Corriente [A]"
            },
        value="Consumo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='CONEQPVAR', className="textResul2")
            ],className="Result4")

        ],className="Result2")
BB=html.Div(
        [
            
    html.Div("BB",className="Result1"),
    html.Div(html.Img(src="/assets/Bomba.png",className="icono1")),
    html.Div("Variables de Interés",className="Result3"),
    
    html.Div([
        html.Div("#BB", className="textResult1"),
        html.Div(id='BB', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("BEP [%]", className="textResult1"),
        html.Div(id='BEP3', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("FC Motor [%]", className="textResult1"),
        html.Div(id='FCMOTOR3', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="EfiSelectedBB",
    options={
             "EfEquipo":"Efi Equipo [%]",
             "EfMotor":"Efi Motor [%]",
             "EfVariador":"Efi Variador [%]",
             "EfConjunto":"Efi Conjunto [%]"
            },
        value="EfEquipo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
    html.Div(id='EFEQPBB', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="ConsumoSelectedBB",
    options={
             "Consumo":"Consumo [kWh]",
             "Corriente":"Corriente [A]"
            },
        value="Consumo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='CONEQPBB', className="textResul2")
            ],className="Result4")

        ],className="Result2")
BPT=html.Div(
        [
    
    html.Div("BPT",className="Result1"),
    html.Div(html.Img(src="/assets/BPT.png",className="icono2")),
    html.Div("Variables de Interés",className="Result3"),
    
    html.Div([
        html.Div("#BPT", className="textResult1"),
        html.Div(id='BPT', className="textResul2")
            ],className="Result4"),
    
    html.Div([
        html.Div("FC Motor [%]", className="textResult1"),
        html.Div(id='FCMOTOR4', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="EfiSelectedBPT",
    options={
             "EfEquipo":"Efi Equipo [%]",
             "EfMotor":"Efi Motor [%]",
             "EfIncrementador":"Efi Incrementador [%]",
             "EfConjunto":"Efi Conjunto [%]"
            },
        value="EfEquipo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='EFEQPBPT', className="textResul2")
            ],className="Result4"),
    
    html.Div([dcc.Dropdown(id="ConsumoSelectedBPT",
    options={
             "Consumo":"Consumo [kWh]",
             "Corriente":"Corriente [A]"
            },
        value="Consumo",
        searchable=False,
        clearable=False,
        optionHeight=30,
        style={'width':'120px','background-color':'#a7a3a3','border':'none'},
            className="Select"),
        html.Div(id='CONEQPBPT', className="textResul2")
            ],className="Result4")

        ],className="Result2")
Costos= html.Div(
        [
            
    html.Div("Costos",className="Result1Costos"),
    html.Div(html.Img(src="https://i.ibb.co/7Js10z8/Recurso-1.png",className="icono1")),
    html.Div("Variables de Interés",className="Result3Costos"),
    
    html.Div([
        html.Div("Costo de DRA Base [COP/h]", className="textResult1"),
        html.Div(id='CDRA_B', className="textResul2Costos")
            ],className="Result4"),
    
    html.Div([
        html.Div("Costo de Energía Base [COP/h]", className="textResult1"),
        html.Div(id='CE_B', className="textResul2Costos")
            ],className="Result4"),
    
    html.Div([
        html.Div("Costo de Energía Total [COP/h]", className="textResult1"),
        html.Div(id='CE_R', className="textResul2Costos")
            ],className="Result4")

        ],className="Result2")
CostosR=html.Div(
        [
            html.Div(
            [
                html.Div("Costos Base",className="Result1Costos"),
                
                html.Div([
                html.Div("Costo de DRA Base [COP/h]", className="textResult1"),
                html.Div(id='CDRA_B', className="textResul2Costos")
                    ],className="Result4Costos"),
                
                html.Div([
                html.Div("Costo de Energía Base [COP/h]", className="textResult1"),
                html.Div(id='CE_B', className="textResul2Costos")
                    ],className="Result4Costos"),
    
                html.Div([
                html.Div("Costo de Energía Total [COP/h]", className="textResult1"),
                html.Div(id='CET_B', className="textResul2Costos")
                    ],className="Result4Costos")
                
                
            ], className="CostoHijo", id="CostoBase"),
            
            html.Div(
            [
            
                html.Div("Costos Optimos",className="Result1Costos"),
                
                html.Div([
                html.Div("Costo de DRA [COP/h]", className="textResult1"),
                html.Div(id='CDRA_O', className="textResul2Costos")
                    ],className="Result4Costos"),
                
                html.Div([
                html.Div("Costo de Energía [COP/h]", className="textResult1"),
                html.Div(id='CE_O', className="textResul2Costos")
                    ],className="Result4Costos"),
    
                html.Div([
                html.Div("Costo de Energía Total [COP/h]", className="textResult1"),
                html.Div(id='CET_O', className="textResul2Costos")
                    ],className="Result4Costos")
                
            ], className="CostoHijoOptimo", id="CostoOptimo")
            
        ],className="CostosR")
Restricciones=html.Div(
        [    
            
            html.Div("RESTRICCIONES",className="TituloRest1"),
            
            html.Div([
                
                    html.Div([
                        html.Div("BPC Fija",className="TituloRest")
                        ],className="RestSubG1"),
                    
                    html.Div([
                        html.Div(dcc.Checklist(
                            
                            ['14B0'],
                            ['14B0'],
                        
                            inline=True, id="C-BPCF", className="Check"))
                        
                            ],className="RestSubG2")
        
                ], className="RestGrupo"),
            
            html.Div([
                
                    html.Div([
                        html.Div("BPC Variable",className="TituloRest")
                        ],className="RestSubG1"),
                    
                    html.Div([
                        html.Div(dcc.Checklist(
                            
                            ['14D0', '14E0'],
                            ['14D0', '14E0'],
                        
                            inline=True, id="C-BPCV", className="Check"))
                        
                            ],className="RestSubG2") 
                ], className="RestGrupo"),
            
            html.Div([
                
                    html.Div([
                        html.Div("BB",className="TituloRest")
                        ],className="RestSubG11"),
                    
                    html.Div([
                        html.Div(dcc.Checklist(
                            
                            ['1401','1402','1403','1404','1405','1406','1407'],
                            ['1401','1402','1403','1404','1405','1406','1407'],
                        
                            inline=True, id="C-BB", className="Check")),
                        
                            ],className="RestSubG2")
                ], className="RestGrupo"),
            
            html.Div([
                
                    html.Div([
                        html.Div("BPT",className="TituloRest")
                        ],className="RestSubG11"),
                    
                    html.Div([
                        html.Div(dcc.Checklist(
                            
                            ['BPT 1410', 'BPT 1420', 'BPT 1430', 'BPT 1440', 'BPT 1450', 'BPT 1460'],
                            ['BPT 1410', 'BPT 1420', 'BPT 1430', 'BPT 1440', 'BPT 1450', 'BPT 1460'],
             
                            inline=True, id="C-BPT", className="Check"))
                        
                            ],className="RestSubG2")
                ], className="RestGrupo"),
            
                   
        ], className="Rest")
Botones=html.Div(
        [
            html.Button('Simular', id='btn-Simular', n_clicks=0, className="btn1"),
            html.Button('Optimizar', id='btn-Optimizar', n_clicks=0, className="btn2"),
            html.Button('Limpiar', id='btn-Limpiar', n_clicks=0, className="btn3"),
            html.Button('Detener', id='btn-Detener', n_clicks=0, className="btn4"),
        ], className="Buttons") 
Estado=html.Div([html.Div(id="EstadoID", className="Estado"),
                 html.Div(id="EstadoID2", className="Estado")
                 ], className="Estados"),
Loading=html.Div(
    [
            dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1"))
            
    ],className="LoadingBox")
AhorroTotal=html.Div(
        [
            html.Div([
            html.Div("Ahorro [%]", className="textResult1AhorroT"),
            html.Div(id='ahorroT', className="textResul2AhorroT")
            ],className="Result4AhorroT")
            
        ],className="CostosRTotal", id="ResultAhorroT")
Resultados=html.Div(
        children=
    [
        CostosR,
        AhorroTotal,
        BPCFija,
        BPCVariable,
        BB,
        BPT,
        Graficos
        
    ],className="Resultado")
Entradas=html.Div(

        children=
    [

        dcc.Store(id='store-data', data=[], storage_type='memory'),
        
        html.Div([
        html.Div("ENTRADAS",className="TituloRest3"),
        html.Button(" ",id='btn-Actualizar', n_clicks=0, className="btn-Actualizar"),
        ],className="TituloRest4"),

        html.Div([
        html.Div("Flujo [BPH]", className="textInput"),
        dcc.Input(id='flujo', value=Flujo_BHP, type='text', className="input")
                ], className="inputsBox"),

        html.Div([
        html.Div("Viscosidad [cSt]", className="textInput"),
        dcc.Input(id='viscocidad', value=Viscocidad_cSt, type='text', className="input")
        ], className="inputsBox"),

        html.Div([
        html.Div("°API", className="textInput"),
        dcc.Input(id='api', value=API, type='text', className="input")
        ], className="inputsBox"),

        html.Div([
        html.Div("Número de Unidades en Paralelo BB", className="textInput"),
        dcc.Input(id='numUnidades', value=NumUndPar, type='text', className="input")
        ], className="inputsBox"),

        html.Div([
        html.Div("Cantidad de Equipos Serie BPC Variable 14D0-14E0", className="textInput"),
        dcc.Input(id='numEqpVar', value=CantEqpSerVar, type='text', className="input")
        ], className="inputsBox"),
        
        html.Div([
        html.Div("Cantidad de Equipos Serie BPC Fija 14B0", className="textInput"),
        dcc.Input(id='numEqpFijo', value=CantEqpSerFij, type='text', className="input")
        ], className="inputsBox"),

        html.Div([
        html.Div("Cantidad de Equipos Paralelo BPT", className="textInput"),
        dcc.Input(id='numEqpPar', value=CantEqpPar, type='text', className="input")
        ], className="inputsBox"),
        
        html.Div([
        html.Div("DRA Total [PPM]", className="textInput"),
        dcc.Input(id='draTot', value=DRAT, type='text', className="input")
        ], className="inputsBox"),
        
        html.Div([
        html.Div("Presión Recibo Próxima Estación [PSIg]", className="textInput"),
        dcc.Input(id='pRec', value=PREC, type='text', className="input")
        ], className="inputsBox"),
        
        html.Div([
        html.Div("Presión de Despacho [PSIg]", className="textInput"),
        dcc.Input(id='pDes', value=PRED, type='text', className="input")
        ], className="inputsBox"),
        
        html.Div([
            html.Div(dcc.Checklist(id="OpcAvanzadas",className="Check",
                options=[{
                        "label":"Opciones Avanzadas",
                        "value": "OpcA"
                        }]))
                        
                ],className="OpcA-Input"),
        
        html.Div([
        html.Div("Tarifa Eléctrica [COP/kwh]", className="textInput"),
        dcc.Input(id='tarifaEle', value=TELE, type='text', className="input")
        ], className="inputsBox", id="tarifaEleA"),
        
        html.Div([
        html.Div("Tarifa DRA [USD/gal]", className="textInput"),
        dcc.Input(id='tarifaDRA', value=TDRA, type='text', className="input")
        ], className="inputsBox", id="tarifaDRAA"),
        
        html.Div([
        html.Div("Ps Booster [PSIg]", className="textInput"),
        dcc.Input(id='pBooster', value=PSBOOSTER, type='text', className="input")
        ], className="inputsBox", id="pBoosterA"),
        
        html.Div([
        html.Div("Voltaje BP [V]", className="textInput"),
        dcc.Input(id='vBP', value=VBP, type='text', className="input")
        ], className="inputsBox", id="vBPA"),
                
    ],className="Entradas", id="EntA")
Cuerpo = html.Div(
    [
                
        dbc.Row(
            [
                dbc.Col(Entradas),                                                    
                dbc.Col(Restricciones),
                dbc.Col(Botones),
                dbc.Col(Loading),                         
                dbc.Col(Estado)                         
            ]
        ),
        
        dbc.Row(
          [
              dbc.Col(Resultados)
          ]
        )

    ], className="Simulador", id="Simulador" )
Creditos = html.Div(
                [
                html.Div("Optimizador Energético - E2 Energía Eficiente S.A E.S.P",className="Creditos1"),
                html.Div("")
                   
                ],className="Creditos")

app.layout = dbc.Container([Encabezados,Cuerpo,Creditos], class_name="BoxMain")

#        CallBacks

#Calculos Principales
@app.callback(
    Output('BPCF', 'children'),
    Output('BEP', 'children'),
    Output('FCMOTOR', 'children'),
    Output('CDRA_B', 'children'),
    Output('CE_B', 'children'),
    Output('CET_B', 'children'),
    Output('CDRA_O', 'children'),
    Output('CE_O', 'children'),
    Output('CET_O', 'children'),
    Output('ahorroT', 'children'),
    Output('BPCV', 'children'),
    Output('BEP2', 'children'),
    Output('FCMOTOR2', 'children'),
    Output('RPM', 'children'),
    Output('BB', 'children'),
    Output('BEP3', 'children'),
    Output('FCMOTOR3', 'children'),
    Output('BPT', 'children'),
    Output('FCMOTOR4', 'children'),
    
    Output("loading-output-1", "children"),
    Output('Grafico1', 'figure'),
    Output('Grafico2', 'figure'),
    
    Output('flujo', 'value'),
    Output('viscocidad', 'value'),
    Output('api', 'value'),
    Output('numUnidades', 'value'),
    Output('numEqpVar', 'value'),
    Output('numEqpFijo', 'value'),
    Output('numEqpPar', 'value'),
    Output('draTot', 'value'),
    Output('pRec', 'value'),
    Output('pDes', 'value'),
    Output('tarifaEle', 'value'),
    Output('tarifaDRA', 'value'),
    Output('pBooster', 'value'),
    Output('vBP', 'value'),
    
    Output('EstadoID','children'),
    Output('EstadoID','style'),
    Output('EstadoID2','style'),
    
    Output("store-data2", "data"),
    
    Input("store-data", "data"),
    
    Input('BPCF', 'children'),
    Input('BEP', 'children'),
    Input('FCMOTOR', 'children'),
    Input('CDRA_B', 'children'),
    Input('CE_B', 'children'),
    Input('CET_B', 'children'),
    Input('CDRA_O', 'children'),
    Input('CE_O', 'children'),
    Input('CET_O', 'children'),
    Input('ahorroT', 'children'),
    Input('BPCV', 'children'),
    Input('BEP2', 'children'),
    Input('FCMOTOR2', 'children'),
    Input('RPM', 'children'),
    Input('BB', 'children'),
    Input('BEP3', 'children'),
    Input('FCMOTOR3', 'children'),
    Input('BPT', 'children'),
    Input('FCMOTOR4', 'children'),
    
    Input('btn-Simular', 'n_clicks'),
    Input('btn-Optimizar', 'n_clicks'),
    Input('btn-Limpiar', 'n_clicks'),
    Input('btn-Actualizar', 'n_clicks'),
    Input('btn-Detener', 'n_clicks'),
    
    Input('flujo', 'value'),
    Input('viscocidad', 'value'),
    Input('api', 'value'),
    Input('numUnidades', 'value'),
    Input('numEqpVar', 'value'),
    Input('numEqpFijo', 'value'),
    Input('numEqpPar', 'value'),
    Input('draTot', 'value'),
    Input('pRec', 'value'),
    Input('pDes', 'value'),
    Input('tarifaEle', 'value'),
    Input('tarifaDRA', 'value'),
    Input('pBooster', 'value'),
    Input('vBP', 'value'),
    
)
def update_output(Data,BPCF,BEP,FCMOTOR,CDRA_B, CE_B, CET_B,CDRA_O, CE_O, CET_O,AhorroT,BPCV,BEP2,FCMOTOR2, RPM,
                  BB,BEP3,FCMOTOR3,BPT,FCMOTOR4,
                  
                  Simular, Optimizar, Limpiar, Actualizar, Detener,
                  
                  flujo,viscocidad, api, numUnidades, numEqpVar, numEqpFijo, numEqpPar,
                  draTot, pRec, pDes, tarifaEle, tarifaDRA, pBooster, vBP
                  
                  ):


    flujoIN=flujo
    viscocidadIN=viscocidad
    apiIN=api
    numUnidadesIN=int(numUnidades)
    numEqpVarIN=int(numEqpVar)
    numEqpFijoIN=int(numEqpFijo)
    numEqpParIN=int(numEqpPar)
    draTotIN=draTot
    pRecIN=pRec
    pDesIN=pDes
    tarifaEleIN=tarifaEle
    tarifaDRAIN=tarifaDRA
    pBoosterIN=pBooster
    vBPIN=vBP
    EstadoID=""
    Est1={"display":"none"}
    Est2={"display":"flex"}
    
    Data2={}
    fig1.data=[]
    fig2.data=[]
    
    if "btn-Simular" == ctx.triggered_id:

        Flujo=float(flujo)
        Pd=float(pDes)
        Ps_TK=float(pBooster)
        Visc=float(viscocidad)
        API=float(api)
        NBB=numUnidades
        NBPCV=numEqpVar
        NBPCF=numEqpFijo
        NBPT=numEqpPar
        DRA_ppm=float(draTot)
        Tarifa_Elect=float(tarifaEle)
        Tarifa_DRA=float(tarifaDRA)
        TRM=trm(date)
        print("TRM: "+str(TRM))
        Tarifa_DRA=Tarifa_DRA*TRM

        GE=141.5/(131.5+API)
        

        ##Factores de ajuste --- Nominal a Real

        e2.Visc_Change("BPC.csv","BPC_var.csv",Visc,GE)
        e2.Visc_Change("BPC.csv","BPC_fija.csv",Visc,GE)
        e2.Visc_Change("BB.csv","BB_corr.csv",Visc,GE)

        e2.Impeller_Change("BPC_var.csv","BPC_var.csv",311.15)
        e2.Impeller_Change("BPC_fija.csv","BPC_fija.csv",323.85)

        e2.Stage_Change("BPC_fija.csv","BPC_fija.csv",3)

        e2.RPM_Change("BPC_fija.csv","BPC_fija.csv",3587)

        Flujo_BB=Flujo/NBB
        Info_BB=e2.curve_calc("BB_corr.csv",Flujo_BB)
        Info_BB_Mot=e2.melec_calc("Elect_Mot_BB.csv",Info_BB["Peje (kW)"][0])
        Consumo_BB=Info_BB_Mot["PotS (kW)"][0]*NBB

        DP_BPC_BB=e2.Covena_dp_bb("BB_BPC.csv",NBPT,NBPCV+NBPCF,Visc,GE,Flujo)

        Ps_BP=Ps_TK+Info_BB["TDH (psi)"]-DP_BPC_BB

        if NBPT>0:
            Info_BPT=e2.bpt_calc("BPT.csv",Visc,GE,Ps_BP,Pd)
            Eff_Incr=0.98
            Info_BPT_Mot=e2.melec_calc("Elect_Mot_BPT.csv",Info_BPT["Peje (kW)"][0]/Eff_Incr)
            Consumo_BPT=Info_BPT_Mot["PotS (kW)"][0]*NBPT
            Flujo_BPT_T=Info_BPT["Flujo (BPH)"][0]*NBPT
        else:
            Eff_Incr=0
            Consumo_BPT=0
            Flujo_BPT_T=0
            Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)']
            Info_BPT=[[0,0,0,0,0,0]]
            Info_BPT=pd.DataFrame(Info_BPT,columns=Name_columns)
            Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
            Info_BPT_Mot=[[0,0,0,0,0,0]]
            Info_BPT_Mot=pd.DataFrame(Info_BPT_Mot,columns=Name_columns)

        if NBPCV>0 or NBPCF>0:
            Flujo_BPC_T=Flujo-Flujo_BPT_T
            
            if NBPCF>0:
                Flujo_BPC_F=Flujo_BPC_T/NBPCF
                Info_BPCF=e2.curve_calc("BPC_fija.csv",Flujo_BPC_F)
                Info_BPCF_Mot=e2.melec_calc("Elect_Mot_BPC.csv",Info_BPCF["Peje (kW)"][0])
                Consumo_BPCF=Info_BPCF_Mot["PotS (kW)"][0]*NBPCF
                PD_BPCF=Info_BPCF["TDH (psi)"][0]
            else:
                Consumo_BPCF=0
                PD_BPCF=0
                Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
                Info_BPCF=[[0,0,0,0,0,0,0]]
                Info_BPCF=pd.DataFrame(Info_BPCF,columns=Name_columns)
                Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
                Info_BPCF_Mot=[[0,0,0,0,0,0]]
                Info_BPCF_Mot=pd.DataFrame(Info_BPCF_Mot,columns=Name_columns)
            
            if NBPCV>0:
                Flujo_BPC_V=Flujo_BPC_T/NBPCV
                TDH_BPCV=(Pd-Ps_BP)-PD_BPCF
                Info_BPCV=e2.rpmvar_predicted("BPC_var.csv",Flujo_BPC_V,TDH_BPCV)
                Info_BPCV_Var=e2.varmec_calc("Var_Hidr.csv",float(Info_BPCV["Vel (RPM)"][0]))
                Info_BPCV_Mot=e2.melec_calc("Elect_Mot_BPC.csv",float(Info_BPCV["Peje (kW)"][0]/Info_BPCV_Var["Eff_Var(%)"][0]))
                Consumo_BPCV=Info_BPCV_Mot["PotS (kW)"][0]*NBPCV
            else:
                Consumo_BPCV=0
                Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
                Info_BPCV=[[0,0,0,0,0,0,0]]
                Info_BPCV=pd.DataFrame(Info_BPCV,columns=Name_columns)
                Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
                Info_BPCV_Mot=[[0,0,0,0,0,0]]
                Info_BPCV_Mot=pd.DataFrame(Info_BPCV_Mot,columns=Name_columns)
                Name_columns=['FCarga (%)','rpm_in','Eff_Var(%)']
                Info_BPCV_Var=[[0,0,0]]
                Info_BPCV_Var=pd.DataFrame(Info_BPCV_Var,columns=Name_columns)

        Eff_ConjBB=Info_BB["Eff (%)"][0]*Info_BB_Mot["Eff_Mot (%)"][0]
        Eff_ConjBPCF=Info_BPCF["Eff (%)"][0]*Info_BPCF_Mot["Eff_Mot (%)"][0]
        Eff_ConjBPCV=Info_BPCV["Eff (%)"][0]*Info_BPCV_Mot["Eff_Mot (%)"][0]*Info_BPCV_Var["Eff_Var(%)"][0]
        Eff_ConjBPT=Info_BPT["Eff (%)"][0]*Info_BPT_Mot["Eff_Mot (%)"][0]*Eff_Incr

        Costo_EE=(Consumo_BPT+Consumo_BPCF+Consumo_BPCV+Consumo_BB)*Tarifa_Elect
        Costo_DRA=(DRA_ppm*Flujo)*42/1e6*Tarifa_DRA
        Costo_T=Costo_DRA+Costo_EE

        #--- GRAFICADORA DE VENTANA OPERATIVA---#
        Flux,TDH,RPM=e2.Covena_Graph("BPC_fija.csv",NBPCF,"BPC_var.csv",NBPCV,"BPT.csv",NBPT,real_ps=float(Ps_BP))
       
        data = {
        'Flujo':Flujo,
        'Pd':Pd,
        'Flux':Flux,
        'TDH':TDH
        }

        df = pd.DataFrame(data)

        fig1.data=[]

        fig1.add_trace(
            go.Line(x=df['Flux'], y=df['TDH'])
                    )

        fig1.add_trace(
            go.Scatter(
                mode="markers",
                x=df['Flujo'],
                y=df['Pd'],
                marker=dict(
                color='Red',
                size=10
                    )))
   
        fig1.update_layout(
             title={
                        'text': "Ventana Operativa",
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
            yaxis_title="Presión de Descarga [psi]",
            xaxis_title="Flujo [BPH]",
            yaxis_range=[max(min(TDH)-500,0),max(TDH)+500],
            xaxis_range=[max(min(Flux)-500,0),max(Flux)+500]
            )
        
        fig1.update_traces(line_color='gold')
        
        CDRA_B="$ {:,.2f}".format(Costo_DRA)
        CE_B="$ {:,.2f}".format(Costo_EE)
        CET_B="$ {:,.2f}".format(Costo_T)
        
        global Costo_TB
        Costo_TB=Costo_T   #Sino lo recibes en un callback aparte y actualizas?... o si lo halñas del sim y lo operas? XD
        
        Data3=0
   
        BPCF=NBPCF
        BEP="{:,.2f} %".format(round(Info_BPCF["%BEP"][0]*100,2))
        FCMOTOR="{:,.2f} %".format(round(Info_BPCF_Mot["FactorCarga (%)"][0]*100,2))
        #FCMOTOR="Error"
        EFIEQP="{:,.2f} %".format(round(Info_BPCF["Eff (%)"][0]*100,2))
        CONEQP="{:,.2f}".format(round(Consumo_BPCF,2))

        BPCV=NBPCV
        BEP2="{:,.2f} %".format(round(Info_BPCV["%BEP"][0]*100,2))
        FCMOTOR2="{:,.2f} %".format(round(Info_BPCV_Mot["FactorCarga (%)"][0]*100,2))
        RPM="{:,.2f}".format(round(Info_BPCV["Vel (RPM)"][0],2))
        #FCMOTOR2="Error"
        EFIEQPVAR="{:,.2f} %".format(round(Info_BPCV["Eff (%)"][0]*100,2))
        CONEQPVAR="{:,.2f}".format(round(Consumo_BPCV,2))

        
        BB=NBB
        BEP3="{:,.2f} %".format(round(Info_BB["%BEP"][0]*100,2))
        FCMOTOR3="{:,.2f} %".format(round(Info_BB_Mot["FactorCarga (%)"][0]*100,2))
        #FCMOTOR3="Error"
        EFEQPBB="{:,.2f} %".format(round(Info_BB["Eff (%)"][0]*100,2))
        CONEQPBB="{:,.2f}".format(round(Consumo_BB,2))
        
        BPT=NBPT
        FCMOTOR4="{:,.2f} %".format(round(Info_BPT_Mot["FactorCarga (%)"][0]*100,2))
        #FCMOTOR4="Error"
        EFEQPBPT="{:,.2f} %".format(round(Info_BPT["Eff (%)"][0]*100,2))
        CONEQPBPT="{:,.2f}".format(round(Consumo_BPT,2))
        
        #EstadoID="Simulación Terminada"
        EstadoID=""
        Est1={"display":"flex"}
        Est2={"display":"none"}
        
        EFIMOTBPCFIJA="{:,.2f} %".format(round(Info_BPCF_Mot["Eff_Mot (%)"][0]*100,2))
        EFICONBPCFIJA="{:,.2f} %".format(round(Eff_ConjBPCF,2)*100)
        CORRIENTEBPCFIJA="{:,.2f}".format(round(Info_BPCF_Mot["Corr (A)"][0],2))
        
        EFIMOTBPCVAR="{:,.2f} %".format(round(Info_BPCV_Mot["Eff_Mot (%)"][0]*100,2))
        EFICONBPCVAR="{:,.2f} %".format(round(Eff_ConjBPCV,2)*100)
        EFIVARBPCVAR="{:,.2f} %".format(round(Info_BPCV_Var["Eff_Var(%)"][0]*100))
        CORRIENTEBPCVAR="{:,.2f}".format(round(Info_BPCV_Mot["Corr (A)"][0],2))
        
        EFIMOTBB="{:,.2f} %".format(round(Info_BB_Mot["Eff_Mot (%)"][0]*100,2))
        EFICONBB="{:,.2f} %".format(round(Eff_ConjBB,2)*100)
        CORRIENTEBB="{:,.2f}".format(round(Info_BB_Mot["Corr (A)"][0],2))
        
        EFIMOTBPT="{:,.2f} %".format(round(Info_BPT_Mot["Eff_Mot (%)"][0]*100,2))
        EFICONBPT="{:,.2f} %".format(round(Eff_ConjBPT,2)*100)
        CORRIENTEBPT="{:,.2f} %".format(round(Info_BPT_Mot["Corr (A)"][0],2))
        EFIINCBPT="{:,.2f}".format(round(Eff_Incr*100,2))
        
        Data2["EfiEquipo BPC Fija"]=EFIEQP
        Data2["EfiMotor BPC Fija"]=EFIMOTBPCFIJA                 
        Data2["EfiVariador BPC Fija"]="NA"          #ND
        Data2["EfiConjunto BPC Fija"]=EFICONBPCFIJA          
        Data2["Consumo BPC Fija"]=CONEQP
        Data2["Corriente BPC Fija"]=CORRIENTEBPCFIJA            
        
        Data2["EfiEquipo BPC Variable"]=EFIEQPVAR
        Data2["EfiMotor BPC Variable"]= EFIMOTBPCVAR             
        Data2["EfiVariador BPC Variable"]=EFIVARBPCVAR      
        Data2["EfiConjunto BPC Variable"]=EFICONBPCVAR      
        Data2["Consumo BPC Variable"]=CONEQPVAR
        Data2["Corriente BPC Variable"]=CORRIENTEBPCVAR        
        
        Data2["EfiEquipo BB"]=EFEQPBB
        Data2["EfiMotor BB"]= EFIMOTBB                       
        Data2["EfiVariador BB"]="NA"              
        Data2["EfiConjunto BB"]=EFICONBB              
        Data2["Consumo BB"]=CONEQPBB
        Data2["Corriente BB"]=CORRIENTEBB               
        
        Data2["EfiEquipo BPT"]=EFEQPBPT
        Data2["EfiMotor BPT"]= EFIMOTBPT                      
        Data2["EfiIncrementador BPT"]=EFIINCBPT         
        Data2["EfiConjunto BPT"]=EFICONBPT              
        Data2["Consumo BPT"]=CONEQPBPT
        Data2["Corriente BPT"]=CORRIENTEBPT                
        
        
        """     MAPA DE VARIABLES
        -> 1 | Formato: $##.###.###,## | Costo_DRA
        -> 2 | Formato: $##.###.###,## | Costo_EE
        -> 3 | Formato: $##.###.###,## | Costo_T
        -> 4 | Formato: ## | NBPCF
        -> 5 | Formato: ##,## % | Info_BPCF["%BEP"][0]*100
        -> 6 | Formato: ##,## % | Info_BPCF_Mot["FactorCarga(%)"][0]*100
        -> 7 | Formato: ##,## % | Info_BPCF["Eff (%)"][0]*100
        -> 8 | Formato: ##.##,## | Consumo_BPCF
        -> 9 | Formato: ## | NBPCV
        -> 10 | Formato: ##,## % | Info_BPCV["%BEP"][0]*100
        -> 11 | Formato: ##,## % | Info_BPCV_Mot["FactorCarga(%)"][0]*100
        -> 12 | Formato: ##,## % | Info_BPCV["Eff (%)"][0]*100
        -> 13 | Formato: ##.##,## | Consumo_BPCV
        -> 14 | Formato: ## | NBB
        -> 15 | Formato: ##,## % | Info_BB["%BEP"][0]*100
        -> 16 | Formato: ##,## % | Info_BB_Mot["FactorCarga(%)"][0]*100
        -> 17 | Formato: ##,## % | Info_BB["Eff (%)"][0]*100
        -> 18 | Formato: ##.##,## | Consumo_BB
        -> 19 | Formato: ## | NBPT
        -> 20 | Formato: ##,## % | Info_BPT_Mot["FactorCarga(%)"][0]*100
        -> 21 | Formato: ##,## % | Info_BPT["Eff (%)"][0]*100 | Se debe corregir. No es eficiencia del intercambiador es eficiencia del equipo
        -> 22 | Formato: ##.##,## | Consumo_BPT
        """
    
    elif "btn-Optimizar" == ctx.triggered_id:
        
        ##Se utiliza para medir el tiempo que tarda el código en correr
        
        start = time.time()
        print("e2 - Simulador se ha Iniciado")


        ##---Inputs necesarios para realizar el proceso de optimización---##

        Flujo=float(flujo)
        Pd_in=1500                     #NP
        Ps_TK=float(pBooster)
        Visc=float(viscocidad)
        API=float(api)
        DRA_ppm=float(draTot)
        Pr_CTG=40                       #NP

        ##--Los inputs económicos

        Tarifa_Elect=float(tarifaEle)
        Tarifa_DRA=float(tarifaDRA)
        TRM=trm(date)
        print("TRM: "+str(TRM))
        Tarifa_DRA=Tarifa_DRA*TRM

        ##--Los inputs económicos

        it=0                            #NP
        it_true=0                       #NP
        it_op=0                         #NP
        Costo_T_opt=1e9                 #NP

        ##--Los inputs económicos

        m_Cov=0.1207                    #NP
        b_Cov=0.0145                    #NP

        ##--Los inputs económicos

        pace=0.5                        #NP (Números racionales - Paso DRA (Opc. Avanzadas = 0.5))
        tol=5                           #NP    5
    
        ##--Los inputs económicos

        GE=141.5/(131.5+API)
        DRA_ppm=max(0,math.floor(DRA_ppm))

        dir_path = os.getcwd()
        endir=os.path.join(dir_path,"Optimizador")
        Limits=pd.read_csv(os.path.join(endir,"Limites.csv"),sep=";",decimal=',')


        ##Establecer Número máximo de equipos
        
        in_Num_max_BB=Data["Num BB"]
        in_Num_max_BPT=Data["Num BPT"]
        in_Num_max_BPCV=Data["Num BPC-V"]
        in_Num_max_BPCF=Data["Num BPC-F"]


        if DRA_ppm>0:
            
            DRA_table=pd.read_csv(os.path.join(endir,"DRA.csv"),sep=";",decimal=',')

            DRA_table=DRA_table.iloc[9:]
            N_Col=DRA_table.iloc[0]
            DRA_table.columns=N_Col
            DRA_table=DRA_table.iloc[1:]
            DRA_table=DRA_table.replace(',','.',regex=True)
            DRA_table=DRA_table.astype(float)
            
            for i in range(len(DRA_table)):
                if Flujo<DRA_table[DRA_table.columns[0]][DRA_table.index[i]]:
                    DRA_base=DRA_table[DRA_table.columns[1]][DRA_table.index[i-1]]
                    break
                elif i==len(DRA_table)-1:
                    DRA_base=DRA_table[DRA_table.columns[1]][DRA_table.index[-1]]
                    
            dp_base=e2.pred_rf_model("COV_CTG.joblib",[[Flujo,GE,Visc,GE]])
            
            if e2.coef_adj_dra(b_Cov,DRA_ppm,Pd_in-Pr_CTG,DRA_base,dp_base,"m")>0:
                m_Cov=e2.coef_adj_dra(b_Cov,DRA_ppm,Pd_in-Pr_CTG,DRA_base,dp_base)

        e2.Visc_Change("BPC.csv","BPC_var.csv",Visc,GE)
        e2.Visc_Change("BPC.csv","BPC_fija.csv",Visc,GE)
        e2.Visc_Change("BB.csv","BB_corr.csv",Visc,GE)

        e2.Impeller_Change("BPC_var.csv","BPC_var.csv",311.15)
        e2.Impeller_Change("BPC_fija.csv","BPC_fija.csv",323.85)

        e2.Stage_Change("BPC_fija.csv","BPC_fija.csv",3)

        e2.RPM_Change("BPC_fija.csv","BPC_fija.csv",3587)

        Loop_BB=e2.Num_CP("BB_corr.csv",Flujo)
        Num_min_BB=max(0,Loop_BB[1])
        Num_max_BB=min(in_Num_max_BB,Loop_BB[0])

        if Num_max_BB<Num_min_BB:
            Num_max_BB=Num_min_BB

        xs = (x * pace for x in range(DRA_ppm*int(1/pace), (25+1)*int(1/pace)))

        for NBB in range (Num_min_BB,Num_max_BB+1): 
            
            Flujo_BB=Flujo/NBB
            Info_BB=e2.curve_calc("BB_corr.csv",Flujo_BB)
            Info_BB_Mot=e2.melec_calc("Elect_Mot_BB.csv",Info_BB["Peje (kW)"][0])
            Consumo_BB=Info_BB_Mot["PotS (kW)"][0]*NBB
            
            DP_BPC_BB_aux=e2.Covena_dp_bb("BB_BPC.csv",1,1,Visc,GE,Flujo)
            
            Ps_BP=Ps_TK+Info_BB["TDH (psi)"]-DP_BPC_BB_aux   


            for ppm_proyec in xs:
                
                # print(ppm_proyec)
                
                Pd=e2.corr_dra(Pd_in-Pr_CTG,DRA_ppm,ppm_proyec,m_Cov,b_Cov)+Pr_CTG
            
                
                for NBPT in range(0,in_Num_max_BPT+1):
                    
                    if NBPT>0:
                        Info_BPT=e2.bpt_calc("BPT.csv",Visc,GE,Ps_BP,Pd)
                        Eff_Incr=0.98
                        Info_BPT_Mot=e2.melec_calc("Elect_Mot_BPT.csv",Info_BPT["Peje (kW)"][0]/Eff_Incr)
                        Consumo_BPT=Info_BPT_Mot["PotS (kW)"][0]*NBPT
                        Flujo_BPT_T=Info_BPT["Flujo (BPH)"][0]*NBPT
                    else:
                        Consumo_BPT=0
                        Flujo_BPT_T=0
                    
                    Flujo_BPC_T=Flujo-Flujo_BPT_T
                    
                    Loop_BPCF=e2.Num_CP("BPC_fija.csv",Flujo_BPC_T)
                    Num_min_BPCF=max(0,Loop_BPCF[1])
                    Num_max_BPCF=min(in_Num_max_BPCF,Loop_BPCF[0])
                    if Num_max_BPCF<Num_min_BPCF:
                        Num_max_BPCF=Num_min_BPCF
                    
                    Loop_BPCV_mrpm=e2.Num_CP("BPC_var.csv",Flujo,3100)
                    Num_max_BPCV=min(in_Num_max_BPCV,Loop_BPCV_mrpm[0])
                    Loop_BPCV_mrpm=e2.Num_CP("BPC_var.csv",Flujo,3560)
                    Num_min_BPCV=min(0,Loop_BPCV_mrpm[1])
                    if Num_max_BPCV<Num_min_BPCV:
                        Num_max_BPCV=Num_min_BPCV
                    
                    for NBPCF in range(Num_min_BPCF,Num_max_BPCF+1):
                        
                        for NBPCV in range(Num_min_BPCV,Num_max_BPCV+1):
                            
                            Cumpl_BB=False
                            Cumpl_BPCV=False
                            Cumpl_BPCF=False
                            Cumpl_BPT=False
                            Cumpl_Flux=False
                            
                            if ((Flujo_BPC_T>0 and (NBPCF+NBPCV>0))or(Flujo_BPC_T==0 and NBPCF+NBPCV==0)):
                                
                                try:
                                    DP_BPC_BB=e2.Covena_dp_bb("BB_BPC.csv",NBPT,NBPCF+NBPCV,Visc,GE,Flujo)
                                    
                                    Ps_BP=Ps_TK+Info_BB["TDH (psi)"]-DP_BPC_BB_aux
                                    PD_BB=float(Ps_TK+Info_BB["TDH (psi)"])
                                    
                                    if NBPT>0:
                                        Info_BPT=e2.bpt_calc("BPT.csv",Visc,GE,Ps_BP,Pd)
                                        Eff_Incr=0.98
                                        Info_BPT_Mot=e2.melec_calc("Elect_Mot_BPT.csv",Info_BPT["Peje (kW)"][0]/Eff_Incr)
                                        Consumo_BPT=Info_BPT_Mot["PotS (kW)"][0]*NBPT
                                        Flujo_BPT_T=Info_BPT["Flujo (BPH)"][0]*NBPT
                                    else:
                                        Eff_Incr=0
                                        Consumo_BPT=0
                                        Flujo_BPT_T=0
                                        Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)']
                                        Info_BPT=[[0,0,0,0,0,0]]
                                        Info_BPT=pd.DataFrame(Info_BPT,columns=Name_columns)
                                        Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
                                        Info_BPT_Mot=[[0,0,0,0,0,0]]
                                        Info_BPT_Mot=pd.DataFrame(Info_BPT_Mot,columns=Name_columns)
                                    
                                    
                                    Flujo_BPC_T=Flujo-Flujo_BPT_T
                                    
                                    if NBPCF>0:
                                        Flujo_BPC_F=Flujo_BPC_T/NBPCF
                                        Info_BPCF=e2.curve_calc("BPC_fija.csv",Flujo_BPC_F)
                                        Info_BPCF_Mot=e2.melec_calc("Elect_Mot_BPC.csv",Info_BPCF["Peje (kW)"][0])
                                        Consumo_BPCF=Info_BPCF_Mot["PotS (kW)"][0]*NBPCF
                                    else:
                                        Consumo_BPCF=0
                                        Flujo_BPC_F=0
                                        Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
                                        Info_BPCF=[[0,0,0,0,0,0,0]]
                                        Info_BPCF=pd.DataFrame(Info_BPCF,columns=Name_columns)
                                        Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
                                        Info_BPCF_Mot=[[0,0,0,0,0,0]]
                                        Info_BPCF_Mot=pd.DataFrame(Info_BPCF_Mot,columns=Name_columns)
                                    
                                    if NBPCV>0:
                                        Flujo_BPC_V=Flujo_BPC_T/NBPCV
                                        TDH_BPCV=(Pd-Ps_BP)-Info_BPCF["TDH (psi)"][0]
                                        Info_BPCV=e2.rpmvar_predicted("BPC_var.csv",Flujo_BPC_V,TDH_BPCV)
                                        Info_BPCV_Var=e2.varmec_calc("Var_Hidr.csv",float(Info_BPCV["Vel (RPM)"][0]))
                                        Info_BPCV_Mot=e2.melec_calc("Elect_Mot_BPC.csv",float(Info_BPCV["Peje (kW)"][0]/Info_BPCV_Var["Eff_Var(%)"][0]))
                                        Consumo_BPCV=Info_BPCV_Mot["PotS (kW)"][0]*NBPCV
                                    else:
                                        Consumo_BPCV=0
                                        Flujo_BPC_V=0
                                        Name_columns=['Flujo (BPH)','TDH (psi)','Vel (RPM)','PH (kW)','Eff (%)','Peje (kW)','%BEP']
                                        Info_BPCV=[[0,0,0,0,0,0,0]]
                                        Info_BPCV=pd.DataFrame(Info_BPCV,columns=Name_columns)
                                        Name_columns=['FactorCarga (%)','PotEn (kW)','Eff_Mot (%)','PotS (kW)','FP (%)','Corr (A)']
                                        Info_BPCV_Mot=[[0,0,0,0,0,0]]
                                        Info_BPCV_Mot=pd.DataFrame(Info_BPCV_Mot,columns=Name_columns)
                                        Name_columns=['FCarga (%)','rpm_in','Eff_Var(%)']
                                        Info_BPCV_Var=[[0,0,0]]
                                        Info_BPCV_Var=pd.DataFrame(Info_BPCV_Var,columns=Name_columns)
                                    
                                    
                                    
                                    if (NBPCV >0 or NBPCF >0):
                                        Pd_BPC=float(Info_BPCF["TDH (psi)"][0]+Info_BPCV["TDH (psi)"][0]+Ps_BP)
                                    
                                    else:
                                        Pd_BPC=float(Pd)
                                        
                                    if (Pd_BPC<=Pd+tol and Pd_BPC>=Pd-tol):
                                        Cumpl_Flux=True    
                                    
                                    if (NBPT>0):
                                        if(Info_BPT_Mot["FactorCarga (%)"][0]<Limits["FC_Motor"][0]):
                                            Cumpl_BPT=True
                                    else:
                                        Cumpl_BPT=True
                                        
                                    if (NBB>0):
                                        if(Info_BB_Mot["FactorCarga (%)"][0]<Limits["FC_Motor"][0] and Info_BB["%BEP"][0]<Limits["BEP"][0] and Info_BB["%BEP"][0]>Limits["BEP"][1]and PD_BB<Limits["PD_BB"][0] and PD_BB>Limits["PD_BB"][1]):
                                            Cumpl_BB=True
                                    else:
                                        Cumpl_BB=True
                                        
                                    if (NBPCV>0):
                                        if(Info_BPCV_Mot["FactorCarga (%)"][0]<Limits["FC_Motor"][0] and Info_BPCV["%BEP"][0]<Limits["BEP"][0] and Info_BPCV["%BEP"][0]>Limits["BEP"][1]and Info_BPCV["Vel (RPM)"][0]<Limits["RPM_var"][0] and Info_BPCV["Vel (RPM)"][0]>Limits["RPM_var"][1]):
                                            Cumpl_BPCV=True
                                    else:
                                        Cumpl_BPCV=True
                                    
                                    if (NBPCF>0):
                                        if(Info_BPCF_Mot["FactorCarga (%)"][0]<Limits["FC_Motor"][0] and Info_BPCF["%BEP"][0]<Limits["BEP"][0] and Info_BPCF["%BEP"][0]>Limits["BEP"][1]):
                                            Cumpl_BPCF=True
                                    else:
                                        Cumpl_BPCF=True    
                                        
                                    
                                    
                                        
                                    Costo_EE=(Consumo_BPT+Consumo_BPCF+Consumo_BPCV+Consumo_BB)*Tarifa_Elect
                                    Costo_DRA=(ppm_proyec*Flujo)*42/1e6*Tarifa_DRA
                                    Costo_T=Costo_DRA+Costo_EE
                                    
                                    it=it+1
                                except:
                                    pass
                                
                                if (Cumpl_BPT and Cumpl_BB and Cumpl_BPCF and Cumpl_BPCV and Cumpl_Flux):
                                    it_true=it_true+1
                                    
                                    if (Costo_T<Costo_T_opt and Costo_T>0):
                                        it_op=it_op+1
                                        Costo_EE_opt=Costo_EE
                                        Costo_DRA_opt=Costo_DRA
                                        Costo_T_opt=Costo_T
            
                                        NBB_opt=NBB
                                        Info_BB_opt=Info_BB
                                        Info_BB_Mot_opt=Info_BB_Mot    
                                        
                                        NBPT_opt=NBPT
                                        Eff_Incr_opt=Eff_Incr
                                        Info_BPT_opt=Info_BPT
                                        Info_BPT_Mot_opt=Info_BPT_Mot    
                                        
                                        NBCPV_opt=NBPCV
                                        Info_BPCV_opt=Info_BPCV
                                        Info_BPCV_Mot_opt=Info_BPCV_Mot    
                                        Info_BPCV_Var_opt=Info_BPCV_Var
                                        
                                        NBCPF_opt=NBPCF
                                        Info_BPCF_opt=Info_BPCF
                                        Info_BPCF_Mot_opt=Info_BPCF_Mot
                                            
                                        ppm_opt=ppm_proyec
                                        Pd_opt=Pd
                                        Ps_BP_opt=Ps_BP
                                        
                                        
                                    
                                                                                
                                    # print(NBB)
                                    # print(NBPT)
                                    # print(NBPCV)
                                    # print(NBPCF)
                                    # print("Costo Total: ",Costo_T)
                                # print("Consumo BB: ", Consumo_BB)
                                # print("Consumo BPT: ",Consumo_BPT)
                                # print("Consumo BPCF: ",Consumo_BPCF)
                                # print("Consumo BPCV: ",Consumo_BPCV)
                                # print("Consumo Total: ",Consumo_BPT+Consumo_BPCF+Consumo_BPCV+Consumo_BB)
                                # print("Costo Total: ",Costo_T)
                
        end = time.time()
        print(end - start)
        print(it)
        print(it_true)
        print(it_op)
        
        Eff_ConjBB=Info_BB_opt["Eff (%)"][0]*Info_BB_Mot_opt["Eff_Mot (%)"][0]
        Eff_ConjBPCF=Info_BPCF_opt["Eff (%)"][0]*Info_BPCF_Mot_opt["Eff_Mot (%)"][0]
        Eff_ConjBPCV=Info_BPCV_opt["Eff (%)"][0]*Info_BPCV_Mot_opt["Eff_Mot (%)"][0]*Info_BPCV_Var_opt["Eff_Var(%)"][0]
        Eff_ConjBPT=Info_BPT_opt["Eff (%)"][0]*Info_BPT_Mot_opt["Eff_Mot (%)"][0]*Eff_Incr_opt

        Flux,TDH,RPM=e2.Covena_Graph("BPC_fija.csv",NBCPF_opt,"BPC_var.csv",NBCPV_opt,"BPT.csv",NBPT_opt,real_ps=float(Ps_BP_opt))

        vec_ppm,vec_red,real_red=e2.dra_graph(ppm_opt,m_Cov,b_Cov)
        
        dataf1 = {
        'Flujo':Flujo,
        'Pd':Pd_opt,
        'Flux':Flux,
        'TDH':TDH
        }
        df1 = pd.DataFrame(dataf1)
        
        fig1.data=[]
        fig2.data=[]
        
        fig1.add_trace(
            go.Line(x=df1['Flux'], y=df1['TDH'])
                    )

        fig1.add_trace(
            go.Scatter(
                mode="markers",
                x=df1['Flujo'],
                y=df1['Pd'],
                marker=dict(
                color='Red',
                size=10
                    )))
   
        fig1.update_layout(
             title={
                        'text': "Ventana Operativa",
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
            yaxis_title="Presión de Descarga [psi]",
            xaxis_title="Flujo [BPH]",
            yaxis_range=[max(min(TDH)-500,0),max(TDH)+500],
            xaxis_range=[max(min(Flux)-500,0),max(Flux)+500]
            )

        fig1.update_traces(line_color='gold')
        
        dataf2 = {
        'VecP':vec_ppm,
        'VecR':vec_red,
        'PpmO':ppm_opt,
        'RealR':real_red
        }
        df2 = pd.DataFrame(dataf2)
        
        fig2.add_trace(
            go.Line(x=df2['VecP'], y=df2['VecR'], marker_color='Gold')
                    )

        fig2.add_trace(
            go.Scatter(
                mode="markers",
                x=df2['PpmO'],
                y=df2['RealR'],
                marker=dict(
                color='Red',
                size=10
                    )))
   
        fig2.update_layout(
             title={
                        'text': "Rendimiento DRA",
                        'y':0.9, # new
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top' # new
                        },
            xaxis_title="DRA (ppm)",
            yaxis_title="Rendimiento",
            )
        
        fig2.update_traces(line_color='gold')
        
        CDRA_O="$ {:,.2f}".format(Costo_DRA_opt)
        CE_O="$ {:,.2f}".format(Costo_EE_opt)
        CET_O="$ {:,.2f}".format(Costo_T_opt)
        
        AhorroT="{:,.2f} %".format(((Costo_TB-Costo_T_opt)/Costo_TB)*100)

        BPCF=NBPCF
        BEP="{:,.2f} %".format(round(Info_BPCF_opt["%BEP"][0]*100,2))
        FCMOTOR="{:,.2f} %".format(round(Info_BPCF_Mot_opt["FactorCarga (%)"][0]*100,2))
        #FCMOTOR="Error"
        EFIEQP="{:,.2f} %".format(round(Info_BPCF_opt["Eff (%)"][0]*100,2))
        CONEQP="{:,.2f}".format(round(Consumo_BPCF,2))

        BPCV=NBPCV
        BEP2="{:,.2f} %".format(round(Info_BPCV_opt["%BEP"][0]*100,2))
        FCMOTOR2="{:,.2f} %".format(round(Info_BPCV_Mot_opt["FactorCarga (%)"][0]*100,2))
        RPM="{:,.2f}".format(round(Info_BPCV_opt["Vel (RPM)"][0],2))
        #FCMOTOR2="Error"
        EFIEQPVAR="{:,.2f} %".format(round(Info_BPCV_opt["Eff (%)"][0]*100,2))
        CONEQPVAR="{:,.2f}".format(round(Consumo_BPCV,2))

        
        BB=NBB
        BEP3="{:,.2f} %".format(round(Info_BB_opt["%BEP"][0]*100,2))
        FCMOTOR3="{:,.2f} %".format(round(Info_BB_Mot_opt["FactorCarga (%)"][0]*100,2))
        #FCMOTOR3="Error"
        EFEQPBB="{:,.2f} %".format(round(Info_BB_opt["Eff (%)"][0]*100,2))
        CONEQPBB="{:,.2f}".format(round(Consumo_BB,2))
        
        BPT=NBPT
        FCMOTOR4="{:,.2f} %".format(round(Info_BPT_Mot_opt["FactorCarga (%)"][0]*100,2))
        #FCMOTOR4="Error"
        EFEQPBPT="{:,.2f} %".format(round(Info_BPT_opt["Eff (%)"][0]*100,2))
        CONEQPBPT="{:,.2f}".format(round(Consumo_BPT,2))
        
        #EstadoID="Simulación Terminada"
        EstadoID=""
        Est1={"display":"flex"}
        Est2={"display":"none"}
        
        EFIMOTBPCFIJA="{:,.2f} %".format(round(Info_BPCF_Mot_opt["Eff_Mot (%)"][0]*100,2))
        EFICONBPCFIJA="{:,.2f} %".format(round(Eff_ConjBPCF,2)*100)
        CORRIENTEBPCFIJA="{:,.2f}".format(round(Info_BPCF_Mot_opt["Corr (A)"][0],2))
        
        EFIMOTBPCVAR="{:,.2f} %".format(round(Info_BPCV_Mot_opt["Eff_Mot (%)"][0]*100,2))
        EFICONBPCVAR="{:,.2f} %".format(round(Eff_ConjBPCV,2)*100)
        EFIVARBPCVAR="{:,.2f} %".format(round(Info_BPCV_Var_opt["Eff_Var(%)"][0]*100))
        CORRIENTEBPCVAR="{:,.2f}".format(round(Info_BPCV_Mot_opt["Corr (A)"][0],2))
        
        EFIMOTBB="{:,.2f} %".format(round(Info_BB_Mot_opt["Eff_Mot (%)"][0]*100,2))
        EFICONBB="{:,.2f} %".format(round(Eff_ConjBB,2)*100)
        CORRIENTEBB="{:,.2f}".format(round(Info_BB_Mot_opt["Corr (A)"][0],2))
        
        EFIMOTBPT="{:,.2f} %".format(round(Info_BPT_Mot_opt["Eff_Mot (%)"][0]*100,2))
        EFICONBPT="{:,.2f} %".format(round(Eff_ConjBPT,2)*100)
        CORRIENTEBPT="{:,.2f} %".format(round(Info_BPT_Mot_opt["Corr (A)"][0],2))
        EFIINCBPT="{:,.2f}".format(round(Eff_Incr_opt*100,2))
        
        Data2["EfiEquipo BPC Fija"]=EFIEQP
        Data2["EfiMotor BPC Fija"]=EFIMOTBPCFIJA                 
        Data2["EfiVariador BPC Fija"]="NA"          #NA
        Data2["EfiConjunto BPC Fija"]=EFICONBPCFIJA          
        Data2["Consumo BPC Fija"]=CONEQP
        Data2["Corriente BPC Fija"]=CORRIENTEBPCFIJA            
        
        Data2["EfiEquipo BPC Variable"]=EFIEQPVAR
        Data2["EfiMotor BPC Variable"]= EFIMOTBPCVAR             
        Data2["EfiVariador BPC Variable"]=EFIVARBPCVAR      
        Data2["EfiConjunto BPC Variable"]=EFICONBPCVAR      
        Data2["Consumo BPC Variable"]=CONEQPVAR
        Data2["Corriente BPC Variable"]=CORRIENTEBPCVAR        
        
        Data2["EfiEquipo BB"]=EFEQPBB
        Data2["EfiMotor BB"]= EFIMOTBB                       
        Data2["EfiVariador BB"]="NA"        #NA        
        Data2["EfiConjunto BB"]=EFICONBB              
        Data2["Consumo BB"]=CONEQPBB
        Data2["Corriente BB"]=CORRIENTEBB               
        
        Data2["EfiEquipo BPT"]=EFEQPBPT
        Data2["EfiMotor BPT"]= EFIMOTBPT                      
        Data2["EfiIncrementador BPT"]=EFIINCBPT         
        Data2["EfiConjunto BPT"]=EFICONBPT              
        Data2["Consumo BPT"]=CONEQPBPT
        Data2["Corriente BPT"]=CORRIENTEBPT           
    
    elif "btn-Limpiar" == ctx.triggered_id:
        print("Limpiar")
        
        BPCF=""
        BEP=""
        FCMOTOR=""
        EFIEQP=""
        CONEQP=""
        CDRA_B=""
        CE_B=""
        CET_B=""
        CDRA_O=""
        CE_O=""
        CET_O=""
        AhorroT=""
        BPCV=""
        BEP2=""
        FCMOTOR2=""
        RPM=""
        EFIEQPVAR=""
        CONEQPVAR=""
        BB=""
        BEP3=""
        FCMOTOR3=""
        EFEQPBB=""
        CONEQPBB=""
        BPT=""
        FCMOTOR4=""
        EFEQPBPT=""
        CONEQPBPT=""
        
        Data2={}
        
        fig1.data=[]
        fig2.data=[]
        
    elif "btn-Actualizar" == ctx.triggered_id:

        Input=Inputs('CENITCOVENAS')
        
        flujoIN=round(Input["flujoIN"],2)
        viscocidadIN=round(Input["viscocidadIN"],2)
        apiIN=round(Input["apiIN"],2)
        numUnidadesIN=Input["numUnidadesIN"]
        numEqpVarIN=Input["numEqpVarIN"]
        numEqpFijoIN=Input["numEqpFijoIN"]
        numEqpParIN=Input["numEqpParIN"]
        draTotIN=round(Input["draTotIN"],2)
        pRecIN=round(Input["pRecIN"],2)
        pDesIN=round(Input["pDesIN"],2)
        tarifaEleIN=round(Input["tarifaEleIN"],2)
        tarifaDRAIN=round(Input["tarifaDRAIN"],2)
        pBoosterIN=round(Input["pBoosterIN"],2)
        vBPIN=0
        
    elif "btn-Detener" == ctx.triggered_id:
        print("Detener")
    
    return [BPCF, BEP, FCMOTOR, CDRA_B, CE_B, CET_B,CDRA_O, CE_O, CET_O,AhorroT,BPCV,BEP2,FCMOTOR2,RPM,BB,BEP3,FCMOTOR3,
                  BPT,FCMOTOR4, Simular, fig1, fig2, flujoIN,viscocidadIN,
                  apiIN, numUnidadesIN, numEqpVarIN, numEqpFijoIN, numEqpParIN,
                  draTotIN, pRecIN, pDesIN, tarifaEleIN, tarifaDRAIN, pBoosterIN, vBPIN, EstadoID, Est1, Est2, Data2]

#Ocultar Tarjetas
@app.callback(
    Output('Grafico1','style'),
    Output('Grafico2','style'),
    Output('CostoBase','style'),
    Output('CostoOptimo','style'),
    Output('ResultAhorroT','style'),
    
    Output('btn-Simular','style'),
    Output('btn-Optimizar','style'),
    Output('btn-Limpiar','style'),
    Output('btn-Detener','style'),
    
    Output('EstadoID2','children'),
   
    Input('btn-Simular','n_clicks'),
    Input('btn-Optimizar','n_clicks'),
    Input('btn-Limpiar','n_clicks'),
)            
def update_style(Simular, Optimizar, Limpiar):

    sty1={"visibility":"hidden"}
    sty2={"visibility":"hidden"}
    sty3={"display":"flex"}
    sty4={"display":"flex"}
    sty5={"display":"block"}
    
    sty6={"displlay":"block"}
    sty7={"display":"hidden"}
    sty8={"display":"hidden"}
    sty9={"display":"hidden"}

    EstadoID2=""
    
    if ctx.triggered_id=="btn-Simular":
        
        sty1={"visibility":"visible"}
        sty2={"visibility":"hidden"}
        sty3={"display":"flex"}
        sty4={"display":"none"}
        sty5={"display":"none"}
        
        #EstadoID2="Simulando..."
        EstadoID2=""
    
    if ctx.triggered_id=="btn-Optimizar":
        
        sty1={"visibility":"visible"}
        sty2={"visibility":"visible"}
        sty3={"display":"flex"}
        sty4={"display":"flex"}
        sty5={"display":"block"}
        
        #EstadoID="Optimizando..."
        EstadoID2=""
    
    if ctx.triggered_id=="btn-Limpiar":
        
        sty1={"visibility":"hidden"}
        sty2={"visibility":"hidden"}
        sty3={"display":"flex"}
        sty4={"display":"flex"}
        sty5={"display":"hidden"}
        
        #Data2={}
        
        #EstadoID="Optimizando..."
        EstadoID2=""
        
    return [sty1, sty2, sty3, sty4, sty5, sty6, sty7, sty8, sty9, EstadoID2]

#Variables Avanzadas
@app.callback(
    
    Output("tarifaEleA", "style"),
    Output("tarifaDRAA", "style"),
    Output("pBoosterA", "style"),
    Output("vBPA", "style"),
    
    Output("EntA", "style"),

    Input("OpcAvanzadas", "value"),
)
def sync_checklists(Opt):
    
    if Opt==None or len(Opt)==0:
        
        sty1={"display":"none"}
        sty2={"display":"none"}
        sty3={"display":"none"}
        sty4={"display":"none"}
        sEnt={"height": "580px"}
        
    else:
        sty1={"display":"block"}
        sty2={"display":"block"}
        sty3={"display":"block"}
        sty4={"display":"block"}
        sEnt={"height": "790px"}

    return [sty1,sty2,sty3,sty4,sEnt]

#Restricciones
@app.callback(
    
    Output("store-data", "data"),

    Input("C-BPCF", "value"),
    Input("C-BPCV", "value"),
    Input("C-BB", "value"),
    Input("C-BPT", "value"),
)
def restricciones(CBPCF, CBPCV, CBB, CBPT):
    C={}
    C["Num BPC-F"]=len(CBPCF)
    C["Num BPC-V"]=len(CBPCV)
    C["Num BB"]=len(CBB)
    C["Num BPT"]=len(CBPT)

    return C

# Select BPC Fija
@app.callback(
    Output('EFIEQP', 'children'),
    Output('CONEQP', 'children'),
    
    Input("store-data2", "data"),
    Input('EfiSelectedBPC', 'value'),
    Input('ConsumoSelectedBPC', 'value'),
    Input('BPCF', 'children')
)
def update_output(Data2, value, value2, inp):

    if inp==None:
        Data2={}
    
    if value=="EfEquipo" and len(Data2)!=0 and value2=="Consumo":    
        return [Data2["EfiEquipo BPC Fija"], Data2["Consumo BPC Fija"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiMotor BPC Fija"], Data2["Consumo BPC Fija"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiVariador BPC Fija"], Data2["Consumo BPC Fija"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiConjunto BPC Fija"], Data2["Consumo BPC Fija"]]
    
    #-----------------------------------------------------------------------

    if value=="EfEquipo" and len(Data2)!=0 and value2=="Corriente":    
        return [Data2["EfiEquipo BPC Fija"], Data2["Corriente BPC Fija"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiMotor BPC Fija"], Data2["Corriente BPC Fija"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiVariador BPC Fija"], Data2["Corriente BPC Fija"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiConjunto BPC Fija"], Data2["Corriente BPC Fija"]]
    
    else:
        return ["",""]

# Select BPC Variable 
@app.callback(
    Output('EFIEQPVAR', 'children'),
    Output('CONEQPVAR', 'children'),
    
    Input("store-data2", "data"),
    Input('EfiSelectedBPCVAR', 'value'),
    Input('ConsumoSelectedBPCVAR', 'value'),
    Input('BPCF', 'children')
)
def update_output(Data2, value, value2, inp):

    if inp==None:
        Data2={}
        
    if value=="EfEquipo" and len(Data2)!=0 and value2=="Consumo":    
        return [Data2["EfiEquipo BPC Variable"], Data2["Consumo BPC Variable"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiMotor BPC Variable"], Data2["Consumo BPC Variable"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiVariador BPC Variable"], Data2["Consumo BPC Variable"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiConjunto BPC Variable"], Data2["Consumo BPC Variable"]]
    
    #-----------------------------------------------------------------------

    if value=="EfEquipo" and len(Data2)!=0 and value2=="Corriente":    
        return [Data2["EfiEquipo BPC Variable"], Data2["Corriente BPC Variable"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiMotor BPC Variable"], Data2["Corriente BPC Variable"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiVariador BPC Variable"], Data2["Corriente BPC Variable"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiConjunto BPC Variable"], Data2["Corriente BPC Variable"]]
    
    else:
        return ["",""]
    
# Select BB  
@app.callback(
    Output('EFEQPBB', 'children'),
    Output('CONEQPBB', 'children'),
    
    Input("store-data2", "data"),
    Input('EfiSelectedBB', 'value'),
    Input('ConsumoSelectedBB', 'value'),
    Input('BPCF', 'children')
)
def update_output(Data2, value, value2, inp):

    if inp==None:
        Data2={}
        
    if value=="EfEquipo" and len(Data2)!=0 and value2=="Consumo":    
        return [Data2["EfiEquipo BB"], Data2["Consumo BB"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiMotor BB"], Data2["Consumo BB"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiVariador BB"], Data2["Consumo BB"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiConjunto BB"], Data2["Consumo BB"]]
    
    #-----------------------------------------------------------------------

    if value=="EfEquipo" and len(Data2)!=0 and value2=="Corriente":    
        return [Data2["EfiEquipo BB"], Data2["Corriente BB"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiMotor BB"], Data2["Corriente BB"]]
    
    elif value=="EfVariador" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiVariador BB"], Data2["Corriente BB"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiConjunto BB"], Data2["Corriente BB"]]
    
    else:
        return ["",""]
    
# Select BPT  
@app.callback(
    Output('EFEQPBPT', 'children'),
    Output('CONEQPBPT', 'children'),
    
    Input("store-data2", "data"),
    Input('EfiSelectedBPT', 'value'),
    Input('ConsumoSelectedBPT', 'value'),
    Input('BPCF', 'children')
)
def update_output(Data2, value, value2, inp):

    if inp==None:
        Data2={}
        
    if value=="EfEquipo" and len(Data2)!=0 and value2=="Consumo":    
        return [Data2["EfiEquipo BPT"], Data2["Consumo BPT"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiMotor BPT"], Data2["Consumo BPT"]]
    
    elif value=="EfIncrementador" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiIncrementador BPT"], Data2["Consumo BPT"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Consumo":
        return [Data2["EfiConjunto BPT"], Data2["Consumo BPT"]]
    
    #-----------------------------------------------------------------------

    if value=="EfEquipo" and len(Data2)!=0 and value2=="Corriente":    
        return [Data2["EfiEquipo BPT"], Data2["Corriente BPT"]]
    
    elif value=="EfMotor" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiMotor BPT"], Data2["Corriente BPT"]]
    
    elif value=="EfIncrementador" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiIncrementador BPT"], Data2["Corriente BPT"]]
    
    elif value=="EfConjunto" and len(Data2)!=0 and value2=="Corriente":
        return [Data2["EfiConjunto BPT"], Data2["Corriente BPT"]]
    
    else:
        return ["",""]

if __name__ == '__main__':
    app.run_server()