import threading
import pandas as pd
import streamlit as st
import requests
import plotly.express as px
import folium
from streamlit_folium import st_folium
from flask import Flask, request, jsonify
from streamlit_autorefresh import st_autorefresh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

st.set_page_config(page_title="Examen 2 IoT", layout="wide")
st.title("🌡️ Examen 2: Internet de las Cosas: TEMA - End Devices")
app = Flask(__name__)
data_path = "data.xlsx"

# Clave secreta AES (16, 24 o 32 bytes) - Cambia esto a tu clave real
SECRET_KEY = b'mysecretkey123456'
IV = b'1234567890123456'

def decrypt_aes(ciphertext):
    try:
        cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CFB(IV), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(base64.b64decode(ciphertext)) + decryptor.finalize()
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Error al descifrar: {e}")
        return None

@app.route("/data", methods=["POST"])
def update_data():
    global data_path
    try:
        encrypted_data = request.get_json().get("encrypted_data")
        decrypted_json = decrypt_aes(encrypted_data)
        if not decrypted_json:
            return jsonify({"status": "error", "message": "Error en el descifrado"})

        new_data = eval(decrypted_json)
        print(new_data)

        dfcambiar = pd.read_excel(data_path)
        dfcambiar.loc[dfcambiar["CODIGO"] == int(new_data["CODIGO"]), ["LATITUD", "LONGITUD", "TEMPERATURA"]] = [new_data["LATITUD"], new_data["LONGITUD"], new_data["TEMPERATURA"]]
        dfcambiar.to_excel(data_path, index=False)
        print(dfcambiar)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def run_flask():
    app.run(host='0.0.0.0', port=80)

def run_streamlit():
    st_autorefresh(interval=5000, key="autorefresh")
    tabs = st.tabs(["Inicio", "Mapa", "Gráficas y Tabla"])

    with tabs[0]:
        st.header("Bienvenido a su Examen de Internet de las Cosas")
        st.write("Las condiciones del proyecto son:")
        st.write("1. Nota 5.0 (100%): Elabora un bundling con un END DEVICE usando WiFi mediante una conexión http al servidor de forma correcta")
        st.write("2. Respeta el formato JSON del paquete así: {\"CODIGO\":\"1015\",\"TEMPERATURA\":19.7,\"LONGITUD\":-75.59048,\"LATITUD\":6.244157}")
    with tabs[1]:
        df = pd.read_excel(data_path)
        m = folium.Map(location=[df["LATITUD"].mean(), df["LONGITUD"].mean()], zoom_start=17)
        for _, row in df.iterrows():
            tooltip = f"Codigo: {row['CODIGO']}<br>Nombre: {row['NOMBRE']}<br>Temp: {row['TEMPERATURA']}°C"
            folium.Marker(
                location=[row["LATITUD"], row["LONGITUD"]],
                tooltip=tooltip,
                icon=folium.Icon(color=row['COLOR'].lower())
            ).add_to(m)
        st_folium(m, width=1200, height=500)

    with tabs[2]:
        df = pd.read_excel(data_path)
        fig = px.bar(df, x="CODIGO", y="TEMPERATURA", color="COLOR", title="Temperatura por Código")
        st.plotly_chart(fig)
        st.dataframe(df, height=1000, use_container_width=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_streamlit()
