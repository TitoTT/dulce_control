import customtkinter as ctk
from tkinter import messagebox
from consultor import Consultor
from insertor import Insertor

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dulce Control POS")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        
        self.consultor = Consultor()
        self.insertor = Insertor()
        self.carrito = []

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.side = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.side.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.side, text="MENU", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkButton(self.side, text="Dashboard", command=self.vista_dash).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="Inventario", command=self.vista_inv).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="VENDER", fg_color="green", command=self.vista_pos).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="opciones", command=self.vista_opciones).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="salir", fg_color="red", command=self.destroy).pack(pady=5, padx=10)

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.vista_dash()

    def vista_dash(self):
        for w in self.main.winfo_children(): w.destroy()
        ctk.CTkLabel(self.main, text="Dashboard", font=("Arial", 24)).pack(pady=10)
        alertas = self.consultor.contar_stock_bajo()
        f = ctk.CTkFrame(self.main, border_width=2, border_color="orange")
        f.pack(pady=20, padx=20)
        ctk.CTkLabel(f, text=f"Insumos con Stock Bajo: {alertas}", font=("Arial", 18)).pack(padx=20, pady=20)

    def vista_inv(self):
        for w in self.main.winfo_children(): w.destroy()
        self.scroll = ctk.CTkScrollableFrame(self.main, label_text="Inventario")
        self.scroll.pack(fill="both", expand=True)
        for r in self.consultor.buscar_ingrediente_para_gui(""):
            f = ctk.CTkFrame(self.scroll)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=r['nombre']).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"{r['stock_actual']} {r['unidad_medida']}").pack(side="right", padx=10)


    def vista_opciones(self):
        for w in self.main.winfo_children(): 
            w.destroy()
        ctk.CTkLabel(self.main, text="Opciones", font=("Arial", 24)).pack(pady=10)
        ctk.CTkLabel(self.main, text="Aquí podrías agregar opciones de configuración o gestión.", font=("Arial", 14)).pack(pady=20)
    # Switch para modo claro/oscuro 
        self.switch_tema = ctk.CTkSwitch(self.main, text="Modo Oscuro", command=self.toggle_tema) 
        self.switch_tema.pack(pady=10) 
        # Estado inicial: activado (oscuro) 
        self.switch_tema.select()
    
    def toggle_tema(self): 
        if self.switch_tema.get() == 1: # activado → oscuro 
            ctk.set_appearance_mode("dark") 
            self.switch_tema.configure(text="Modo Oscuro") 
        else: # desactivado → claro 
            ctk.set_appearance_mode("light") 
            self.switch_tema.configure(text="Modo Claro")

    def vista_pos(self):
        for w in self.main.winfo_children(): w.destroy()
        self.carrito = []
        
        # Configurar grid para mejor distribución de espacio
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)  # Catalogo - se expande
        container.grid_columnconfigure(1, weight=1, minsize=400)  # Carrito - también se expande
        container.grid_rowconfigure(0, weight=1)  # Expande verticalmente
        
        # Catalogo
        izq = ctk.CTkScrollableFrame(container, label_text="Productos")
        izq.grid(row=0, column=0, sticky="nsew", padx=5)
        for p in self.consultor.obtener_catalogo_productos():
            ctk.CTkButton(izq, text=f"{p['nombre']} - ${p['precio']}", 
                          command=lambda x=p: self.agregar(x)).pack(fill="x", pady=2)

        # Carrito
        der = ctk.CTkFrame(container, fg_color="transparent")
        der.grid(row=0, column=1, sticky="nsew", padx=5)
        der.grid_rowconfigure(0, weight=1)  # Carrito se expande verticalmente
        der.grid_columnconfigure(0, weight=1)
        
        self.cart_view = ctk.CTkScrollableFrame(der, label_text="Carrito")
        self.cart_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.btn_pagar = ctk.CTkButton(der, text="COBRAR $0.00", fg_color="green", command=self.finalizar)
        self.btn_pagar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    def agregar(self, p):
        self.carrito.append(p)
        self.render_cart()

    def render_cart(self):
        for w in self.cart_view.winfo_children(): w.destroy()
        total = 0
        
        for idx, item in enumerate(self.carrito):
            total += float(item['precio'])
            
            # Frame horizontal para cada item
            item_frame = ctk.CTkFrame(self.cart_view)
            item_frame.pack(fill="x", pady=2, padx=2)
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Nombre del producto truncado si es muy largo
            nombre_truncado = item['nombre']
            if len(nombre_truncado) > 35:
                nombre_truncado = nombre_truncado[:32] + "..."
            
            # Label del producto
            ctk.CTkLabel(
                item_frame, 
                text=f"{nombre_truncado} - ${item['precio']}", 
                anchor="w"
            ).grid(row=0, column=0, sticky="ew", padx=5)
            
            # Botón eliminar (papelera)
            ctk.CTkButton(
                item_frame,
                text="🗑️",
                width=30,
                height=20,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=idx: self.eliminar_del_carrito(i)
            ).grid(row=0, column=1, padx=5)
        
        self.btn_pagar.configure(text=f"COBRAR ${total:.2f}")

    def eliminar_del_carrito(self, indice):
        """Elimina un item del carrito por su índice"""
        if 0 <= indice < len(self.carrito):
            self.carrito.pop(indice)
            self.render_cart()

    def finalizar(self):
        if not self.carrito: return
        
        # Transformar carrito para validar
        items = []
        for c in self.carrito:
            items.append({'id': c['id_producto'], 'cantidad': 1, 'precio': float(c['precio'])})
        
        # Validar ingredientes disponibles
        es_valido, mensaje = self.consultor.validar_ingredientes_disponibles(items)
        
        if not es_valido:
            messagebox.showerror("Ingredientes Insuficientes", mensaje)
            return
        
        res = self.insertor.registrar_pedido_completo_gui(1, "2024-12-31", "Efectivo", items)
        if res:
            messagebox.showinfo("Éxito", "Venta realizada e inventario descontado.")
            self.carrito = []
            self.vista_pos()
        else:
            messagebox.showerror("Error", "No se pudo procesar la venta.")

if __name__ == "__main__":
    App().mainloop()