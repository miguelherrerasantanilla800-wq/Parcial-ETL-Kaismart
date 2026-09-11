from pathlib import Path

import pandas as pd


def crear_df_logistica(ruta=None):
	"""Lee la fuente Excel y devuelve df_logistica sin transformar los datos."""
	if ruta is None:
		ruta = Path(__file__).with_name("kaismart_eventos_logisticos.xlsx")
	df = pd.read_excel(ruta)

	print("COMPROBACIÓN DE EXTRACCIÓN: df_logistica")
	print(f"Dimensiones (shape): {df.shape}")
	print("\nColumnas del DataFrame de logística:")
	print(df.columns.tolist())
	print("\nPrimeras 5 filas (head):")
	print(df.head())
	print("\nMuestra aleatoria de 5 registros (sample):")
	print(df.sample(5, random_state=42) if len(df) >= 5 else df)

	print("COMPRENSIÓN INICIAL: ¿Qué representa una fila?")
	print("• Una fila de df_logistica representa un evento o hito en el ciclo de vida logístico de un pedido (procesamiento, despacho, tránsito, entrega, incidencia).")
	if "fecha_evento" in df.columns:
		fechas = pd.to_datetime(df["fecha_evento"], errors="coerce")
		print(f"• Rango de fechas de eventos en df_logistica: {fechas.min()} hasta {fechas.max()}")

	return df

def _clasificar_columnas(df):
	"""Identifica fechas, IDs, variables categóricas y variables numéricas."""
	variables_fecha = [
		columna
		for columna in df.columns
		if (
			pd.api.types.is_datetime64_any_dtype(df[columna])
			or any(
				palabra in str(columna).lower()
				for palabra in ("fecha", "date", "tiempo", "time", "hora", "timestamp")
			)
		)
	]
	variables_id = [
		columna
		for columna in df.columns
		if df[columna].notna().any()
		and (
			str(columna).lower() == "id"
			or str(columna).lower().endswith("_id")
			or str(columna).lower().startswith("id_")
			or any(
				palabra in str(columna).lower()
				for palabra in ("codigo", "código", "code", "guia", "guía")
			)
		)
	]
	categoricas = [
		columna
		for columna in df.select_dtypes(include=["str", "category", "bool"]).columns
		if columna not in variables_fecha and columna not in variables_id
	]
	numericas = [
		columna
		for columna in df.select_dtypes(include="number").columns
		if columna not in variables_id
	]
	return {
		"fechas_tiempos": variables_fecha,
		"identificadores": variables_id,
		"categoricas": categoricas,
		"numericas": numericas,
	}

def exploracion_inicial(df, nombre="df_logistica"):
	"""Muestra y devuelve la exploración estructural inicial."""
	clasificacion = _clasificar_columnas(df)
	no_nulos = df.notna().sum()
	resultado = {
		"registros": len(df),
		"variables": len(df.columns),
		"columnas": list(df.columns),
		"tipos": df.dtypes.astype(str),
		"no_nulos": no_nulos,
		**clasificacion,
	}

	print(f"\nExploración inicial: {nombre}")
	print(f"Número de registros: {resultado['registros']}")
	print(f"Número de variables: {resultado['variables']}")
	print(f"Nombre de todas las variables: {resultado['columnas']}")
	print("Tipo de dato y registros no nulos por variable:")
	for columna in df.columns:
		print(f"  - {columna}: {df[columna].dtype}; no nulos = {no_nulos[columna]}")
	print(f"Variables que pueden considerarse identificadores: {clasificacion['identificadores']}")
	print(f"Variables categóricas: {clasificacion['categoricas']}")
	print(f"Variables numéricas: {clasificacion['numericas']}")
	print(f"Variables asociadas con fechas o tiempos: {clasificacion['fechas_tiempos']}")
	return resultado


def _interpretar_nulos(columna, cantidad):
	"""Clasifica los nulos sin modificarlos ni imputarlos."""
	if cantidad == 0:
		return "sin valores nulos"
	columna_min = str(columna).lower()
	if any(palabra in columna_min for palabra in ("observacion", "incidencia", "calificacion")):
		return "posiblemente normal si el evento o la calificación no aplica; validar el proceso"
	if any(palabra in columna_min for palabra in ("transportadora", "guia", "id_tienda")):
		return "posiblemente normal antes de asignar transporte, guía o tienda; validar reglas del proceso"
	return "posible problema de calidad en un campo esperado; revisar origen y reglas de obligatoriedad"


def perfil_calidad(df):
	"""Muestra y devuelve nulos, cardinalidad, duplicados y revisión de tipos."""
	clasificacion = _clasificar_columnas(df)
	nulos = pd.DataFrame({
		"cantidad_nulos": df.isna().sum(),
		"porcentaje_nulos": (df.isna().mean() * 100).round(2),
	}).sort_values("porcentaje_nulos", ascending=False)
	nulos["interpretacion"] = [
		_interpretar_nulos(columna, cantidad)
		for columna, cantidad in nulos["cantidad_nulos"].items()
	]
	valores_unicos = pd.DataFrame({
		"valores_unicos": df.nunique(dropna=True),
		"porcentaje_unicos": (df.nunique(dropna=True) / len(df) * 100).round(2),
		"tipo": df.dtypes.astype(str),
	}).sort_values("valores_unicos", ascending=False)
	categoricas = set(clasificacion["categoricas"])
	alta_cardinalidad = [
		columna for columna in categoricas if df[columna].nunique(dropna=True) > 50
	]
	baja_cardinalidad = [
		columna for columna in categoricas if df[columna].nunique(dropna=True) <= 10
	]
	valores_categoricos = {
		columna: df[columna].dropna().unique().tolist()
		for columna in baja_cardinalidad
	}
	identificadores_unicos = [
		columna for columna in df.columns
		if df[columna].notna().all()
		and df[columna].nunique(dropna=True) == len(df)
	]
	identificadores_esperados_unicos = [
		columna for columna in ("id_venta", "evento_id") if columna in df.columns
	]
	columnas_revisar_id = list(dict.fromkeys(
		identificadores_unicos
		+ clasificacion["identificadores"]
		+ [columna for columna in ("id_venta", "pedido_id", "evento_id") if columna in df]
	))
	repetidos_ids = {
		columna: int(df[columna].duplicated(keep=False).sum())
		for columna in columnas_revisar_id
	}
	tipos_revision = {}
	for columna in df.columns:
		columna_min = str(columna).lower()
		if "fecha" in columna_min and not pd.api.types.is_datetime64_any_dtype(df[columna]):
			revision = "revisar: parece fecha, pero está almacenada como texto"
		elif pd.api.types.is_datetime64_any_dtype(df[columna]):
			revision = "coherente como fecha o tiempo"
		elif columna in clasificacion["identificadores"]:
			revision = "coherente como identificador; conservar como texto si puede contener ceros iniciales"
		elif any(palabra in columna_min for palabra in ("costo", "precio", "valor")):
			revision = "revisar unidad y moneda antes de analizar"
		elif pd.api.types.is_numeric_dtype(df[columna]):
			revision = "coherente como variable numérica"
		else:
			revision = "coherente como variable categórica o textual"
		tipos_revision[columna] = revision
	resultado = {
		"nulos": nulos,
		"valores_unicos": valores_unicos,
		"alta_cardinalidad": alta_cardinalidad,
		"baja_cardinalidad": baja_cardinalidad,
		"valores_categoricos": valores_categoricos,
		"identificadores_unicos": identificadores_unicos,
		"identificadores_esperados_unicos": identificadores_esperados_unicos,
		"filas_duplicadas": int(df.duplicated().sum()),
		"repetidos_ids": repetidos_ids,
		"revision_tipos": tipos_revision,
	}

	print("\nPerfil de calidad: valores nulos")
	print(nulos)
	print("Interpretación: nulos de proceso pueden ser esperados; los de campos obligatorios requieren revisión.")
	print("No se eliminan ni imputan valores nulos.")
	print("\nPerfil de calidad: valores únicos")
	print(valores_unicos)
	print(f"Alta cardinalidad (>50): {alta_cardinalidad}")
	print(f"Baja cardinalidad (<=10): {baja_cardinalidad}")
	print("Valores de variables categóricas con pocos niveles:")
	for columna, valores in valores_categoricos.items():
		print(f"  - {columna}: {valores}")
	print(f"Identificadores completamente únicos: {identificadores_unicos}")
	for columna in ("id_venta", "pedido_id", "evento_id"):
		if columna in df:
			print(f"{columna}: {df[columna].nunique(dropna=True)} valores únicos")
		else:
			print(f"{columna}: no existe en este DataFrame")
	print("\nPerfil de calidad: duplicados")
	print(f"Filas completamente duplicadas: {resultado['filas_duplicadas']}")
	print(f"Identificadores que deberían ser únicos: {identificadores_esperados_unicos}")
	for columna, cantidad in repetidos_ids.items():
		print(f"Registros repetidos en {columna}: {cantidad}")
	print("Los duplicados se conservan y no se eliminan.")
	print("\nPerfil de calidad: revisión de tipos")
	for columna, revision in tipos_revision.items():
		print(f"  - {columna}: {df[columna].dtype}; {revision}")
	return resultado

def estadisticos_descriptivos(df):
	"""Muestra y devuelve los estadísticos de las variables numéricas."""
	numericas = df.select_dtypes(include="number").columns
	resultado = df[numericas].describe().T
	print("\nEstadísticos descriptivos de variables numéricas:")
	print(resultado)
	return resultado


def resumenes_categoricos(df):
	"""Muestra valores únicos, categorías, frecuencias y moda por variable categórica."""
	columnas = _clasificar_columnas(df)["categoricas"]
	resultado = {}
	print("\nResúmenes de variables categóricas:")
	for columna in columnas:
		frecuencias = df[columna].value_counts(dropna=False)
		resultado[columna] = {
			"valores_unicos": int(df[columna].nunique(dropna=True)),
			"categorias": df[columna].dropna().unique().tolist(),
			"frecuencias": frecuencias,
			"categoria_mas_frecuente": (
				frecuencias.index[0] if not frecuencias.empty else None
			),
		}
		print(f"\n{columna}: {resultado[columna]['valores_unicos']} valores únicos")
		print(f"Categorías: {resultado[columna]['categorias']}")
		print(f"Frecuencias:\n{frecuencias}")
		print(f"Categoría más frecuente: {resultado[columna]['categoria_mas_frecuente']}")
	return resultado


def resumenes_solicitados(df):
	"""Muestra y devuelve las frecuencias y resúmenes solicitados."""
	frecuencias = {}
	for columna in ("estado_evento", "ciudad_destino", "transportadora", "incidencia"):
		if columna in df:
			frecuencias[columna] = df[columna].value_counts(dropna=False)
			print(f"\nFrecuencia de {columna}:")
			print(frecuencias[columna])
	resumenes = {}
	for columna in ("tiempo_etapa_horas", "costo_envio"):
		if columna in df:
			resumenes[columna] = df[columna].describe()
			print(f"\nResumen estadístico de {columna}:")
			print(resumenes[columna])
	return {"frecuencias": frecuencias, "resumenes_numericos": resumenes}

def ejecutar_analisis(df=None):
	"""Ejecuta todas las secciones en el orden del informe."""
	if df is None:
		df = crear_df_logistica()

	exploracion_inicial(df, "df_logistica")
	perfil_calidad(df)
	estadisticos_descriptivos(df)
	resumenes_categoricos(df)
	resumenes_solicitados(df)
	return df

if __name__ == "__main__":
	df_logistica = crear_df_logistica()
	df_logistica = ejecutar_analisis(df_logistica)

