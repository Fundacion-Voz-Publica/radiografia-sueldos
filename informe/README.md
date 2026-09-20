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
- `subir_a_drive.py` — sube el PDF a una carpeta de Google Drive usando una
  cuenta de servicio. Si ya existe un archivo con el mismo nombre en la
  carpeta, lo reemplaza (nueva versión) en vez de duplicarlo.

## Subida a Drive

Requiere `informe/drive-service-account.json` (credencial de la cuenta de
servicio — **nunca se versiona**, está en `.gitignore`; si no existe, pide
una nueva pasando por Google Cloud Console → IAM y administración →
Cuentas de servicio → Claves). La carpeta destino de Drive debe estar
compartida con el correo de esa cuenta de servicio (o su Unidad compartida,
si aplica) con rol de Editor / Administrador de contenido.

```bash
python3 informe/subir_a_drive.py informe/informe_agosto_2026.pdf <id_carpeta_drive>
```

## Flujo mensual

Este generador se ejecuta como parte de la Rutina mensual de actualización
de datos (ver el trigger programado): genera el PDF, lo sube a la carpeta
de Drive definida, y además lo manda por chat con un resumen. **Nada se
publica automáticamente para el público** — la carpeta de Drive es para
revisión interna antes de publicar.

Si cambia el nombre de la constante de gasto real en `dashboard.html` (por
ejemplo de `GASTO_SUBT21_JULIO2026` a `GASTO_SUBT21_AGOSTO2026`), no hay que
tocar nada acá: `generar_informe.py` la detecta automáticamente por patrón.
