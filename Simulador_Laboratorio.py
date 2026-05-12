import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import random
import requests 
from datetime import datetime

# <--- URL DE POWER BI --->
POWER_BI_URL = "https://api.powerbi.com/beta/cbc2c381-2f2e-4d93-91d1-506c9316ace7/datasets/44afbca6-0e3e-4780-bd6e-b44995072977/rows?experience=power-bi&key=xYjQxS9CuNb%2FWodUgHS%2FEPhJhnDMyTP4WyWxNxus%2BPOVupsLqeJggUR5wJ%2FVsBwE1vRrUZUHncNYJ%2BIOQ13YXw%3D%3D"

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA
# ==========================================
st.set_page_config(page_title="Laboratorio de Biodiésel", page_icon="🔬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; color: #2C3E50; font-family: 'Arial', sans-serif;}
    .lab-box { background-color: #FFFFFF; padding: 20px; border-radius: 8px; border-left: 5px solid #2980B9; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .display-lcd { background-color: #D5F5E3; color: #0E6251; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; padding: 10px; border-radius: 5px; text-align: right; border: 2px inset #1ABC9C;}
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 3px solid #2980B9; }
</style>
""", unsafe_allow_html=True)

# Diccionario Bilingüe
T = {
    'title': {'es': '🏭 Laboratorio Interactivo: Producción de Biodiésel', 'en': '🏭 Interactive Lab: Biodiesel Production'},
    'tab1': {'es': '1. Calculadora Estequiométrica', 'en': '1. Stoichiometric Calculator'},
    'tab2': {'es': '2. Reactor R-201 (Live)', 'en': '2. Reactor R-201 (Live)'},
    'tab3': {'es': '3. Decantador D-301', 'en': '3. Decanter D-301'},
    'tab4': {'es': '4. Certificación NTC 5444', 'en': '4. NTC 5444 Certification'}
}

if 'lang' not in st.session_state: st.session_state.lang = "es"
def t(key): return T.get(key, {}).get(st.session_state.lang, key)

# ==========================================
# 2. BASE DE DATOS DE MATRICES (AMPLIADA CON CONTEXTO)
# ==========================================
MUESTRAS = {
    "OP-001 (AVU)": {
        "vol": 1200.0, "acidez_real": 1.5, "humedad": 4.5, 
        "tipo": "Aceite Vegetal Usado (AVU)", 
        "desc": "Recolectado de restaurantes. Presenta alta humedad por procesos de fritura profunda."
    },
    "OP-002 (Grasa Pollo)": {
        "vol": 800.0, "acidez_real": 6.8, "humedad": 0.2, 
        "tipo": "Grasa Animal Degradada", 
        "desc": "Baja humedad, pero se sospecha de una acidez extremadamente alta por descomposición orgánica."
    },
    "OP-003 (Aceite Palma)": {
        "vol": 1500.0, "acidez_real": 2.8, "humedad": 1.8, 
        "tipo": "Aceite Crudo de Palma", 
        "desc": "Alta densidad y volumen. Humedad moderada. Requiere atención en la inercia térmica del reactor."
    }
}

# ==========================================
# 3. MEMORIA RAM (st.session_state)
# ==========================================
if 'ficha_grupo' not in st.session_state: st.session_state.ficha_grupo = ""
if 'op_actual' not in st.session_state: st.session_state.op_actual = "OP-001 (AVU)"
if 'resultados_turno' not in st.session_state: st.session_state.resultados_turno = []
if 'intentos_actuales' not in st.session_state: st.session_state.intentos_actuales = 1
if 'total_muestras_gastadas' not in st.session_state: st.session_state.total_muestras_gastadas = 1

# Fase 1: Analítica
if 'volumen_titulante' not in st.session_state: st.session_state.volumen_titulante = 0.0
if 'peso_balanza' not in st.session_state: st.session_state.peso_balanza = 0.0
if 'met_ingresado' not in st.session_state: st.session_state.met_ingresado = 0.0
if 'humedad_actual' not in st.session_state: st.session_state.humedad_actual = 4.5
if 'fenolftaleina_agregada' not in st.session_state: st.session_state.fenolftaleina_agregada = False

# Fase 2: Reactor
if 'tiempo_rx' not in st.session_state: st.session_state.tiempo_rx = 0
if 'temp_rx' not in st.session_state: st.session_state.temp_rx = 25.0
if 'fase_rx_completada' not in st.session_state: st.session_state.fase_rx_completada = False
if 'hubo_evaporacion' not in st.session_state: st.session_state.hubo_evaporacion = False
if 'degradacion_termica' not in st.session_state: st.session_state.degradacion_termica = False
if 'valvula_metoxido' not in st.session_state: st.session_state.valvula_metoxido = 0

# Fase 3: Decantación
if 'progreso_dec' not in st.session_state: st.session_state.progreso_dec = 0.0
if 'ph_metro' not in st.session_state: st.session_state.ph_metro = 10.5
if 'fase_dec_completada' not in st.session_state: st.session_state.fase_dec_completada = False
if 'hubo_saponificacion' not in st.session_state: st.session_state.hubo_saponificacion = False
if 'rendimiento_final' not in st.session_state: st.session_state.rendimiento_final = 100.0

def reset_ensayo_laboratorio():
    st.session_state.humedad_actual = MUESTRAS[st.session_state.op_actual]["humedad"]
    st.session_state.volumen_titulante = 0.0
    st.session_state.peso_balanza = 0.0
    st.session_state.met_ingresado = 0.0
    st.session_state.fenolftaleina_agregada = False
    st.session_state.tiempo_rx = 0
    st.session_state.temp_rx = 25.0
    st.session_state.valvula_metoxido = 0
    st.session_state.progreso_dec = 0.0
    st.session_state.ph_metro = 10.5
    st.session_state.fase_rx_completada = False
    st.session_state.fase_dec_completada = False
    st.session_state.hubo_saponificacion = False
    st.session_state.hubo_evaporacion = False
    st.session_state.degradacion_termica = False
    st.session_state.rendimiento_final = 100.0

def cambiar_op(nueva_op):
    st.session_state.op_actual = nueva_op
    st.session_state.intentos_actuales = 1 
    reset_ensayo_laboratorio()

# ==========================================
# 4. MOTORES GRÁFICOS HTML/SVG BLINDADOS
# ==========================================
def html_titulacion(volumen, volumen_meta, indicador_activo):
    margen = 0.3
    color_liq = "#EBF5FB" 
    msg = "Titulando..."
    color_msg = "#2C3E50"
    
    if indicador_activo:
        if volumen > (volumen_meta + margen): 
            color_liq = "#E74C3C" 
            msg = "SOBRETITULADO"
            color_msg = "#C0392B"
        elif volumen >= (volumen_meta - margen): 
            color_liq = "#FADBD8" 
            msg = "VIRAJE ALCANZADO"
            color_msg = "#8E44AD"
    else:
        msg = "Falta Indicador (Fenolftaleína)"
        color_msg = "#7F8C8D"
        
    nivel_bureta = min(100, (volumen / 50.0) * 100)

    return f"""<!DOCTYPE html><html><head><style>body {{ margin: 0; display: flex; justify-content: center; background: white; }}</style></head><body>
    <svg viewBox="0 0 250 400" width="100%" height="350">
        <rect x="110" y="10" width="20" height="150" fill="none" stroke="#7F8C8D" stroke-width="2"/>
        <rect x="112" y="{10 + nivel_bureta}" width="16" height="{150 - nivel_bureta}" fill="#3498DB" opacity="0.6"/>
        <line x1="105" y1="160" x2="135" y2="160" stroke="#333" stroke-width="4"/>
        <line x1="120" y1="160" x2="120" y2="180" stroke="#7F8C8D" stroke-width="2"/>
        <path d="M 110,190 L 130,190 L 130,230 L 180,320 L 60,320 L 110,230 Z" fill="none" stroke="#34495E" stroke-width="4"/>
        <path d="M 105,240 L 170,315 L 70,315 Z" fill="{color_liq}" opacity="0.9"/>
        <text x="120" y="350" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="14" fill="{color_msg}">{msg}</text>
    </svg></body></html>"""

def html_balanza(peso):
    radio_polvo = min(50, peso * 1.5) if peso > 0 else 0
    return f"""<!DOCTYPE html><html><head><style>body {{ margin: 0; display: flex; justify-content: center; background: white; }}</style></head><body>
    <svg viewBox="0 0 300 200" width="100%" height="200">
        <rect x="40" y="120" width="220" height="60" fill="#ECF0F1" stroke="#BDC3C7" stroke-width="4" rx="10"/>
        <ellipse cx="150" cy="120" rx="80" ry="15" fill="#BDC3C7" stroke="#7F8C8D" stroke-width="2"/>
        <path d="M 100,115 Q 150,135 200,115" fill="none" stroke="#95A5A6" stroke-width="2"/>
        <path d="M {150 - radio_polvo},{115} Q 150,{115 - radio_polvo} {150 + radio_polvo},{115}" fill="#FDFEFE" stroke="#D0D3D4"/>
    </svg></body></html>"""

def html_probeta(volumen):
    nivel = min(150, (volumen / 500.0) * 150)
    return f"""<!DOCTYPE html><html><head><style>body {{ margin: 0; display: flex; justify-content: center; background: white; }}</style></head><body>
    <svg viewBox="0 0 100 200" width="100%" height="200">
        <rect x="30" y="20" width="40" height="160" fill="none" stroke="#BDC3C7" stroke-width="3" rx="5"/>
        <rect x="32" y="{180 - nivel}" width="36" height="{nivel}" fill="#9B59B6" opacity="0.8" rx="2"/>
        <line x1="30" y1="60" x2="40" y2="60" stroke="#7F8C8D" stroke-width="2"/>
        <line x1="30" y1="100" x2="40" y2="100" stroke="#7F8C8D" stroke-width="2"/>
        <line x1="30" y1="140" x2="40" y2="140" stroke="#7F8C8D" stroke-width="2"/>
    </svg></body></html>"""

def html_reactor(temp, rpm, dosificacion):
    color_temp = "#27AE60" if (50 <= temp <= 60) else ("#3498DB" if temp < 50 else "#E74C3C")
    color_liquido = "#F1C40F" if temp < 50 else ("#D35400" if temp < 65 else "#78281F")
    humo = '<g style="animation: humo 1s infinite;"><circle cx="150" cy="80" r="20" fill="#BDC3C7" opacity="0.7"/><circle cx="130" cy="60" r="15" fill="#BDC3C7" opacity="0.5"/></g>' if temp >= 65 else ""
    giro = f"spin {max(0.1, 1.5 - (rpm/500))}s linear infinite" if rpm > 0 else "none"
    flujo = f'<rect x="90" y="20" width="8" height="80" fill="#9B59B6" opacity="{dosificacion/100.0}"/>' if dosificacion > 0 else ""

    return f"""<!DOCTYPE html><html><head><style>
        body {{ margin: 0; display: flex; justify-content: center; background: white; font-family: 'Courier New', monospace; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        @keyframes humo {{ 0% {{ transform: translateY(0) scale(1); opacity:0.8;}} 100% {{ transform: translateY(-40px) scale(1.5); opacity:0;}} }}
    </style></head><body>
    <svg viewBox="0 0 300 320" width="100%" height="400">
        {humo}
        <path d="M 50,20 L 90,20 L 90,60" fill="none" stroke="#2C3E50" stroke-width="6"/>
        {flujo}
        <text x="10" y="15" font-size="12" font-family="Arial" font-weight="bold" fill="#2C3E50">Metóxido</text>
        <rect x="135" y="20" width="30" height="40" fill="#2980B9" stroke="#2C3E50" stroke-width="2"/>
        <rect x="90" y="60" width="120" height="10" fill="#7F8C8D" stroke="#2C3E50"/>
        <path d="M 100,70 L 200,70 L 200,240 A 50 40 0 0 1 100,240 Z" fill="#ECF0F1" stroke="#2C3E50" stroke-width="4"/>
        <path d="M 102,120 L 198,120 L 198,240 A 48 38 0 0 1 102,240 Z" fill="{color_liquido}"/>
        <rect x="146" y="70" width="8" height="150" fill="#95A5A6"/>
        <g style="transform-box: fill-box; transform-origin: center; animation: {giro};">
            <ellipse cx="150" cy="220" rx="35" ry="8" fill="#34495E"/>
        </g>
        <rect x="10" y="260" width="280" height="50" fill="#F4F6F9" rx="5" stroke="#BDC3C7" stroke-width="2"/>
        <text x="20" y="280" font-size="16" font-weight="bold" fill="{color_temp}">TT-201: {temp:.1f} °C</text>
        <text x="20" y="300" font-size="16" font-weight="bold" fill="#2980B9">ST-201: {rpm} RPM</text>
    </svg></body></html>"""

def html_decantador(progreso, ph, jabon):
    h_tot = 120
    h_bio = (h_tot * 0.8 * progreso) if not jabon else (h_tot * 0.3 * progreso)
    h_jab = 0 if not jabon else (h_tot * 0.5 * progreso)
    h_gli = h_tot * 0.2 * progreso
    
    color_bio = "#F1C40F" if ph <= 7.5 else "#D4AC0D"
    lbl_jab = f'<text x="175" y="{50 + h_bio + (h_jab/2)}" text-anchor="middle" fill="#C0392B" font-weight="bold" font-family="Arial" font-size="14">EMULSIÓN JABONOSA</text>' if progreso > 0.5 and jabon else ""

    return f"""<!DOCTYPE html><html><head><style>body {{ margin: 0; display: flex; justify-content: center; background: white; }}</style></head><body>
    <svg viewBox="0 0 350 400" width="100%" height="450">
        <rect x="50" y="20" width="10" height="300" fill="#7F8C8D"/>
        <defs><clipPath id="fun"><path d="M 100,50 L 250,50 L 210,200 L 210,280 L 140,280 L 140,200 Z" /></clipPath></defs>
        <g clip-path="url(#fun)">
            <rect x="0" y="50" width="350" height="{h_tot}" fill="#B9770E"/>
            <rect x="0" y="50" width="350" height="{h_bio}" fill="{color_bio}"/>
            <rect x="0" y="{50+h_bio}" width="350" height="{h_jab}" fill="#ECF0F1" opacity="0.9"/>
            <rect x="0" y="{190-h_gli}" width="350" height="{h_gli}" fill="#5D4037"/>
        </g>
        <path d="M 100,50 L 250,50 L 210,200 L 210,280 L 140,280 L 140,200 Z" fill="none" stroke="#2C3E50" stroke-width="4"/>
        <rect x="150" y="240" width="50" height="10" fill="#E74C3C"/>
        {lbl_jab}
        <rect x="230" y="10" width="8" height="100" fill="#34495E"/>
        <circle cx="234" cy="115" r="8" fill="#3498DB"/>
        <rect x="200" y="20" width="130" height="50" fill="#F4F6F9" stroke="#34495E" stroke-width="2" rx="5"/>
        <text x="210" y="35" font-family="Arial" font-size="12" font-weight="bold">Medidor AE-301</text>
        <text x="265" y="60" text-anchor="middle" font-family="Courier New" font-weight="bold" font-size="24" fill="#E74C3C">pH {ph:.1f}</text>
    </svg></body></html>"""

# ==========================================
# 5. SIDEBAR: CONTROL DE CUADRILLA
# ==========================================
st.sidebar.markdown("### 📋 Recepción de Turno")
if not st.session_state.ficha_grupo:
    nom = st.sidebar.text_input("Ingrese Ficha / Cuadrilla:")
    if st.sidebar.button("Ingresar", type="primary"):
        st.session_state.ficha_grupo = nom
        st.rerun()
    st.stop()

st.sidebar.success(f"**Operando:** {st.session_state.ficha_grupo}")

op_sel = st.sidebar.selectbox("📋 Matriz a Procesar", list(MUESTRAS.keys()), index=list(MUESTRAS.keys()).index(st.session_state.op_actual))
if op_sel != st.session_state.op_actual:
    cambiar_op(op_sel)
    st.rerun()

datos_op = MUESTRAS[st.session_state.op_actual]
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Volumen Asignado:** {datos_op['vol']} mL")
st.sidebar.info(f"**Muestras Gastadas (Actual):** {st.session_state.intentos_actuales}")
st.sidebar.warning(f"**Total Muestras Turno:** {st.session_state.total_muestras_gastadas}")

# ==========================================
# 6. INTERFAZ PRINCIPAL
# ==========================================
st.markdown(f"<h2 style='color:#2C3E50; border-bottom: 3px solid #2980B9;'>🔬 Operaciones Unitarias: {st.session_state.op_actual}</h2>", unsafe_allow_html=True)

# --- NUEVA FICHA TÉCNICA (CONTEXTO DE LA MUESTRA) ---
st.info(f"📋 **FICHA TÉCNICA DE LA MUESTRA**\n"
        f"- **Tipo de Matriz:** {datos_op['tipo']}\n"
        f"- **Descripción:** {datos_op['desc']}\n"
        f"- **Volumen a Procesar:** {datos_op['vol']} mL\n"
        f"- **Humedad Inicial (Sensor MI-101):** {datos_op['humedad']}% *(Tratar en Pestaña 1 si >0.5%)*\n"
        f"- **Índice de Acidez (FFA):** ❓ *Desconocido. Requiere titulación química (Pestaña 1).*")

tab1, tab2, tab3, tab4 = st.tabs(["1. Lab Analítico (Química)", "2. Reactor R-201 (SCADA)", "3. Decantador y Lavado", "4. Certificación NTC"])

# ---------------------------------------------------------
# PESTAÑA 1: LABORATORIO ANALÍTICO (Titulación y Pesaje)
# ---------------------------------------------------------
with tab1:
    st.info("💡 **Guía de Laboratorio:** Antes de reaccionar el aceite, debe determinar su acidez libre (FFA) para calcular el catalizador, y asegurarse de que el aceite esté libre de humedad para evitar saponificación.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""<div class="lab-box">
        <h4>1. Ensayo de Acidez (Bureta)</h4>
        <p>Añada fenolftaleína y titule 10g de aceite con KOH 0.1 N.</p>
        </div>""", unsafe_allow_html=True)
        
        vol_meta = (datos_op['acidez_real'] * 10) / (0.1 * 56.1)
        
        if st.button("🧪 Añadir gotas de Fenolftaleína", use_container_width=True):
            st.session_state.fenolftaleina_agregada = True
            st.rerun()
            
        c_1, c_2, c_3 = st.columns(3)
        if c_1.button("💧 + 1.0 mL"): st.session_state.volumen_titulante += 1.0; st.rerun()
        if c_2.button("💧 + 0.1 mL"): st.session_state.volumen_titulante += 0.1; st.rerun()
        if c_3.button("🔄 Vaciar Bureta"): st.session_state.volumen_titulante = 0.0; st.rerun()
        
        components.html(html_titulacion(st.session_state.volumen_titulante, vol_meta, st.session_state.fenolftaleina_agregada), height=380)
        
        if st.session_state.volumen_titulante > 0:
            st.markdown("**Ecuación de Índice de Acidez:**")
            st.latex(r"IA = \frac{Vol_{gastado} \times 0.1 \times 56.1}{10}")

    with col_b:
        st.markdown("""<div class="lab-box">
        <h4>2. Acondicionamiento y Estequiometría</h4>
        <p>Secar el aceite y calcular masa de reactivos.</p>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("**A. Acondicionamiento Físico**")
        st.metric("Humedad del Aceite (Sensor MI-101)", f"{st.session_state.humedad_actual:.2f}%")
        if st.button("🔥 Activar Secado Inicial por Vacío", use_container_width=True):
            if st.session_state.humedad_actual > 0.1:
                st.session_state.humedad_actual = 0.05
                st.success("✅ Secado exitoso. Riesgo de saponificación mitigado.")
                st.rerun()
                
        st.markdown("---")
        st.markdown("**B. Cálculos Estequiométricos**")
        st.latex(r"Masa_{Aceite} = V_{aceite} \times 0.9")
        st.latex(r"NaOH\ (g) = (Masa_{Aceite} \times 0.01) + (IA \times Masa_{Aceite} \times 0.001)")
        st.latex(r"Metanol\ (mL) = V_{aceite} \times 0.20")
        
        c_bal, c_prob = st.columns(2)
        with c_bal:
            peso_input = st.number_input("Peso NaOH (g):", min_value=0.0, step=0.1, value=st.session_state.peso_balanza)
            st.session_state.peso_balanza = peso_input
            st.markdown(f"<div class='display-lcd'>{st.session_state.peso_balanza:.1f} g</div>", unsafe_allow_html=True)
            components.html(html_balanza(st.session_state.peso_balanza), height=230)
            
        with c_prob:
            met_input = st.number_input("Volumen Metanol (mL):", min_value=0.0, step=10.0, value=st.session_state.met_ingresado)
            st.session_state.met_ingresado = met_input
            st.markdown(f"<div class='display-lcd'>{st.session_state.met_ingresado:.0f} mL</div>", unsafe_allow_html=True)
            components.html(html_probeta(st.session_state.met_ingresado), height=230)

# ---------------------------------------------------------
# PESTAÑA 2: REACTOR SCADA
# ---------------------------------------------------------
with tab2:
    st.markdown("#### HMI: Control Termodinámico R-201")
    st.info("💡 **Dinámica de Planta:** El reactor posee inercia térmica. La temperatura subirá gradualmente y tardará en bajar si apaga la resistencia. Si calienta la mezcla sin encender el agitador, el aceite se degradará térmicamente.")
    
    if st.session_state.fase_rx_completada:
        st.success("✅ Reacción completada. Proceda a la pestaña 3.")
    else:
        col_ctrl, col_svg = st.columns([1, 1.5])
        with col_ctrl:
            v_met = st.slider("Apertura Válvula Metóxido (%)", 0, 100, 0, step=10)
            rpm_val = st.slider("Velocidad Agitador (RPM)", 0, 500, 0, step=50)
            pwr_res = st.slider("Potencia Resistencia Térmica (%)", 0, 100, 0, step=10)
            
            st.markdown(f"**Tiempo de Reacción:** {st.session_state.tiempo_rx} / 45 Minutos")
            
            if pwr_res > 0 and rpm_val == 0:
                st.error("🚨 ALARMA HSE: Degradación Térmica Localizada por falta de agitación.")
                st.session_state.degradacion_termica = True
            
            if st.button("⏱️ Avanzar 5 Minutos (Control Manual)", type="primary", use_container_width=True):
                st.session_state.valvula_metoxido = v_met
                
                dT = (pwr_res * 0.45) - ((st.session_state.temp_rx - 25.0) * 0.05)
                st.session_state.temp_rx += dT
                st.session_state.temp_rx = max(25.0, st.session_state.temp_rx)
                st.session_state.tiempo_rx += 5
                
                if st.session_state.temp_rx >= 65.0:
                    st.session_state.hubo_evaporacion = True
                
                st.rerun()
                
            if st.button("⏹️ Finalizar Reacción y Transferir", use_container_width=True):
                masa_aceite = datos_op['vol'] * 0.9
                cat_ideal = (masa_aceite * 0.01) + (datos_op['acidez_real'] * masa_aceite * 0.001)
                margen_error = abs(st.session_state.peso_balanza - cat_ideal) / cat_ideal if cat_ideal > 0 else 1.0
                
                if st.session_state.humedad_actual > 0.5 or margen_error > 0.15:
                    st.session_state.hubo_saponificacion = True
                
                rend = 100.0
                if st.session_state.hubo_evaporacion: rend -= 40.0
                if st.session_state.degradacion_termica: rend -= 15.0
                if st.session_state.valvula_metoxido < 50: rend -= 60.0
                if st.session_state.tiempo_rx < 45: rend -= 25.0
                
                st.session_state.rendimiento_final = max(0.0, rend)
                st.session_state.fase_rx_completada = True
                st.rerun()

        with col_svg:
            components.html(html_reactor(st.session_state.temp_rx, rpm_val, v_met), height=420)
            if st.session_state.temp_rx >= 65.0:
                st.error("🔥 ALARMA HSE: Ebullición y fuga de metanol. Enfríe el sistema.")

# ---------------------------------------------------------
# PESTAÑA 3: DECANTADOR Y LAVADO
# ---------------------------------------------------------
with tab3:
    st.markdown("#### Separación de Fases y Lavado Químico (D-301)")
    st.info("💡 **Procedimiento:** Añadir agua neutraliza el pH, pero emulsiona agua en el biodiésel. Debe aplicar un secado final antes de certificar.")
    
    if not st.session_state.fase_rx_completada:
        st.warning("⚠️ Debe sintetizar el biocombustible en el R-201 primero.")
    elif st.session_state.fase_dec_completada:
        st.success("✅ Procesos físicos terminados. Revise el certificado.")
        components.html(html_decantador(1.0, st.session_state.ph_metro, st.session_state.hubo_saponificacion), height=450)
    else:
        col7, col8 = st.columns([1, 1.5])
        with col7:
            st.markdown("**Control Gravitacional**")
            st.metric("Progreso de Separación", f"{int(st.session_state.progreso_dec * 100)} %")
            
            if st.button("⏳ Avanzar Reposo (+15 Min)", type="primary", use_container_width=True):
                st.session_state.progreso_dec += 0.25
                if st.session_state.progreso_dec >= 1.0:
                    st.session_state.progreso_dec = 1.0
                    st.session_state.fase_dec_completada = True
                    if st.session_state.hubo_saponificacion:
                        st.session_state.rendimiento_final -= 50.0
                        st.session_state.rendimiento_final = max(0.0, st.session_state.rendimiento_final)
                st.rerun()
            
            st.markdown("---")
            st.markdown("**Control Químico (Lavado y Secado)**")
            if st.button("🚿 Añadir Agua de Lavado (Bajar pH)", use_container_width=True):
                st.session_state.ph_metro = max(7.0, st.session_state.ph_metro - 0.5)
                st.session_state.humedad_actual = 8.0 
                st.rerun()
                
            if st.session_state.humedad_actual > 0.5 and st.session_state.progreso_dec > 0.0:
                st.warning("⚠️ Alta humedad detectada por retención de agua de lavado.")
                if st.button("🔥 Secado Final por Evaporación (TK-302)", use_container_width=True):
                    st.session_state.humedad_actual = 0.05
                    st.success("✅ Secado final exitoso.")
                    st.rerun()

            if st.session_state.hubo_saponificacion and st.session_state.progreso_dec > 0.4:
                st.error("❌ ALARMA: Emulsión jabonosa intermedia detectada. Reacción comprometida.")

        with col8:
            components.html(html_decantador(st.session_state.progreso_dec, st.session_state.ph_metro, st.session_state.hubo_saponificacion), height=450)

# ---------------------------------------------------------
# PESTAÑA 4: CERTIFICACIÓN NTC
# ---------------------------------------------------------
with tab4:
    st.markdown("#### Certificado de Calidad NTC 5444")
    
    if not st.session_state.fase_dec_completada:
        st.warning("⏳ Finalice el proceso de separación y lavado.")
    else:
        rend = st.session_state.rendimiento_final
        if st.session_state.hubo_saponificacion:
            rend = random.uniform(30.0, 48.0)
        elif not st.session_state.hubo_evaporacion and not st.session_state.degradacion_termica and st.session_state.valvula_metoxido >= 50 and st.session_state.tiempo_rx >= 45:
            rend = random.uniform(97.0, 99.5)
            
        aprobado = (rend >= 96.5) and not st.session_state.hubo_saponificacion and st.session_state.ph_metro <= 7.5 and st.session_state.humedad_actual < 0.5
        
        st.markdown(f"**Cuadrilla:** `{st.session_state.ficha_grupo}` | **Lote:** `{st.session_state.op_actual}` | **Ensayo N°:** `{st.session_state.intentos_actuales}`")
        
        df_ntc = pd.DataFrame({
            "Parámetro Físico-Químico": ["Contenido de Ésteres C14-C24", "Humedad Libre (Secado Final)", "Acidez / pH (Lavado)", "Aspecto Visual"],
            "Límite NTC 5444": ["> 96.5 %", "< 0.5 %", "pH Neutro (7.0 - 7.5)", "Límpido, sin jabón"],
            "Resultado del Lote": [f"{rend:.2f} %", f"{st.session_state.humedad_actual:.2f} %", f"pH {st.session_state.ph_metro:.1f}", "Emulsionado" if st.session_state.hubo_saponificacion else "Límpido"],
            "Veredicto": ["✅ Cumple" if rend >= 96.5 else "❌ Falla", 
                          "✅ Cumple" if st.session_state.humedad_actual < 0.5 else "❌ Falla",
                          "✅ Cumple" if st.session_state.ph_metro <= 7.5 else "❌ Falla",
                          "❌ Falla" if st.session_state.hubo_saponificacion else "✅ Cumple"]
        })
        st.table(df_ntc)
        
        if aprobado:
            st.success("✅ **LOTE APROBADO:** El biocombustible cumple la Norma Técnica Nacional.")
            if st.button("💾 REGISTRAR LOTE", type="primary"):
                # 1. Empaquetar los datos tal cual los tienes
                registro = {
                    "Cuadrilla": st.session_state.ficha_grupo,
                    "Matriz": st.session_state.op_actual,
                    "Intentos_Requeridos": st.session_state.intentos_actuales,
                    "NaOH_Pesado_g": st.session_state.peso_balanza,
                    "Metanol_mL": st.session_state.met_ingresado,
                    "Temp_Maxima_Alcanzada": st.session_state.temp_rx,
                    "Saponificacion": "SI" if st.session_state.hubo_saponificacion else "NO",
                    "pH_Final": st.session_state.ph_metro,
                    "OEE_Rendimiento_%": round(rend, 2)
                }
                
                # 2. Guardar en la tabla local del simulador (trazabilidad)
                st.session_state.resultados_turno.append(registro)
                
                # 3. ENVÍO DIRECTO A POWER BI
                try:
                    # Nota los corchetes [registro] que exige Power BI
                    respuesta = requests.post(POWER_BI_URL, json=[registro]) 
                    if respuesta.status_code == 200:
                        st.success("✅ Lote registrado localmente y transmitido en vivo al Dashboard de Planta (Power BI).")
                    else:
                        st.warning(f"⚠️ Lote registrado localmente. Fallo de conexión con Power BI: Status {respuesta.status_code}")
                except Exception as e:
                    st.warning("⚠️ Lote registrado localmente. No hay conexión a internet para transmitir a Power BI.")
                    
                st.success("Lote registrado. Seleccione la siguiente matriz en el panel lateral.")
        else:
            st.error("❌ **LOTE RECHAZADO:** Causas Raíz detectadas:")
            if st.session_state.hubo_saponificacion: st.write("- 🧼 **Saponificación:** Fallo en la titulación (cálculo de IA), pesaje incorrecto en la balanza o falta de secado inicial.")
            if st.session_state.degradacion_termica: st.write("- 🌡️ **Degradación Térmica:** La resistencia se encendió sin agitación en el R-201.")
            if st.session_state.humedad_actual >= 0.5: st.write("- 💧 **Exceso de Humedad:** El producto no fue secado después del lavado.")
            if st.session_state.ph_metro > 7.5: st.write("- 🧪 **Alta Alcalinidad:** Faltó lavar el producto.")
            
            st.markdown("---")
            st.warning("Debe repetir el ensayo para esta muestra.")
            if st.button("🔄 Descartar Lote Fallido y Repetir Ensayo", type="secondary"):
                st.session_state.intentos_actuales += 1
                st.session_state.total_muestras_gastadas += 1
                reset_ensayo_laboratorio()
                st.rerun()

    if len(st.session_state.resultados_turno) > 0:
        st.markdown("#### 📥 Trazabilidad del Turno")
        df_turno = pd.DataFrame(st.session_state.resultados_turno)
        st.dataframe(df_turno, use_container_width=True)
        csv_str = df_turno.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar Reporte (.CSV)", data=csv_str, file_name=f"Auditoria_{st.session_state.ficha_grupo}.csv", mime="text/csv", type="secondary")
