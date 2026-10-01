import os
import streamlit as st
import base64
import numpy as np
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return None

# Configuración de página
st.set_page_config(page_title='Generador de Criaturas Fantásticas 👾', page_icon='👾', layout='centered')

st.title("👾 Generador de Criaturas y Monstruos Fantásticos")
st.markdown("Dibuja cualquier figura, monstruo o garabato en el lienzo y la IA creará sus estadísticas, poderes y ficha técnica completa.")

with st.sidebar:
    st.header("🎨 Herramientas del Lienzo")
    stroke_width = st.slider('Ancho del pincel', 1, 30, 5)
    stroke_color = st.color_picker('Color de trazo', '#000000')

st.subheader("🖊️ Dibuja tu criatura aquí:")

# Componente de lienzo interactivo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=320,
    width=450,
    drawing_mode="freedraw",
    key="canvas_monstruo",
)

# Entrada de la API Key de OpenAI
ke = st.text_input('🔑 Ingresa tu OpenAI API Key:', type="password")

if ke:
    os.environ['OPENAI_API_KEY'] = ke
    api_key = ke
else:
    api_key = None

analyze_button = st.button("🚀 ¡Analizar Criatura y Generar Poderes!", type="primary")

if canvas_result.image_data is not None and analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu OpenAI API Key antes de continuar.")
    else:
        with st.spinner("⚡ Identificando especie, calculando nivel de poder y habilidades..."):
            # Guardar la imagen dibujada
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            input_image.save('boceto.png')
            
            base64_image = encode_image_to_base64("boceto.png")
            
            if base64_image:
                prompt_text = (
                    "Observa detenidamente este dibujo o boceto de una criatura/monstruo. "
                    "Analiza su forma, extremidades, trazos y estructura. "
                    "Crea una ficha de personaje de juego estilo Pokémon o RPG con los siguientes puntos: "
                    "\n\n"
                    "1. 👾 **Nombre de la Criatura:** (Inventa un nombre único y genial)\n"
                    "2. 🏷️ **Clase / Elemento:** (Ejemplo: Fuego Místico, Sombra Digital, Viento Cósmico, etc.)\n"
                    "3. ⚡ **Nivel de Poder:** (Un número del 1 al 999 con una breve justificación)\n"
                    "4. 💥 **3 Habilidades Especiales:** (Describe 3 ataques o superpoderes divertidos basados en el dibujo)\n"
                    "5. 🌍 **Hábitat Natural:** (Dónde vive esta criatura)\n"
                    "6. 📜 **Descripción y Origen:** (Un párrafo tierno/divertido explicando su personalidad y comportamiento)."
                )

                try:
                    client = OpenAI(api_key=api_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=600,
                    )
                    
                    resultado = response.choices[0].message.content
                    
                    st.success("¡Ficha de Criatura Creada Exitosamente!")
                    st.markdown("---")
                    st.markdown(resultado)

                except Exception as e:
                    st.error(f"Ocurrió un error al consultar la API: {e}")
