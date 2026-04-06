import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import bootstrap


# La fecha del corte de los datos.
FECHA_FUENTE = "25/03/2026"

# Estos colores serán la paleta para todas las gráficas.
PLOT_COLOR = "#1A1A1D"
PAPER_COLOR = "#3B1C32"


# Estos bins serán usados para agrupar las edades.
BINS = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 120]

LABELS = [
    "0-4",
    "5-9",
    "10-14",
    "15-19",
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-74",
    "75-79",
    "80-84",
    "≥85",
]

# Estos grupos son los que usa la SSA en sus reportes de morbilidad.
# Estos serán usados en la gráfica de vacunación.
GRUPOS_ETARIOS = [
    [0, 0],
    [1, 4],
    [5, 9],
    [10, 14],
    [15, 19],
    [20, 24],
    [25, 44],
    [45, 49],
    [50, 59],
    [60, 64],
    [65, 120],
]

MESES = {
    1: "Ene.",
    2: "Feb.",
    3: "Mar.",
    4: "Abr.",
    5: "May.",
    6: "Jun.",
    7: "Jul.",
    8: "Ago.",
    9: "Sep.",
    10: "Oct.",
    11: "Nov.",
    12: "Dic.",
}


def tendencia_semanal(año, xanchor="left"):
    """
    Genera una gráfica de barras con la incidencia
    semanal de sarampión.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    xanchor : str
        Especifica de qué lado estará colocada la leyenda.
        Puede ser 'left' o 'right'.

    """

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(f"./data/{año}.csv")

    # Quitamos las fechas inválidas.
    df = df[df["FECHA_DIAGNOSTICO"] != "9999-99-99"]

    # Convertimos el resto de fechas a datetime.
    try:
        df["FECHA_DIAGNOSTICO"] = pd.to_datetime(df["FECHA_DIAGNOSTICO"])
    except Exception as _:
        df["FECHA_DIAGNOSTICO"] = pd.to_datetime(df["FECHA_DIAGNOSTICO"], dayfirst=True)

    df = df.pivot_table(
        index="FECHA_DIAGNOSTICO",
        columns="DIAGNOSTICO",
        values="ID_REGISTRO",
        aggfunc="count",
        fill_value=0,
    )

    # Haremos un remuestreo semanal de lunes a viernes.
    df = df.resample("W-MON", label="left", closed="left").sum()

    # Fix para fechas incorrectas.
    df = df[df[3] > 1]

    # Creamos las etiquetas para nuestro eje horizontal.
    # Si hay más de 25 barras, solo crearemos la mitad de etiquetas
    # para evitar saturación visual.
    if len(df) > 25:
        etiquetas = [
            f"{item.day:02}<br>{MESES[item.month]}" if i % 2 == 0 else ""
            for i, item in enumerate(df.index)
        ]

    else:
        etiquetas = [f"{item.day:02}<br>{MESES[item.month]}" for item in df.index]

    # Crearemos una gráfica de barras apilada.
    # Una será de casos confirmados y otra de casos descartados.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[1],
            name=f"Positivo para sarampión<br>(total: <b>{df[1].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#f57c00",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[3],
            name=f"Descartado por sarampión<br>(total: <b>{df[3].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#2196f3",
        )
    )

    fig.update_xaxes(
        tickvals=df.index,
        ticktext=etiquetas,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Casos semanales",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_title=" <b>Diagnóstico del caso</b> ",
        legend_bordercolor="#FFFFFF",
        legend_x=0.01 if xanchor == "left" else 0.99,
        legend_y=0.98,
        legend_xanchor=xanchor,
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la incidencia de sarampión en México durante {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Semana de diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./semanal_{año}.png")


def tendencia_mensual(*años):
    """
    Genera una gráfica de barras con la incidencia
    mensual de sarampión.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        temp_df = pd.read_csv(f"./data/{año}.csv")

        # Quitamos las fechas inválidas.
        temp_df = temp_df[temp_df["FECHA_DIAGNOSTICO"] != "9999-99-99"]

        # Convertimos el resto de fechas a datetime.
        try:
            temp_df["FECHA_DIAGNOSTICO"] = pd.to_datetime(temp_df["FECHA_DIAGNOSTICO"])
        except Exception as _:
            temp_df["FECHA_DIAGNOSTICO"] = pd.to_datetime(
                temp_df["FECHA_DIAGNOSTICO"], dayfirst=True
            )

        dfs.append(temp_df)

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Contamos el número de casos por tipo y día de diagnóstico.
    df = df.pivot_table(
        index="FECHA_DIAGNOSTICO",
        columns="DIAGNOSTICO",
        values="ID_REGISTRO",
        aggfunc="count",
        fill_value=0,
    )

    # Haremos un remuestreo mensual.
    df = df.resample("MS").sum()

    # Fix para fechas incorrectas (muy pocos registros).
    df["total"] = df.sum(axis=1)
    df = df[df["total"] > 5]

    # Creamos las etiquetas mensuales.
    etiquetas = [f"{MESES[item.month]}<br>{item.year}" for item in df.index]

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Crearemos una gráfica de barras apilada.
    # Una será de casos confirmados y otra de casos descartados.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[1],
            name=f"Positivo para sarampión<br>(total: <b>{df[1].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#f57c00",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[3],
            name=f"Descartado por sarampión<br>(total: <b>{df[3].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#2196f3",
        )
    )

    fig.update_xaxes(
        tickvals=df.index,
        ticktext=etiquetas,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
    )

    fig.update_yaxes(
        title="Casos mensuales",
        tickformat="s",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_title=" <b>Diagnóstico del caso</b> ",
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la incidencia de sarampión en México durante {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes de diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./mensual_{año}.png")


def tendencia_semanal_origen(año, xanchor="left"):
    """
    Genera una gráfica de barras con la incidencia
    semanal de sarampión según el origen del caso.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    xanchor : str
        Especifica de qué lado estará colocada la leyenda.
        Puede ser 'left' o 'right'.

    """

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(f"./data/{año}.csv")

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Quitamos las fechas inválidas.
    df = df[df["FECHA_DIAGNOSTICO"] != "9999-99-99"]

    # Convertimos el resto de fechas a datetime.
    try:
        df["FECHA_DIAGNOSTICO"] = pd.to_datetime(df["FECHA_DIAGNOSTICO"])
    except Exception as _:
        df["FECHA_DIAGNOSTICO"] = pd.to_datetime(df["FECHA_DIAGNOSTICO"], dayfirst=True)

    # Contamos el número de casos según su origen y fecha de diagnóstico.
    df = df.pivot_table(
        index="FECHA_DIAGNOSTICO",
        columns="ORIGEN_CASO",
        values="ID_REGISTRO",
        aggfunc="count",
        fill_value=0,
    )

    # Vamos a crear valores default para los 4 posibles orígenes.
    for i in [1, 2, 3, 4]:
        if i not in df.columns:
            df[i] = 0

    # Haremos un remuestreo semanal de lunes a viernes.
    df = df.resample("W-MON", label="left", closed="left").sum()

    # Creamos las etiquetas para nuestro eje horizontal.
    # Si hay más de 25 barras, solo crearemos la mitad de etiquetas
    # para evitar saturación visual.
    if len(df) > 25:
        etiquetas = [
            f"{item.day:02}<br>{MESES[item.month]}" if i % 2 == 0 else ""
            for i, item in enumerate(df.index)
        ]

    else:
        etiquetas = [f"{item.day:02}<br>{MESES[item.month]}" for item in df.index]

    # Crearemos una gráfica de barras apilada.
    # Una será de casos confirmados y otra de casos descartados.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[1],
            name=f"Importado<br>(total: <b>{df[1].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#00bfa5",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[2],
            name=f"Relacionado a importación<br>(total: <b>{df[2].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ab47bc",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[3],
            name=f"Autóctono<br>(total: <b>{df[3].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ff4081",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[4],
            name=f"Fuente desconocida<br>(total: <b>{df[4].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ffc107",
        )
    )

    fig.update_xaxes(
        tickvals=df.index,
        ticktext=etiquetas,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Casos semanales",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        legend_traceorder="normal",
        showlegend=True,
        legend_title=" <b>Origen de casos positivos</b> ",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01 if xanchor == "left" else 0.99,
        legend_y=0.98,
        legend_xanchor=xanchor,
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la incidencia de sarampión en México durante {año} según origen del caso",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Semana de diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./origen_semanal_{año}.png")


def tendencia_mensual_origen(*años):
    """
    Genera una gráfica de barras con la incidencia
    mensual de sarampión según el origen del caso.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        temp_df = pd.read_csv(f"./data/{año}.csv")

        # Quitamos las fechas inválidas.
        temp_df = temp_df[temp_df["FECHA_DIAGNOSTICO"] != "9999-99-99"]

        # Convertimos el resto de fechas a datetime.
        try:
            temp_df["FECHA_DIAGNOSTICO"] = pd.to_datetime(temp_df["FECHA_DIAGNOSTICO"])
        except Exception as _:
            temp_df["FECHA_DIAGNOSTICO"] = pd.to_datetime(
                temp_df["FECHA_DIAGNOSTICO"], dayfirst=True
            )

        dfs.append(temp_df)

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Contamos el número de casos según su origen y fecha de diagnóstico.
    df = df.pivot_table(
        index="FECHA_DIAGNOSTICO",
        columns="ORIGEN_CASO",
        values="ID_REGISTRO",
        aggfunc="count",
        fill_value=0,
    )

    # Vamos a crear valores default para los 4 posibles orígenes.
    for i in [1, 2, 3, 4]:
        if i not in df.columns:
            df[i] = 0

    # Haremos un remuestreo semanal de lunes a viernes.
    df = df.resample("MS").sum()

    # Fix para fechas incorrectas (muy pocos registros).
    df["total"] = df.sum(axis=1)
    df = df[df["total"] > 5]

    # Creamos las etiquetas mensuales.
    etiquetas = [f"{MESES[item.month]}<br>{item.year}" for item in df.index]

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Crearemos una gráfica de barras apilada.
    # Una será de casos confirmados y otra de casos descartados.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[1],
            name=f"Importado<br>(total: <b>{df[1].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#00bfa5",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[2],
            name=f"Relacionado a importación<br>(total: <b>{df[2].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ab47bc",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[3],
            name=f"Autóctono<br>(total: <b>{df[3].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ff4081",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[4],
            name=f"Fuente desconocida<br>(total: <b>{df[4].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#ffc107",
        )
    )

    fig.update_xaxes(
        tickvals=df.index,
        ticktext=etiquetas,
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Casos mensuales",
        tickformat="s",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        legend_traceorder="normal",
        showlegend=True,
        legend_title=" <b>Origen de casos positivos</b> ",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la incidencia de sarampión en México durante {año} según origen del caso",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes de diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./origen_mensual_{año}.png")


def evolucion_casos(*años):
    """
    Genera un diagrama sankey con la evolución
    de los casos confirmados de sarampión.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(pd.read_csv(f"./data/{año}.csv"))

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Vamos a calcular los totales para cada etapa.
    casos_confirmados = len(df)

    vac_si = df[df["VACUNACION"] == 1]
    vac_no = df[df["VACUNACION"] == 2]

    vac_si_comp_si = vac_si[vac_si["COMPLICACIONES"] == 1]
    vac_si_comp_no = vac_si[vac_si["COMPLICACIONES"] == 2]

    vac_no_comp_si = vac_no[vac_no["COMPLICACIONES"] == 1]
    vac_no_comp_no = vac_no[vac_no["COMPLICACIONES"] == 2]

    def_vac_si_comp_si = vac_si_comp_si[vac_si_comp_si["DEFUNCION"] == 1]
    def_vac_si_comp_no = vac_si_comp_no[vac_si_comp_no["DEFUNCION"] == 1]

    def_vac_no_comp_si = vac_no_comp_si[vac_no_comp_si["DEFUNCION"] == 1]
    def_vac_no_comp_no = vac_no_comp_no[vac_no_comp_no["DEFUNCION"] == 1]

    # Este valor es para evitar que los nodos de las defunciones no aparezcan.
    epsilon = 60

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Un diagrama sankey requiere especificar todos los valores.
    # Para nuestros 11 nodos ya tenemos los cálculos ya hechos.
    fig = go.Figure()

    fig.add_trace(
        go.Sankey(
            node=dict(
                pad=50,
                label=[
                    f"<b>Casos confirmados</b><br>({casos_confirmados:,})",
                    f"<b>Vacunados</b><br>({len(vac_si):,})",
                    f"<b>No vacunados</b><br>({len(vac_no):,})",
                    f"<b>Con complicaciones*</b><br>({len(vac_si_comp_si):,})",
                    f"<b>Sin complicaciones</b><br>({len(vac_si_comp_no):,})",
                    f"<b>Con complicaciones*</b><br>({len(vac_no_comp_si):,})",
                    f"<b>Sin complicaciones</b><br>({len(vac_no_comp_no):,})",
                    f"<b>Defunción</b><br>({len(def_vac_si_comp_si):,})",
                    f"<b>Defunción</b><br>({len(def_vac_si_comp_no):,})",
                    f"<b>Defunción</b><br>({len(def_vac_no_comp_si):,})",
                    f"<b>Defunción</b><br>({len(def_vac_no_comp_no):,})",
                ],
                color=[
                    "#1de9b6",
                    "#42a5f5",
                    "#ffca28",
                    "#ba68c8",
                    "#ba68c8",
                    "#fb8c00",
                    "#fb8c00",
                    "#d32f2f",
                    "#d32f2f",
                    "#d32f2f",
                    "#d32f2f",
                ],
            ),
            link=dict(
                color="hsla(0, 100, 100, 0.225)",
                source=[
                    0,
                    0,
                    1,
                    1,
                    2,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],
                target=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                value=[
                    len(vac_si),
                    len(vac_no),
                    len(vac_si_comp_si),
                    len(vac_si_comp_no),
                    len(vac_no_comp_si),
                    len(vac_no_comp_no),
                    len(def_vac_si_comp_si) + epsilon,
                    len(def_vac_si_comp_no) + epsilon,
                    len(def_vac_no_comp_si) + epsilon,
                    len(def_vac_no_comp_no) + epsilon,
                ],
            ),
        )
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de los casos confirmados de sarampión en México durante {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_r=100,
        margin_b=160,
        margin_l=100,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="*Otitis media, neumonía, laringotraqueobronquitis y/o encefalitis",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./evolucion_{año}.png")


def defunciones(*años):
    """
    Genera una gráfica con la distribución de defunciones
    por sarampión según edad y sexo.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(pd.read_csv(f"./data/{año}.csv"))

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Seleccionamos los registros positivos por sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Seleccionamos las defunciones.
    df = df[df["DEFUNCION"] == 1]

    # Creamos dos DataFrames, uno para mujeres y otro para hombres.
    mujeres = df[df["SEXO"] == 1]
    hombres = df[df["SEXO"] == 2]

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Vamos a crear dos strip plots, uno para cada sexo.
    fig = go.Figure()

    fig.add_traces(
        go.Box(
            x=hombres["EDAD_ANOS"],
            y=[f"<b>Hombres</b><br>(total: {len(hombres)})"] * len(hombres),
            boxpoints="all",
            pointpos=0,
            whiskerwidth=0,
            line_width=0,
            fillcolor="hsla(0, 0, 0, 0)",
            marker_color="#00e5ff",
            jitter=1,
            marker_size=20,
            marker_symbol="circle-open",
            marker_line_width=4,
            orientation="h",
        )
    )

    fig.add_traces(
        go.Box(
            x=mujeres["EDAD_ANOS"],
            y=[f"<b>Mujeres</b><br>(total: {len(mujeres)})"] * len(mujeres),
            boxpoints="all",
            pointpos=0,
            whiskerwidth=0,
            line_width=0,
            fillcolor="hsla(0, 0, 0, 0)",
            marker_color="#ffea00",
            jitter=1,
            marker_size=20,
            marker_symbol="circle-open",
            marker_line_width=4,
            orientation="h",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Defunciones por sarampión en México durante {año} según edad y sexo",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=180,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Edad al momento del diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./defunciones_{año}.png")


def razon_riesgo(*años):
    """
    Genera una gráfica con el modelo de riesgo
    de sarampión grave en función de edad y vacunación de la persona.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(pd.read_csv(f"./data/{año}.csv"))

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Modificamos la columna de vacunación para que sean ceros (no vacunados) y unos (vacunados).
    df["VACUNACION"] = df["VACUNACION"].map({2: 0, 1: 1})

    # Modificamos la columna de complicaciones para que sean ceros (sin complicaciones) y unos (con complicaciones).
    df["COMPLICACIONES"] = df["COMPLICACIONES"].map({2: 0, 1: 1})

    # Dado que la incidencia de casos severos de sarampión no es baja, el modelo logístico puede no ser el más adecuado.
    # Por ello, emplearemos un modelo de Poisson con estimadores robustos, que permite obtener riesgos relativos directamente.
    modelo = smf.glm(
        formula="COMPLICACIONES ~ VACUNACION + EDAD_ANOS",
        data=df,
        family=sm.families.Poisson(),
    ).fit(cov_type="HC0")

    # Mostraremos las mismas edades que las de nuestro dataset.
    edades = np.linspace(df["EDAD_ANOS"].min(), df["EDAD_ANOS"].max(), 100)

    # Extraemos los resultados del modelo para vacunados y no vacunados.
    vacunados = pd.DataFrame({"EDAD_ANOS": edades, "VACUNACION": 1})
    pred_vacunados = modelo.get_prediction(vacunados)
    ic_vacunados = pred_vacunados.conf_int()

    vacunados["mean"] = pred_vacunados.predicted_mean * 100
    vacunados["lower"] = ic_vacunados[:, 0] * 100
    vacunados["upper"] = ic_vacunados[:, 1] * 100

    no_vacunados = pd.DataFrame({"EDAD_ANOS": edades, "VACUNACION": 0})
    pred_no_vacunados = modelo.get_prediction(no_vacunados)
    ic_no_vacunados = pred_no_vacunados.conf_int()

    no_vacunados["mean"] = pred_no_vacunados.predicted_mean * 100
    no_vacunados["lower"] = ic_no_vacunados[:, 0] * 100
    no_vacunados["upper"] = ic_no_vacunados[:, 1] * 100

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Vamos a crear dos bandas continuas, una para vacunados y otra para no vacunados.
    fig = go.Figure()

    # Para generar una banda necesitamos convertir las series a listas.
    x = vacunados["EDAD_ANOS"].tolist()
    upper = vacunados["upper"].tolist()
    lower = vacunados["lower"].tolist()

    fig.add_traces(
        go.Scatter(
            x=x + x[::-1],
            y=upper + lower[::-1],
            fill="toself",
            mode="lines",
            name="Vacunados (IC 95%)",
            line_width=2,
            line_color="hsla(190, 100, 50, 0.4)",
            legendrank=2,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=vacunados["EDAD_ANOS"],
            y=vacunados["mean"],
            mode="lines",
            name="Vacunados (media)",
            line_width=2,
            line_color="hsla(190, 100, 80, 1)",
            legendrank=1,
        )
    )

    x = no_vacunados["EDAD_ANOS"].tolist()
    upper = no_vacunados["upper"].tolist()
    lower = no_vacunados["lower"].tolist()

    fig.add_traces(
        go.Scatter(
            x=x + x[::-1],
            y=upper + lower[::-1],
            fill="toself",
            mode="lines",
            name="No vacunados (IC 95%)",
            line_width=2,
            line_color="hsla(35, 100, 50, 0.4)",
            legendrank=4,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=no_vacunados["EDAD_ANOS"],
            y=no_vacunados["mean"],
            mode="lines",
            name="No vacunados (media)",
            line_width=2,
            line_color="hsla(35, 100, 80, 1)",
            legendrank=3,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Probabilidad estimada de presentar complicaciones",
        ticksuffix="%",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_title=" <b>Estado de vacunación</b> ",
        legend_bordercolor="#FFFFFF",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Riesgo de complicaciones en casos de sarampión según vacunación en México ({año})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=160,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Edad al momento del diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./riesgo_{año}.png")


def tasas_edad_sexo(*años):
    """
    Crea una gráfica de dispersión mostrando las distintas
    tasas de incidencia de sarampión por grupo de edad y sexo.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de la población de hombres por grupos de edad.
    hombres_pop = pd.read_csv("./assets/poblacion_quinquenal/hombres.csv", index_col=0)

    # Seleccionamos la población del año (o años) que nos interesa.
    hombres_pop = hombres_pop[[str(año) for año in años]].mean(axis=1)

    # Cargamos el dataset de la población de mujeres por grupos de edad.
    mujeres_pop = pd.read_csv("./assets/poblacion_quinquenal/mujeres.csv", index_col=0)

    # Seleccionamos la población del año (o años) que nos interesa.
    mujeres_pop = mujeres_pop[[str(año) for año in años]].mean(axis=1)

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(
            pd.read_csv(
                f"./data/{año}.csv", dtype={"ENTIDAD_RES": str, "MUNICIPIO_RES": str}
            )
        )

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Categorizamos la edad.
    df["EDAD_ANOS"] = pd.cut(
        df["EDAD_ANOS"], bins=BINS, labels=LABELS, include_lowest=True
    )

    # Contamos el total de registros por grupo de edad y sexo.
    df = df.pivot_table(
        index="EDAD_ANOS",
        columns="SEXO",
        values="DIAGNOSTICO",
        aggfunc="count",
        observed=True,
    )

    # Agregamos la columna de población para cada sexo.
    df["poblacion_hombres"] = hombres_pop
    df["poblacion_mujeres"] = mujeres_pop

    # Calculamos la tasa por cada 100,000 hombres para cada grupo de edad.
    df["tasa_hombres"] = df[2] / df["poblacion_hombres"] * 100000
    df["tasa_mujeres"] = df[1] / df["poblacion_mujeres"] * 100000

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    # Agregamos la gráfica de dispersión para hombres.
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["tasa_hombres"],
            mode="markers",
            name=f"<b>Hombres</b><br>{df[2].sum():,.0f} casos",
            marker_color="#00e5ff",
            marker_symbol="circle-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    # Agregamos la gráfica de dispersión para mujeres.
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["tasa_mujeres"],
            mode="markers",
            name=f"<b>Mujeres</b><br>{df[1].sum():,.0f} casos",
            marker_color="#ffea00",
            marker_symbol="diamond-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    fig.update_xaxes(
        range=[-0.7, len(df) - 0.3],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
    )

    fig.update_yaxes(
        range=[-0.8, None],
        title="Tasa por cada 100,000 hombres/mujeres dentro del grupo de edad",
        ticks="outside",
        title_font_size=22,
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    # Personalizamos la leyenda y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Incidencia de sarampión en México según edad y sexo de la persona infectada durante {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=130,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Grupo de edad al momento del diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./tasas_edad_{año}.png")


def cobertura_vacunacion(*años):
    """
    Crea una gráfica de barras comparando la cobertura
    de vacunación por grupo etario y tipo de caso.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(pd.read_csv(f"./data/{año}.csv"))

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Modificamos la columna de vacunación para que sean ceros (no vacunados) y unos (vacunados).
    df["VACUNACION"] = df["VACUNACION"].map({2: 0, 1: 1})

    # Separamos los registros en dos categorías principales.
    confirmados = df[df["DIAGNOSTICO"] == 1]
    descartados = df[df["DIAGNOSTICO"] == 3]

    data = list()

    # Iteramos y filtramos por cada grupo etario.
    for a, b in GRUPOS_ETARIOS:
        temp_confirmados = confirmados[confirmados["EDAD_ANOS"].between(a, b)]
        temp_descartados = descartados[descartados["EDAD_ANOS"].between(a, b)]

        # Vamos a calcular el intervalo de confianza
        # usando bootstrap. Uno para casos confirmados
        # y otro para casos descartados.
        resultado_confirmados = bootstrap(
            (temp_confirmados["VACUNACION"],),
            statistic=np.mean,
            confidence_level=0.95,
            rng=12345,
            vectorized=False,
        )

        resultado_descartados = bootstrap(
            (temp_descartados["VACUNACION"],),
            statistic=np.mean,
            confidence_level=0.95,
            rng=12345,
            vectorized=False,
        )

        # Extraemos los resultados.
        data.append(
            {
                "edad": f"{a}-{b}",
                "confirmados_low": resultado_confirmados.confidence_interval.low,
                "confirmados_mean": temp_confirmados["VACUNACION"].mean(),
                "confirmados_high": resultado_confirmados.confidence_interval.high,
                "descartados_low": resultado_descartados.confidence_interval.low,
                "descartados_mean": temp_descartados["VACUNACION"].mean(),
                "descartados_high": resultado_descartados.confidence_interval.high,
            }
        )

    # Consolidamos los resultados en un nuevo DataFrame.
    final = pd.DataFrame.from_dict(data)

    # Renombramos un par de grupos etarios.
    final["edad"] = final["edad"].replace({"0-0": "<1", "65-120": "≥65"})
    final.set_index("edad", inplace=True)

    # Convertimos todas las cifras a porcentaje.
    final *= 100

    # Dependiendo de cuantos años fueron analizados será el título y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    # Agregamos la gráfica de barras para casos confirmados.
    fig.add_trace(
        go.Bar(
            x=final.index,
            y=final["confirmados_mean"],
            name=f"Positivo para sarampión<br>(total: <b>{len(confirmados):,.0f}</b>)",
            marker_color="#ff6f00",
            marker_line_width=0,
            error_y_array=final["confirmados_high"] - final["confirmados_mean"],
            error_y_arrayminus=final["confirmados_mean"] - final["confirmados_low"],
            error_y_type="data",
            error_y_color="#FFFFFF",
            error_y_width=8,
            error_y_thickness=4,
        )
    )

    # Agregamos la gráfica de barras para casos descartados.
    fig.add_trace(
        go.Bar(
            x=final.index,
            y=final["descartados_mean"],
            name=f"Descartado por sarampión<br>(total: <b>{len(descartados):,.0f}</b>)",
            marker_color="#00897b",
            marker_line_width=0,
            error_y_array=final["descartados_high"] - final["descartados_mean"],
            error_y_arrayminus=final["descartados_mean"] - final["descartados_low"],
            error_y_type="data",
            error_y_color="#FFFFFF",
            error_y_width=8,
            error_y_thickness=4,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
    )

    fig.update_yaxes(
        title="Cobertura de vacunación (con intervalo de confianza al 95%)",
        ticks="outside",
        ticksuffix="%",
        title_font_size=22,
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    # Personalizamos la leyenda y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_title=" <b>Diagnóstico del caso</b> ",
        legend_bordercolor="#FFFFFF",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Cobertura de vacunación en personas sospechosas por sarampión en México durante {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=150,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Grupo de edad al momento del diagnóstico",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./vacunacion_{año}.png")


if __name__ == "__main__":
    tendencia_semanal(2025)
    tendencia_mensual(2025, 2026)

    tendencia_semanal_origen(2025, "right")
    tendencia_mensual_origen(2025, 2026)

    evolucion_casos(2025, 2026)
    defunciones(2025, 2026)
    razon_riesgo(2025, 2026)
    tasas_edad_sexo(2025, 2026)
    cobertura_vacunacion(2025, 2026)
