#!/usr/bin/env python3
"""Sube un archivo a una carpeta de Google Drive usando una cuenta de servicio.
Uso:
    python3 subir_a_drive.py <archivo_local> <id_carpeta_drive>
Requiere informe/drive-service-account.json (nunca se versiona, ver .gitignore).
"""
import sys, os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE, "drive-service-account.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]


def subir(ruta_archivo, id_carpeta):
    if not os.path.exists(CRED_PATH):
        raise SystemExit(f"No se encontró la credencial en {CRED_PATH}")
    creds = service_account.Credentials.from_service_account_file(CRED_PATH, scopes=SCOPES)
    servicio = build("drive", "v3", credentials=creds)

    nombre = os.path.basename(ruta_archivo)

    # Si ya existe un archivo con el mismo nombre en la carpeta, lo reemplaza
    # (crea una nueva versión) en vez de duplicarlo.
    # supportsAllDrives/includeItemsFromAllDrives: necesario si la carpeta vive
    # en un Drive compartido (Shared Drive) del Workspace, no en "Mi unidad".
    query = f"name = '{nombre}' and '{id_carpeta}' in parents and trashed = false"
    existentes = servicio.files().list(
        q=query, fields="files(id, name)",
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute().get("files", [])

    media = MediaFileUpload(ruta_archivo, mimetype="application/pdf", resumable=True)

    if existentes:
        file_id = existentes[0]["id"]
        archivo = servicio.files().update(
            fileId=file_id, media_body=media, fields="id, webViewLink",
            supportsAllDrives=True,
        ).execute()
        accion = "actualizado"
    else:
        metadata = {"name": nombre, "parents": [id_carpeta]}
        archivo = servicio.files().create(
            body=metadata, media_body=media, fields="id, webViewLink",
            supportsAllDrives=True,
        ).execute()
        accion = "creado"

    print(f"Archivo {accion} en Drive: {archivo.get('webViewLink')}")
    return archivo


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python3 subir_a_drive.py <archivo_local> <id_carpeta_drive>")
    subir(sys.argv[1], sys.argv[2])
