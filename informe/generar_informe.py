#!/usr/bin/env python3
"""Genera el informe mensual (PDF) de Radiografía de Sueldos a partir de
public/dashboard.html del repo radiografia-sueldos. Uso:
    python3 generar_informe.py <mes_es> <anio> <ruta_dashboard_html> <salida.pdf>
Ej:
    python3 generar_informe.py Julio 2026 /home/user/radiografia-sueldos/public/dashboard.html informe.pdf
"""
import sys, json, re, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))

def extraer_datos(dashboard_html_path):
    out_json = os.path.join(BASE, "_data.json")
    node_script = f"""
const fs = require('fs');
const html = fs.readFileSync('{dashboard_html_path}','utf8');
function extractArr(varName){{
  const re = new RegExp('const '+varName+' = (\\\\[[\\\\s\\\\S]*?\\\\n\\\\]);');
  const m = html.match(re);
  if(!m) throw new Error('not found: '+varName);
  return eval(m[1]);
}}
// nombre de la constante de gasto puede cambiar de mes a mes (GASTO_SUBT21_<MES><ANIO>)
const gastoVarMatch = html.match(/const (GASTO_SUBT21_\\w+) = /);
if(!gastoVarMatch) throw new Error('no se encontró la constante de gasto real');
const GASTO = extractArr(gastoVarMatch[1]);
const MIN2025 = extractArr('MINISTERIOS_2025');
const DOT = extractArr('DOTACION_SERIE');
const EUS = extractArr('EUS');
fs.writeFileSync('{out_json}', JSON.stringify({{GASTO,MIN2025,DOT,EUS,gastoVarName:gastoVarMatch[1]}}));
"""
    subprocess.run(["node", "-e", node_script], check=True)
    with open(out_json) as f:
        return json.load(f)

def main():
    mes, anio, dashboard_path, salida = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    data = extraer_datos(dashboard_path)
    GASTO = data["GASTO"]
    MIN2025 = data["MIN2025"]
    DOT = data["DOT"]
    EUS = data["EUS"]

    # ---------- cálculos ----------
    gasto_total = sum(v for _, v in GASTO)
    gasto_sorted = sorted(GASTO, key=lambda x: -x[1])
    top_gasto = gasto_sorted[:15]
    top3 = gasto_sorted[:3]

    dotacion_total = sum(r[1]+r[2]+r[3]+r[4] for r in MIN2025)
    dot_por_cat = [0,0,0,0]
    for r in MIN2025:
        for i in range(4):
            dot_por_cat[i] += r[i+1]
    dot_sorted = sorted(MIN2025, key=lambda r: -(r[1]+r[2]+r[3]+r[4]))
    top_dotacion = dot_sorted[0]
    crecimiento = (DOT[-1]["total"]/DOT[0]["total"] - 1)*100

    cats = ["Directivos","Profesionales","Técnicos","Adm. y Auxiliares"]
    def eus_range(catname):
        vals = [e["bruta"] for e in EUS if e["cat"]==catname]
        return min(vals), max(vals)
    rango_dir = eus_range("Directivos")
    rango_prof = eus_range("Profesionales")
    rango_tec = eus_range("Técnicos y Adm.")
    rango_admaux_vals = [e["bruta"] for e in EUS if e["cat"] in ("Técnicos y Adm.","Téc., Adm. y Aux.")]
    rango_admaux = (min(rango_admaux_vals), max(rango_admaux_vals))
    grado_mas_bajo = min(EUS, key=lambda e: e["bruta"])

    from graficos import graficar_ranking, graficar_evolucion
    chart1 = os.path.join(BASE, "_chart_ranking.png")
    chart2 = os.path.join(BASE, "_chart_evolucion.png")
    graficar_ranking(top_gasto, chart1)
    graficar_evolucion(DOT, chart2)

    from armar_pdf import construir_pdf
    construir_pdf(
        salida=salida, mes=mes, anio=anio,
        gasto_total=gasto_total, top_gasto=top_gasto, top3=top3,
        dotacion_total=dotacion_total, dot_por_cat=dict(zip(cats,dot_por_cat)),
        top_dotacion=top_dotacion, crecimiento=crecimiento,
        rangos_eus={"Directivos":rango_dir,"Profesionales":rango_prof,"Técnicos":rango_tec,"Adm. y Auxiliares":rango_admaux},
        grado_mas_bajo=grado_mas_bajo,
        chart_ranking=chart1, chart_evolucion=chart2,
        dotacion_serie=DOT,
    )
    print("PDF generado:", salida)

if __name__ == "__main__":
    main()
