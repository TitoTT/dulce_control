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
        ctk.CTkButton(self.side, text="🍬 Productos", command=self.vista_productos).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="📋 Pedidos", command=self.vista_pedidos).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="👥 Clientes", command=self.vista_clientes).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="opciones", command=self.vista_opciones).pack(pady=5, padx=10)
        ctk.CTkButton(self.side, text="salir", fg_color="red", command=self.destroy).pack(pady=5, padx=10)

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.vista_dash()

    #ventana menu, aletas y acceso a las demas aopciones, estadisticas y otras cosas q tal vez agregue despues,
    #si es que me acuerdo, claro
    def vista_dash(self):
        for w in self.main.winfo_children(): w.destroy()
        ctk.CTkLabel(self.main, text="Dashboard", font=("Arial", 24, "bold")).pack(pady=10)

        # Alerta stock bajo
        alertas = self.consultor.contar_stock_bajo()
        f = ctk.CTkFrame(self.main, border_width=2, border_color="orange")
        f.pack(pady=(0, 10), padx=20, fill="x")
        ctk.CTkLabel(f, text=f"⚠ Insumos con Stock Bajo: {alertas}", font=("Arial", 16)).pack(padx=20, pady=12)

        # Últimas ventas
        ventas_frame = ctk.CTkScrollableFrame(self.main, label_text="🛒 Últimas ventas")
        ventas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Encabezado de columnas
        header = ctk.CTkFrame(ventas_frame, fg_color="#2a2a2a")
        header.pack(fill="x", pady=(0, 2))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=1)
        header.grid_columnconfigure(3, weight=1)
        header.grid_columnconfigure(4, weight=1)
        for col, texto in enumerate(["#Pedido", "Cliente", "Fecha", "Método", "Total"]):
            ctk.CTkLabel(header, text=texto, font=("Arial", 11, "bold"),
                         text_color="gray").grid(row=0, column=col, padx=8, pady=4, sticky="w")

        ventas = self.consultor.obtener_ultimas_ventas(20)
        if not ventas:
            ctk.CTkLabel(ventas_frame, text="No hay ventas registradas aún.",
                         text_color="gray").pack(pady=20)
        else:
            for v in ventas:
                row = ctk.CTkFrame(ventas_frame)
                row.pack(fill="x", pady=2)
                row.grid_columnconfigure(0, weight=1)
                row.grid_columnconfigure(1, weight=2)
                row.grid_columnconfigure(2, weight=1)
                row.grid_columnconfigure(3, weight=1)
                row.grid_columnconfigure(4, weight=1)
                ctk.CTkLabel(row, text=f"#{v['id_pedido']}").grid(row=0, column=0, padx=8, pady=6, sticky="w")
                ctk.CTkLabel(row, text=v['cliente']).grid(row=0, column=1, padx=8, pady=6, sticky="w")
                ctk.CTkLabel(row, text=str(v['fecha_pedido'])).grid(row=0, column=2, padx=8, pady=6, sticky="w")
                ctk.CTkLabel(row, text=v['metodo_de_pago']).grid(row=0, column=3, padx=8, pady=6, sticky="w")
                ctk.CTkLabel(row, text=f"${float(v['total']):.2f}",
                             text_color="lightgreen").grid(row=0, column=4, padx=8, pady=6, sticky="w")

    #############################################################################################################################################
    def vista_inv(self):
        for w in self.main.winfo_children(): w.destroy()

        # Título y botón agregar
        header_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(header_frame, text="Inventario", font=("Arial", 24, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="➕ Agregar Insumo", fg_color="green",
                      command=self.abrir_agregar_insumo).pack(side="right", padx=10)

        # Pestañas
        tabs = ctk.CTkTabview(self.main)
        tabs.pack(fill="both", expand=True, padx=10, pady=5)
        tabs.add("📦 Insumos")
        tabs.add("📋 Movimientos")

        # ── Pestaña Insumos ──
        tab_insumos = tabs.tab("📦 Insumos")
        scroll = ctk.CTkScrollableFrame(tab_insumos)
        scroll.pack(fill="both", expand=True)
        for r in self.consultor.buscar_ingrediente_para_gui(""):
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=r['nombre']).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"{r['stock_actual']} {r.get('unidad_medida','')}").pack(side="right", padx=(5, 10))
            ctk.CTkButton(
                f, text="＋", width=28, height=24, corner_radius=4,
                font=ctk.CTkFont(size=12), fg_color="#1a6b3c", hover_color="#145530",
                command=lambda ing=r: self.abrir_aumentar_stock(ing)
            ).pack(side="right", padx=2, pady=2)
            ctk.CTkButton(
                f, text="🗑️", width=28, height=24, corner_radius=4,
                font=ctk.CTkFont(size=10), fg_color="#BF0000", hover_color="darkred",
                command=lambda n=r['nombre']: self.confirmar_y_eliminar(n)
            ).pack(side="right", padx=2, pady=2)

        # ── Pestaña Movimientos ──
        tab_mov = tabs.tab("📋 Movimientos")
        mov_scroll = ctk.CTkScrollableFrame(tab_mov)
        mov_scroll.pack(fill="both", expand=True)

        movimientos = self.consultor.obtener_movimientos_recientes(30)
        if not movimientos:
            ctk.CTkLabel(mov_scroll, text="No hay movimientos en los últimos 30 días.",
                         text_color="gray").pack(pady=20)
        else:
            for m in movimientos:
                texto = f"[{m['fecha']}]  {m['tipo_entidad']}  {m['nombre']}  —  {m['tipo']}  {m['cantidad']}"
                if m['observaciones']:
                    texto += f"  ({m['observaciones']})"
                ctk.CTkLabel(mov_scroll, text=texto, anchor="w").pack(fill="x", padx=10, pady=2)

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

    def abrir_aumentar_stock(self, ingrediente: dict):
        """Ventana para aumentar stock y actualizar precio de un ingrediente."""
        nombre    = ingrediente.get('nombre', '')
        stock_act = ingrediente.get('stock_actual', 0)
        unidad    = ingrediente.get('unidad_medida', '')
        costo_act = float(ingrediente.get('costo_unitario', 0))

        vent = ctk.CTkToplevel(self)
        vent.title(f"Actualizar — {nombre}")
        vent.geometry("380x320")
        vent.resizable(False, False)
        vent.attributes('-topmost', True)
        vent.focus()
        vent.grab_set()

        ctk.CTkLabel(vent, text=f"📦 {nombre}", font=("Arial", 16, "bold")).pack(pady=(14, 4))

        # Stock actual (solo lectura)
        info_frame = ctk.CTkFrame(vent)
        info_frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(info_frame, text="Stock actual:", anchor="w").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(info_frame, text=f"{stock_act} {unidad}",
                     font=("Arial", 13, "bold"), text_color="lightblue").grid(row=0, column=1, padx=10, sticky="w")

        # Cantidad a agregar
        ctk.CTkLabel(info_frame, text=f"Cantidad a agregar ({unidad}):", anchor="w").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        entry_cantidad = ctk.CTkEntry(info_frame, placeholder_text="Ej: 50", width=120)
        entry_cantidad.grid(row=1, column=1, padx=10, pady=6)

        # Nuevo precio unitario
        ctk.CTkLabel(info_frame, text="Nuevo costo unitario ($):", anchor="w").grid(row=2, column=0, padx=10, pady=6, sticky="w")
        entry_costo = ctk.CTkEntry(info_frame, width=120)
        entry_costo.insert(0, str(costo_act))   # precarga el valor actual
        entry_costo.grid(row=2, column=1, padx=10, pady=6)

        def guardar():
            cant_str  = entry_cantidad.get().strip()
            costo_str = entry_costo.get().strip()

            if not cant_str:
                messagebox.showwarning("Campo vacío", "Ingresá la cantidad a agregar.", parent=vent)
                return
            try:
                cant_agregar = float(cant_str)
                nuevo_costo  = float(costo_str) if costo_str else costo_act
            except ValueError:
                messagebox.showerror("Error", "Cantidad y costo deben ser números.", parent=vent)
                return
            if cant_agregar <= 0:
                messagebox.showwarning("Valor inválido", "La cantidad debe ser mayor a 0.", parent=vent)
                return

            ok = self.insertor.actualizar_ingrediente(
                nombre, cant_agregar, unidad, nuevo_costo, ingrediente.get('stock_minimo', 0)
            )
            if ok:
                nuevo_total = stock_act + cant_agregar
                messagebox.showinfo("✅ Actualizado",
                                    f"Stock de '{nombre}' actualizado.\n"
                                    f"{stock_act} + {cant_agregar} = {nuevo_total} {unidad}\n"
                                    f"Nuevo costo: ${nuevo_costo:.2f}", parent=vent)
                vent.destroy()
                self.vista_inv()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el ingrediente.", parent=vent)

        ctk.CTkButton(vent, text="Guardar cambios", fg_color="green",
                      height=38, command=guardar).pack(pady=14, padx=20, fill="x")
    ###############################################################################################################################################

    def vista_clientes(self):
        for w in self.main.winfo_children(): w.destroy()
        ctk.CTkLabel(self.main, text="Clientes", font=("Arial", 24, "bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(self.main, label_text="Clientes registrados")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        clientes = self.consultor.obtener_todos_los_clientes()
        if not clientes:
            ctk.CTkLabel(scroll, text="No hay clientes registrados.",
                         text_color="gray").pack(pady=20)
            return

        for c in clientes:
            nombre = f"{c.get('nombre','')} {c.get('apellido','')}".strip()
            dni    = c.get('dni') or '—'
            tel    = c.get('telefono') or '—'
            fila   = ctk.CTkFrame(scroll)
            fila.pack(fill="x", pady=2, padx=5)
            fila.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(fila, text=nombre, font=("Arial", 13),
                         anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(fila, text=f"DNI: {dni}  |  Tel: {tel}",
                         text_color="gray", font=("Arial", 11),
                         anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
            ctk.CTkButton(fila, text="Ver detalle", width=90,
                          command=lambda cl=c: self.abrir_detalle_cliente(cl)
                          ).grid(row=0, column=2, padx=10, pady=6)

    def abrir_detalle_cliente(self, cliente: dict):
        nombre_completo = f"{cliente.get('nombre','')} {cliente.get('apellido','')}".strip()
        id_cli = int(cliente.get('id_cliente') or 0)

        vent = ctk.CTkToplevel(self)
        vent.title(f"Cliente — {nombre_completo}")
        vent.geometry("560x520")
        vent.attributes('-topmost', True)
        vent.focus()
        vent.grab_set()

        # Datos personales
        ctk.CTkLabel(vent, text=f"👤 {nombre_completo}",
                     font=("Arial", 18, "bold")).pack(pady=(14, 4))

        datos_frame = ctk.CTkFrame(vent)
        datos_frame.pack(fill="x", padx=20, pady=6)
        datos = [
            ("DNI",       cliente.get('dni') or '—'),
            ("Teléfono",  cliente.get('telefono') or '—'),
            ("Dirección", cliente.get('direccion') or '—'),
            ("Registrado", str(cliente.get('created_at', '—'))),
        ]
        for i, (label, valor) in enumerate(datos):
            ctk.CTkLabel(datos_frame, text=f"{label}:", font=("Arial", 11, "bold"),
                         anchor="w", width=90).grid(row=i, column=0, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(datos_frame, text=valor, anchor="w"
                         ).grid(row=i, column=1, padx=10, pady=3, sticky="w")

        # Historial de pedidos
        ctk.CTkLabel(vent, text="Historial de pedidos",
                     font=("Arial", 13, "bold")).pack(pady=(12, 2))

        pedidos_scroll = ctk.CTkScrollableFrame(vent, height=200)
        pedidos_scroll.pack(fill="both", expand=True, padx=20, pady=4)

        pedidos = self.consultor.obtener_detalle_cliente(id_cli)
        if not pedidos:
            ctk.CTkLabel(pedidos_scroll, text="Sin pedidos registrados.",
                         text_color="gray").pack(pady=10)
        else:
            monto_total = 0
            for p in pedidos:
                monto_total += float(p.get('total') or 0)
                row = ctk.CTkFrame(pedidos_scroll)
                row.pack(fill="x", pady=2)
                row.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(row, text=f"#{p['id_pedido']}  |  {p['fecha_pedido']}",
                             font=("Arial", 11)).grid(row=0, column=0, padx=8, pady=5, sticky="w")
                ctk.CTkLabel(row, text=f"{p['estado']}  —  {p['metodo_de_pago']}",
                             text_color="gray").grid(row=0, column=1, padx=8, sticky="w")
                ctk.CTkLabel(row, text=f"${float(p['total']):.2f}",
                             text_color="lightgreen").grid(row=0, column=2, padx=8, sticky="e")

            ctk.CTkLabel(vent, text=f"Total acumulado:  ${monto_total:.2f}",
                         font=("Arial", 13, "bold"), text_color="lightgreen").pack(pady=8)

   # Opciones y configuración (modo claro/oscuro)############################################################################################################### 

    def vista_opciones(self):
        for w in self.main.winfo_children(): 
            w.destroy()
        ctk.CTkLabel(self.main, text="Opciones", font=("Arial", 24)).pack(pady=10)
        ctk.CTkLabel(self.main, text="Aquí van las config xd", font=("Arial", 14)).pack(pady=20)
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


    #####################################################################################################################################################
    def vista_pos(self):
        for w in self.main.winfo_children(): w.destroy()
        self.carrito = [] # cada item: {'id_producto', 'nombre', 'precio', 'cantidad'}
        
        # Configurar grid para mejor distribución de espacio
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkFrame(self.main, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)  # Catalogo - se expande
        container.grid_columnconfigure(1, weight=1, minsize=400)  # Carrito - también se expande
        container.grid_rowconfigure(0, weight=1)  # Expande verticalmente
        
        # Catalogo izquierdo#################################################
        izq = ctk.CTkScrollableFrame(container, label_text="Productos")
        izq.grid(row=0, column=0, sticky="nsew", padx=5)
        for p in self.consultor.obtener_catalogo_productos():
            ctk.CTkButton(
                izq,
                text=f"{p['nombre']}  —  ${float(p['precio']):.2f}",
                anchor="w",
                command=lambda x=p: self.agregar(x)
            ).pack(fill="x", pady=2)

            
          # ── Panel derecho (carrito + controles) ─────────────────────
        der = ctk.CTkFrame(container, fg_color="transparent")
        der.grid(row=0, column=1, sticky="nsew", padx=5)
        der.grid_rowconfigure(1, weight=1)  # Carrito se expande verticalmente
        der.grid_columnconfigure(0, weight=1)
        
        # — Selector de cliente —
        cliente_frame = ctk.CTkFrame(der, border_width=1, border_color="#444")
        cliente_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        cliente_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cliente_frame, text="👤 Cliente", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(8, 2), sticky="w")

        self.entry_cliente = ctk.CTkEntry(cliente_frame, placeholder_text="Escribí nombre o DNI")
        self.entry_cliente.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(10, 5), pady=5)
        self.entry_cliente.bind("<Return>", lambda e: self._buscar_cliente_pos())

        ctk.CTkButton(cliente_frame, text="🔍 Buscar", width=90,
                      command=self._buscar_cliente_pos).grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(cliente_frame, text="➕ Nuevo Cliente", width=140,
                      fg_color="#1a6b3c", hover_color="#145530",
                      command=self._ventana_nuevo_cliente).grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

        self.label_cliente_sel = ctk.CTkLabel(cliente_frame, text="⚠ Sin cliente seleccionado",
                                               text_color="orange", font=("Arial", 11))
        self.label_cliente_sel.grid(row=2, column=1, columnspan=2, padx=8, pady=(0, 8), sticky="w")
        self._id_cliente_sel = None


        # - Carrito -
        self.cart_view = ctk.CTkScrollableFrame(der, label_text="Carrito")
        self.cart_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # — Fecha de entrega —
        fecha_frame = ctk.CTkFrame(der, fg_color="transparent")
        fecha_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        fecha_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(fecha_frame, text="Entrega (AAAA-MM-DD):", width=170).grid(row=0, column=0, padx=5)
        self.entry_fecha = ctk.CTkEntry(fecha_frame, placeholder_text="2025-12-31")
        self.entry_fecha.grid(row=0, column=1, sticky="ew", padx=5)

         # — Método de pago —
        pago_frame = ctk.CTkFrame(der, fg_color="transparent")
        pago_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        pago_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pago_frame, text="Método de pago:", width=170).grid(row=0, column=0, padx=5)
        self.combo_pago = ctk.CTkComboBox(pago_frame, values=["Efectivo", "Transferencia", "Débito", "Crédito"])
        self.combo_pago.set("Efectivo")
        self.combo_pago.grid(row=0, column=1, sticky="ew", padx=5)
        
        # — Botón cobrar —
        self.btn_pagar = ctk.CTkButton(der, text="COBRAR  $0.00", fg_color="green",
                                        height=45, font=("Arial", 15, "bold"),
                                        command=self.finalizar)
        self.btn_pagar.grid(row=4, column=0, sticky="ew", padx=10, pady=10)



    # ── Buscar cliente desde el POS ─────────────────────────────────
    def _buscar_cliente_pos(self):
        termino = self.entry_cliente.get().strip()
        if not termino:
            messagebox.showwarning("Buscar cliente", "Escribí un nombre o DNI antes de buscar.")
            return

        resultados = self.consultor.buscar_cliente(termino)

        if not resultados:
            crear = messagebox.askyesno(
                "Cliente no encontrado",
                f"No se encontró ningún cliente con '{termino}'.\n\n¿Querés crear un cliente nuevo?"
            )
            if crear:
                self._ventana_nuevo_cliente()
            return

        if len(resultados) == 1:
            self._seleccionar_cliente(resultados[0])
            return

        # Varios resultados → ventana para elegir
        vent = ctk.CTkToplevel(self)
        vent.title("Seleccionar cliente")
        vent.geometry("500x320")
        vent.attributes('-topmost', True)
        vent.focus()
        ctk.CTkLabel(vent, text=f"Se encontraron {len(resultados)} clientes. Elegí uno:",
                     font=("Arial", 13)).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(vent)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        def elegir(cl, v):
            self._seleccionar_cliente(cl)
            v.destroy()

        for c in resultados:
            nombre = f"{c.get('nombre','')} {c.get('apellido','')}".strip()
            dni    = c.get('dni') or '—'
            tel    = c.get('telefono') or '—'
            texto  = f"{nombre}   |   DNI: {dni}   |   Tel: {tel}"
            ctk.CTkButton(
                scroll, text=texto, anchor="w",
                command=lambda cl=c: elegir(cl, vent)
            ).pack(fill="x", pady=3)




    def _seleccionar_cliente(self, cliente: dict):
        self._id_cliente_sel = cliente.get('id_cliente')
        nombre_completo = f"{cliente.get('nombre','')} {cliente.get('apellido','')}".strip()
        self.label_cliente_sel.configure(
            text=f"✅ {nombre_completo}  (ID {self._id_cliente_sel})",
            text_color="lightgreen"
        )

    def _ventana_nuevo_cliente(self):
        """Formulario rápido para crear un cliente desde el POS."""
        vent = ctk.CTkToplevel(self)
        vent.title("Nuevo Cliente")
        vent.geometry("380x380")
        vent.attributes('-topmost', True)
        vent.focus()

        ctk.CTkLabel(vent, text="Nuevo Cliente", font=("Arial", 16, "bold")).pack(pady=12)
        form = ctk.CTkFrame(vent)
        form.pack(fill="both", expand=True, padx=20, pady=5)

        campos = {}
        for campo, placeholder in [("nombre", "Juan"), ("apellido", "Pérez"),
                                    ("dni", "12345678"), ("telefono", "3815000000"),
                                    ("direccion", "Calle 123")]:
            ctk.CTkLabel(form, text=campo.capitalize() + ":", anchor="w").pack(fill="x", pady=(6, 0))
            e = ctk.CTkEntry(form, placeholder_text=placeholder)
            e.pack(fill="x", pady=2)
            campos[campo] = e

        def guardar():
            nombre = campos['nombre'].get().strip()
            apellido = campos['apellido'].get().strip()
            if not nombre or not apellido:
                messagebox.showwarning("Faltan datos", "Nombre y apellido son obligatorios.")
                return
            conn = self.consultor.conexion.conectar()
            if not conn:
                messagebox.showerror("Error", "Sin conexión a la base de datos.")
                return
            try:
                import pymysql

                def nulo(campo):
                    v = campos[campo].get().strip()
                    return v if v else None
                
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO cliente (nombre, apellido, dni, telefono, direccion) VALUES (%s,%s,%s,%s,%s)",
                        (nombre, apellido,
                         nulo('dni'),
                         nulo('telefono'),
                         nulo('direccion'))
                    )
                    conn.commit()
                    nuevo_id = cur.lastrowid
                self.consultor.conexion.cerrar()
                self._seleccionar_cliente({'id_cliente': nuevo_id, 'nombre': nombre, 'apellido': apellido})
                messagebox.showinfo("Éxito", f"Cliente '{nombre} {apellido}' creado.")
                vent.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(vent, text="Guardar", fg_color="green", command=guardar).pack(pady=12, padx=20, fill="x")

    # ── Carrito ─────────────────────────────────────────────────────
    def agregar(self, p):
        """Agrega el producto al carrito. Si ya existe, suma la cantidad."""
        for item in self.carrito:
            if item['id_producto'] == p['id_producto']:
                item['cantidad'] += 1
                self.render_cart()
                return
        self.carrito.append({**p, 'cantidad': 1})
        self.render_cart()



    def render_cart(self):
        for w in self.cart_view.winfo_children():
            w.destroy()
        total = 0

        for idx, item in enumerate(self.carrito):
            subtotal = float(item['precio']) * item['cantidad']
            total += subtotal

            row = ctk.CTkFrame(self.cart_view)
            row.pack(fill="x", pady=2, padx=2)
            row.grid_columnconfigure(0, weight=1)

            nombre_truncado = item['nombre'][:30] + "..." if len(item['nombre']) > 30 else item['nombre']
            ctk.CTkLabel(row, text=f"{nombre_truncado}  ${float(item['precio']):.2f}",
                         anchor="w").grid(row=0, column=0, sticky="ew", padx=6)

            # Controles de cantidad: − cantidad +
            ctk.CTkButton(row, text="−", width=28, height=24, fg_color="#555",
                          command=lambda i=idx: self._cambiar_cantidad(i, -1)
                          ).grid(row=0, column=1)
            ctk.CTkLabel(row, text=str(item['cantidad']), width=28).grid(row=0, column=2)
            ctk.CTkButton(row, text="+", width=28, height=24, fg_color="#555",
                          command=lambda i=idx: self._cambiar_cantidad(i, +1)
                          ).grid(row=0, column=3)

            ctk.CTkLabel(row, text=f"${subtotal:.2f}", width=60, anchor="e"
                         ).grid(row=0, column=4, padx=4)

            ctk.CTkButton(row, text="🗑️", width=32, height=24,
                          fg_color="red", hover_color="darkred",
                          command=lambda i=idx: self.eliminar_del_carrito(i)
                          ).grid(row=0, column=5, padx=4)

        self.btn_pagar.configure(text=f"COBRAR  ${total:.2f}")


    def _cambiar_cantidad(self, indice, delta):
        item = self.carrito[indice]
        nueva = item['cantidad'] + delta
        if nueva <= 0:
            self.carrito.pop(indice)
        else:
            item['cantidad'] = nueva
        self.render_cart()



    def eliminar_del_carrito(self, indice):
        """Elimina un item del carrito por su índice"""
        if 0 <= indice < len(self.carrito):
            self.carrito.pop(indice)
            self.render_cart()



    # ── Confirmación y cierre de venta ───────────────────────────────
    def finalizar(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacio", "Agrega productos antes de cobrar.")
            return
        
        # Si no hay cliente seleccionado, usar cliente "Mostrador"
        if not self._id_cliente_sel:
            mostrador = self.consultor.buscar_cliente("Mostrador")
            if mostrador:
                self._id_cliente_sel = mostrador[0]['id_cliente']
            else:
                messagebox.showwarning(
                    "Sin cliente base",
                    "No existe el cliente 'Mostrador' en la base de datos.\n"
                    "Crealo una vez con ese nombre para habilitar ventas rápidas."
                )
                return
        
         # Validar fecha
        fecha = self.entry_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Sin fecha", "Ingresá la fecha de entrega.")
            return
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha):
            messagebox.showwarning("Fecha inválida", "Usá el formato AAAA-MM-DD, por ejemplo 2025-06-30.")
            return

        metodo_pago = self.combo_pago.get()

        # Construir items con cantidad real
        items = [{'id': c['id_producto'], 'cantidad': c['cantidad'], 'precio': float(c['precio'])}
                 for c in self.carrito]

        # Validar stock de ingredientes
        es_valido, msg = self.consultor.validar_ingredientes_disponibles(items)
        if not es_valido:
            messagebox.showerror("Ingredientes insuficientes", msg)
            return

        # Pantalla de confirmación
        total = sum(c['cantidad'] * float(c['precio']) for c in self.carrito)
        lineas = "\n".join(f"  • {c['nombre']}  x{c['cantidad']}  =  ${c['cantidad']*float(c['precio']):.2f}"
                           for c in self.carrito)
        resumen = (f"Cliente ID: {self._id_cliente_sel}\n"
                   f"Entrega: {fecha}    Pago: {metodo_pago}\n\n"
                   f"{lineas}\n\n"
                   f"TOTAL:  ${total:.2f}\n\n"
                   f"¿Confirmás la venta?")

        if not messagebox.askyesno("Confirmar venta", resumen):
            return

        res = self.insertor.registrar_pedido_completo_gui(
            self._id_cliente_sel, fecha, metodo_pago, items
        )
        if res:
            messagebox.showinfo("✅ Venta registrada", f"Pedido #{res} guardado correctamente.\nInventario actualizado.")
            self.carrito = []
            self._id_cliente_sel = None
            self.vista_pos()
        else:
            messagebox.showerror("Error", "No se pudo procesar la venta.")


    def vista_pedidos(self):
        for w in self.main.winfo_children(): w.destroy()

        # Título
        ctk.CTkLabel(self.main, text="📋 Pedidos", font=("Arial", 24, "bold")).pack(pady=10)

        # Filtro por estado
        filtro_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        filtro_frame.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(filtro_frame, text="Filtrar por estado:").pack(side="left", padx=(0, 10))
        self.combo_filtro = ctk.CTkComboBox(
            filtro_frame,
            values=["todos", "Pendiente", "En preparación", "Listo", "Entregado"],
            command=lambda v: self._recargar_pedidos(v)
        )
        self.combo_filtro.set("todos")
        self.combo_filtro.pack(side="left")

        # Encabezado de columnas
        self.pedidos_container = ctk.CTkFrame(self.main, fg_color="transparent")
        self.pedidos_container.pack(fill="both", expand=True, padx=20)

        header = ctk.CTkFrame(self.pedidos_container, fg_color="#2a2a2a")
        header.pack(fill="x", pady=(0, 2))
        for col, (texto, w) in enumerate([
            ("#", 50), ("Cliente", 180), ("Estado", 120),
            ("Entrega", 100), ("Pago", 110), ("Total", 80), ("", 160)
        ]):
            header.grid_columnconfigure(col, minsize=w)
            ctk.CTkLabel(header, text=texto, font=("Arial", 11, "bold"),
                         text_color="gray").grid(row=0, column=col, padx=8, pady=5, sticky="w")

        # Lista scrolleable
        self.pedidos_scroll = ctk.CTkScrollableFrame(self.pedidos_container)
        self.pedidos_scroll.pack(fill="both", expand=True)

        self._recargar_pedidos("todos")

    def _recargar_pedidos(self, estado: str):
        """Limpia y vuelve a cargar la lista de pedidos según el filtro."""
        for w in self.pedidos_scroll.winfo_children():
            w.destroy()

        ESTADOS     = ["Pendiente", "En preparación", "Listo", "Entregado"]
        COLORES     = {
            "Pendiente":       "#b58900",
            "En preparación":  "#2066a8",
            "Listo":           "#1a6b3c",
            "Entregado":       "#555555",
        }

        pedidos = self.consultor.obtener_pedidos(estado)
        if not pedidos:
            ctk.CTkLabel(self.pedidos_scroll, text="No hay pedidos para mostrar.",
                         text_color="gray").pack(pady=20)
            return

        for p in pedidos:
            row = ctk.CTkFrame(self.pedidos_scroll)
            row.pack(fill="x", pady=2)
            for col in range(7):
                row.grid_columnconfigure(col, weight=1)

            color_estado = COLORES.get(p['estado'], "#555")

            ctk.CTkLabel(row, text=f"#{p['id_pedido']}", width=50
                         ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=p['cliente'], width=180
                         ).grid(row=0, column=1, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=p['estado'], width=120,
                         text_color=color_estado, font=("Arial", 11, "bold")
                         ).grid(row=0, column=2, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=str(p['fecha_entrega']), width=100
                         ).grid(row=0, column=3, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=p['metodo_de_pago'], width=110
                         ).grid(row=0, column=4, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=f"${float(p['total']):.2f}", width=80,
                         text_color="lightgreen"
                         ).grid(row=0, column=5, padx=8, pady=8, sticky="w")

            # Botones: cambiar estado y ver detalle
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=6, padx=4, pady=4)

            ctk.CTkButton(
                btn_frame, text="Ver", width=50,
                command=lambda pid=p['id_pedido'], pcli=p['cliente'],
                               pest=p['estado'], pfecha=p['fecha_entrega'],
                               ppago=p['metodo_de_pago'], ptotal=p['total']:
                    self._abrir_detalle_pedido(pid, pcli, pest, pfecha, ppago, ptotal)
            ).pack(side="left", padx=2)

            idx_actual = ESTADOS.index(p['estado']) if p['estado'] in ESTADOS else -1
            sig_estado = ESTADOS[idx_actual + 1] if idx_actual < len(ESTADOS) - 1 else None

            if sig_estado:
                ctk.CTkButton(
                    btn_frame, text=f"→ {sig_estado}", width=110,
                    fg_color=COLORES.get(sig_estado, "#555"),
                    hover_color="#333",
                    command=lambda pid=p['id_pedido'], sig=sig_estado:
                        self._avanzar_estado(pid, sig)
                ).pack(side="left", padx=2)


    def _avanzar_estado(self, id_pedido: int, nuevo_estado: str):
        ok = self.consultor.cambiar_estado_pedido(id_pedido, nuevo_estado)
        if ok:
            self._recargar_pedidos(self.combo_filtro.get())
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado del pedido.")



    def _abrir_detalle_pedido(self, id_pedido, cliente, estado, fecha_entrega, metodo_pago, total):
        vent = ctk.CTkToplevel(self)
        vent.title(f"Pedido #{id_pedido}")
        vent.geometry("480x420")
        vent.attributes('-topmost', True)
        vent.focus()
        vent.grab_set()

        ctk.CTkLabel(vent, text=f"Pedido #{id_pedido}",
                     font=("Arial", 18, "bold")).pack(pady=(14, 4))

        # Datos del pedido
        datos_frame = ctk.CTkFrame(vent)
        datos_frame.pack(fill="x", padx=20, pady=6)
        for i, (label, valor) in enumerate([
            ("Cliente",    cliente),
            ("Estado",     estado),
            ("Entrega",    str(fecha_entrega)),
            ("Método pago", metodo_pago),
        ]):
            ctk.CTkLabel(datos_frame, text=f"{label}:", font=("Arial", 11, "bold"),
                         anchor="w", width=100).grid(row=i, column=0, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(datos_frame, text=valor,
                         anchor="w").grid(row=i, column=1, padx=10, pady=3, sticky="w")

        # Productos del pedido
        ctk.CTkLabel(vent, text="Productos", font=("Arial", 13, "bold")).pack(pady=(10, 2))
        items_scroll = ctk.CTkScrollableFrame(vent, height=150)
        items_scroll.pack(fill="x", padx=20, pady=4)

        items = self.consultor.obtener_items_pedido(id_pedido)
        for item in items:
            r = ctk.CTkFrame(items_scroll)
            r.pack(fill="x", pady=2)
            r.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(r, text=item['producto'], anchor="w"
                         ).grid(row=0, column=0, padx=8, pady=4, sticky="w")
            ctk.CTkLabel(r, text=f"x{item['cantidad']}  @${float(item['precio_unitario']):.2f}"
                         ).grid(row=0, column=1, padx=8)
            ctk.CTkLabel(r, text=f"${float(item['subtotal']):.2f}",
                         text_color="lightgreen").grid(row=0, column=2, padx=8)

        ctk.CTkLabel(vent, text=f"Total:  ${float(total):.2f}",
                     font=("Arial", 14, "bold"), text_color="lightgreen").pack(pady=10)    
        


    def vista_productos(self):
        for w in self.main.winfo_children(): w.destroy()

        header_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        header_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(header_frame, text="🍬 Productos", font=("Arial", 24, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="➕ Nuevo Producto", fg_color="green",
                      command=lambda: self.abrir_form_producto()).pack(side="right", padx=10)

        scroll = ctk.CTkScrollableFrame(self.main, label_text="Catálogo")
        scroll.pack(fill="both", expand=True, padx=10, pady=5)

        productos = self.consultor.obtener_todos_los_productos()
        if not productos:
            ctk.CTkLabel(scroll, text="No hay productos registrados.",
                         text_color="gray").pack(pady=20)
            return

        # Encabezado
        header = ctk.CTkFrame(scroll, fg_color="#2a2a2a")
        header.pack(fill="x", pady=(0, 2))
        for col, texto in enumerate(["Nombre", "Categoría", "Precio", "Stock", ""]):
            header.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(header, text=texto, font=("Arial", 11, "bold"),
                         text_color="gray").grid(row=0, column=col, padx=8, pady=5, sticky="w")

        for p in productos:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            for col in range(5):
                row.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(row, text=p['nombre'], anchor="w"
                         ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=p['categoria'], anchor="w"
                         ).grid(row=0, column=1, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=f"${float(p['precio']):.2f}",
                         text_color="lightgreen"
                         ).grid(row=0, column=2, padx=8, pady=8, sticky="w")
            ctk.CTkLabel(row, text=str(p['stock'])
                         ).grid(row=0, column=3, padx=8, pady=8, sticky="w")

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=4, padx=4, pady=4)
            ctk.CTkButton(btn_frame, text="✏️ Editar", width=80,
                          command=lambda prod=p: self.abrir_form_producto(prod)
                          ).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="📋 Receta", width=80, fg_color="#1a4a7a",
                          command=lambda prod=p: self.abrir_receta(prod)
                          ).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑️", width=36,
                          fg_color="#BF0000", hover_color="darkred",
                          command=lambda pid=p['id_producto'], pnom=p['nombre']:
                              self._eliminar_producto(pid, pnom)
                          ).pack(side="left", padx=2)

    def abrir_form_producto(self, producto: dict | None = None):
        """Formulario para crear o editar un producto."""
        es_edicion = producto is not None
        vent = ctk.CTkToplevel(self)
        vent.title("Editar Producto" if es_edicion else "Nuevo Producto")
        vent.geometry("420x480")
        vent.resizable(False, False)
        vent.attributes('-topmost', True)
        vent.focus()
        vent.grab_set()

        ctk.CTkLabel(vent, text="Editar Producto" if es_edicion else "Nuevo Producto",
                     font=("Arial", 16, "bold")).pack(pady=12)

        form = ctk.CTkFrame(vent)
        form.pack(fill="both", expand=True, padx=20, pady=5)

        campos = {}
        filas = [
            ("nombre",             "Nombre",              "Ej: Tarta de chocolate"),
            ("precio",             "Precio ($)",          "Ej: 1500.00"),
            ("stock",              "Stock inicial",       "Ej: 10"),
            ("categoria",          "Categoría",           "Ej: Torta, Factura, Postre"),
            ("tiempo_preparacion", "Tiempo prep. (min)",  "Ej: 60"),
            ("descripcion",        "Descripción",         "Opcional"),
        ]
        for key, label, placeholder in filas:
            ctk.CTkLabel(form, text=label + ":", anchor="w").pack(fill="x", pady=(8, 0))
            e = ctk.CTkEntry(form, placeholder_text=placeholder)
            if es_edicion and producto.get(key) is not None:
                e.insert(0, str(producto[key]))
            e.pack(fill="x", pady=2)
            campos[key] = e

        def guardar():
            nombre   = campos['nombre'].get().strip()
            precio   = campos['precio'].get().strip()
            stock    = campos['stock'].get().strip()
            categoria = campos['categoria'].get().strip()

            if not nombre or not precio or not stock or not categoria:
                messagebox.showwarning("Faltan datos",
                                       "Nombre, precio, stock y categoría son obligatorios.",
                                       parent=vent)
                return
            try:
                precio_f = float(precio)
                stock_i  = int(stock)
                tiempo   = int(campos['tiempo_preparacion'].get().strip() or 0)
            except ValueError:
                messagebox.showerror("Error", "Precio, stock y tiempo deben ser números.",
                                     parent=vent)
                return

            descripcion = campos['descripcion'].get().strip() or None

            if es_edicion and producto is not None:
                ok = self.insertor.actualizar_producto(
                    producto['id_producto'], nombre, precio_f,
                    stock_i, categoria, tiempo, descripcion)
            else:
                ok = self.insertor.insertar_producto(
                    nombre, precio_f, stock_i, categoria, tiempo, descripcion)

            if ok:
                messagebox.showinfo("✅ Éxito",
                                    "Producto actualizado." if es_edicion else "Producto creado.",
                                    parent=vent)
                vent.destroy()
                self.vista_productos()
            else:
                messagebox.showerror("Error", "No se pudo guardar el producto.", parent=vent)

        ctk.CTkButton(vent, text="Guardar", fg_color="green",
                      height=38, command=guardar).pack(pady=12, padx=20, fill="x")

    def _eliminar_producto(self, id_producto: int, nombre: str):
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar el producto '{nombre}'? Esta acción no se puede deshacer."):
            return
        ok, mensaje = self.insertor.eliminar_producto(id_producto)
        if ok:
            messagebox.showinfo("Eliminado", mensaje)
            self.vista_productos()
        else:
            messagebox.showerror("Error", mensaje)
    
    def abrir_receta(self, producto: dict):
        id_producto = producto['id_producto']
        nombre_prod = producto['nombre']

        vent = ctk.CTkToplevel(self)
        vent.title(f"Receta — {nombre_prod}")
        vent.geometry("520x500")
        vent.attributes('-topmost', True)
        vent.focus()
        vent.grab_set()

        ctk.CTkLabel(vent, text=f"📋 Receta de {nombre_prod}",
                     font=("Arial", 16, "bold")).pack(pady=(14, 4))

        # Frame de ingredientes actuales
        ctk.CTkLabel(vent, text="Ingredientes en la receta:",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20)

        lista_frame = ctk.CTkScrollableFrame(vent, height=180)
        lista_frame.pack(fill="x", padx=20, pady=6)

        def recargar_lista():
            for w in lista_frame.winfo_children():
                w.destroy()
            receta = self.consultor.obtener_receta_producto(id_producto)
            if not receta:
                ctk.CTkLabel(lista_frame, text="Sin ingredientes cargados.",
                             text_color="gray").pack(pady=10)
                return
            for item in receta:
                r = ctk.CTkFrame(lista_frame)
                r.pack(fill="x", pady=2)
                r.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(r, text=f"{item['ingrediente']}",
                             anchor="w").grid(row=0, column=0, padx=8, pady=5, sticky="w")
                ctk.CTkLabel(r, text=f"{item['cantidad_requerida']} {item['unidad_medida']}",
                             text_color="lightblue").grid(row=0, column=1, padx=8)

                # Editar cantidad
                entry_cant = ctk.CTkEntry(r, width=70)
                entry_cant.insert(0, str(item['cantidad_requerida']))
                entry_cant.grid(row=0, column=2, padx=4)

                def guardar_cantidad(id_rec=item['id_receta'], entry=entry_cant):
                    try:
                        nueva = float(entry.get().strip())
                    except ValueError:
                        messagebox.showerror("Error", "Ingresá un número válido.", parent=vent)
                        return
                    ok, msg = self.insertor.actualizar_cantidad_receta(id_rec, nueva)
                    if ok:
                        recargar_lista()
                    else:
                        messagebox.showerror("Error", msg, parent=vent)

                ctk.CTkButton(r, text="✔", width=30, fg_color="#1a6b3c",
                              command=guardar_cantidad).grid(row=0, column=3, padx=2)
                ctk.CTkButton(r, text="🗑️", width=30, fg_color="#BF0000",
                              command=lambda id_rec=item['id_receta']: (
                                  self.insertor.eliminar_ingrediente_receta(id_rec),
                                  recargar_lista()
                              )).grid(row=0, column=4, padx=2)

        recargar_lista()

        # Formulario para agregar ingrediente
        ctk.CTkLabel(vent, text="Agregar ingrediente:",
                     font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))

        add_frame = ctk.CTkFrame(vent)
        add_frame.pack(fill="x", padx=20, pady=6)
        add_frame.grid_columnconfigure(0, weight=1)

        # Cargar lista de ingredientes disponibles
        ingredientes = self.consultor.obtener_todos_los_ingredientes()
        opciones = {f"{i['nombre']} ({i['unidad_medida']})": i['id_ingredientes']
                    for i in ingredientes}

        ctk.CTkLabel(add_frame, text="Ingrediente:", anchor="w").grid(
            row=0, column=0, padx=8, pady=6, sticky="w")
        combo_ing = ctk.CTkComboBox(add_frame, values=list(opciones.keys()))
        if opciones:
            combo_ing.set(list(opciones.keys())[0])
        combo_ing.grid(row=0, column=1, columnspan=2, padx=8, pady=6, sticky="ew")

        ctk.CTkLabel(add_frame, text="Cantidad:", anchor="w").grid(
            row=1, column=0, padx=8, pady=6, sticky="w")
        entry_nueva_cant = ctk.CTkEntry(add_frame, placeholder_text="Ej: 0.250")
        entry_nueva_cant.grid(row=1, column=1, padx=8, pady=6, sticky="ew")

        def agregar():
            seleccion = combo_ing.get()
            if seleccion not in opciones:
                messagebox.showwarning("Sin ingrediente", "Seleccioná un ingrediente.", parent=vent)
                return
            try:
                cantidad = float(entry_nueva_cant.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Ingresá una cantidad válida.", parent=vent)
                return
            id_ing = opciones[seleccion]
            ok, msg = self.insertor.agregar_ingrediente_receta(id_producto, id_ing, cantidad)
            if ok:
                entry_nueva_cant.delete(0, "end")
                recargar_lista()
            else:
                messagebox.showerror("Error", msg, parent=vent)

        ctk.CTkButton(add_frame, text="➕ Agregar", fg_color="green",
                      command=agregar).grid(row=1, column=2, padx=8, pady=6)

if __name__ == "__main__":
    App().mainloop()