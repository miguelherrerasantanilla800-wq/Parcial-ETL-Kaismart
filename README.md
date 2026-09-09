# Examen Práctico de ETL - Kaismart Solutions S.A.S.

Proyecto de extracción, diagnóstico inicial de calidad y consultas analíticas sobre los sistemas de información comercial y logístico de **Kaismart Solutions S.A.S.**

---

## 📁 Estructura del Repositorio

- **`Extracción_BD.py`**: Conexión a la base de datos MySQL `clientes`, extracción de la tabla `ventas` a `df_ventas`, exploración inicial, perfil de calidad y resúmenes estadísticos.
- **`Extracción_excel.py`**: Lectura del archivo `kaismart_eventos_logisticos.xlsx` a `df_logistica`, diagnóstico de nulos, unicidad, duplicados y frecuencias de eventos.
- **`Plan_extraccion.py`**: Automatización y calendarización del proceso de extracción diaria mediante la librería `schedule`.
- **`Interfaz.py`**: Aplicación de escritorio moderna construida en **Tkinter** para realizar consultas interactivas, visualizar comprobaciones, responder preguntas de negocio y rastrear pedidos por `pedido_id`.
- **`Conclusiones.md`**: Resumen analítico con los principales hallazgos encontrados en `df_ventas` y `df_logistica`.

---

## 🚀 Requisitos e Instalación

1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd "Parcial ETL"
   ```

2. Instalar dependencias necesarias:
   ```bash
   pip install pandas openpyxl mysql-connector-python schedule
   ```

---

## 💻 Ejecución

- **Lanzar la Interfaz Gráfica (Tkinter):**
  ```bash
  python Interfaz.py
  ```

- **Ejecutar extracción de Base de Datos:**
  ```bash
  python Extracción_BD.py
  ```

- **Ejecutar extracción de Archivo Excel:**
  ```bash
  python Extracción_excel.py
  ```

- **Iniciar plan de extracción programado:**
  ```bash
  python Plan_extraccion.py
  ```
