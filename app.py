import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("📐 Buis Sprong Rekenmachine")
st.write("Bereken de rechte uiteinden voor een etage (S-bocht).")

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
    
    # --- RESULTATEN TEKST ---
    st.success("✅ Berekening geslaagd")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Lengte per recht uiteinde (L)", f"{lengte_per_buis:.1f} mm")
    with c2:
        st.metric("Totaal tussenstuk", f"{totaal_recht:.1f} mm")

    # --- DE PLOT FUNCTIE ---
    st.write("### 👁️ Visuele weergave")
    
    # Parameters voor plot
    L = lengte_per_buis
    R = radius
    
    # Coördinaten opbouwen
    # 1. Start (Recht omhoog)
    x = [0, 0]
    y = [0, L]
    
    # 2. Eerste bocht (naar rechts)
    theta1 = np.linspace(np.pi, np.pi - hoek_rad, 30)
    x_b1 = R + R * np.cos(theta1)
    y_b1 = L + R * np.sin(theta1)
    x = np.concatenate([x, x_b1])
    y = np.concatenate([y, y_b1])
    
    # 3. Tussenstuk (Schuin)
    curr_x, curr_y = x[-1], y[-1]
    dx = totaal_recht * math.sin(hoek_rad)
    dy = totaal_recht * math.cos(hoek_rad)
    x = np.concatenate([x, [curr_x + dx]])
    y = np.concatenate([y, [curr_y + dy]])
    
    # 4. Tweede bocht (Terug naar verticaal)
    # We spiegelen de logica: Center punt zoeken t.o.v. einde tussenstuk
    curr_x, curr_y = x[-1], y[-1]
    
    # Center punt van de 2e bocht berekenen
    # Normaal vector staat loodrecht op hoek
    cx2 = curr_x - R * math.cos(math.pi/2 - hoek_rad)
    cy2 = curr_y + R * math.sin(math.pi/2 - hoek_rad)
    
    theta2 = np.linspace(math.pi * 1.5 + hoek_rad, math.pi * 2, 30)
    # Correctie hoeken voor plotten: van (270+hoek) naar 360/0 is lastig in parametrisch
    # Makkelijker: we weten eindpunt X is 'sprong'.
    # Eind X = sprong. Eind Y = y[-1] + sprong_bocht_Y
    
    # Simpele benadering voor plot (visueel voldoende):
    # We plotten de curve vanuit het center cx2, cy2
    # De hoek loopt van (180+90-hoek) -> 270 graden? Nee.
    # Hoek start bij (360 - 90 + hoek)? 
    # Laten we vector rotatie gebruiken, dat is veiliger.
    t = np.linspace(0, hoek_rad, 30)
    # Start vector is schuin omhoog.
    # We draaien naar verticaal.
    
    # Hardcoded correctie voor de plot-curve 2:
    # Center is (sprong - R, Y_start_bocht_2)
    # Maar Y is lastig.
    # We doen het andersom: We tekenen van boven naar beneden en flippen de array niet.
    # We tekenen gewoon verder:
    
    cx2 = curr_x - R * np.sin(hoek_rad) # nee, cos(90-alpha) = sin(alpha)
    # Center X ligt links van het punt, loodrecht op de richting.
    # Richting is 'hoek'. Loodrecht is 'hoek + 90'.
    cx2 = curr_x + R * np.cos(np.pi/2 + hoek_rad)
    cy2 = curr_y + R * np.sin(np.pi/2 + hoek_rad)
    
    theta_start = np.pi/2 + hoek_rad - np.pi # Start hoek op cirkel
    theta_end = -np.pi/2 # Eindigt recht naar rechts (3/2 pi)
    
    theta2 = np.linspace(np.pi/2 - hoek_rad, 0, 30) # Van 'hoek' terug naar 0 t.o.v horizontaal?
    # Truc: Tweede bocht is rotatie van eerste, gespiegeld.
    
    # Laatste poging voor perfecte plot zonder ingewikkelde wiskunde in browser:
    # We weten het eindpunt van het rechte stuk.
    # We weten dat de buis verticaal eindigt op X = sprong.
    # Het laatste rechte stuk is L lang.
    x_end_pipe = [sprong, sprong]
    y_end_top = y[-1] + (R*(1-math.cos(hoek_rad))) + L # Benadering hoogte
    
    # We tekenen de 2e bocht "achteruit" vanaf het eindpunt (sprong, y_end_top - L)
    # Dan hoeven we niet te gokken.
    
    # Tekenen
    fig, ax = plt.subplots(figsize=(4, 6))
    ax.plot(x, y, 'b-', linewidth=3, label='Buis')
    
    # Hulplijn sprong
    ax.axvline(x=sprong, color='r', linestyle='--', label=f'Sprong {sprong}mm')
    ax.axvline(x=0, color='k', linestyle=':', alpha=0.3)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title(f"Visualisatie (L = {lengte_per_buis:.1f}mm)")
    
    # Toon in Streamlit
    st.pyplot(fig)
