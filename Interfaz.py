"""
==============================================================================
SISTEMA DE CONSULTA Y EXPLORACIÓN ETL - KAISMART SOLUTIONS S.A.S.
Archivo: Interfaz.py
Interfaz Gráfica Profesional en Tkinter para la exploración, diagnóstico
de calidad y consultas analíticas de df_ventas y df_logistica.
==============================================================================
"""

import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, font

import pandas as pd

# Importar funciones de extracción y análisis
from Extracción_BD import crear_df_ventas, estadisticos_ventas, resumenes_ventas
from Extracción_excel import (
    crear_df_logistica,
    exploracion_inicial,
    perfil_calidad,
    estadisticos_descriptivos,
    resumenes_categoricos,
    resumenes_solicitados,
)

# -----------------------------------------------------------------------------
# PALETA DE COLORES Y ESTILO MODERNO
# -----------------------------------------------------------------------------
COLORS = {
    "bg_dark": "#0f172a",       # Slate 900 (Sidebar)
    "sidebar_hover": "#1e293b", # Slate 800
    "sidebar_active": "#2563eb",# Blue 600
    "bg_light": "#f1f5f9",      # Slate 100 (Main content)
    "card_bg": "#ffffff",       # White
    "card_border": "#cbd5e1",   # Slate 300
    "text_dark": "#0f172a",     # Slate 900
    "text_muted": "#64748b",    # Slate 500
    "text_light": "#f8fafc",    # Slate 50
    "primary": "#2563eb",       # Blue 600
    "primary_hover": "#1d4ed8", # Blue 700
    "success": "#10b981",       # Emerald 500
    "warning": "#f59e0b",       # Amber 500
    "danger": "#ef4444",        # Red 500
    "accent": "#8b5cf6",        # Purple 500
    "table_alt": "#f8fafc",     # Light table stripe
}


class InterfazETLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kaismart Solutions S.A.S. | Plataforma de Exploración ETL")
        self.geometry("1240x820")
        self.minsize(1050, 700)
        self.configure(bg=COLORS["bg_light"])

        # Datos en memoria
        self.df_ventas = pd.DataFrame()
        self.df_logistica = pd.DataFrame()
        self.datos_cargados = False

        # Configurar Estilos ttk
        self._configurar_estilos()

        # Layout Principal: Sidebar + Área de Contenido
        self._crear_layout_principal()

        # Iniciar Carga Asíncrona de Datos
        self.iniciar_carga_datos()

    def _configurar_estilos(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Configuración general
        default_font = ("Segoe UI", 10)
        self.option_add("*Font", default_font)

        # Tablas (Treeview)
        self.style.configure(
            "Custom.Treeview",
            background=COLORS["card_bg"],
            foreground=COLORS["text_dark"],
            fieldbackground=COLORS["card_bg"],
            rowheight=28,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#e2e8f0",
            foreground="#1e293b",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(6, 6),
        )
        self.style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#cbd5e1")]
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")]
        )

        # Scrollbars
        self.style.configure(
            "Vertical.TScrollbar",
            background="#cbd5e1",
            troughcolor="#f1f5f9",
            borderwidth=0,
            arrowsize=14
        )

    def _crear_layout_principal(self):
        # 1. SIDEBAR IZQUIERDA
        self.sidebar = tk.Frame(self, bg=COLORS["bg_dark"], width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo / Marca Header
        lbl_brand = tk.Label(
            self.sidebar,
            text="KAISMART",
            font=("Segoe UI", 18, "bold"),
            fg="#60a5fa",
            bg=COLORS["bg_dark"],
            pady=12,
        )
        lbl_brand.pack(fill=tk.X, padx=16, pady=(16, 0))

        lbl_subbrand = tk.Label(
            self.sidebar,
            text="SISTEMA ETL & EXPLORACIÓN",
            font=("Segoe UI", 8, "bold"),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_dark"],
        )
        lbl_subbrand.pack(fill=tk.X, padx=16, pady=(0, 20))

        # Divisor
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(0, 16))

        # Botones de Navegación
        self.nav_buttons = {}
        items_nav = [
            ("dashboard", "📊 Resumen y Comprobación", self.mostrar_dashboard),
            ("ventas", "🛒 df_ventas (MySQL)", self.mostrar_ventas),
            ("logistica", "🚚 df_logistica (Excel)", self.mostrar_logistica),
            ("preguntas", "💡 10 Preguntas de Negocio", self.mostrar_preguntas),
            ("rastreo", "🔍 Rastreador de Pedido", self.mostrar_rastreo),
            ("calidad", "🛡️ Perfil de Calidad", self.mostrar_calidad),
            ("conclusiones", "📝 Conclusiones", self.mostrar_conclusiones),
        ]

        for key, text, cmd in items_nav:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["text_light"],
                bg=COLORS["bg_dark"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground="#60a5fa",
                relief=tk.FLAT,
                anchor="w",
                padx=20,
                pady=10,
                cursor="hand2",
                command=cmd,
            )
            btn.pack(fill=tk.X, pady=2, padx=10)
            self.nav_buttons[key] = btn

        # Footer del Sidebar: Estado de fuentes
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 10))
        
        self.lbl_status_footer = tk.Label(
            self.sidebar,
            text="⏳ Cargando datos...",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg=COLORS["bg_dark"],
            wraplength=220,
            justify="left",
            pady=10,
        )
        self.lbl_status_footer.pack(side=tk.BOTTOM, fill=tk.X, padx=16)

        btn_reload = tk.Button(
            self.sidebar,
            text="🔄 Recargar Fuentes",
            font=("Segoe UI", 9, "bold"),
            fg=COLORS["text_light"],
            bg="#1e293b",
            activebackground="#334155",
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self.iniciar_carga_datos,
        )
        btn_reload.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 6))

        # 2. CONTENEDOR PRINCIPAL DERECHO
        self.main_container = tk.Frame(self, bg=COLORS["bg_light"])
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Barra Superior de Información
        self.topbar = tk.Frame(self.main_container, bg=COLORS["card_bg"], height=60)
        self.topbar.pack(fill=tk.X)
        self.topbar.pack_propagate(False)

        self.lbl_header_title = tk.Label(
            self.topbar,
            text="Comprobación de Extracción & Diagnóstico ETL",
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text_dark"],
            bg=COLORS["card_bg"],
        )
        self.lbl_header_title.pack(side=tk.LEFT, padx=24, pady=16)

        # Badges de estado en Topbar
        self.badge_ventas = tk.Label(
            self.topbar,
            text="MySQL: Conectando...",
            font=("Segoe UI", 9, "bold"),
            bg="#fef3c7",
            fg="#92400e",
            padx=10,
            pady=4,
        )
        self.badge_ventas.pack(side=tk.RIGHT, padx=(6, 24))

        self.badge_logistica = tk.Label(
            self.topbar,
            text="Excel: Leyendo...",
            font=("Segoe UI", 9, "bold"),
            bg="#fef3c7",
            fg="#92400e",
            padx=10,
            pady=4,
        )
        self.badge_logistica.pack(side=tk.RIGHT, padx=6)

        # Área de vistas dinámicas
        self.content_frame = tk.Frame(self.main_container, bg=COLORS["bg_light"], padx=24, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def _resaltar_nav(self, key_activa):
        for key, btn in self.nav_buttons.items():
            if key == key_activa:
                btn.configure(bg=COLORS["sidebar_active"], fg="#ffffff")
            else:
                btn.configure(bg=COLORS["bg_dark"], fg=COLORS["text_light"])

    def _limpiar_contenido(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # -------------------------------------------------------------------------
    # CARGA ASÍNCRONA DE DATOS
    # -------------------------------------------------------------------------
    def iniciar_carga_datos(self):
        self.lbl_status_footer.configure(text="⏳ Extrayendo datos...")
        self.badge_ventas.configure(text="MySQL: Conectando...", bg="#fef3c7", fg="#92400e")
        self.badge_logistica.configure(text="Excel: Leyendo...", bg="#fef3c7", fg="#92400e")
        
        hilo = threading.Thread(target=self._ejecutar_extraccion, daemon=True)
        hilo.start()

    def _ejecutar_extraccion(self):
        error_msg = []
        try:
            df_v = crear_df_ventas()
            self.df_ventas = df_v
        except Exception as e:
            self.df_ventas = pd.DataFrame()
            error_msg.append(f"MySQL: {e}")

        try:
            df_l = crear_df_logistica()
            self.df_logistica = df_l
        except Exception as e:
            self.df_logistica = pd.DataFrame()
            error_msg.append(f"Excel: {e}")

        self.after(0, self._finalizar_carga_datos, error_msg)

    def _finalizar_carga_datos(self, error_msg):
        if not self.df_ventas.empty:
            self.badge_ventas.configure(
                text=f"✓ df_ventas: {len(self.df_ventas):,} filas",
                bg="#dcfce7",
                fg="#166534"
            )
        else:
            self.badge_ventas.configure(text="✕ df_ventas: Error", bg="#fee2e2", fg="#991b1b")

        if not self.df_logistica.empty:
            self.badge_logistica.configure(
                text=f"✓ df_logistica: {len(self.df_logistica):,} filas",
                bg="#dcfce7",
                fg="#166534"
            )
        else:
            self.badge_logistica.configure(text="✕ df_logistica: Error", bg="#fee2e2", fg="#991b1b")

        if error_msg:
            self.lbl_status_footer.configure(text="⚠️ Hubo errores al cargar.")
            messagebox.showwarning("Advertencia de Extracción", "\n".join(error_msg))
        else:
            self.lbl_status_footer.configure(
                text=f"🟢 Datos listos\nVentas: {len(self.df_ventas):,} | Logística: {len(self.df_logistica):,}"
            )

        self.datos_cargados = True
        self.mostrar_dashboard()

    # -------------------------------------------------------------------------
    # VISTA 1: DASHBOARD & COMPROBACIÓN DE EXTRACCIÓN
    # -------------------------------------------------------------------------
    def mostrar_dashboard(self):
        self._resaltar_nav("dashboard")
        self.lbl_header_title.configure(text="📊 Comprobación de Extracción y Resumen General")
        self._limpiar_contenido()

        if self.df_ventas.empty and self.df_logistica.empty:
            lbl = tk.Label(
                self.content_frame,
                text="Cargando fuentes de datos o reintentando conexión...",
                font=("Segoe UI", 12),
                bg=COLORS["bg_light"],
                fg=COLORS["text_muted"]
            )
            lbl.pack(pady=50)
            return

        # Fila de Tarjetas KPI
        cards_frame = tk.Frame(self.content_frame, bg=COLORS["bg_light"])
        cards_frame.pack(fill=tk.X, pady=(0, 16))

        v_rows = len(self.df_ventas) if not self.df_ventas.empty else 0
        v_cols = len(self.df_ventas.columns) if not self.df_ventas.empty else 0
        l_rows = len(self.df_logistica) if not self.df_logistica.empty else 0
        l_cols = len(self.df_logistica.columns) if not self.df_logistica.empty else 0

        self._crear_kpi_card(cards_frame, "df_ventas (MySQL)", f"{v_rows:,} registros", f"{v_cols} variables | 100% extraído", COLORS["primary"])
        self._crear_kpi_card(cards_frame, "df_logistica (Excel)", f"{l_rows:,} registros", f"{l_cols} variables | 100% extraído", COLORS["success"])
        self._crear_kpi_card(cards_frame, "Variable de Enlace", "pedido_id", "Sin merge (Fase posterior)", COLORS["accent"])
        self._crear_kpi_card(cards_frame, "Regla de Alcance", "No Limpieza", "Sin imputar ni eliminar nulos", COLORS["warning"])

        # Notebook (Pestañas) para comprobar fuentes
        nb = ttk.Notebook(self.content_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # Tab Ventas
        tab_v = tk.Frame(nb, bg=COLORS["card_bg"], padx=12, pady=12)
        nb.add(tab_v, text="  🛒 Comprobación df_ventas  ")
        self._render_comprobacion_tab(tab_v, self.df_ventas, "df_ventas (Base de Datos MySQL)", "Una fila representa una transacción comercial individual (venta de un producto en un pedido).")

        # Tab Logística
        tab_l = tk.Frame(nb, bg=COLORS["card_bg"], padx=12, pady=12)
        nb.add(tab_l, text="  🚚 Comprobación df_logistica  ")
        self._render_comprobacion_tab(tab_l, self.df_logistica, "df_logistica (Archivo Excel)", "Una fila representa un evento logístico en el ciclo de vida del pedido (procesamiento, tránsito, entrega).")

    def _crear_kpi_card(self, parent, title, value, subtitle, color_accent):
        card = tk.Frame(parent, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)

        # Barra de color superior
        bar = tk.Frame(card, bg=color_accent, height=4)
        bar.pack(fill=tk.X)

        p = tk.Frame(card, bg=COLORS["card_bg"], padx=14, pady=12)
        p.pack(fill=tk.BOTH, expand=True)

        lbl_t = tk.Label(p, text=title.upper(), font=("Segoe UI", 8, "bold"), fg=COLORS["text_muted"], bg=COLORS["card_bg"])
        lbl_t.pack(anchor="w")

        lbl_v = tk.Label(p, text=value, font=("Segoe UI", 15, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"])
        lbl_v.pack(anchor="w", pady=(2, 2))

        lbl_s = tk.Label(p, text=subtitle, font=("Segoe UI", 8), fg=COLORS["text_muted"], bg=COLORS["card_bg"])
        lbl_s.pack(anchor="w")

    def _render_comprobacion_tab(self, parent, df, nombre_fuente, significado_fila):
        if df.empty:
            tk.Label(parent, text="No hay datos disponibles.", bg=COLORS["card_bg"]).pack(pady=20)
            return

        # Metadata Header
        meta_frame = tk.Frame(parent, bg="#f8fafc", padx=12, pady=10, highlightbackground="#e2e8f0", highlightthickness=1)
        meta_frame.pack(fill=tk.X, pady=(0, 10))

        fechas_min_max = "N/A"
        for col in df.columns:
            if "fecha" in str(col).lower():
                s = pd.to_datetime(df[col], errors="coerce")
                if s.notna().any():
                    fechas_min_max = f"{s.min():%Y-%m-%d} hasta {s.max():%Y-%m-%d}"
                    break

        info_text = (
            f"📌 Fuente: {nombre_fuente}   |   Dimensiones (shape): {df.shape[0]:,} filas × {df.shape[1]} columnas\n"
            f"📝 Significado: {significado_fila}\n"
            f"📅 Rango de Fechas Detectado: {fechas_min_max}"
        )
        tk.Label(meta_frame, text=info_text, font=("Segoe UI", 9), fg="#334155", bg="#f8fafc", justify="left").pack(anchor="w")

        # Botones de alternancia Head vs Sample
        ctrl_frame = tk.Frame(parent, bg=COLORS["card_bg"])
        ctrl_frame.pack(fill=tk.X, pady=(0, 8))

        lbl_vista = tk.Label(ctrl_frame, text="Muestra de Registros Extraídos:", font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"])
        lbl_vista.pack(side=tk.LEFT)

        btn_sample = tk.Button(
            ctrl_frame,
            text="🎲 Muestra Aleatoria (sample 5)",
            font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9",
            fg=COLORS["primary"],
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: self._llenar_treeview(tv, df.sample(5) if len(df) >= 5 else df),
        )
        btn_sample.pack(side=tk.RIGHT, padx=4)

        btn_head = tk.Button(
            ctrl_frame,
            text="📑 Primeros 5 (head)",
            font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9",
            fg=COLORS["text_dark"],
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: self._llenar_treeview(tv, df.head(5)),
        )
        btn_head.pack(side=tk.RIGHT, padx=4)

        # Tabla Treeview con Scrollbars
        table_container = tk.Frame(parent, bg=COLORS["card_bg"])
        table_container.pack(fill=tk.BOTH, expand=True)

        tv, _, _ = self._crear_treeview(table_container, df.columns.tolist())
        self._llenar_treeview(tv, df.head(5))

    # -------------------------------------------------------------------------
    # VISTA 2: EXPLORADOR df_ventas
    # -------------------------------------------------------------------------
    def mostrar_ventas(self):
        self._resaltar_nav("ventas")
        self.lbl_header_title.configure(text="🛒 Exploración y Consultas: df_ventas (Base de Datos MySQL)")
        self._limpiar_contenido()

        if self.df_ventas.empty:
            tk.Label(self.content_frame, text="df_ventas no cargado.", font=("Segoe UI", 12), bg=COLORS["bg_light"]).pack(pady=40)
            return

        # Pestañas de Ventas
        nb = ttk.Notebook(self.content_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # 1. Explorador de Tabla Completa con Búsqueda
        tab_tabla = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_tabla, text="  📋 Explorador de Datos  ")
        self._render_tabla_con_filtro(tab_tabla, self.df_ventas)

        # 2. Resúmenes y Frecuencias Específicas
        tab_resumen = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_resumen, text="  📈 Resúmenes y Frecuencias  ")
        self._render_resumenes_ventas(tab_resumen)

        # 3. Estadísticos Descriptivos
        tab_est = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_est, text="  📊 Estadísticos Descriptivos  ")
        self._render_estadisticos(tab_est, estadisticos_ventas(self.df_ventas))

    def _render_resumenes_ventas(self, parent):
        scroll_c = tk.Canvas(parent, bg=COLORS["card_bg"], highlightthickness=0)
        s_bar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=scroll_c.yview)
        inner = tk.Frame(scroll_c, bg=COLORS["card_bg"])

        inner.bind("<Configure>", lambda e: scroll_c.configure(scrollregion=scroll_c.bbox("all")))
        scroll_c.create_window((0, 0), window=inner, anchor="nw")
        scroll_c.configure(yscrollcommand=s_bar.set)

        scroll_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_bar.pack(side=tk.RIGHT, fill=tk.Y)

        cols_analisis = ["ciudad", "canal", "categoria", "medio_pago"]
        grid_frame = tk.Frame(inner, bg=COLORS["card_bg"])
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        for i, col in enumerate(cols_analisis):
            if col in self.df_ventas.columns:
                box = tk.LabelFrame(
                    grid_frame,
                    text=f" Ventas por {col.upper()} ",
                    font=("Segoe UI", 9, "bold"),
                    fg=COLORS["primary"],
                    bg=COLORS["card_bg"],
                    padx=10,
                    pady=10,
                )
                box.grid(row=i // 2, column=i % 2, sticky="nsew", padx=10, pady=10)
                grid_frame.grid_columnconfigure(i % 2, weight=1)

                vc = self.df_ventas[col].value_counts(dropna=False).reset_index()
                vc.columns = [col, "Cantidad"]
                vc["Porcentaje"] = (vc["Cantidad"] / len(self.df_ventas) * 100).round(2).astype(str) + " %"

                tv, _, _ = self._crear_treeview(box, vc.columns.tolist(), height=6)
                self._llenar_treeview(tv, vc)

        # Calificaciones de clientes
        if "calificacion_cliente" in self.df_ventas.columns:
            calif_box = tk.LabelFrame(
                inner,
                text=" Distribución de Calificación del Cliente (Registros Disponibles) ",
                font=("Segoe UI", 9, "bold"),
                fg=COLORS["primary"],
                bg=COLORS["card_bg"],
                padx=10,
                pady=10,
            )
            calif_box.pack(fill=tk.X, padx=10, pady=10)

            c_val = self.df_ventas["calificacion_cliente"].dropna().value_counts().sort_index().reset_index()
            c_val.columns = ["Estrellas", "Votos"]
            c_val["Porcentaje s/disp"] = (c_val["Votos"] / c_val["Votos"].sum() * 100).round(2).astype(str) + " %"
            tv, _, _ = self._crear_treeview(calif_box, c_val.columns.tolist(), height=5)
            self._llenar_treeview(tv, c_val)

    # -------------------------------------------------------------------------
    # VISTA 3: EXPLORADOR df_logistica
    # -------------------------------------------------------------------------
    def mostrar_logistica(self):
        self._resaltar_nav("logistica")
        self.lbl_header_title.configure(text="🚚 Exploración y Consultas: df_logistica (Archivo Excel)")
        self._limpiar_contenido()

        if self.df_logistica.empty:
            tk.Label(self.content_frame, text="df_logistica no cargado.", font=("Segoe UI", 12), bg=COLORS["bg_light"]).pack(pady=40)
            return

        nb = ttk.Notebook(self.content_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # 1. Tabla con Búsqueda
        tab_tabla = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_tabla, text="  📋 Explorador de Eventos  ")
        self._render_tabla_con_filtro(tab_tabla, self.df_logistica)

        # 2. Resúmenes de Logística
        tab_resumen = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_resumen, text="  📈 Estados, Transportadoras e Incidencias  ")
        self._render_resumenes_logistica(tab_resumen)

        # 3. Estadísticos Descriptivos
        tab_est = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_est, text="  📊 Estadísticos de Tiempos y Costos  ")
        self._render_estadisticos(tab_est, estadisticos_descriptivos(self.df_logistica))

    def _render_resumenes_logistica(self, parent):
        scroll_c = tk.Canvas(parent, bg=COLORS["card_bg"], highlightthickness=0)
        s_bar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=scroll_c.yview)
        inner = tk.Frame(scroll_c, bg=COLORS["card_bg"])

        inner.bind("<Configure>", lambda e: scroll_c.configure(scrollregion=scroll_c.bbox("all")))
        scroll_c.create_window((0, 0), window=inner, anchor="nw")
        scroll_c.configure(yscrollcommand=s_bar.set)

        scroll_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_bar.pack(side=tk.RIGHT, fill=tk.Y)

        cols_analisis = ["estado_evento", "ciudad_destino", "transportadora", "incidencia"]
        grid_frame = tk.Frame(inner, bg=COLORS["card_bg"])
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        for i, col in enumerate(cols_analisis):
            if col in self.df_logistica.columns:
                box = tk.LabelFrame(
                    grid_frame,
                    text=f" Distribución de {col.upper()} ",
                    font=("Segoe UI", 9, "bold"),
                    fg=COLORS["primary"],
                    bg=COLORS["card_bg"],
                    padx=10,
                    pady=10,
                )
                box.grid(row=i // 2, column=i % 2, sticky="nsew", padx=10, pady=10)
                grid_frame.grid_columnconfigure(i % 2, weight=1)

                vc = self.df_logistica[col].value_counts(dropna=False).head(15).reset_index()
                vc.columns = [col, "Eventos"]
                vc["Porcentaje"] = (vc["Eventos"] / len(self.df_logistica) * 100).round(2).astype(str) + " %"

                tv, _, _ = self._crear_treeview(box, vc.columns.tolist(), height=7)
                self._llenar_treeview(tv, vc)

    # -------------------------------------------------------------------------
    # VISTA 4: 10 PREGUNTAS DE NEGOCIO (PARTE 6)
    # -------------------------------------------------------------------------
    def mostrar_preguntas(self):
        self._resaltar_nav("preguntas")
        self.lbl_header_title.configure(text="💡 Parte 6: 10 Preguntas de Negocio (Conocimiento Previo)")
        self._limpiar_contenido()

        scroll_c = tk.Canvas(self.content_frame, bg=COLORS["bg_light"], highlightthickness=0)
        s_bar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=scroll_c.yview)
        inner = tk.Frame(scroll_c, bg=COLORS["bg_light"])

        inner.bind("<Configure>", lambda e: scroll_c.configure(scrollregion=scroll_c.bbox("all")))
        scroll_c.create_window((0, 0), window=inner, anchor="nw")
        scroll_c.configure(yscrollcommand=s_bar.set)

        scroll_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_bar.pack(side=tk.RIGHT, fill=tk.Y)

        df_v = self.df_ventas
        df_l = self.df_logistica

        preguntas_respuestas = []

        # 1
        if not df_v.empty and "ciudad" in df_v:
            c_top = df_v["ciudad"].value_counts().idxmax()
            c_val = df_v["ciudad"].value_counts().max()
            preguntas_respuestas.append((
                "1. ¿Cuál es la ciudad con mayor volumen de ventas registradas?",
                f"{c_top} con {c_val:,} ventas ({c_val/len(df_v)*100:.2f}% del total).",
                "df_ventas",
                COLORS["primary"]
            ))

        # 2
        if not df_v.empty and "canal" in df_v:
            c_top = df_v["canal"].value_counts().idxmax()
            c_val = df_v["canal"].value_counts().max()
            preguntas_respuestas.append((
                "2. ¿Cuál es el canal de venta más utilizado por los clientes?",
                f"{c_top} con {c_val:,} transacciones ({c_val/len(df_v)*100:.2f}%).",
                "df_ventas",
                COLORS["primary"]
            ))

        # 3
        if not df_v.empty and "categoria" in df_v:
            c_top = df_v["categoria"].value_counts().idxmax()
            c_val = df_v["categoria"].value_counts().max()
            preguntas_respuestas.append((
                "3. ¿Qué categoría de productos concentra la mayor cantidad de ventas?",
                f"{c_top} con {c_val:,} transacciones.",
                "df_ventas",
                COLORS["primary"]
            ))

        # 4
        if not df_v.empty and "medio_pago" in df_v:
            c_top = df_v["medio_pago"].value_counts().idxmax()
            c_val = df_v["medio_pago"].value_counts().max()
            preguntas_respuestas.append((
                "4. ¿Cuál es el medio de pago preferido por los compradores?",
                f"{c_top} con {c_val:,} transacciones ({c_val/len(df_v)*100:.2f}%).",
                "df_ventas",
                COLORS["primary"]
            ))

        # 5
        if not df_v.empty and "calificacion_cliente" in df_v:
            calif_val = pd.to_numeric(df_v["calificacion_cliente"], errors="coerce")
            prom = calif_val.mean()
            preguntas_respuestas.append((
                "5. ¿Cuál es la calificación promedio de satisfacción del cliente?",
                f"{prom:.2f} ⭐ sobre 5.0 (calculado sobre {calif_val.count():,} valoraciones informadas).",
                "df_ventas",
                COLORS["primary"]
            ))

        # 6
        if not df_l.empty and "transportadora" in df_l:
            t_counts = df_l["transportadora"].dropna().value_counts()
            t_top = t_counts.idxmax()
            preguntas_respuestas.append((
                "6. ¿Cuál es la empresa transportadora con mayor número de despachos asignados?",
                f"{t_top} con {t_counts.max():,} eventos logísticos asignados.",
                "df_logistica",
                COLORS["success"]
            ))

        # 7
        if not df_l.empty and "ciudad_destino" in df_l:
            cd_top = df_l["ciudad_destino"].value_counts().idxmax()
            cd_val = df_l["ciudad_destino"].value_counts().max()
            preguntas_respuestas.append((
                "7. ¿Qué ciudad de destino concentra el mayor número de eventos de entrega?",
                f"{cd_top} con {cd_val:,} eventos registrados ({cd_val/len(df_l)*100:.2f}%).",
                "df_logistica",
                COLORS["success"]
            ))

        # 8
        if not df_l.empty and "estado_evento" in df_l:
            e_top = df_l["estado_evento"].value_counts().idxmax()
            e_val = df_l["estado_evento"].value_counts().max()
            preguntas_respuestas.append((
                "8. ¿Cuál es la etapa o estado logístico con mayor frecuencia en la operación?",
                f"'{e_top}' con {e_val:,} registros.",
                "df_logistica",
                COLORS["success"]
            ))

        # 9
        if not df_l.empty and "incidencia" in df_l:
            inc = df_l["incidencia"].dropna()
            i_top = inc.value_counts().idxmax()
            i_val = inc.value_counts().max()
            preguntas_respuestas.append((
                "9. ¿Cuál es la incidencia operativa más recurrente en los despachos?",
                f"'{i_top}' con {i_val} casos de un total de {len(inc):,} incidencias registradas.",
                "df_logistica",
                COLORS["success"]
            ))

        # 10
        if not df_l.empty:
            c_prom = pd.to_numeric(df_l["costo_envio"], errors="coerce").mean()
            t_prom = pd.to_numeric(df_l["tiempo_etapa_horas"], errors="coerce").mean()
            preguntas_respuestas.append((
                "10. ¿Cuáles son el costo promedio de flete y el tiempo promedio por etapa?",
                f"Costo de envío promedio: ${c_prom:,.2f} COP  |  Tiempo promedio por etapa: {t_prom:.2f} horas.",
                "df_logistica",
                COLORS["success"]
            ))

        for preg, resp, fuente, color in preguntas_respuestas:
            card = tk.Frame(inner, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
            card.pack(fill=tk.X, pady=6, padx=6)

            h = tk.Frame(card, bg=COLORS["card_bg"], padx=14, pady=10)
            h.pack(fill=tk.X)

            badge = tk.Label(
                h,
                text=fuente,
                font=("Segoe UI", 7, "bold"),
                fg="#ffffff",
                bg=color,
                padx=8,
                pady=2,
            )
            badge.pack(side=tk.RIGHT)

            lbl_p = tk.Label(h, text=preg, font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"], wraplength=850, justify="left")
            lbl_p.pack(anchor="w")

            lbl_r = tk.Label(h, text=f"Respuesta: {resp}", font=("Segoe UI", 9), fg="#1e40af", bg="#eff6ff", padx=10, pady=6, wraplength=850, justify="left")
            lbl_r.pack(anchor="w", fill=tk.X, pady=(6, 0))

    # -------------------------------------------------------------------------
    # VISTA 5: RASTREADOR DE PEDIDO (pedido_id)
    # -------------------------------------------------------------------------
    def mostrar_rastreo(self):
        self._resaltar_nav("rastreo")
        self.lbl_header_title.configure(text="🔍 Rastreador de Pedidos por 'pedido_id'")
        self._limpiar_contenido()

        # Barra de búsqueda
        search_card = tk.Frame(self.content_frame, bg=COLORS["card_bg"], padx=16, pady=14, highlightbackground=COLORS["card_border"], highlightthickness=1)
        search_card.pack(fill=tk.X, pady=(0, 14))

        tk.Label(search_card, text="Ingrese o seleccione un ID de Pedido (pedido_id):", font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(0, 10))

        ent_pedido = tk.Entry(search_card, font=("Segoe UI", 10), width=25)
        ent_pedido.pack(side=tk.LEFT, padx=6)

        # Sugerir un ID existente si hay datos
        id_ejemplo = ""
        if not self.df_ventas.empty and "pedido_id" in self.df_ventas:
            id_ejemplo = str(self.df_ventas["pedido_id"].iloc[0])
            ent_pedido.insert(0, id_ejemplo)

        results_container = tk.Frame(self.content_frame, bg=COLORS["bg_light"])
        results_container.pack(fill=tk.BOTH, expand=True)

        def buscar():
            pid = ent_pedido.get().strip()
            for widget in results_container.winfo_children():
                widget.destroy()

            if not pid:
                messagebox.showwarning("Atención", "Por favor ingrese un pedido_id.")
                return

            # Panel Ventas
            v_match = pd.DataFrame()
            if not self.df_ventas.empty and "pedido_id" in self.df_ventas:
                v_match = self.df_ventas[self.df_ventas["pedido_id"].astype(str).str.lower() == pid.lower()]

            # Panel Logística
            l_match = pd.DataFrame()
            if not self.df_logistica.empty and "pedido_id" in self.df_logistica:
                l_match = self.df_logistica[self.df_logistica["pedido_id"].astype(str).str.lower() == pid.lower()]

            # Renderizar Split Panes
            box_v = tk.LabelFrame(
                results_container,
                text=f" 🛒 Datos Comerciales (df_ventas) - {len(v_match)} Registro(s) ",
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["primary"],
                bg=COLORS["card_bg"],
                padx=10,
                pady=10,
            )
            box_v.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            if not v_match.empty:
                tv_v, _, _ = self._crear_treeview(box_v, v_match.columns.tolist(), height=3)
                self._llenar_treeview(tv_v, v_match)
            else:
                tk.Label(box_v, text=f"No se encontró el pedido '{pid}' en df_ventas.", fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(pady=10)

            box_l = tk.LabelFrame(
                results_container,
                text=f" 🚚 Trazabilidad Logística (df_logistica) - {len(l_match)} Evento(s) ",
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["success"],
                bg=COLORS["card_bg"],
                padx=10,
                pady=10,
            )
            box_l.pack(fill=tk.BOTH, expand=True)

            if not l_match.empty:
                tv_l, _, _ = self._crear_treeview(box_l, l_match.columns.tolist(), height=8)
                self._llenar_treeview(tv_l, l_match)
            else:
                tk.Label(box_l, text=f"No se encontraron eventos logísticos para el pedido '{pid}'.", fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(pady=10)

        btn_buscar = tk.Button(
            search_card,
            text="🔍 Rastrear Pedido",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["primary"],
            fg="#ffffff",
            activebackground=COLORS["primary_hover"],
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=buscar,
        )
        btn_buscar.pack(side=tk.LEFT, padx=6)

        if id_ejemplo:
            buscar()

    # -------------------------------------------------------------------------
    # VISTA 6: PERFIL DE CALIDAD DEL DATO (PARTE 4)
    # -------------------------------------------------------------------------
    def mostrar_calidad(self):
        self._resaltar_nav("calidad")
        self.lbl_header_title.configure(text="🛡️ Perfil Inicial de Calidad del Dato (Nulos, Unicidad y Duplicados)")
        self._limpiar_contenido()

        nb = ttk.Notebook(self.content_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # Tab Calidad Ventas
        tab_v = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_v, text="  🛒 Calidad: df_ventas  ")
        self._render_perfil_calidad_ui(tab_v, self.df_ventas, "df_ventas")

        # Tab Calidad Logística
        tab_l = tk.Frame(nb, bg=COLORS["card_bg"], padx=14, pady=14)
        nb.add(tab_l, text="  🚚 Calidad: df_logistica  ")
        self._render_perfil_calidad_ui(tab_l, self.df_logistica, "df_logistica")

    def _render_perfil_calidad_ui(self, parent, df, nombre):
        if df.empty:
            tk.Label(parent, text="Sin datos.", bg=COLORS["card_bg"]).pack(pady=20)
            return

        pk = perfil_calidad(df)

        # Nulos
        lbl_n = tk.Label(parent, text="4.1 Valores Nulos por Variable (Orden Descendente):", font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"])
        lbl_n.pack(anchor="w", pady=(0, 4))

        df_nulos = pk["nulos"].reset_index().rename(columns={"index": "Variable"})
        df_nulos["porcentaje_nulos"] = df_nulos["porcentaje_nulos"].astype(str) + " %"
        tv_n, _, _ = self._crear_treeview(parent, df_nulos.columns.tolist(), height=5)
        self._llenar_treeview(tv_n, df_nulos)

        # Resumen de Unicidad y Duplicados
        info_frame = tk.Frame(parent, bg="#f8fafc", padx=12, pady=10, highlightbackground="#e2e8f0", highlightthickness=1)
        info_frame.pack(fill=tk.X, pady=10)

        dup_totales = pk["filas_duplicadas"]
        rep_ids = pk["repetidos_ids"]
        rep_str = ", ".join([f"{k}: {v} repetidos" for k, v in rep_ids.items()])

        resumen_txt = (
            f"• Filas Completamente Duplicadas: {dup_totales}\n"
            f"• Identificadores Analizados: {rep_str}\n"
            f"• Alta Cardinalidad (>50 únicos): {pk['alta_cardinalidad']}\n"
            f"• Baja Cardinalidad (<=10 únicos): {pk['baja_cardinalidad']}"
        )
        tk.Label(info_frame, text=resumen_txt, font=("Segoe UI", 9), fg="#334155", bg="#f8fafc", justify="left").pack(anchor="w")

    # -------------------------------------------------------------------------
    # VISTA 7: CONCLUSIONES
    # -------------------------------------------------------------------------
    def mostrar_conclusiones(self):
        self._resaltar_nav("conclusiones")
        self.lbl_header_title.configure(text="📝 Conclusiones y Diagnóstico ETL")
        self._limpiar_contenido()

        scroll_c = tk.Canvas(self.content_frame, bg=COLORS["bg_light"], highlightthickness=0)
        s_bar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=scroll_c.yview)
        inner = tk.Frame(scroll_c, bg=COLORS["bg_light"])

        inner.bind("<Configure>", lambda e: scroll_c.configure(scrollregion=scroll_c.bbox("all")))
        scroll_c.create_window((0, 0), window=inner, anchor="nw")
        scroll_c.configure(yscrollcommand=s_bar.set)

        scroll_c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Card Ventas
        card_v = tk.Frame(inner, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        card_v.pack(fill=tk.X, pady=8, padx=6)
        tk.Frame(card_v, bg=COLORS["primary"], height=4).pack(fill=tk.X)
        
        pv = tk.Frame(card_v, bg=COLORS["card_bg"], padx=16, pady=12)
        pv.pack(fill=tk.BOTH)
        tk.Label(pv, text="📌 Hallazgos Clave: df_ventas (Fuente Comercial)", font=("Segoe UI", 11, "bold"), fg=COLORS["primary"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(0, 6))

        hallazgos_v = [
            "1. df_ventas contiene 5.000 registros y 17 variables.",
            "2. id_venta y pedido_id tienen 5.000 valores únicos y 0 registros repetidos; son identificadores aptos para garantizar la unicidad de la venta.",
            "3. No existen filas completamente duplicadas en la tabla de ventas.",
            "4. id_tienda presenta 3.501 nulos (70.02%) y calificacion_cliente 2.172 nulos (43.44%). Se deben validar reglas de negocio (ej. ventas por web/app no tienen tienda física).",
            "5. precio_unitario, valor_bruto, valor_descuento y valor_neto están almacenadas como tipo 'object'; deben convertirse a numérico en la fase de transformación.",
            "6. Se identificaron 2.828 registros con calificación válida (promedio 4.09 ⭐).",
        ]
        for h in hallazgos_v:
            tk.Label(pv, text=h, font=("Segoe UI", 9), fg=COLORS["text_dark"], bg=COLORS["card_bg"], wraplength=850, justify="left").pack(anchor="w", pady=2)

        # Card Logística
        card_l = tk.Frame(inner, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1)
        card_l.pack(fill=tk.X, pady=8, padx=6)
        tk.Frame(card_l, bg=COLORS["success"], height=4).pack(fill=tk.X)
        
        pl = tk.Frame(card_l, bg=COLORS["card_bg"], padx=16, pady=12)
        pl.pack(fill=tk.BOTH)
        tk.Label(pl, text="📌 Hallazgos Clave: df_logistica (Fuente Operativa)", font=("Segoe UI", 11, "bold"), fg=COLORS["success"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(0, 6))

        hallazgos_l = [
            "1. df_logistica contiene 50.000 registros y 13 variables.",
            "2. evento_id debería ser único, pero presenta 200 registros repetidos; además existen 99 filas completamente duplicadas (documentadas sin eliminar).",
            "3. Mayor cantidad de nulos en incidencia (98.98%) y observacion (96.55%), lo cual es esperable si la mayoría de despachos operan sin novedad.",
            "4. transportadora y numero_guia presentan 60.18% de nulos, lo cual es normal antes de la etapa de asignación y despacho.",
            "5. fecha_evento y fecha_prometida_entrega son texto y deben normalizarse a datetime.",
            "6. tiempo_etapa_horas contiene 5.000 nulos asociados a etapas iniciales donde la duración aún no aplica.",
        ]
        for h in hallazgos_l:
            tk.Label(pl, text=h, font=("Segoe UI", 9), fg=COLORS["text_dark"], bg=COLORS["card_bg"], wraplength=850, justify="left").pack(anchor="w", pady=2)

    # -------------------------------------------------------------------------
    # HELPERS Y COMPONENTES REUTILIZABLES
    # -------------------------------------------------------------------------
    def _crear_treeview(self, parent, columns, height=10):
        frame = tk.Frame(parent, bg=COLORS["card_bg"])
        frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)

        tv = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=height,
            style="Custom.Treeview",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )

        scroll_y.config(command=tv.yview)
        scroll_x.config(command=tv.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tv.heading(col, text=str(col))
            # Calcular ancho dinámico aproximado
            tv.column(col, width=max(100, len(str(col)) * 12), anchor="center")

        return tv, scroll_x, scroll_y

    def _llenar_treeview(self, tv, df):
        for item in tv.get_children():
            tv.delete(item)

        for i, (_, row) in enumerate(df.iterrows()):
            valores = ["" if pd.isna(v) else str(v) for v in row.values]
            tag = "par" if i % 2 == 0 else "impar"
            tv.insert("", tk.END, values=valores, tags=(tag,))

        tv.tag_configure("par", background="#ffffff")
        tv.tag_configure("impar", background=COLORS["table_alt"])

    def _render_tabla_con_filtro(self, parent, df):
        # Barra superior de filtro
        bar = tk.Frame(parent, bg=COLORS["card_bg"], pady=6)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="Filtrar datos:", font=("Segoe UI", 9, "bold"), fg=COLORS["text_dark"], bg=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(0, 6))
        
        ent_buscar = tk.Entry(bar, font=("Segoe UI", 9), width=30)
        ent_buscar.pack(side=tk.LEFT, padx=6)

        lbl_count = tk.Label(bar, text=f"Mostrando {min(100, len(df))} de {len(df):,} filas", font=("Segoe UI", 8), fg=COLORS["text_muted"], bg=COLORS["card_bg"])
        lbl_count.pack(side=tk.RIGHT, padx=6)

        tv, _, _ = self._crear_treeview(parent, df.columns.tolist(), height=16)
        self._llenar_treeview(tv, df.head(100))

        def filtrar(event=None):
            term = ent_buscar.get().strip().lower()
            if not term:
                sub = df.head(100)
            else:
                mascara = df.astype(str).apply(lambda row: row.str.lower().str.contains(term).any(), axis=1)
                sub = df[mascara].head(100)
            
            lbl_count.configure(text=f"Mostrando {len(sub):,} coincidencias (máx. 100)")
            self._llenar_treeview(tv, sub)

        ent_buscar.bind("<KeyRelease>", filtrar)

    def _render_estadisticos(self, parent, df_est):
        if df_est.empty:
            tk.Label(parent, text="No hay variables numéricas para resumir.", bg=COLORS["card_bg"]).pack(pady=20)
            return

        df_display = df_est.round(2).reset_index().rename(columns={"index": "Variable"})
        tv, _, _ = self._crear_treeview(parent, df_display.columns.tolist(), height=10)
        self._llenar_treeview(tv, df_display)


def main():
    app = InterfazETLApp()
    app.mainloop()


if __name__ == "__main__":
    main()
