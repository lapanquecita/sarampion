import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


# La fecha del corte de los datos.
FECHA_FUENTE = "09/03/2026"

# Estos colores serán la paleta para todas las gráficas.
PLOT_COLOR = "#1A1A1D"
PAPER_COLOR = "#3B1C32"


# para poder referenciar cada entidad con su clave numérica.
ENTIDADES = {
    0: "México",
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}


def crear_mapa(entidad_id, *años):
    """
    Genera un mapa choropleth con la incidencia de sarampión
    por municipio de la entidad y año(s) especificados.

    Parameters
    ----------
    entidad_id : int
        La entidad que se desea graficar.

    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    # Seleccionamos solo los municipios de la entidad de nuestro interés.
    pop = pop[pop["Entidad"] == ENTIDADES[entidad_id]]

    # Seleccionamos la población del año especificado.
    # Si son múltiples años, los promediamos.
    pop = pop[[str(año) for año in años]].mean(axis=1)

    # Calculamos la población total de la entidad.
    poblacion_total = pop.sum()

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

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Seleccionamos solo los registros de la entidad especificada.
    df = df[df["CVE"].str.startswith(str(entidad_id).zfill(2))]

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Agregamos la población para cada municipio.
    df["poblacion"] = pop

    # Calculamos la tasa por cada 100,000 habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Calculamos el total de casos confirmados.
    total_casos = df["total"].sum()

    # Calculamos la tasa de incidencia estatal.
    tasa_estatal = total_casos / poblacion_total * 100000

    # Preparamos el subtítulo.
    subtitulo = f"Tasa estatal: <b>{tasa_estatal:,.1f}</b> (con <b>{total_casos:,.0f}</b> casos confirmados)"

    # Quitamos los valores NaN para no distorsionar los siguientes cálculos.
    # df = df.dropna(axis=0)

    # Obtenemos la tasa mínima y la máxima.
    # Para la máxima usaremos el percentil 95
    # debido a que hay valores atípicos.
    valor_min = np.nanmin(df["tasa"])
    valor_max = np.quantile(df["tasa"], 0.95)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        if item >= 10:
            etiquetas.append(f"{item:,.0f}")
        else:
            etiquetas.append(f"{item:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el archivo GeoJSON de la enitdad especificada.
    geojson = json.load(
        open(f"./assets/{ENTIDADES[entidad_id]}.json", "r", encoding="utf-8")
    )

    # Dependiendo de cuantos años fueron analizados será el titulo y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    # Nuestro mapa choropleth tendrá dos capas.
    # La primera mostrará la intensidad de la incidencia
    # y la segunda será para mostrar la división política.
    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["tasa"],
            featureidkey="properties.CVEGEO",
            colorscale="matter_r",
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.065,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=24,
            ),
        )
    )

    # Esta es la capa de la división política.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=pop.index,
            z=[1 for _ in range(len(pop))],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0,0,0,0)", "hsla(0,0,0,0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=2,
            zmin=0,
            zmax=1,
            showscale=False,
        )
    )

    # Para el tipo de proyección debemos escoger entre
    # mercator y orthographic dependiendo de la geometría de la entidad.
    fig.update_geos(
        fitbounds="geojson",
        projection_type="orthographic",
        showocean=True,
        oceancolor="#000000",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#000000",
    )

    fig.update_layout(
        showlegend=False,
        legend_xanchor="left",
        legend_yanchor="bottom",
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=1.0,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=0,
        margin_b=80,
        margin_l=0,
        width=2000,
        height=2000,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.015,
                xanchor="center",
                yanchor="top",
                text=f"Tasas de incidencia de sarampión en <b>{ENTIDADES[entidad_id]}</b> durante {año}",
                font_size=40,
            ),
            dict(
                x=0.06,
                y=0.48,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
            ),
            dict(
                x=0.05,
                y=-0.03,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.03,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=0.96,
                y=-0.03,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./mapa_{año}_{entidad_id}.png")


def crear_mapa_estatal(*años):
    """
    Crea un mapa choropleth con la incidencia de sarampión
    por entidad para los años especificados.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv")

    # Agrupamos por entidad.
    pop = pop.groupby("Entidad").sum(numeric_only=True)

    # Seleccionamos la población del año especificado.
    # Si son múltiples años, los promediamos.
    pop = pop[[str(año) for año in años]].mean(axis=1)

    # Esta lista será utilizada para agrupar los DataFrames.
    dfs = list()

    # Vamos a iterar sobre cada año y cargar el dataset correspondiente.
    for año in años:
        dfs.append(pd.read_csv(f"./data/{año}.csv"))

    # Unimos todos los DataFrames en uno solo.
    df = pd.concat(dfs)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Preparamos el subtítulo con los datos a nivel nacional.
    total_casos = len(df)
    total_oblacion = pop.sum()

    subtitulo = f"Tasa nacional: <b>{total_casos / total_oblacion * 100000:,.1f}</b> (con <b>{total_casos:,.0f}</b> casos)"

    # Seleccionamos los registros de residentes de México.
    df = df[df["ENTIDAD_RES"].between(1, 32)]

    # Contamos el número de registros por entidad de residencia y sexo.
    df = df.pivot_table(
        index="ENTIDAD_RES",
        columns="SEXO",
        values="DIAGNOSTICO",
        aggfunc="count",
        fill_value=0,
    )

    # Calculamos el total por entidad.
    df["total"] = df.sum(axis=1)

    # Convertimos los identificadores de entidad a sus nombres comunes.
    df.index = df.index.map(ENTIDADES)

    # Agregamos la población y calculamos las tasas.
    df["pop"] = pop
    df["tasa"] = df["total"] / df["pop"] * 100000

    # Ordenamos de mayor a menor tasa.
    df.sort_values("tasa", ascending=False, inplace=True)

    # Obtenemos la tasa mínima y la máxima.
    # Para la máxima usaremos el percentil 95
    # debido a que hay valores atípicos.
    valor_min = np.nanmin(df["tasa"])
    valor_max = np.quantile(df["tasa"], 0.95)

    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = [f"{item:,.1f}" for item in marcas]

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el archivo GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    # Dependiendo de cuantos años fueron analizados será el titulo y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    # Vamos a crear un mapa Choropleth con todas las variables anteriormente definidas.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["tasa"],
            featureidkey="properties.NOM_ENT",
            colorscale="matter_r",
            marker_line_color="#FFFFFF",
            marker_line_width=1.5,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#FFFFFF",
                ticklen=10,
            ),
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor=PLOT_COLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=40,
        margin_b=60,
        margin_l=40,
        width=1920,
        height=1080,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.025,
                xanchor="center",
                yanchor="top",
                text=f"Tasas de incidencia de sarampión en México por entidad de residencia durante {año}",
                font_size=42,
            ),
            dict(
                x=0.0275,
                y=0.46,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
            ),
            dict(
                x=0.01,
                y=-0.056,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.056,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=-0.056,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./0.png")

    # Vamos a crear dos tablas, cada una con la información de 16 entidades.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[160, 90],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#00897b", "#00897b", "#00897b", "#00897b", "#e65100"],
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df[2][:16],
                    df[1][:16],
                    df["total"][:16],
                    df["tasa"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",", ",", ",", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[160, 90],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Hombres</b>",
                    "<b>Mujeres</b>",
                    "<b>Total</b>",
                    "<b>Tasa ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#00897b", "#00897b", "#00897b", "#00897b", "#e65100"],
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df[2][16:],
                    df[1][16:],
                    df["total"][16:],
                    df["tasa"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",", ",", ",", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1920,
        height=840,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=25,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_COLOR,
    )

    fig.write_image("./1.png")

    # Unimos el mapa y las tablas en una sola imagen.
    image1 = Image.open("./0.png")
    image2 = Image.open("./1.png")

    result_width = image1.width
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save(f"./mapa_estatal_{año}.png")

    # Borramos las imágenes originales.
    os.remove("./0.png")
    os.remove("./1.png")


def crear_mapa_municipal(*años):
    """
    Crea un mapa choropleth con la incidencia de sarampión
    por municipio para los años especificados.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    # Seleccionamos la población del año especificado.
    # Si son múltiples años, los promediamos.
    pop = pop[[str(año) for año in años]].mean(axis=1)

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

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Agregamos la población y calculamos las tasas.
    df["pop"] = pop
    df["tasa"] = df["total"] / df["pop"] * 100000

    # Calculamos los totaales nacionales.
    total_nacional = df["total"].sum()
    poblacion_nacional = pop.sum()

    # Preparamos los valores para nuestro subtítulo.
    subtitulo = f"Tasa nacional: <b>{total_nacional / poblacion_nacional * 100000:,.1f}</b> (con <b>{total_nacional:,.0f}</b> casos)"

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = [
        "Estadísticas descriptivas",
        "<b>(tasa bruta)</b>",
        f"Media: <b>{np.nanmean(df['tasa']):,.1f}</b>",
        f"Mediana: <b>{np.nanmedian(df['tasa']):,.1f}</b>",
        f"DE: <b>{np.nanstd(df['tasa']):,.1f}</b>",
        f"25%: <b>{np.nanquantile(df['tasa'], 0.25):,.1f}</b>",
        f"75%: <b>{np.nanquantile(df['tasa'], 0.75):,.1f}</b>",
        f"95%: <b>{np.nanquantile(df['tasa'], 0.95):,.1f}</b>",
        f"Máximo: <b>{np.nanmax(df['tasa']):,.1f}</b>",
    ]

    estadisticas = "<br>".join(estadisticas)

    # Determinamos los valores mínimos y máximos para nuestra escala.
    # Obtenemos la tasa mínima y la máxima.
    # Para la máxima usaremos el percentil 95
    # debido a que hay valores atípicos.
    valor_min = np.nanmin(df["tasa"])
    valor_max = np.nanquantile(df["tasa"], 0.95)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        if item >= 10:
            etiquetas.append(f"{item:,.0f}")
        else:
            etiquetas.append(f"{item:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{etiquetas[-1]}"

    # Cargamos el GeoJSON de municipios de México.
    geojson = json.loads(open("./assets/municipios.json", "r", encoding="utf-8").read())

    # Dependiendo de cuantos años fueron analizados será el titulo y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["tasa"],
            featureidkey="properties.CVEGEO",
            colorscale="matter_r",
            marker_line_color="#FFFFFF",
            marker_line_width=1,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.035,
                y=0.5,
                thickness=150,
                ypad=400,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
            ),
        )
    )

    # Vamos a sobreponer otro mapa Choropleth, el cual
    # tiene el único propósito de mostrar la división política
    # de las entidades federativas.

    # Cargamos el archivo GeoJSON de México.
    geojson_borde = json.loads(
        open("./assets/mexico.json", "r", encoding="utf-8").read()
    )

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson_borde,
            locations=[f"{i:02}" for i in range(1, 33)],
            z=[1 for _ in range(32)],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0, 0, 0, 0)", "hsla(0, 0, 0, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor="#092635",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#000000",
    )

    # Agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Tasas de incidencia de sarampión en México por municipio de residencia durante {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.49,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Tasa bruta por cada 100,000 habitantes",
                font_size=100,
            ),
            dict(
                x=0.98,
                y=0.9,
                xanchor="right",
                yanchor="top",
                text=estadisticas,
                align="left",
                borderpad=30,
                bordercolor="#FFFFFF",
                bgcolor="#000000",
                borderwidth=5,
                font_size=120,
            ),
            dict(
                x=0.01,
                y=-0.003,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
                font_size=120,
            ),
            dict(
                x=0.5,
                y=-0.003,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
                font_size=120,
            ),
            dict(
                x=1.0,
                y=-0.003,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=120,
            ),
        ],
    )

    fig.write_image(f"./mapa_municipal_{año}.png")


def crear_tabla_absolutos(*años):
    """
    Crea una tabla listando los municipios con
    mayor incidencia absoluta de sarampión.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    # Seleccionamos la población del año especificado.
    # Si son múltiples años, los promediamos.
    pop["poblacion"] = pop[[str(año) for año in años]].mean(axis=1)

    # Seleccionamos las columnas de nuestro interés.
    pop = pop[["Entidad", "Municipio", "poblacion"]]

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

    # Quitamos municipios no identificados.
    df = df[df["MUNICIPIO_RES"] != "999"]

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos los DataFrames.
    df = df.join(pop)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Juntamos el nombre del municipio con la entidad.
    df["nombre"] = df["Municipio"] + ", " + df["Entidad"]

    # Ordenamos los resultados por número de registros de mayor a menor.
    df.sort_values(["total", "tasa"], ascending=False, inplace=True)

    # Reseteamos el índice y solo escogemos el top 30.
    df.reset_index(inplace=True)
    df.index += 1

    df = df.head(30)

    # Por ahora el subtítulo no será usado.
    subtitulo = ""

    # Dependiendo de cuantos años fueron analizados será el titulo y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[40, 210, 80, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>No. casos ↓</b>",
                    "<b>Tasa 100k habs.</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#00897b", "#00897b", "#e65100", "#00897b"],
                line_width=0.75,
                align="center",
                height=43,
            ),
            cells=dict(
                values=[df.index, df["nombre"], df["total"], df["tasa"]],
                line_width=0.75,
                fill_color=PLOT_COLOR,
                height=43,
                format=["", "", ",.0f", ",.1f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=25,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text=f"Los 30 municipios de México con la mayor<br><b>incidencia</b> de sarampión durante {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.02,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.02,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.02,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./tabla_absolutos_{año}.png")


def crear_tabla_tasa(*años):
    """
    Crea una tabla listando los municipios con
    mayor tasa de incidencia de sarampión.

    Parameters
    ----------
    años : list
        Los años que nos interesa graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    pop["poblacion"] = pop[[str(año) for año in años]].mean(axis=1)

    # Seleccionamos las columnas de nuestro interés.
    pop = pop[["Entidad", "Municipio", "poblacion"]]

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

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos los DataFrames.
    df = df.join(pop)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Juntamos el nombre del municipio con la entidad.
    df["nombre"] = df["Municipio"] + ", " + df["Entidad"]

    # Ordenamos los resultados por la tasa ajustada por población.
    df.sort_values(["tasa", "tasa"], ascending=False, inplace=True)

    # Reseteamos el índice y solo escogemos el top 30.
    df.reset_index(inplace=True)
    df.index += 1

    df = df.head(30)

    # Por ahora el subtítulo no será usado.
    subtitulo = ""

    # Dependiendo de cuantos años fueron analizados será el titulo y nombre de archivo.
    if len(años) == 1:
        año = años[0]
    else:
        año = f"{min(años)}-{max(años)}"

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[40, 210, 80, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>No. casos</b>",
                    "<b>Tasa 100k habs. ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#00897b", "#00897b", "#00897b", "#e65100"],
                line_width=0.75,
                align="center",
                height=43,
            ),
            cells=dict(
                values=[df.index, df["nombre"], df["total"], df["tasa"]],
                line_width=0.75,
                fill_color=PLOT_COLOR,
                height=43,
                format=["", "", ",.0f", ",.1f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=25,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text=f"Los 30 municipios de México con la mayor<br><b>tasa</b> de sarampión durante {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.02,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.02,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.02,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./tabla_absolutos_tasa_{año}.png")


if __name__ == "__main__":
    crear_mapa(8, 2025, 2026)
    crear_mapa(14, 2025, 2026)

    crear_mapa_estatal(2025, 2026)
    crear_mapa_municipal(2025, 2026)
    crear_tabla_absolutos(2025, 2026)
    crear_tabla_tasa(2025, 2026)