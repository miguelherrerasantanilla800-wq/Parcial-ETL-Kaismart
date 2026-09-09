# Conclusiones

## df_ventas

1. `df_ventas` contiene 5.000 registros y 17 variables.
2. `id_venta` y `pedido_id` tienen 5.000 valores únicos y no presentan registros repetidos; son identificadores adecuados para controlar la unicidad de la venta.
3. No existen filas completamente duplicadas en la fuente.
4. `id_tienda` presenta 3.501 valores nulos, equivalentes al 70,02 %, y `calificacion_cliente` presenta 2.172 nulos, equivalentes al 43,44 %. Estos campos requieren validar si la ausencia responde al proceso o a un problema de calidad.
5. `fecha_venta` está correctamente detectada como fecha, pero `precio_unitario`, `valor_bruto`, `valor_descuento` y `valor_neto` están almacenadas como `object`; deben convertirse o revisarse como variables monetarias antes de análisis posteriores.
6. `id_cliente` tiene alta cardinalidad, mientras que `canal`, `ciudad`, `categoria`, `producto` y `medio_pago` son variables categóricas útiles para segmentar las ventas.
7. Solo 2.828 registros tienen información en `calificacion_cliente`; la distribución de calificaciones debe analizarse sobre esos registros disponibles.

## df_logistica

1. `df_logistica` contiene 50.000 registros y 13 variables.
2. `evento_id` debería ser único, pero presenta 200 registros repetidos; además existen 99 filas completamente duplicadas que deben documentarse y conservarse.
3. Los nulos más altos se encuentran en `incidencia` con 98,98 %, `observacion` con 96,55 %, `transportadora` con 60,18 % y `numero_guia` con 60,14 %. Los primeros pueden ser normales cuando no ocurre una incidencia; transporte y guía deben validarse según la etapa del proceso.
4. `fecha_evento` y `fecha_prometida_entrega` están almacenadas como texto, por lo que deben revisarse y convertirse a fecha antes de realizar análisis temporales.
5. `estado_evento`, `centro_logistico`, `ciudad_destino`, `transportadora`, `incidencia` y `observacion` son variables categóricas; `tiempo_etapa_horas` y `costo_envio` son variables numéricas.
6. La variable `estado_evento` tiene 10 categorías y permite analizar la distribución de los eventos logísticos por etapa.
7. `tiempo_etapa_horas` contiene 5.000 nulos y `costo_envio` no contiene nulos; antes de modelar tiempos debe definirse cómo tratar los eventos donde la duración no aplica, sin imputar automáticamente.
