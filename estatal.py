import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# La fecha del corte de los datos.
FECHA_FUENTE = "12/06/2025"

# Estos colores serán la paleta para todas las gráficas.
PLOT_COLOR = "#1A1A1D"
PAPER_COLOR = "#3B1C32"


ENTIDADES = {
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
    99: "Se desconoce",
}


def crear_mapa(año, entidad):
    """
    Genera un mapa choropleth con la incidencia de sarampión
    por municipio de la entidad y año especificados.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    entidad : int
        La entidad que se desea graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    # Renombramos algunos estados a sus nombres más comunes.
    pop["Entidad"] = pop["Entidad"].replace(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Seleccionamos solo los municipios de la entidad de nuestro interés.
    pop = pop[pop["Entidad"] == ENTIDADES[entidad]]

    # Seleccionamos la población del año especificado.
    pop = pop[str(año)]

    # Calculamos la población total de la entidad.
    poblacion_total = pop.sum()

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(
        f"./data/{año}.csv",
        dtype={"ENTIDAD_RES": str, "MUNICIPIO_RES": str},
    )

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Seleccionamos solo los registros de la entidad especificada.
    df = df[df["ENTIDAD_RES"] == str(entidad)]

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
    df = df.dropna(axis=0)

    # Obtenemos la tasa mínima y la máxima.
    # Para la máxima usaremos el percentil 95
    # debido a que hay valores atípicos.
    valor_min = df["tasa"].min()
    valor_max = df["tasa"].quantile(0.95)

    # Vamos a crear nuestra escala con 13 intervalos.
    marcas = np.linspace(valor_min, valor_max, 13)
    etiquetas = list()

    for item in marcas:
        if item >= 10:
            etiquetas.append(f"{item:,.0f}")
        else:
            etiquetas.append(f"{item:,.1f}")

    # A la última etiqueta le agregamos el símbolo de 'mayor o igual que'.
    etiquetas[-1] = f"≥{valor_max:,.0f}"

    # Cargamos el archivo GeoJSON de la enitdad especificada.
    geojson = json.load(
        open(f"./assets/{ENTIDADES[entidad]}.json", "r", encoding="utf-8")
    )

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
            colorscale="portland",
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
        # projection_type="mercator",
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
                text=f"Tasas de incidencia de sarampión en <b>{ENTIDADES[entidad]}</b> durante el {año}",
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
    fig.write_image(f"./mapa_{año}_{entidad}.png")


def crear_tabla_absolutos(año, entidad):
    """
    Genera una tabla con la incidencia de sarampión
    por municipio de la entidad y año especificados.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    entidad : int
        La entidad que se desea graficar.

    """

    # Cargamos el dataset de población por municipio.
    pop = pd.read_csv("./assets/poblacion.csv", dtype={"CVE": str}, index_col=0)

    # Renombramos algunos estados a sus nombres más comunes.
    pop["Entidad"] = pop["Entidad"].replace(
        {
            "Coahuila de Zaragoza": "Coahuila",
            "México": "Estado de México",
            "Michoacán de Ocampo": "Michoacán",
            "Veracruz de Ignacio de la Llave": "Veracruz",
        }
    )

    # Seleccionamos las columnas de nuestro interés.
    pop = pop[["Entidad", "Municipio", str(año)]]

    # Renombramos las columnas.
    pop.columns = ["entidad", "municipio", "poblacion"]

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(
        f"./data/{año}.csv",
        dtype={"ENTIDAD_RES": str, "MUNICIPIO_RES": str},
    )

    # Creamos el CVE para entidad y municipio.
    df["CVE"] = df["ENTIDAD_RES"].str.zfill(2) + df["MUNICIPIO_RES"].str.zfill(3)

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    # Seleccionamos solo los registros de la entidad especificada.
    df = df[df["ENTIDAD_RES"] == str(entidad)]

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos los DataFrames.
    df = df.join(pop)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Ordenamos los resultados por número de registros de mayor a menor.
    df.sort_values("total", ascending=False, inplace=True)

    # Reseteamos el índice y solo escogemos el top 30.
    df.reset_index(inplace=True)
    df.index += 1

    df = df.head(30)

    # Por ahora el subtítulo no será usado.
    subtitulo = ""

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[50, 200, 80, 100],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio</b>",
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
                values=[df.index, df["municipio"], df["total"], df["tasa"]],
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
        title_text=f"Los 30 municipios de <b>{ENTIDADES[entidad]}</b> con la mayor<br><b>incidencia</b> de sarampión durante el {año}",
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
                x=1.01, y=0.02, xanchor="right", yanchor="top", text="🧁 @lapanquecita"
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./tabla_{año}_{entidad}.png")


if __name__ == "__main__":
    crear_mapa(2025, 8)
    crear_tabla_absolutos(2025, 8)
