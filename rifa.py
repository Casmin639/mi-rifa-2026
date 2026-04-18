import tkinter as tk
from tkinter import ttk
import json
import os

ARCHIVO = 'datos_rifa.json'
VALOR_NUMERO = 20000

# Colores solicitados
COLOR_FONDO = "#FDF5E6"      # Crema
COLOR_PAGADO = "#87CEEB"     # Azul Claro
COLOR_MORA = "#FF6B6B"       # Rojo
COLOR_DISPONIBLE = "#FFFFFF" # Blanco
COLOR_TEXTO = "#4A4A4A"
COLOR_CAFE = "#8B7355"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, 'r') as f:
                return json.load(f)
        except:
            pass
    return {f"{i:02d}": {"nombre": "", "tel": "", "estado": "Disponible"} for i in range(100)}

datos = cargar_datos()

def guardar_datos():
    with open(ARCHIVO, 'w') as f:
        json.dump(datos, f, indent=4)
    actualizar_resumen()

def actualizar_resumen():
    pagados = sum(1 for d in datos.values() if d.get("estado") == "Pagado")
    en_mora = sum(1 for d in datos.values() if d.get("estado") == "En Mora")
    lbl_resumen.config(text=f"Pagados: {pagados} (${pagados*VALOR_NUMERO:,}) | En Mora: {en_mora} (${en_mora*VALOR_NUMERO:,})")

def abrir_formulario(num, boton):
    ventana = tk.Toplevel(root)
    ventana.title(f"Número {num}")
    ventana.geometry("350x350")
    ventana.configure(bg=COLOR_FONDO)
    ventana.grab_set() # Hace que no puedas tocar la ventana de atrás hasta cerrar esta

    # Contenedor principal interno
    main_frame = tk.Frame(ventana, bg=COLOR_FONDO)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text=f"DETALLES NÚMERO {num}", font=("Arial", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_CAFE).pack(pady=10)
    
    tk.Label(main_frame, text="Nombre del Cliente:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w")
    entry_n = tk.Entry(main_frame, font=("Arial", 11))
    entry_n.insert(0, datos[num].get("nombre", ""))
    entry_n.pack(pady=5, fill="x")

    tk.Label(main_frame, text="Teléfono:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w")
    entry_t = tk.Entry(main_frame, font=("Arial", 11))
    entry_t.insert(0, datos[num].get("tel", ""))
    entry_t.pack(pady=5, fill="x")

    tk.Label(main_frame, text="Estado:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w")
    estado_var = tk.StringVar(value=datos[num].get("estado", "Disponible"))
    combo = ttk.Combobox(main_frame, textvariable=estado_var, values=["Disponible", "Pagado", "En Mora"], state="readonly")
    combo.pack(pady=5, fill="x")

    def confirmar():
        datos[num] = {"nombre": entry_n.get(), "tel": entry_t.get(), "estado": estado_var.get()}
        guardar_datos()
        
        if estado_var.get() == "Pagado":
            boton.config(bg=COLOR_PAGADO, fg="white")
        elif estado_var.get() == "En Mora":
            boton.config(bg=COLOR_MORA, fg="white")
        else:
            boton.config(bg=COLOR_DISPONIBLE, fg=COLOR_TEXTO)
            
        ventana.destroy()

    tk.Button(main_frame, text="GUARDAR", command=confirmar, bg=COLOR_CAFE, fg="white", 
              font=("Arial", 10, "bold"), relief="flat", height=2).pack(pady=20, fill="x")

# Ventana Principal
root = tk.Tk()
root.title("Gestor de Rifa Pro")
root.geometry("750x850")
root.configure(bg=COLOR_FONDO)

header = tk.Frame(root, bg=COLOR_FONDO)
header.pack(pady=20)
tk.Label(header, text="TABLERO DE CONTROL", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_CAFE).pack()
lbl_resumen = tk.Label(header, text="", font=("Arial", 11), bg=COLOR_FONDO, fg="#555")
lbl_resumen.pack()

grid_frame = tk.Frame(root, bg=COLOR_FONDO)
grid_frame.pack(pady=10)

for i in range(100):
    n = f"{i:02d}"
    est = datos[n].get("estado", "Disponible")
    bg_c = COLOR_PAGADO if est == "Pagado" else COLOR_MORA if est == "En Mora" else COLOR_DISPONIBLE
    fg_c = "white" if est in ["Pagado", "En Mora"] else COLOR_TEXTO
    
    btn = tk.Button(grid_frame, text=n, width=5, height=2, font=("Arial", 9, "bold"),
                   bg=bg_c, fg=fg_c, relief="flat")
    btn.config(command=lambda num=n, b=btn: abrir_formulario(num, b))
    btn.grid(row=i//10, column=i%10, padx=2, pady=2)

actualizar_resumen()
root.mainloop()