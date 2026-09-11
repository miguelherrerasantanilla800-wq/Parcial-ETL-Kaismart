import mysql.connector
import pandas as pd

from Extracción_excel import (
	exploracion_inicial,
	perfil_calidad,
	resumenes_categoricos,
)


def crear_df_ventas(
	host="107.180.112.11",
	user="admin",
	password="adminuao2026",
	database="clientes",
):
	"""Extrae la tabla ventas y devuelve el DataFrame resultante."""
	conexion = mysql.connector.connect(
		host=host,
		user=user,
		password=password,
		database=database,
	)
	try:
		cursor = conexion.cursor()
		cursor.execute("SELECT * FROM ventas")
		filas = cursor.fetchall()
		columnas = [descripcion[0] for descripcion in cursor.description]
		cursor.close()
		return pd.DataFrame(filas, columns=columnas)
	finally:
		conexion.close()


def explorar_df_ventas():
	"""Muestra la estructura y calidad del DataFrame de ventas."""
	df_ventas = crear_df_ventas()
	print("COMPROBACIÓN DE EXTRACCIÓN: df_ventas")
	print(f"Dimensiones (shape): {df_ventas.shape}")
	print("\nColumnas del DataFrame de ventas:")
	print(df_ventas.columns.tolist())
	print("\nPrimeras 5 filas (head):")
	print(df_ventas.head())
	print("\nMuestra aleatoria de 5 registros (sample):")
	print(df_ventas.sample(5, random_state=42) if len(df_ventas) >= 5 else df_ventas)
	
	print("¿Qué representa una fila?")
	print("• Una fila de df_ventas representa una transacción comercial individual (venta de un producto específico en un pedido realizado por un cliente).")
	if "fecha_venta" in df_ventas.columns:
		fechas = pd.to_datetime(df_ventas["fecha_venta"], errors="coerce")
		print(f"• Rango de fechas en df_ventas: {fechas.min()} hasta {fechas.max()}")

	exploracion_inicial(df_ventas, "df_ventas")
	perfil_calidad(df_ventas)
	estadisticos_ventas(df_ventas)
	resumenes_categoricos(df_ventas)
	resumenes_ventas(df_ventas)
	return df_ventas


def estadisticos_ventas(df):
	"""Calcula estadísticas de numéricas nativas y monetarias convertibles."""
	columnas = list(df.select_dtypes(include="number").columns)
	resultado = df[columnas].describe().T
	for columna in ("precio_unitario", "valor_bruto", "valor_descuento", "valor_neto"):
		if columna in df.columns:
			serie = pd.to_numeric(df[columna], errors="coerce")
			resultado.loc[columna] = serie.describe()
	resultado = resultado.sort_index()
	print("\nEstadísticos descriptivos de df_ventas:")
	print(resultado)
	return resultado


def resumenes_ventas(df):
	"""Calcula los resúmenes solicitados específicamente para df_ventas."""
	resultado = {"frecuencias": {}, "estadisticos": {}, "calificaciones": None}
	for columna in ("ciudad", "canal", "categoria"):
		if columna in df.columns:
			resultado["frecuencias"][columna] = df[columna].value_counts(dropna=False)
			print(f"\nNúmero de ventas por {columna}:")
			print(resultado["frecuencias"][columna])

	if "cantidad" in df.columns:
		resultado["frecuencias"]["cantidad"] = df["cantidad"].value_counts().sort_index()
		print("\nDistribución de la cantidad de productos vendidos:")
		print(resultado["frecuencias"]["cantidad"])

	for columna in ("precio_unitario", "valor_bruto", "valor_descuento", "valor_neto"):
		if columna in df.columns:
			serie = pd.to_numeric(df[columna], errors="coerce")
			resultado["estadisticos"][columna] = serie.describe()
			print(f"\nResumen estadístico de {columna}:")
			print(resultado["estadisticos"][columna])

	if "calificacion_cliente" in df.columns:
		calificaciones = df["calificacion_cliente"].dropna()
		resultado["calificaciones"] = calificaciones.value_counts().sort_index()
		print("\nDistribución de calificacion_cliente (registros informados):")
		print(resultado["calificaciones"])
	return resultado


if __name__ == "__main__":
	df_ventas = explorar_df_ventas()
