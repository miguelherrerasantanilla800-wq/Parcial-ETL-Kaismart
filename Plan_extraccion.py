from datetime import datetime
from pathlib import Path
import time

import pandas as pd
import schedule

from Extracción_BD import crear_df_ventas

RUTA_EXCEL = Path(__file__).with_name("kaismart_eventos_logisticos.xlsx")


def extraer_excel():
    """Lee la fuente Excel y devuelve el DataFrame extraído."""
    df_logistica = pd.read_excel(RUTA_EXCEL)
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        f"Excel extraído: {len(df_logistica)} registros"
    )
    return df_logistica


def extraer_bd():
    """Extrae la tabla ventas desde MySQL y devuelve el DataFrame."""
    df_ventas = crear_df_ventas()
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
        f"Base de datos extraída: {len(df_ventas)} registros"
    )
    return df_ventas


def planificar_extraccion():
    """Registra la extracción diaria de las fuentes disponibles."""
    schedule.every().day.at("08:00").do(extraer_excel)
    schedule.every().day.at("08:15").do(extraer_bd)
    print("Plan registrado: Excel a las 08:00 y base de datos a las 08:15.")


if __name__ == "__main__":
    planificar_extraccion()
    extraer_excel()
    extraer_bd()

    print("Plan de extracción activo. Presione Ctrl+C para detenerlo.")
    while True:
        schedule.run_pending()
        time.sleep(1)