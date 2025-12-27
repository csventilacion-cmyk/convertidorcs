import streamlit as st
import pandas as pd

# Configuración de la página (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Master Unit Converter",
    page_icon="📐",
    layout="centered"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Estilo del Título Principal */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A; /* Azul oscuro corporativo */
        text-align: center;
        font-weight: 700;
        margin-bottom: 1rem;
        margin-top: -2rem; /* Ajuste para subirlo un poco */
    }
    /* Caja del Resultado */
    .result-box {
        background-color: #F3F4F6; /* Gris muy claro */
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        border: 2px solid #E5E7EB; /* Borde gris suave */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .result-label {
        font-size: 1.1rem;
        color: #6B7280; /* Gris medio */
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .result-value {
        font-size: 3.5rem;
        color: #059669; /* Verde esmeralda fuerte */
        font-weight: 800;
        line-height: 1.2;
    }
    .result-unit {
        font-size: 1.5rem;
        color: #374151; /* Gris oscuro */
        margin-top: 5px;
        font-weight: 500;
    }
    /* Ajuste de inputs */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 1.1rem;
    }
    /* Ajustes de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
        border-right: 1px solid #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE CONVERSIÓN ---
# Estrategia: Definir una "Unidad Base" para cada categoría.
# El factor es el multiplicador para convertir DE la unidad A LA base.
# Ejemplo Longitud (Base: metros): 1 ft = 0.3048 m -> factor 0.3048

CONVERSION_FACTORS = {
    "Caudal (Flow)": {
        "base_unit": "m³/seg",
        "units": {
            "m³/seg": 1.0,
            "CFM": 0.0004719,  # Según imagen
            "m³/hr": 1/3600,   # 0.0002777...
            "l/seg": 0.001,
            "l/min": 0.00001667 # 1/60000
        }
    },
    "Volumen": {
        "base_unit": "m³",
        "units": {
            "m³": 1.0,
            "ft³": 0.028317,   # Según imagen
            "in³": 0.00001639, # Según imagen
            "Litros (l)": 0.001
        }
    },
    "Velocidad": {
        "base_unit": "m/seg",
        "units": {
            "m/seg": 1.0,
            "fpm": 0.00508,     # Según imagen
            "m/min": 0.0166667,
            "fps": 0.3048
        }
    },
    "Presión": {
        "base_unit": "Pa",
        "units": {
            "Pa": 1.0,
            "in H₂O": 248.84,   # Según imagen
            "in Hg": 3386.4,    # Según imagen
            "mm H₂O": 9.80665,  # Estándar derivado
            "mm Hg": 133.32,    # Según imagen
            "psi": 6894.76,     # Estándar
            "atm": 101325
        }
    },
    "Area": {
        "base_unit": "m²",
        "units": {
            "m²": 1.0,
            "ft²": 0.092903,
            "in²": 0.00064516,
            "mm²": 0.000001
        }
    },
    "Densidad": {
        "base_unit": "kg/m³",
        "units": {
            "kg/m³": 1.0,
            "lb/ft³": 16.0185 # Según imagen (aprox 16.02)
        }
    },
    "Longitud": {
        "base_unit": "m",
        "units": {
            "m": 1.0,
            "ft": 0.3048,
            "in": 0.0254,
            "mm": 0.001
        }
    },
    "Peso": {
        "base_unit": "kg",
        "units": {
            "kg": 1.0,
            "lb": 0.45359,
            "oz": 0.0283495,
            "gramos": 0.001
        }
    },
    "Potencia": {
        "base_unit": "W",
        "units": {
            "W": 1.0,
            "kW": 1000.0,
            "HP": 745.7 # Según imagen
        }
    },
    "Temperatura": {
        "units": ["°C", "°F"] # Lógica especial manejada aparte
    }
}

# --- LÓGICA DE CONVERSIÓN ---

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    
    # Convertir a Celsius primero
    celsius = value
    if from_unit == "°F":
        celsius = (value - 32) * 5/9
    
    # Convertir de Celsius al destino
    if to_unit == "°C":
        return celsius
    elif to_unit == "°F":
        return (celsius * 9/5) + 32
    return value

def convert_general(value, category, from_unit, to_unit):
    try:
        factors = CONVERSION_FACTORS[category]["units"]
        # Fórmula: Valor * (Factor Origen -> Base) / (Factor Destino -> Base)
        base_value = value * factors[from_unit]
        result = base_value / factors[to_unit]
        return result
    except KeyError:
        return 0.0

# --- INTERFAZ DE USUARIO (UI) ---

# 1. Configuración de la Barra Lateral (Sidebar)
with st.sidebar:
    # --- INTEGRACIÓN DEL LOGOTIPO ---
    # NOTA IMPORTANTE:
    # Asegúrate de subir un archivo llamado 'logo.png' al mismo directorio
    # que este archivo app.py en tu repositorio de GitHub.
    # Si tu archivo tiene otro nombre, cámbialo aquí abajo.
    logo_filename = "logo.png"
    try:
        # Muestra el logo. 'use_column_width=True' hace que se ajuste al ancho de la barra lateral.
        st.image(logo_filename, use_column_width=True)
    except FileNotFoundError:
        # Mensaje amigable si se te olvida subir la imagen
        st.warning(f"⚠️ No se encontró '{logo_filename}'. Por favor, sube tu imagen al repositorio.")
        st.markdown("---")

    # Título y Selección de Categoría
    st.header("Panel de Control")
    categories = list(CONVERSION_FACTORS.keys())
    category = st.selectbox("📂 Seleccione Magnitud", categories, index=0)

    # Información del pie de página lateral
    st.markdown("---")
    st.info("Factores de conversión basados en estándares de ingeniería.")
    st.caption("Versión Pro 1.1 | 2025")


# 2. Panel Principal
st.markdown('<div class="main-header">Master Unit Converter</div>', unsafe_allow_html=True)

# Contenedor principal con un poco de padding superior
main_container = st.container()

with main_container:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Datos de Origen")
        # Input numérico
        input_value = st.number_input("Ingrese el valor numérico:", value=1.0, format="%.4f", step=0.1)
        
        # Selector de unidad de origen
        if category == "Temperatura":
            unit_options = CONVERSION_FACTORS[category]["units"]
        else:
            unit_options = list(CONVERSION_FACTORS[category]["units"].keys())
            
        from_unit = st.selectbox("Unidad Actual:", unit_options, key="from_unit")

    with col2:
        st.subheader("Datos de Destino")
        # Selector de unidad de destino
        to_unit = st.selectbox("Convertir a:", unit_options, index=1 if len(unit_options)>1 else 0, key="to_unit")
        
        # --- CÁLCULO AUTOMÁTICO ---
        if category == "Temperatura":
            result = convert_temperature(input_value, from_unit, to_unit)
        else:
            result = convert_general(input_value, category, from_unit, to_unit)

        # --- VISUALIZACIÓN DEL RESULTADO ---
        # Usamos notación científica (g) si el número es muy grande o muy pequeño
        formatted_result = f"{result:,.5g}"

        st.markdown(f"""
            <div style="margin-top: 28px;"></div> <div class="result-box">
                <div class="result-label">Resultado Calculado</div>
                <div class="result-value">{formatted_result}</div>
                <div class="result-unit">{to_unit}</div>
            </div>
        """, unsafe_allow_html=True)

# Footer final discreto
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>
        © 2025 Ingeniería y Soluciones Técnicas. Herramienta de uso profesional.
    </div>
""", unsafe_allow_html=True)
