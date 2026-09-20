# Generador del informe mensual (PDF)

Genera el informe "Radiografía de Sueldos del Estado" en PDF a partir de los
mismos datos que usa `public/dashboard.html` (no hay que mantener los
números en dos lugares — este script los lee directo del dashboard).

## Uso

```bash
pip install -r informe/requirements.txt
python3 informe/generar_informe.py <Mes> <Año> public/dashboard.html informe/informe_<mes>_<anio>.pdf
```

Ejemplo:

```bash
python3 informe/generar_informe.py Agosto 2026 public/dashboard.html informe/informe_agosto_2026.pdf
```

## Archivos

- `generar_informe.py` — orquesta todo: extrae los datos del dashboard,
  calcula los totales/rankings, genera los gráficos y arma el PDF.
- `graficos.py` — genera los gráficos (matplotlib) que se insertan en el PDF.
- `armar_pdf.py` — arma el documento (reportlab): portada, KPIs, tablas,
  metodología.

## Flujo mensual

Este generador se ejecuta como parte de la Rutina mensual de actualización
de datos (ver el trigger programado). El PDF resultante **se manda para
revisión humana antes de publicarse** — este script no publica nada por su
cuenta.

Si cambia el nombre de la constante de gasto real en `dashboard.html` (por
ejemplo de `GASTO_SUBT21_JULIO2026` a `GASTO_SUBT21_AGOSTO2026`), no hay que
tocar nada acá: `generar_informe.py` la detecta automáticamente por patrón.
