import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURATIE ---
st.set_page_config(page_title="Vacuüm Transport Calculator", layout="wide", page_icon="🌪️")

st.title("🌪️ Vacuüm Transport Calculator")
st.markdown("""
Bereken de benodigde pompcapaciteit en optimale buisdiameter voor het transporteren van granulaat.
""")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Procesgegevens")
capaciteit = st.sidebar.number_input("Gewenste capaciteit (kg/h)", value=500, step=50)
stortgewicht = st.sidebar.number_input("Stortgewicht granulaat (kg/m³)", value=600, step=50)

st.sidebar.header("2. Leidingwerk")
lengte_horizontaal = st.sidebar.number_input("Horizontale afstand (m)", value=20, step=1)
lengte_verticaal = st.sidebar.number_input("Verticale hoogte (m)", value=5, step=1)
aantal_bochten = st.sidebar.number_input("Aantal 90° bochten", value=4, step=1)

st.sidebar.header("3. Parameters")
# Veilige transportsnelheid voor granulaat (meestal 20-25 m/s)
v_target = st.sidebar.slider("Minimale luchtsnelheid (m/s)", 18.0, 30.0, 22.0, help="Snelheid nodig om product zwevend te houden. Granulaat = ca 22 m/s.")

# --- REKENKERN ---
def bereken_scenario(d_mm):
    # 1. Geometrie
    d_m = d_mm / 1000.0
    oppervlakte = np.pi * (d_m / 2)**2
    
    # Equivalente lengte berekenen (Bochten geven weerstand alsof de buis langer is)
    # Vuistregel: 1 bocht = ca 1.5 meter rechte buis equivalent
    eq_lengte = lengte_horizontaal + lengte_verticaal + (aantal_bochten * 1.5)
    
    # 2. Luchtvolume (Q)
    # Q = A * v (m3/s) -> * 3600 voor m3/h
    # We rekenen met aanzuigcondities (atmosferisch), in de leiding wordt het volume groter door vacuum, 
    # maar we dimensioneren de pomp meestal op 'displacement'.
    luchtvolume_m3h = oppervlakte * v_target * 3600
    luchtmassa_kg_h = luchtvolume_m3h * 1.2 # Dichtheid lucht ca 1.2 kg/m3
    
    # 3. Beladingsgraad (Solids Loading Ratio - mu)
    # Hoeveel kg product per kg lucht?
    mu = capaciteit / luchtmassa_kg_h
    
    # 4. Drukverlies Schatting (Vereenvoudigde Pneumatische Formule)
    # Drukverlies bestaat uit: Luchtweerstand + Materiaalweerstand + Lift
    
    # A. Luchtweerstand (Darcy-Weisbach benadering voor gladde buis)
    lambda_lucht = 0.02 # Wrijvingscoefficient buis
    dp_lucht = lambda_lucht * (eq_lengte / d_m) * (0.5 * 1.2 * v_target**2)
    
    # B. Materiaalweerstand (Extra weerstand door botsingen granulaat)
    # Vuistregel: dp_totaal = dp_lucht * (1 + K * mu)
    # K factor voor granulaat in dilute phase ligt vaak rond 1.5 - 2.0
    k_factor = 1.8
    dp_frictie = dp_lucht * (1 + k_factor * mu)
    
    # C. Lift (Verticale arbeid)
    # P = rho_bulk * g * h * concentratie_factor? 
    # Simpeler: Arbeid om massa omhoog te tillen per m3 lucht
    # Druk = Kracht/Oppervlakte. F = m*g. 
    # Dit is complex, we gebruiken een opslagfactor voor verticaal transport.
    dp_lift = lengte_verticaal * 150 # Ca 150 Pascal per verticale meter bij volle belading (schatting)
    
    # Totaal drukverschil in Pascal
    dp_totaal_pa = dp_frictie + dp_lift
    
    # Veiligheidsmarge en Filterweerstand
    dp_totaal_pa += 2500 # 25 mbar voor filter en inlaatverliezen
    dp_totaal_mbar = dp_totaal_pa / 100
    
    return {
        "Diameter": f"Ø {d_mm} mm",
        "Luchtvolume (m³/h)": round(luchtvolume_m3h, 1),
        "Vacuüm (mbar)": round(dp_totaal_mbar, 0),
        "Belading (kg prod/kg lucht)": round(mu, 1),
        "Snelheid (m/s)": v_target,
        "Ruwe Diameter": d_mm
    }

# --- SCENARIO'S DOORREKENEN ---
results = []
for dia in [40, 50, 60, 70]: # Je kunt hier diameters toevoegen
    results.append(bereken_scenario(dia))

df = pd.DataFrame(results)

# --- RESULTATEN WEERGEVEN ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Vergelijking Diameters")
    
    # Kleurcodering voor haalbaarheid
    # Max vacuum voor zijkanaal is vaak 300-350 mbar. Klauwenpomp gaat tot 600-800.
    def color_vacuum(val):
        if val < 250: return "🟢 Zijkanaal (Licht)"
        elif val < 400: return "🟡 Zijkanaal (Zwaar) / Klauwen"
        elif val < 800: return "🟠 Klauwenpomp / Roots"
        else: return "🔴 Kritisch / Verstoppingsrisico"

    df["Type Pomp Advies"] = df["Vacuüm (mbar)"].apply(color_vacuum)
    
    # Tabel tonen
    st.dataframe(
        df[["Diameter", "Luchtvolume (m³/h)", "Vacuüm (mbar)", "Belading (kg prod/kg lucht)", "Type Pomp Advies"]],
        use_container_width=True,
        hide_index=True
    )

    # Grafiek
    fig = px.bar(df, x="Diameter", y="Vacuüm (mbar)", 
                 title="Benodigd Vacuüm per Diameter",
                 text="Vacuüm (mbar)",
                 color="Vacuüm (mbar)",
                 color_continuous_scale=["green", "yellow", "orange", "red"])
    fig.add_hline(y=350, line_dash="dot", annotation_text="Grens Zijkanaalventilatoren", annotation_position="bottom right")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💡 Advies")
    
    # Beste optie selecteren (laagste energieverbruik dat technisch haalbaar is)
    # We zoeken de kleinste diameter die onder de 600 mbar blijft (praktische limiet vacuumtransport)
    # En waar de belading niet absurd hoog is (>15 is proppen)
    
    viable = df[(df["Vacuüm (mbar)"] < 600) & (df["Belading (kg prod/kg lucht)"] < 15)]
    
    if not viable.empty:
        # Sorteer op laagste luchtvolume (is vaak energiezuinigst)
        best = viable.sort_values("Luchtvolume (m³/h)").iloc[0]
        
        st.success(f"**Aanbevolen Diameter: {best['Diameter']}**")
        st.write(f"Bij deze diameter heb je een pomp nodig die:")
        st.markdown(f"""
        * Minimaal **{best['Luchtvolume (m³/h)']} m³/h** levert (bij 0 mbar)
        * Een onderdruk van **{best['Vacuüm (mbar)']} mbar** aankan.
        """)
        
        if best["Vacuüm (mbar)"] < 300:
            st.info("✅ Een standaard **Zijkanaalventilator** (Side Channel Blower) is voldoende.")
        elif best["Vacuüm (mbar)"] < 500:
            st.warning("⚠️ Dit vereist een **High-Pressure Zijkanaalventilator** of een kleine **Klauwenpomp**.")
        else:
            st.error("🔥 Dit vereist een **Klauwenpomp (Claw Pump)** of **Roots Blower** voor diep vacuüm.")
            
    else:
        st.error("Geen geschikte diameter gevonden binnen normale vacuümgrenzen. De afstand is te groot of de capaciteit te hoog voor deze diameters. Overweeg persluchttransport.")

st.markdown("---")
st.caption("Disclaimer: Dit model gebruikt de 'Dilute Phase' berekeningsmethode. Het gaat uit van vrije inlaat lucht. Specifieke materiaaleigenschappen (zoals kleverigheid of vorm) kunnen de weerstand beïnvloeden.")
