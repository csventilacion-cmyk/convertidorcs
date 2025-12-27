import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Master Unit Converter",
    page_icon="⚙️",
    layout="wide" # Cambiado a 'wide' para aprovechar mejor el espacio horizontal
)

# --- 2. ESTILOS CSS AVANZADOS ---
st.markdown("""
    <style>
    /* Título Principal */
    .main-header {
        font-size: 2.2rem;
        color: #0f172a;
        font-weight: 800;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
    }
    
    /* Branding */
    .branding-text {
        font-size: 0.9rem;
        color: #3b82f6; /* Azul brillante */
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 5px;
        margin-bottom: 20px;
    }

    /* Caja de Input (Izquierda) */
    .input-container {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #cbd5e1;
    }

    /* Caja de Resultado (Derecha) */
    .result-box {
        background-color: #ecfdf5; /* Fondo verde muy suave */
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 2px solid #10b981; /* Borde verde */
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.1);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .result-value {
        font-size: 3rem; /* Números grandes */
        color: #047857;
        font-weight: 800;
        word-wrap: break-word; /* Evita que números muy largos rompan el diseño */
        line-height: 1.1;
    }
    .result-unit {
        font-size: 1.2rem;
        color: #065f46;
        font-weight: 500;
        margin-top: 10px;
    }

    /* Ajustes generales de Streamlit */
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border-color: #cbd5e1;
    }
    .stNumberInput input {
        font-weight: bold;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATOS DE CONVERSIÓN ---
CONVERSION_FACTORS = {
    "Caudal (Flow)": {
        "base_unit": "m³/seg",
        "units": {
            "m³/seg": 1.0, "CFM": 0.0004719, "m³/hr": 1/3600, "l/seg": 0.001, "l/min": 0.00001667
        }
    },
    "Volumen": {
        "base_unit": "m³",
        "units": {
            "m³": 1.0, "ft³": 0.028317, "in³": 0.00001639, "Litros (l)": 0.001
        }
    },
    "Velocidad": {
        "base_unit": "m/seg",
        "units": {
            "m/seg": 1.0, "fpm": 0.00508, "m/min": 0.0166667, "fps": 0.3048
        }
    },
    "Presión": {
        "base_unit": "Pa",
        "units": {
            "Pa": 1.0, "in H₂O": 248.84, "in Hg": 3386.4, "mm H₂O": 9.80665,
            "mm Hg": 133.32, "psi": 6894.76, "atm": 101325
        }
    },
    "Area": {
        "base_unit": "m²",
        "units": {
            "m²": 1.0, "ft²": 0.092903, "in²": 0.00064516, "mm²": 0.000001
        }
    },
    "Densidad": {
        "base_unit": "kg/m³",
        "units": { "kg/m³": 1.0, "lb/ft³": 16.0185 }
    },
    "Longitud": {
        "base_unit": "m",
        "units": { "m": 1.0, "ft": 0.3048, "in": 0.0254, "mm": 0.001 }
    },
    "Peso": {
        "base_unit": "kg",
        "units": { "kg": 1.0, "lb": 0.45359, "oz": 0.0283495, "gramos": 0.001 }
    },
    "Potencia": {
        "base_unit": "W",
        "units": { "W": 1.0, "kW": 1000.0, "HP": 745.7 }
    },
    "Temperatura": {
        "units": ["°C", "°F"]
    }
}

# --- 4. FUNCIONES LÓGICAS ---

def format_number_smart(value):
    """
    Formatea el número para evitar notación científica y mostrar decimales relevantes.
    Ejemplo: 123456.789 en lugar de 1.23e+05
    """
    if value == 0:
        return "0"
    
    # Si es entero, mostrar sin decimales
    if value.is_integer():
        return f"{int(value):,}"
    
    # Si es decimal, usar hasta 8 decimales y quitar ceros a la derecha
    # La coma ',' añade separador de miles
    formatted = f"{value:,.8f}".rstrip('0').rstrip('.')
    return formatted

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit: return value
    celsius = value if from_unit == "°C" else (value - 32) * 5/9
    return celsius if to_unit == "°C" else (celsius * 9/5) + 32

def convert_general(value, category, from_unit, to_unit):
    try:
        factors = CONVERSION_FACTORS[category]["units"]
        base_value = value * factors[from_unit]
        return base_value / factors[to_unit]
    except:
        return 0.0

# --- 5. INTERFAZ GRÁFICA (UI) ---

# --- BARRA LATERAL (Panel de Control Ágil) ---
with st.sidebar:
    # 1. Logo
    logo_filename = "logo.png"
    try:
        st.image(logo_filename, use_column_width=True)
    except:
        st.markdown("### ⚙️ Master Converter")
    
    st.markdown("---")
    
    # 2. Selector de Categoría ÁGIL (Radio Buttons)
    # Usamos radio buttons porque son un solo clic (más rápidos que selectbox)
    st.subheader("📍 Seleccione Variable")
    category = st.radio(
        "Categoría:",
        options=list(CONVERSION_FACTORS.keys()),
        label_visibility="collapsed" # Ocultamos la etiqueta para que se vea más limpio
    )
    
    st.markdown("---")
    # Mensaje fijo en sidebar
    st.markdown("**Propiedad de CS Sistemas de Aire**")

# --- PANEL PRINCIPAL ---
st.markdown('<div class="main-header">Calculadora de Conversión</div>', unsafe_allow_html=True)

# Mensaje de propiedad dinámico bajo el título
st.markdown(f'<div class="branding-text">🛠️ Configurando: {category} | Propiedad de CS Sistemas de Aire</div>', unsafe_allow_html=True)

# Contenedor principal
with st.container():
    # Usamos columnas con proporción 2:3 para dar espacio al resultado
    col_input, col_result = st.columns([1, 1.5], gap="large")

    # --- COLUMNA IZQUIERDA: INPUTS ---
    with col_input:
        st.markdown("### 📥 Datos de Entrada")
        
        # El input numérico
        input_value = st.number_input(
            "Valor Numérico:", 
            value=1.0, 
            format="%.4f", 
            step=1.0,
            help="Escriba el valor que desea convertir"
        )
        
        # Lógica para obtener unidades
        if category == "Temperatura":
            unit_options = CONVERSION_FACTORS[category]["units"]
        else:
            unit_options = list(CONVERSION_FACTORS[category]["units"].keys())
        
        # Selectores de unidades
        # Usamos st.radio horizontal si son pocas unidades (<=3) para ser más ágil, sino selectbox
        st.write("---")
        st.markdown("**De (Unidad Origen):**")
        from_unit = st.selectbox("Seleccione origen", unit_options, label_visibility="collapsed", key="u_from")
        
        st.markdown("**A (Unidad Destino):**")
        to_unit = st.selectbox("Seleccione destino", unit_options, index=1 if len(unit_options)>1 else 0, label_visibility="collapsed", key="u_to")

    # --- CÁLCULO ---
    if category == "Temperatura":
        result_val = convert_temperature(input_value, from_unit, to_unit)
    else:
        result_val = convert_general(input_value, category, from_unit, to_unit)

    # --- COLUMNA DERECHA: RESULTADO ---
    with col_result:
        # Formateo sin notación científica
        final_display = format_number_smart(result_val)
        
        st.markdown(f"""
        <div style="height: 25px;"></div> <div class="result-box">
            <div style="font-size: 1rem; color: #64748b; margin-bottom: 10px;">RESULTADO FINAL</div>
            <div class="result-value">{final_display}</div>
            <div class="result-unit">{to_unit}</div>
        </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Aplicación optimizada para uso técnico en ingeniería.")
