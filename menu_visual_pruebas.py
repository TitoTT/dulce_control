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

        # Sidebar la barra lateral con botones
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
        
        # Frame superior para titulo y botón de agregar
        header_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(header_frame, text="Inventario", font=("Arial", 24, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="➕ Agregar Insumo", fg_color="green", command=self.abrir_agregar_insumo).pack(side="right", padx=10)
        
        self.scroll = ctk.CTkScrollableFrame(self.main, label_text="Ingredientes")
        self.scroll.pack(fill="both", expand=True)
        for r in self.consultor.buscar_ingrediente_para_gui(""):
            f = ctk.CTkFrame(self.scroll)
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=r['nombre']).pack(side="left", padx=10)
            # Mostrar stock y unidad
            ctk.CTkLabel(f, text=f"{r['stock_actual']} {r.get('unidad_medida','')}").pack(side="right", padx=(5,10))
            # Botón eliminar para cada insumo (falta acomodar el boton, ni idea como acomodarlo bonito, despues de 20 intentos no me sale xd)
            ctk.CTkButton(
                f,
                text="🗑️",
                width=10,
                height=9,
                corner_radius=4,
                font=ctk.CTkFont(size=10),
                fg_color="#BF0000",
                hover_color="darkred",
                command=lambda n=r['nombre']: self.confirmar_y_eliminar(n)
            ).pack(side="right", padx=0, pady=0)

    def abrir_agregar_insumo(self):
        """Abre una ventana para agregar un nuevo insumo al inventario"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Insumo")
        ventana.geometry("450x500")
        ventana.resizable(False, False)
        ventana.attributes('-topmost', True)  # Pone la ventana siempre al frente
        ventana.focus()  # Enfoca la ventana
        
        # Título
        ctk.CTkLabel(ventana, text="Agregar Nuevo Insumo", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Frame para los campos
        form_frame = ctk.CTkFrame(ventana)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campo: Nombre
        ctk.CTkLabel(form_frame, text="Nombre del Insumo:", anchor="w").pack(fill="x", pady=(10, 0))
        entry_nombre = ctk.CTkEntry(form_frame, placeholder_text="Ej: Harina")
        entry_nombre.pack(fill="x", pady=5)
        
        # Campo: Stock Actual
        ctk.CTkLabel(form_frame, text="Stock Actual:", anchor="w").pack(fill="x", pady=(10, 0))
        entry_stock = ctk.CTkEntry(form_frame, placeholder_text="Ej: 100")
        entry_stock.pack(fill="x", pady=5)
        
        # Campo: Unidad de Medida
        ctk.CTkLabel(form_frame, text="Unidad de Medida:", anchor="w").pack(fill="x", pady=(10, 0))
        entry_unidad = ctk.CTkComboBox(form_frame, values=["kg", "g", "L", "ml", "unidad", "docena"])
        entry_unidad.pack(fill="x", pady=5)
        
        # Campo: Costo Unitario
        ctk.CTkLabel(form_frame, text="Costo Unitario:", anchor="w").pack(fill="x", pady=(10, 0))
        entry_costo = ctk.CTkEntry(form_frame, placeholder_text="Ej: 50.00")
        entry_costo.pack(fill="x", pady=5)
        
        # Campo: Stock Mínimo
        ctk.CTkLabel(form_frame, text="Stock Mínimo:", anchor="w").pack(fill="x", pady=(10, 0))
        entry_stock_min = ctk.CTkEntry(form_frame, placeholder_text="Ej: 20")
        entry_stock_min.pack(fill="x", pady=5)
        
        # Frame para los botones
        btn_frame = ctk.CTkFrame(ventana, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def guardar_insumo():
            """Guarda el nuevo insumo en la base de datos"""
            nombre = entry_nombre.get().strip()
            stock = entry_stock.get().strip()
            unidad = entry_unidad.get().strip()
            costo = entry_costo.get().strip()
            stock_min = entry_stock_min.get().strip()
            
            # Validaciones básicas
            if not nombre or not stock or not unidad or not costo or not stock_min:
                messagebox.showwarning("Campos Incompletos", "Por favor completa todos los campos.")
                return
            
            try:
                stock = float(stock)
                costo = float(costo)
                stock_min = float(stock_min)
            except ValueError:
                messagebox.showerror("Error", "Stock, Costo y Stock Mínimo deben ser números.")
                return
            
            # Verificar si el nombre ya existe
            if self.consultor.ingrediente_existe(nombre):
                respuesta = messagebox.askyesno(
                    "Insumo Existente",
                    f"Ya existe un insumo llamado '{nombre}'.\n\n¿Deseas AUMENTAR el stock de este insumo?\n\n"
                    f"(Se sumarán {stock} {unidad} al stock existente y se actualizarán los demás datos)"
                )
                if not respuesta:
                    return
                
                # Actualizar ingrediente existente
                try:
                    resultado = self.insertor.actualizar_ingrediente(nombre, stock, unidad, costo, stock_min)
                    if resultado:
                        messagebox.showinfo("Éxito", f"Insumo '{nombre}' actualizado correctamente.\nStock aumentado en {stock} {unidad}.")
                        ventana.destroy()
                        self.vista_inv()  # Recargar la vista del inventario
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el insumo. Verifica los datos.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            else:
                # Es un insumo nuevo, insertarlo
                try:
                    resultado = self.insertor.insertar_ingrediente(nombre, stock, unidad, costo, stock_min)
                    if resultado:
                        messagebox.showinfo("Éxito", f"Insumo '{nombre}' agregado correctamente.")
                        ventana.destroy()
                        self.vista_inv()  # Recargar la vista del inventario
                    else:
                        messagebox.showerror("Error", "No se pudo agregar el insumo. Verifica los datos.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        def eliminar_insumo():
            """Elimina el insumo cuyo nombre esté en el campo Nombre (si existe)."""
            nombre_elim = entry_nombre.get().strip()
            if not nombre_elim:
                messagebox.showwarning("Nombre vacío", "Ingresa el nombre del insumo a eliminar.")
                return
            if not self.consultor.ingrediente_existe(nombre_elim):
                messagebox.showinfo("No encontrado", f"No existe un insumo llamado '{nombre_elim}'.")
                return
            confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Eliminar el insumo '{nombre_elim}' de la base de datos? Esta acción no se puede deshacer.")
            if not confirmar:
                return
            try:
                ok, mensaje = self.insertor.eliminar_ingrediente(nombre_elim)
                if ok:
                    messagebox.showinfo("Eliminado", mensaje)
                    ventana.destroy()
                    self.vista_inv()
                else:
                    messagebox.showerror("Error", mensaje)
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

        ctk.CTkButton(btn_frame, text="Guardar", fg_color="green", command=guardar_insumo).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#BF0000", command=eliminar_insumo).pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", command=ventana.destroy).pack(side="right", padx=5, fill="x", expand=True)

    def confirmar_y_eliminar(self, nombre: str):
        """Confirma y elimina un insumo existente del inventario. Si hay duplicados, permite elegir."""
        if not nombre:
            messagebox.showwarning("Nombre vacío", "Nombre inválido para eliminación.")
            return
        
        # Obtener todos los ingredientes con ese nombre (pueden ser duplicados)
        ingredientes = self.consultor.obtener_todos_con_nombre(nombre)
        
        if not ingredientes:
            messagebox.showinfo("No encontrado", f"No existe un insumo llamado '{nombre}'.")
            return
        
        # Si hay duplicados, permitir elegir cuál eliminar
        if len(ingredientes) > 1:
            self.mostrar_selector_duplicados(nombre, ingredientes)
            return
        
        # Si solo hay uno, proceder directamente
        ing = ingredientes[0]
        id_ing = int(ing.get('id_ingredientes', 0)) if isinstance(ing, dict) else int(ing['id_ingredientes'])
        self.eliminar_con_confirmacion(id_ing, nombre)
    
    def mostrar_selector_duplicados(self, nombre: str, ingredientes: list):
        """Muestra un diálogo para seleccionar cuál duplicado eliminar."""
        ventana_sel = ctk.CTkToplevel(self)
        ventana_sel.title(f"Seleccionar cuál '{nombre}' eliminar")
        ventana_sel.geometry("400x350")
        ventana_sel.attributes('-topmost', True)
        ventana_sel.focus()
        
        ctk.CTkLabel(ventana_sel, text=f"Hay {len(ingredientes)} insumos con el nombre '{nombre}'.\n¿Cuál deseas eliminar?", 
                     font=("Arial", 12)).pack(pady=15, padx=10)
        
        frame_opciones = ctk.CTkScrollableFrame(ventana_sel)
        frame_opciones.pack(fill="both", expand=True, padx=10, pady=10)
        
        def eliminar_seleccionado(id_ing):
            """Elimina el ingrediente seleccionado y cierra el diálogo."""
            self.eliminar_con_confirmacion(id_ing, nombre)
            ventana_sel.destroy()
        
        for ing in ingredientes:
            id_ing = int(ing.get('id_ingredientes', 0)) if isinstance(ing, dict) else int(ing['id_ingredientes'])
            stock = ing.get('stock_actual', 0) if isinstance(ing, dict) else ing['stock_actual']
            unidad = ing.get('unidad_medida', '') if isinstance(ing, dict) else ing['unidad_medida']
            costo = ing.get('costo_unitario', 0.0) if isinstance(ing, dict) else ing['costo_unitario']
            
            btn_frame = ctk.CTkFrame(frame_opciones)
            btn_frame.pack(fill="x", pady=5)
            
            info_text = f"ID: {id_ing} | Stock: {stock} {unidad} | Costo: ${costo:.2f}"
            ctk.CTkLabel(btn_frame, text=info_text, font=("Arial", 10)).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="Eliminar", fg_color="red", width=80, 
                         command=lambda i=id_ing: eliminar_seleccionado(i)).pack(side="right", padx=5)
    
    def eliminar_con_confirmacion(self, id_ing: int, nombre: str):
        """Pide confirmación y elimina el ingrediente por ID."""
        confirmar = messagebox.askyesno("Confirmar eliminación", 
                                       f"¿Eliminar el insumo '{nombre}' de la base de datos? Esta acción no se puede deshacer.")
        if not confirmar:
            return
        
        try:
            ok, mensaje = self.insertor.eliminar_ingrediente_por_id(id_ing)
            if ok:
                messagebox.showinfo("Eliminado", mensaje)
                self.vista_inv()
            else:
                messagebox.showerror("Error", mensaje)
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

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