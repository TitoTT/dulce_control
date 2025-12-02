"""

MENU DE TESTEO, PENDIENTE A MEJORAS Y DE FUNCIONALIDADES

Menu principal del sistema Dulce Control
Interfaz gráfica moderna usando customtkinter
"""

import customtkinter as ctk #Importa la librería de interfaz gráfica moderna. El as ctk es un alias para escribir menos
from tkinter import messagebox #Importa los cuadros de diálogo (alertas, confirmaciones) del tkinter estándar
import sys #Para poder cerrar el programa completamente con sys.exit()

# Configuración de apariencia
ctk.set_appearance_mode("dark")  # "dark" o "light" o "system", sirve para cambiar el modo de apariencia (system usa la configuración del sistema operativo)
ctk.set_default_color_theme("blue")  #Define el color principal de los botones y elementos. Opciones: "blue", "green", "dark-blue"


class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("🍬 Dulce Control - Sistema de Gestión")
        self.geometry("600x650")
        self.resizable(True, True)
        
        # Centrar ventana
        self.center_window()
        
        # Crear interfaz
        self.crear_widgets()
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame,
            text="🍬 DULCE CONTROL",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        titulo.pack(pady=(20, 10))
        
        # Subtítulo
        subtitulo = ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestión de Dulcería",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitulo.pack(pady=(0, 30))
        
        # Frame para los botones
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="both", expand=True, padx=40)
        
        # Botones del menú
        btn_productos = ctk.CTkButton(
            botones_frame,
            text="📦 Gestión de Productos",
            command=self.abrir_productos,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        btn_productos.pack(pady=10, fill="x")
        
        btn_inventario = ctk.CTkButton(
            botones_frame,
            text="📊 Control de Inventario",
            command=self.abrir_inventario,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        btn_inventario.pack(pady=10, fill="x")
        
        btn_ventas = ctk.CTkButton(
            botones_frame,
            text="💰 Ventas",
            command=self.abrir_ventas,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        btn_ventas.pack(pady=10, fill="x")
        
        btn_reportes = ctk.CTkButton(
            botones_frame,
            text="📈 Reportes",
            command=self.abrir_reportes,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10
        )
        btn_reportes.pack(pady=10, fill="x")
        
        btn_configuracion = ctk.CTkButton(
            botones_frame,
            text="⚙️ Configuración",
            command=self.abrir_configuracion,
            height=50,
            font=ctk.CTkFont(size=16),
            corner_radius=10,
            fg_color="gray40",
            hover_color="gray30"
        )
        btn_configuracion.pack(pady=10, fill="x")
        
        # Separador visual
        separador = ctk.CTkFrame(botones_frame, height=2, fg_color="gray30")
        separador.pack(pady=15, fill="x")
        
        # Botón de salir
        btn_salir = ctk.CTkButton(
            botones_frame,
            text="❌ SALIR",
            command=self.salir,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#DC143C",
            hover_color="#8B0000",
            corner_radius=10,
            border_width=2,
            border_color="white"
        )
        btn_salir.pack(pady=10, fill="x")
        
        # Frame inferior (pie de página)
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=40, pady=20)
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0 - Dulce Control © 2024",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        version_label.pack()
    
    def abrir_productos(self):
        """Abrir módulo de productos"""
        messagebox.showinfo("Productos", "Módulo de Gestión de Productos\n(Por implementar)")
        # Aquí importarías y abrirías tu módulo de productos
        # from productos import VentanaProductos
        # VentanaProductos(self)
    
    def abrir_inventario(self):
        """Abrir módulo de inventario"""
        messagebox.showinfo("Inventario", "Módulo de Control de Inventario\n(Por implementar)")
        # from inventario import VentanaInventario
        # VentanaInventario(self)
    
    def abrir_ventas(self):
        """Abrir módulo de ventas"""
        messagebox.showinfo("Ventas", "Módulo de Ventas\n(Por implementar)")
        # from ventas import VentanaVentas
        # VentanaVentas(self)
    
    def abrir_reportes(self):
        """Abrir módulo de reportes"""
        messagebox.showinfo("Reportes", "Módulo de Reportes\n(Por implementar)")
        # from reportes import VentanaReportes
        # VentanaReportes(self)
    
    def abrir_configuracion(self):
        """Abrir configuración"""
        messagebox.showinfo("Configuración", "Configuración del Sistema\n(Por implementar)")
        # from configuracion import VentanaConfiguracion
        # VentanaConfiguracion(self)
    
    def salir(self):
        """Cerrar la aplicación"""
        respuesta = messagebox.askyesno(
            "Salir",
            "¿Estás seguro que deseas salir?"
        )
        if respuesta:
            self.quit()
            self.destroy()
            sys.exit(0)


def main():
    """Función principal para ejecutar el menú"""
    app = MenuPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()