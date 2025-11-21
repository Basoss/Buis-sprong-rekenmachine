import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Pagina configuratie
st.set_page_config(page_title="Buis Rekenmeester", layout="wide", page_icon="📐")

# --- ZIJBALK MENU ---
st.sidebar.title("Menukaart 🛠️")
modus = st.sidebar.radio(
    "Kies je berekening:",
    ("1. Platte S-Bocht (2D)", "2. 3D Etage (Gedraaid)")
)

st.sidebar.info("""
**Uitleg:**
* **Platte S-Bocht:** Twee gelijke bochten om een horizontale sprong te maken.
* **3D Etage:** Een 90° bocht die kantelt, gevolgd door een correctiebocht.
""")

# =========================================================
# MODUS 1: DE PLATTE S-BOCHT (Jouw eerste app)
# =========================================================
if modus == "1. Platte S-Bocht (2D)":
    st.title("📐 Platte S-Bocht Calculator")
    st.write("Bereken de rechte uiteinden voor een simpele etage.")

    # --- INPUT ---
    col1, col2, col3 = st.columns(3)
    with col1:
        sprong = st.number_input("Gewenste Sprong (mm)", value=500.0, step=10.0)
    with col2:
        radius = st.number_input("Radius (R) in mm", value=500.0, step=10.0)
    with col3:
        hoek = st.slider("Hoek (graden)", 15, 90, 45, step=5)

    # --- BEREKENING ---
    hoek_rad = math.radians(hoek)
    sprong_bochten = 2 * radius * (1 - math.cos(hoek_rad))

    st.markdown("---")

    if sprong_bochten > sprong:
        st.error(f"⚠️ **Niet mogelijk!**")
        st.write(f"De bochten alleen maken al een sprong van **{sprong_bochten:.1f} mm**.")
    else:
        resterend = sprong - sprong_bochten
        totaal_recht = resterend / math.sin(hoek_rad)
        lengte_per_buis = totaal_recht / 2
        
        # --- RESULTATEN ---
        st.success("✅ Berekening geslaagd")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Lengte per recht uiteinde (L)", f"{lengte_per_buis:.1f} mm")
        with c2:
            st.metric("Totaal tussenstuk", f"{totaal_recht:.1f} mm")

        # --- PLOT (Matplotlib) ---
        st.write("### 👁️ Visuele weergave")
        L = lengte_per_buis
        R = radius
        
        # Coördinaten opbouwen
        x = [0, 0]
        y = [0, L]
        
        theta1 = np.linspace(np.pi, np.pi - hoek_rad, 30)
        x_b1 = R + R * np.cos(theta1)
        y_b1 = L + R * np.sin(theta1)
        x = np.concatenate([x, x_b1])
        y = np.concatenate([y, y_b1])
        
        curr_x, curr_y = x[-1], y[-1]
        dx = totaal_recht * math.sin(hoek_rad)
        dy = totaal_recht * math.cos(hoek_rad)
        x = np.concatenate([x, [curr_x + dx]])
        y = np.concatenate([y, [curr_y + dy]])
        
        # De "Terug" bocht simulatie voor plaatje
        # We tekenen gewoon naar het eindpunt toe
        x_end = [sprong, sprong]
        y_end_top = y[-1] + (R*(1-math.cos(hoek_rad))) + L
        # Simpele lijn voor visualisatie (exacte curve is lastig in 2D plot zonder center calc)
        x = np.concatenate([x, x_end])
        y = np.concatenate([y, [y_end_top, y_end_top + L]]) # Beetje valsspelen voor het plaatje

        fig, ax = plt.subplots(figsize=(4, 6))
        ax.plot(x, y, 'b-', linewidth=3, label='Buis')
        ax.axvline(x=sprong, color='r', linestyle='--', label=f'Sprong {sprong}mm')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)


# =========================================================
# MODUS 2: DE 3D ETAGE (Jouw tweede app)
# =========================================================
elif modus == "2. 3D Etage (Gedraaid)":
    st.title("📐 3D Buis: 90° Bocht + Rol")
    st.write("Bereken Hoogte (Z) en Zijsprong (Y) bij een gekantelde montage.")

    # --- INPUTS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hoek = st.number_input("Rolhoek / 2e Bocht (°)", value=45.0, step=5.0)
    with col2:
        R1 = st.number_input("Radius 1 (90° bocht)", value=500.0, step=10.0)
    with col3:
        R2 = st.number_input("Radius 2 (2e bocht)", value=250.0, step=10.0)
    with col4:
        L_mid = st.number_input("Recht tussenstuk (mm)", value=400.0, step=10.0)

    # --- BEREKENINGEN ---
    rad = np.radians(hoek)
    sin_a = np.sin(rad)
    cos_a = np.cos(rad)

    z1 = R1 * sin_a
    y1 = R1 * cos_a
    z_mid = L_mid * sin_a
    y_mid = L_mid * cos_a
    z2 = R2 * (1 - cos_a)
    y2 = R2 * sin_a

    total_z = z1 + z_mid + z2
    total_y = y1 + y_mid + y2

    # --- RESULTATEN ---
    st.divider()
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.info(f"⬆️ **Totale Hoogte (Z):**\n# {total_z:.1f} mm")
    with res_col2:
        st.info(f"➡️ **Totale Zijsprong (Y):**\n# {total_y:.1f} mm")
    with res_col3:
        st.success(f"📏 **Materiaal:**\n1x 90° (R{int(R1)})\n1x {int(hoek)}° (R{int(R2)})\nRecht: {int(L_mid)} mm")

    # --- 3D VISUALISATIE (PLOTLY) ---
    st.divider()
    st.subheader(f"👁️ 3D Weergave")

    path_x, path_y, path_z = [], [], []
    cur_x, cur_y, cur_z = 0, 0, 0
    path_x.append(cur_x); path_y.append(cur_y); path_z.append(cur_z)

    # Stap 1: 90 graden bocht (gerold)
    theta = np.linspace(0, np.pi/2, 20)
    xb = R1 * np.sin(theta)
    yb = R1 * (1 - np.cos(theta))
    zb = np.zeros_like(theta)
    yb_rot = yb * np.cos(rad) - zb * np.sin(rad)
    zb_rot = yb * np.sin(rad) + zb * np.cos(rad)
    path_x.extend(cur_x + xb)
    path_y.extend(cur_y + yb_rot)
    path_z.extend(cur_z + zb_rot)
    
    cur_x, cur_y, cur_z = path_x[-1], path_y[-1], path_z[-1]

    # Stap 2: Recht
    steps = np.linspace(0, L_mid, 10)
    path_x.extend(np.full_like(steps, cur_x))
    path_y.extend(cur_y + steps * cos_a)
    path_z.extend(cur_z + steps * sin_a)
    
    cur_x, cur_y, cur_z = path_x[-1], path_y[-1], path_z[-1]

    # Stap 3: 2e bocht (Benadering cirkelboog)
    cy = cur_y + R2 * np.sin(rad)
    cz = cur_z - R2 * np.cos(rad)
    angles = np.linspace(np.pi/2 + rad, np.pi/2, 20)
    y_arc = cy + R2 * np.cos(angles)
    z_arc = cz + R2 * np.sin(angles)
    
    path_x.extend(np.full_like(y_arc, cur_x))
    path_y.extend(y_arc)
    path_z.extend(z_arc)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=path_x, y=path_y, z=path_z, mode='lines', line=dict(color='#1f77b4', width=10), name='Buis'))
    fig.add_trace(go.Scatter3d(x=[0, 0, 0], y=[0, total_y, total_y], z=[0, 0, total_z], mode='lines', line=dict(color='red', dash='dash', width=4), name='Afmetingen'))
    fig.update_layout(scene=dict(aspectmode='data', xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
