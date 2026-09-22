import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

AZUL = "#2a78d6"
AZUL_CLARO = "#a9c8ee"
GRIS = "#52514e"
GRIS_CLARO = "#e1e0d9"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["text.color"] = "#0b0b0b"
plt.rcParams["axes.edgecolor"] = GRIS_CLARO
plt.rcParams["axes.labelcolor"] = GRIS
plt.rcParams["xtick.color"] = GRIS
plt.rcParams["ytick.color"] = "#0b0b0b"


def fmt_miles_millones(v):
    s = f"{v/1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${s} mil M"


def graficar_ranking(top_gasto, out_path):
    nombres = [n for n, _ in reversed(top_gasto)]
    valores = [v for _, v in reversed(top_gasto)]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
    colors = [AZUL if i >= len(valores)-3 else AZUL_CLARO for i in range(len(valores))]
    bars = ax.barh(nombres, valores, color=colors, height=0.65)
    ax.set_xlabel("Gasto real en personal (pesos)")
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False)
    ax.set_xlim(0, max(valores) * 1.18)
    for bar, v in zip(bars, valores):
        ax.text(bar.get_width() + max(valores)*0.012, bar.get_y() + bar.get_height()/2,
                 fmt_miles_millones(v), va="center", ha="left", fontsize=8, color="#0b0b0b")
    ax.xaxis.set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def graficar_evolucion(dotacion_serie, out_path):
    # dotacion_serie es trimestral (DIPRES, Informe Trimestral de Empleo en el Sector Público):
    # se grafica por índice para no repetir el año 4 veces en el eje, y solo se etiqueta
    # el corte de marzo de cada año.
    totales = [d["total"] for d in dotacion_serie]
    x = list(range(len(dotacion_serie)))
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    ax.plot(x, totales, color=AZUL, linewidth=2.2, marker="o", markersize=3)
    ax.fill_between(x, totales, color=AZUL, alpha=0.12)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(GRIS_CLARO)
    ax.spines["bottom"].set_color(GRIS_CLARO)
    ax.set_ylim(0, max(totales)*1.15)
    tick_pos = [i for i, d in enumerate(dotacion_serie) if d.get("trim") == "mar"]
    tick_labels = [dotacion_serie[i]["anio"] for i in tick_pos]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labels, fontsize=8)
    ax.yaxis.set_major_formatter(lambda x, pos: f"{int(x/1000)}k")
    ax.tick_params(labelsize=8)
    plt.tight_layout()
    plt.savefig(out_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
