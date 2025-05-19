import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# La fecha del corte de los datos.
FECHA_FUENTE = "07/05/2025"

# Estos colores serán la paleta para todas las gráficas.
PLOT_COLOR = "#1A1A1D"
PAPER_COLOR = "#3B1C32"


EDADES = [
    (0, 4),
    (5, 9),
    (10, 14),
    (15, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 44),
    (45, 49),
    (50, 54),
    (55, 59),
    (60, 64),
    (65, 69),
    (70, 74),
    (75, 79),
    (80, 84),
    (85, 120),
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


def tsas_edad_sexo(año):
    """
    Crea una gráfica de dispersión mostrando las distintas
    tasas de incidencia de sarampión por grupo de edad y sexo.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset del año especificado.
    df = pd.read_csv(f"./data/{año}.csv")

    # Seleccionamos los casos confirmados de sarampión.
    df = df[df["DIAGNOSTICO"] == 1]

    data = list()

    # Iteramos sobre todos nuestros grupos de edad y contamos los registros
    # para cada uno.
    for a, b in EDADES:
        temp_mujeres = df[(df["SEXO"] == 1) & (df["EDAD_ANOS"].between(a, b))]
        temp_hombres = df[(df["SEXO"] == 2) & (df["EDAD_ANOS"].between(a, b))]

        # Para el último grupo de edad le agregamos el símbolo de 'mayor o igual que'
        # para que coincida con el índice de los datasets de población quinquenal.
        data.append(
            {
                "edad": f"{a}-{b}" if a < 85 else "≥85",
                "mujeres": len(temp_mujeres),
                "hombres": len(temp_hombres),
            }
        )

    # Creamos un DataFrame con los conteos de cada grupo de edad y sexo.
    final = pd.DataFrame.from_records(data, index="edad")

    # Cargamos el dataset de la población de hombres por grupos de edad.
    hombres_pop = pd.read_csv("./assets/poblacion_quinquenal/hombres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    hombres_pop = hombres_pop["2025"]

    # Agregamos la columna de población de hombres.
    final["poblacion_hombres"] = hombres_pop

    # Calculamos la tasa por cada 100k hombres para cada grupo de edad.
    final["tasa_hombres"] = final["hombres"] / final["poblacion_hombres"] * 100000

    # Cargamos el dataset de la población de mujeres por grupos de edad.
    mujeres_pop = pd.read_csv("./assets/poblacion_quinquenal/mujeres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    mujeres_pop = mujeres_pop["2025"]

    # Agregamos la columna de población de mujeres.
    final["poblacion_mujeres"] = mujeres_pop

    # Calculamos la tasa por cada 100k mujeres para cada grupo de edad.
    final["tasa_mujeres"] = final["mujeres"] / final["poblacion_mujeres"] * 100000

    fig = go.Figure()

    # Agregamos la gráfica de dispersión para hombres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_hombres"],
            mode="markers",
            name=f"<b>Hombres</b><br>{final['hombres'].sum():,.0f} casos",
            marker_color="#00e5ff",
            marker_symbol="circle-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    # Agregamos la gráfica de dispersión para mujeres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_mujeres"],
            mode="markers",
            name=f"<b>Mujeres</b><br>{final['mujeres'].sum():,.0f} casos",
            marker_color="#ffea00",
            marker_symbol="diamond-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    fig.update_xaxes(
        range=[-0.7, len(final) - 0.3],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(final) + 1,
    )

    fig.update_yaxes(
        range=[-0.09, None],
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
        title_text=f"Incidencia de sarampión en <b>México</b> según edad y sexo de la persona infectada ({año})",
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
                text="Grupo de edad al momento de la infección",
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


def tendencia(año):
    """
    Genera una gráfica de barras con la incidencia
    semanal de sarampión.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    """

    # Cargamos el dataset del año especificado.
    df = pd.read_csv("./data/2025.csv")

    # Quitamos las fechas inválidas.
    df = df[df["FECHA_DIAGNOSTICO"] != "9999-99-99"]

    # Convertimos el resto de fechas a datetime.
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

    # Creamos las etiquetas para nuestro eje horizontal.
    etiquetas = [f"{item.day:02}<br>{MESES[item.month]}" for item in df.index]

    # Crearemos una gráfica de barras apilada.
    # Una será de casos confirmados y otra de casos descartados.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[1],
            name=f"Positivo para sarampión<br>(total acumulado: <b>{df[1].sum():,.0f}</b>)",
            marker_line_width=0,
            marker_color="#f57c00",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df[3],
            name=f"Descartado por sarampión<br>(total acumulado: <b>{df[3].sum():,.0f}</b>)",
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
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=24,
        title_text="Evolución de la incidencia de <b>sarampión</b> en México durante el 2025",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor="#1A1A1D",
        paper_bgcolor="#3B1C32",
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
    fig.write_image(f"./tendencia_{año}.png")


def evolucion_casos(año):
    """
    Genera un diagrama sankey con la evolución
    de los casos confirmados de sarampión.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

    """

    # Cargamos el dataset del año especificado.
    df = pd.read_csv("./data/2025.csv")

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
    epsilon = 30

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
                    "#bdbdbd",
                    "#bdbdbd",
                    "#d32f2f",
                    "#bdbdbd",
                ],
            ),
            link=dict(
                color="hsla(0, 100, 100, 0.25)",
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
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=24,
        title_text="Evolución de los casos confirmados de <b>sarampión</b> en México durante el 2025",
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_r=40,
        margin_b=160,
        margin_l=140,
        title_font_size=36,
        plot_bgcolor="#1A1A1D",
        paper_bgcolor="#3B1C32",
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


def crear_tabla_absolutos(año):
    """
    Genera una tabla con la incidencia de sarampión
    por municipio de residencia.

    Parameters
    ----------
    año : int
        El año que se desea graficar.

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

    # Contamos los registros por municipio.
    df = df["CVE"].value_counts().to_frame("total")

    # Unimos los DataFrames.
    df = df.join(pop)

    # Calculamos la tasa por cada 100k habitantes.
    df["tasa"] = df["total"] / df["poblacion"] * 100000

    # Juntamos el nombre del municipio con la entidad.
    df["nombre"] = df["municipio"] + ", " + df["entidad"]

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
                    "<b>Municipio, Entidad</b>",
                    "<b>No. casos ↓</b>",
                    "<b>Tasa 100k habs.</b>",
                ],
                font_color="#FFFFFF",
                fill_color=["#00897b", "#00897b", "#e65100", "#00897b"],
                line_width=0.75,
                align="center",
                height=28,
            ),
            cells=dict(
                values=[df.index, df["nombre"], df["total"], df["tasa"]],
                line_width=0.75,
                fill_color=PLOT_COLOR,
                height=28,
                format=["", "", ",.0f", ",.1f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        showlegend=False,
        width=840,
        height=1050,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=16,
        margin_t=110,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=24,
        title_text=f"Los 30 municipios de <b>México</b> con la mayor<br><b>incidencia</b> de sarampión durante el {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.015,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SSA ({FECHA_FUENTE})",
            ),
            dict(
                x=0.57,
                y=0.015,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01, y=0.015, xanchor="right", yanchor="top", text="🧁 @lapanquecita"
            ),
        ],
    )

    # Nombramos el archivo resultante con los parámetros de la función.
    fig.write_image(f"./tabla_{año}.png")


if __name__ == "__main__":
    tsas_edad_sexo(2025)
    evolucion_casos(2025)
    tendencia(2025)
    crear_tabla_absolutos(2025)
