import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Master Unit Converter",
    page_icon="⚙️",
    layout="wide"
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

    /* Estilo para los "Botones" de selección (Radio Buttons) */
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: stretch;
        flex-wrap: wrap; /* Permite que bajen de línea si no caben */
        gap: 10px;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background-color: #f8fafc;
        padding: 8px 16px;
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        margin-right: 0px; /* Controlado por gap */
        transition: all 0.2s;
        font-weight: 500;
        font-size: 0.9rem;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #e2e8f0;
        border-color: #94a3b8;
        cursor: pointer;
    }

    /* Caja de Resultado (Derecha) */
    .result-box {
        background-color: #ecfdf5; /* Fondo verde muy suave */
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        border: 2px solid #10b981; /* Borde verde */
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 250px;
    }
    .result-value {
        /* Usamos clamp para que el texto se reduzca si es MUY largo */
        font-size: clamp(2rem, 5vw, 3.5rem); 
        color: #047857;
        font-weight: 800;
        word-wrap: break-word;
        line-height: 1.1;
    }
    .result-unit {
        font-size: 1.5rem;
        color: #065f46;
        font-weight: 600;
        margin-top: 15px;
    }
    
    /* Inputs */
    .stNumberInput input {
        font-size: 1.2rem;
        font-weight: bold;
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

# --- 4. LÓGICA DE FORMATEO Y CONVERSIÓN ---

def format_clean_number(value):
    """
    Formatea el número a MÁXIMO 4 decimales.
    Si el número es 100.0000 -> Devuelve "100"
    Si el número es 10.123456 -> Devuelve "10.1235"
    """
    if value == 0:
        return "0"
    
    # 1. Formatear fijo a 4 decimales con comas de miles
    # Ejemplo: 1234.56789 -> "1,234.5679"
    formatted = "{:,.4f}".format(value)
    
    # 2. Limpiar ceros a la derecha y punto si sobra
    # "10.5000" -> "10.5"
    # "100.0000" -> "100"
    formatted = formatted.rstrip('0').rstrip('.')
    
    # Caso especial: Si el redondeo lo dejó vacío o solo signo (aunque es raro con el format anterior)
    if formatted == "" or formatted == "-":
        return "0"
        
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

# --- BARRA LATERAL ---
with st.sidebar:
    # Logo
    logo_filename = "logo.png"
    try:
        st.image(logo_filename, use_column_width=True)
    except:
        st.markdown("### ⚙️ Master Converter")
    
    st.markdown("---")
    
    # SELECTOR DE VARIABLE (Radio Buttons Verticales)
    st.subheader("📍 VARIABLE")
    category = st.radio(
        "Seleccione Magnitud:",
        options=list(CONVERSION_FACTORS.keys()),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Propiedad de CS Sistemas de Aire**")

# --- PANEL PRINCIPAL ---
st.markdown('<div class="main-header">Calculadora de Conversión</div>', unsafe_allow_html=True)
st.markdown(f'<div class="branding-text">🛠️ Configurando: {category} | Propiedad de CS Sistemas de Aire</div>', unsafe_allow_html=True)

# Layout de columnas (Input | Resultado)
col_input, col_result = st.columns([1.5, 1], gap="large")

# Obtenemos las unidades disponibles
if category == "Temperatura":
    unit_options = CONVERSION_FACTORS[category]["units"]
else:
    unit_options = list(CONVERSION_FACTORS[category]["units"].keys())

with col_input:
    st.markdown("### 1. Ingrese Valor")
    input_value = st.number_input(
        "Valor:", 
        value=1.0, 
        format="%.4f", 
        step=1.0,
        label_visibility="collapsed"
    )
    
    st.markdown("### 2. Unidad Origen (De)")
    # Selector tipo BOTÓN (Radio horizontal con wrapping)
    from_unit = st.radio(
        "De:", 
        unit_options, 
        horizontal=True, 
        key="from_u",
        label_visibility="collapsed"
    )
    
    st.markdown("### 3. Unidad Destino (A)")
    # Selector tipo BOTÓN (Radio horizontal con wrapping)
    # Seleccionamos por defecto el segundo elemento si existe
    default_idx = 1 if len(unit_options) > 1 else 0
    to_unit = st.radio(
        "A:", 
        unit_options, 
        index=default_idx, 
        horizontal=True, 
        key="to_u",
        label_visibility="collapsed"
    )

# --- CÁLCULO ---
if category == "Temperatura":
    result_val = convert_temperature(input_value, from_unit, to_unit)
else:
    result_val = convert_general(input_value, category, from_unit, to_unit)

# --- VISUALIZACIÓN ---
with col_result:
    # Aplicamos el formateo limpio limitado a 4 decimales
    final_display = format_clean_number(result_val)
    
    st.markdown(f"""
    <div class="result-box">
        <div style="font-size: 1rem; color: #64748b; margin-bottom: 10px; text-transform: uppercase;">Resultado Final</div>
        <div class="result-value">{final_display}</div>
        <div class="result-unit">{to_unit}</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
