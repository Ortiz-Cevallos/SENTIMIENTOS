# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 09:13:39 2020

@author: q31487
"""

import plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np

annotations =[
    ["2008-07-14",'Quiebra <br />Martinsa-Fadesa ',-60],
    ["2008-09-15",' Caída de<br /> Lehman ',0],
    ["2009-03-28",' Intervención <br /> Caja Castilla-<br /> La Mancha ',40],
    ["2010-05-01",' Primer<br /> Rescate<br /> Grecia ',10],
    ["2012-01-02",' Segundo<br> rescate <br /> Grecia ',-30],
    ["2012-05-07",' Rescate <br \> Bankia',0],
    ["2012-06-09"," Rescate <br \> Bancario <br \> Español ",40],
    ["2015-03-09",' Inicio <br \> "Plan Draghi" ',-40],
    ["2015-12-16"," Subida tipos <br \> de la FED ",-30],
    ["2017-03-29", ' Comunicación <br \> Brexit ',-60],
    ["2017-06-07", ' Intervención <br \> Banco Popular ',-10],
    ["2017-10-01", ' Referéndum <br \> Independencia<br> Cataluña',30],
    ["2018-03-22", ' Trump anuncia <br \> aranceles a <br \> China ',70],
    ["2020-03-14", ' Inicio <br \> Estado Alarma ',10],
    ["2022-02-24", ' Invasión rusa <br \> de Ucrania ',10],
   ]

# Edit the layout
layout = {
    'plot_bgcolor':'#EEEEEE',
    'margin':{'t': 100},
    'xaxis': {
        'title': 'Año',
        'tickmode':'linear',
        'tick0': 2002,
        'dtick': 'M12',
        'tickformat': '%Y',
        'range':["2002-07-01","2020-12-01"]
    },
}

default_shapes= [{
            'type': 'rect',
            # x-reference is assigned to the x-values
            'xref': 'x',
            # y-reference is assigned to the plot paper [0,1]
            'yref': 'paper',
            'x0': '2002-07-01',
            'y0': 0,
            'x1': '2006-07-12',
            'y1': 1,
            'fillcolor': '#d3d3d3',
            'opacity': 0.2,
            'line': {
                'width': 0
            }
        },{
            'type': 'rect',
            # x-reference is assigned to the x-values
            'xref': 'x',
            # y-reference is assigned to the plot paper [0,1]
            'yref': 'paper',
            'x0': '2012-06-11',
            'y0': 0,
            'x1': '2018-06-11',
            'y1': 1,
            'fillcolor': '#d3d3d3',
            'opacity': 0.3,
            'line': {
                'width': 0
            }
        }
    
    ]


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def update_layout(fig, title, ytitle1, range1, ytitle2="", range2=0):
    if range2 !=0:
        yaxis2= {
        'range': [-range2,range2],
        'side':"right",
        'anchor':"x",
        'overlaying':"y",
        'title': ytitle2
        }
    else:
        yaxis2={}
        
    fig.update_layout(
    legend_orientation="h",
    legend=dict(x=0, y=-.2),
#    autosize=True,
#
     autosize=False,
     width=1500,
     height=500,
#
    title = title,
    yaxis = {'title': ytitle1,'range': [-range1,range1] , 'side':'left'},
    yaxis2=yaxis2,
    annotations=[
        go.layout.Annotation(
         showarrow=True,
         x =a[0],
         y=range1,
         text= a[1],
         ax=a[2],
         ay=-20,
         font=dict(
         family='verdana',
         size=9,
         color='black')            
        ) 
        for a in annotations
    ],
    shapes=default_shapes +[{
            'type': 'line',
            'x0': a[0],
            'y0': -1,
            'x1': a[0],
            'y1': 1,
            'line': {
                'color': 'rgb(55, 128, 191)',
                'width': 1,
                'dash': 'dash'
                    }
    } for a in annotations]
    )
    

def generate_isef_chart(df, attr):

    #py.offline.init_notebook_mode(connected=True)
    title = "Evolución del ISEF"
    
    
    
    name = f"ISEF {attr['name']}"
    trace4 = go.Scatter(x=df.date, 
                       y=df['index'], 
                       mode = 'lines+markers',
                       name=name,
                       line=dict(color=attr["color"], width=4),
                       hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df["date"]],
                       yaxis = "y")
    
    
    data = [trace4]
        
    #fig = dict(data=data, layout=layout)
    #fig = py.offline.iplot(fig)
    max_t = df["date"].max()
    max_t = f"{max_t.year}-12-31"
    layout["xaxis"]["range"][1]=max_t
    fig = go.FigureWidget(data=data, layout=layout)
    
    update_layout(fig,title=title,ytitle1="ISEF",range1=1)
    #config = {"toImageButtonOptions": {"width": None, "height": None}}
    #import dash_core_components as dcc
    #dcc.Graph(figure=fig, config=config)
    fig.write_html(f"../output/charts/isef_{attr['folder']}.html", include_plotlyjs='directory')



def generate_neg_pos_chart(df, attr):

    #py.offline.init_notebook_mode(connected=True)
    title = "Evolución de la positividad y la negatividad"
    
    
    
    name = f"Positividad {attr['name']}"
    trace1 = go.Scatter(x=df.date, 
                   y=df['positivity'], 
                   mode = 'lines+markers',
                   hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                   name=name,
                   hoverinfo= 'none',
                   line=dict(color='rgb(92, 189, 107)', width=4),
                   text= [f"{d.day}-{d.month}-{d.year}" for d in df["date"]],
                   yaxis="y")
    

    name = f"Negatividad {attr['name']}"
    trace2 = go.Scatter(x=df.date, 
                   y=df['negativity'], 
                   mode = 'lines+markers',
                   name=name,
                   line=dict(color='rgb(160, 45, 63)', width=4),
                   hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                   text= [f"{d.day}-{d.month}-{d.year}" for d in df["date"]],
                   yaxis="y")


    name = f"Negatividad Neta {attr['name']}"
    trace3 = go.Scatter(x=df.date, 
                       y=(df['negativity']-df['positivity']), 
                       mode = 'lines+markers',
                       name= name,
                       line=dict(color='rgb(27, 72, 139)', width=4),
                       hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df["date"]],
                       yaxis="y")
    
    
    data = [trace1, trace2, trace3]
        
    #fig = dict(data=data, layout=layout)
    #fig = py.offline.iplot(fig)
    max_t = df["date"].max()
    max_t = f"{max_t.year}-12-31"
    layout["xaxis"]["range"][1]=max_t
    fig = go.FigureWidget(data=data, layout=layout)
    
    if attr['name'] == 'cuerpo':
        range1 = 0.02
    else:
        range1 = 0.04
    update_layout(fig,title=title,ytitle1="Índice",range1=range1)
    #config = {"toImageButtonOptions": {"width": None, "height": None}}
    #import dash_core_components as dcc
    #dcc.Graph(figure=fig, config=config)
    fig.write_html(f"../output/charts/neg_pos_{attr['folder']}.html", include_plotlyjs='directory')


def generate_boxplot_chart(df, df_isef, attr):
    
    df_body_q = df.groupby('date')['score'].agg(
        [  percentile(0), percentile(25), percentile(50),  percentile(75), percentile(100)]).reset_index(drop=True)
    
    title = f"ISEF {attr['name']}"
    
    name = f"Pendiente {attr['name']}"
    trace1 = go.Box(x=df.date, 
                       y=df['slope'] *2.5  , 
                       name=name,
                       hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]],
                       boxpoints='outliers', # only outliers
                       visible= 'legendonly'
                   )
    
    name = f"ISEF {attr['name']}"
    trace2 = go.Scatter(x=df_isef.date, 
                       y=df_isef['index']  , 
                       mode = 'lines+markers',
                       name=name,
                       hovertemplate='<b>'+ name +'</b><br>Fecha: %{text}<br>Valor: %{y:.2r}',
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    
    trace3 = go.Scatter(x=df_isef.date, 
                       y=df_body_q['percentile_50'], 
                       mode = 'lines',
                       line=dict(width=0),
                       name="p50",
                       showlegend = False,
                       hovertemplate="<b>Rango 50</b><br>Fecha: %{text}<br>ISEF: %{y:.2r}",
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    trace4 = go.Scatter(x=df_isef.date, 
                       y=df_body_q['percentile_25'], 
                       mode = 'lines',
                       line=dict(width=0),
                       name="p25",
                       fill = "tonexty",
                       showlegend = False,
                       hovertemplate="<b>Rango 25</b><br>Fecha: %{text}<br>ISEF: %{y:.2r}",
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    trace5 = go.Scatter(x=df_isef.date, 
                       y=df_body_q['percentile_100'], 
                       mode = 'lines',
                       line=dict(width=0),
                       name="p100",
                       fill = "tonexty",
                       showlegend = False,
                       hovertemplate="<b>Rango 100</b><br>Fecha: %{text}<br>ISEF: %{y:.2r}",
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    trace6 = go.Scatter(x=df_isef.date, 
                       y=df_body_q['percentile_75'], 
                       mode = 'lines',
                       line=dict(width=0),
                       name="p75",
                       fill = "tonexty",
                       showlegend = False,
                       hovertemplate="<b>Rango 75</b><br>Fecha: %{text}<br>ISEF: %{y:.2r}",
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    trace7 = go.Scatter(x=df_isef.date, 
                       y=df_body_q['percentile_0'], 
                       mode = 'lines',
                       line=dict(width=0),
                       name="p0",
                       fill = "tonexty",
                       showlegend = False,
                       hovertemplate="<b>Rango 0</b><br>Fecha: %{text}<br>ISEF: %{y:.2r}",
                       text= [f"{d.day}-{d.month}-{d.year}" for d in df_isef["date"]])
    
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7]
    
        
    max_t = df["date"].max()
    max_t = f"{max_t.year}-12-31"
    min_t = df["date"].min()
    if min_t.month >=7:
        month = "07"
    else:
        month = "01"
    min_t = f"{min_t.year}-{month}-01"
    layout["xaxis"]["range"]=[min_t, max_t]
        
    fig = go.FigureWidget(data=data, layout=layout)
    
    update_layout(fig, title=title, ytitle1=title, range1=1  )
    
    fig.write_html(f"../output/charts/boxplot_{attr['folder']}.html", include_plotlyjs='directory')