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
st.set_page_config(page_title='Tablero Inteligente - Creador de Cuentos', page_icon='🎨')

st.title("🎨 Creador de Cuentos Mágicos desde tus Bocetos")

with st.sidebar:
    st.header("✨ Acerca de la App")
    st.write(
        "¡Dibuja cualquier personaje o escena en el lienzo! "
        "Nuestra Inteligencia Artificial interpretará tu boceto y creará un "
        "cuento infantil único con título, historia y moraleja."
    )
    stroke_width = st.slider('Ancho del pincel', 1, 30, 5)
    stroke_color = st.color_picker('Color del pincel', '#000000')

st.subheader("🖍️ Dibuja tu personaje o escena aquí:")

# Componente de lienzo interactivo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=320,
    width=450,
    drawing_mode="freedraw",
    key="canvas_cuentos",
)

# Entrada de la API Key de OpenAI
ke = st.text_input('🔑 Ingresa tu OpenAI API Key:', type="password")

if ke:
    os.environ['OPENAI_API_KEY'] = ke
    api_key = ke
else:
    api_key = None

analyze_button = st.button("✨ ¡Convertir mi dibujo en un Cuento Mágico!", type="primary")

# Procesamiento al presionar el botón
if canvas_result.image_data is not None and analyze_button:
    if not api_key:
        st.warning("⚠ Por favor ingresa tu OpenAI API Key antes de continuar.")
    else:
        with st.spinner("🧙‍♂️ La IA está analizando tu dibujo y tejiendo la historia..."):
            # Guardar la imagen dibujada en el lienzo
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            input_image.save('boceto.png')
            
            # Codificar la imagen a Base64
            base64_image = encode_image_to_base64("boceto.png")
            
            if base64_image:
                # Prompt creativo para generar el cuento infantil
                prompt_text = (
                    "Observa detenidamente este dibujo o boceto. "
                    "1. Identifica qué objetos, personajes o figuras parecen estar dibujados. "
                    "2. Con base en esa interpretación, escribe un cuento infantil mágico, muy tierno y divertido. "
                    "3. Estructura la respuesta con: "
                    "   - 📖 **Título de la Historia** "
                    "   - 🎨 **Lo que vi en tu dibujo:** (una breve frase explicando qué reconoció) "
                    "   - ✨ **El Cuento:** (un cuento de 2 a 3 párrafos ideal para niños) "
                    "   - 🌟 **Moraleja:** (una enseñanza bonita relacionada al cuento)."
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
                    
                    st.success("¡Historia generada con éxito!")
                    st.markdown("---")
                    st.markdown(resultado)

                except Exception as e:
                    st.error(f"Ocurrió un error al consultar OpenAI: {e}")
