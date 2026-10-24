import streamlit as st
import datetime

# =========================================================================
# 1. CLASES Y ESTRUCTURAS DE DATOS (LÓGICA PURA - ESTILO USMP)
# =========================================================================

class NodoMedicamento:
    def __init__(self, nombre, stock, fecha_vencimiento):
        self.nombre = nombre
        self.stock = stock
        self.fecha_vencimiento = datetime.datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date()
        self.sig = None  
        self.ant = None  

class ListaDobleMedicamentos:
    def __init__(self):
        self.cabecera = None  
        self.cola = None      

    def insertar_medicamento(self, nombre, stock, fecha_vencimiento):
        nuevo = NodoMedicamento(nombre, stock, fecha_vencimiento)
        if self.cabecera is None:  
            self.cabecera = nuevo
            self.cola = nuevo
        else:                      
            nuevo.ant = self.cola
            self.cola.sig = nuevo
            self.cola = nuevo
        self.ordenar_por_vencimiento_burbuja()

    def ordenar_por_vencimiento_burbuja(self):
        if self.cabecera is None:
            return
        p = self.cabecera
        while p.sig is not None:
            q = self.cabecera
            while q.sig is not None:
                if q.fecha_vencimiento > q.sig.fecha_vencimiento:
                    q.nombre, q.sig.nombre = q.sig.nombre, q.nombre
                    q.stock, q.sig.stock = q.sig.stock, q.stock
                    q.fecha_vencimiento, q.sig.fecha_vencimiento = q.sig.fecha_vencimiento, q.fecha_vencimiento
                q = q.sig
            p = p.sig

    def eliminar_por_nombre(self, nombre):
        p = self.cabecera
        while p is not None:
            if p.nombre == nombre:
                if p.ant is not None:
                    p.ant.sig = p.sig
                else:
                    self.cabecera = p.sig
                if p.sig is not None:
                    p.sig.ant = p.ant
                else:
                    self.cola = p.ant
                return True
            p = p.sig
        return False

    def exportar_a_lista_python(self):
        elementos = []
        p = self.cabecera
        while p:
            elementos.append({
                "Nombre": p.nombre,
                "Stock": p.stock,
                "Vencimiento": p.fecha_vencimiento.strftime("%Y-%m-%d")
            })
            p = p.sig
        return elementos

class NodoPaciente:
    def __init__(self, dni, nombre, prioridad):
        self.dni = int(dni)
        self.nombre = nombre
        self.prioridad = prioridad  
        self.sig = None

class ColaTurnosPrioridad:
    def __init__(self):
        self.frente = None

    def encolar_paciente(self, dni, nombre, prioridad):
        nuevo = NodoPaciente(dni, nombre, prioridad)
        if self.frente is None or prioridad < self.frente.prioridad:
            nuevo.sig = self.frente
            self.frente = nuevo
        else:
            p = self.frente
            while p.sig is not None and p.sig.prioridad <= prioridad:
                p = p.sig
            nuevo.sig = p.sig
            p.sig = nuevo

    def desencolar_paciente(self):
        if self.frente is None:
            return None
        paciente_atendido = self.frente
        self.frente = self.frente.sig
        return paciente_atendido

    def exportar_a_lista_python(self):
        elementos = []
        p = self.frente
        while p:
            desc_prioridad = "1 - Alta (Urgencia)" if p.prioridad == 1 else ("2 - Media (Control)" if p.prioridad == 2 else "3 - Baja (General)")
            elementos.append({
                "DNI": p.dni,
                "Paciente": p.nombre,
                "Prioridad": desc_prioridad
            })
            p = p.sig
        return elementos

class PilaDeshacer:
    def __init__(self):
        self.items = []

    def push_accion(self, tipo_accion, datos_accion):
        self.items.append((tipo_accion, datos_accion))

    def pop_accion(self):
        if len(self.items) == 0:
            return None
        return self.items.pop()

def busqueda_binaria_pacientes(lista_ordenada_dni, dni_objetivo):
    left = 0
    right = len(lista_ordenada_dni) - 1
    while left <= right:
        mid = (left + right) // 2
        if lista_ordenada_dni[mid]['DNI'] == int(dni_objetivo):
            return mid  
        elif lista_ordenada_dni[mid]['DNI'] < int(dni_objetivo):
            left = mid + 1  
        else:
            right = mid - 1  
    return -1  

# =========================================================================
# 2. INTERFAZ GRÁFICA WEB (STREAMLIT)
# =========================================================================

st.set_page_config(page_title="MediPosta ODS 3 - USMP", layout="wide", page_icon="🏥")

st.title("🏥 Sistema MediPosta - Gestión de Turnos y Stock (ODS 3)")
st.markdown("---")

if "medicamentos" not in st.session_state:
    st.session_state.medicamentos = ListaDobleMedicamentos()
    st.session_state.medicamentos.insertar_medicamento("Paracetamol 500mg", 500, "2026-12-15")
    st.session_state.medicamentos.insertar_medicamento("Amoxicilina 250mg", 150, "2026-08-20")
    st.session_state.medicamentos.insertar_medicamento("Ibuprofeno 400mg", 300, "2027-02-10")

if "cola_turnos" not in st.session_state:
    st.session_state.cola_turnos = ColaTurnosPrioridad()

if "pila_auditoria" not in st.session_state:
    st.session_state.pila_auditoria = PilaDeshacer()

col_turnos, col_farmacia = st.columns(2)

with col_turnos:
    st.header("🎟️ Módulo 1: Admisión y Turnos")
    
    with st.form("form_paciente"):
        input_dni = st.text_input("Número de DNI:", max_chars=8)
        input_nombre = st.text_input("Nombre Completo del Paciente:")
        input_prioridad = st.selectbox(
            "Clasificación de Vulnerabilidad:",
            options=[1, 2, 3],
            format_func=lambda x: "1 - Prioridad Alta (Gestante / Niño / Anciano)" if x == 1 else ("2 - Prioridad Media (Enfermo Crónico)" if x == 2 else "3 - Prioridad Baja (Control de Rutina)")
        )
        boton_encolar = st.form_submit_button("Registrar e Insertar en Cola")
        
        if boton_encolar:
            if input_dni.isdigit() and len(input_dni) == 8 and input_nombre:
                st.session_state.cola_turnos.encolar_paciente(input_dni, input_nombre, input_prioridad)
                st.success(f"Paciente {input_nombre} encolado exitosamente.")
                st.rerun()
            else:
                st.error("Ingrese un DNI válido de 8 dígitos y un nombre.")

    st.subheader("Filas de Atención Médica Actual:")
    pacientes_en_cola = st.session_state.cola_turnos.exportar_a_lista_python()
    if pacientes_en_cola:
        st.dataframe(pacientes_en_cola, width="stretch")
        if st.button("Atender Siguiente Paciente (Desencolar)"):
            atendido = st.session_state.cola_turnos.desencolar_paciente()
            st.toast(f"Atendiendo a: {atendido.nombre}")
            st.rerun()
    else:
        st.info("No hay pacientes esperando.")

    st.markdown("---")
    st.subheader("🔍 Búsqueda Rápida (Búsqueda Binaria)")
    dni_buscar = st.text_input("DNI a buscar en los turnos activos:")
    if st.button("Buscar Paciente"):
        lista_ordenada_busqueda = sorted(st.session_state.cola_turnos.exportar_a_lista_python(), key=lambda x: x['DNI'])
        if dni_buscar.isdigit():
            indice_encontrado = busqueda_binaria_pacientes(lista_ordenada_busqueda, dni_buscar)
            if indice_encontrado != -1:
                datos = lista_ordenada_busqueda[indice_encontrado]
                st.success(f"🎉 Paciente Encontrado: {datos['Paciente']} | Fila ordenada pos: {indice_encontrado}.")
            else:
                st.error("El paciente no está en los turnos activos.")
        else:
            st.warning("Ingrese un DNI numérico válido.")

with col_farmacia:
    st.header("💊 Módulo 2: Inventario de Farmacia")
    
    with st.form("form_medicamento"):
        med_nombre = st.text_input("Nombre del Medicamento:")
        med_stock = st.number_input("Cantidad (Stock):", min_value=1, step=1)
        med_vencimiento = st.date_input("Fecha de Vencimiento:")
        boton_guardar_med = st.form_submit_button("Registrar Lote")
        
        if boton_guardar_med:
            if med_nombre:
                f_venc_str = med_vencimiento.strftime("%Y-%m-%d")
                st.session_state.pila_auditoria.push_accion("INSERTAR", {"nombre": med_nombre})
                st.session_state.medicamentos.insertar_medicamento(med_nombre, med_stock, f_venc_str)
                st.success(f"Lote de {med_nombre} añadido.")
                st.rerun()

    if st.button("🔄 Deshacer Último Registro (Pila - LIFO)"):
        ultima_accion = st.session_state.pila_auditoria.pop_accion()
        if ultima_accion:
            tipo, datos = ultima_accion
            if tipo == "INSERTAR":
                st.session_state.medicamentos.eliminar_por_nombre(datos["nombre"])
                st.warning(f"Acción revertida: Se eliminó el lote de '{datos['nombre']}'.")
                st.rerun()
        else:
            st.error("No hay acciones en la Pila para deshacer.")

    st.subheader("Inventario Automatizado (Orden FEFO - Burbuja):")
    inventario_lista = st.session_state.medicamentos.exportar_a_lista_python()
    if inventario_lista:
        st.table(inventario_lista)
    else:
        st.info("Almacén vacío.")
