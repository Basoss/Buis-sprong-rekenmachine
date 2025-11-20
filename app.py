import streamlit as st
import numpy as np
import math

st.title("📐 Buis Sprong Rekenmachine")

st.write("Bereken de benodigde rechte uiteinden voor een specifieke sprong.")

# Input velden
col1, col2, col3 = st.columns(3)

with col1:
    sprong = st.number_input("Gewenste Sprong (mm)", value=500.0, step=10.0)
with col2:
    radius = st.number_input("Radius (R) in mm", value=500.0, step=10.0)
with col3:
    hoek = st.slider("Hoek (graden)", min_value=15, max_value=90, value=45, step=15)

# Berekening
hoek_rad = math.radians(hoek)

# 1. Sprong door bochten alleen
sprong_bochten = 2 * radius * (1 - math.cos(hoek_rad))

st.markdown("---")

if sprong_bochten > sprong:
    st.error(f"⚠️ **Niet mogelijk!**")
    st.write(f"De bochten (zonder tussenstuk) maken al een sprong van **{sprong_bochten:.1f} mm**.")
    st.write("Probeer een grotere sprong, een kleinere radius of een kleinere hoek.")
else:
    # 2. Berekening lengte
    resterend = sprong - sprong_bochten
    totaal_recht = resterend / math.sin(hoek_rad)
    lengte_per_buis = totaal_recht / 2
    
    # Resultaten tonen
    st.success("✅ Berekening geslaagd")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric(label="Lengte per recht uiteinde (L)", value=f"{lengte_per_buis:.1f} mm")
        st.caption("Dit moet de lengte zijn van het rechte stuk aan elke buis.")
        
    with col_res2:
        st.metric(label="Totaal tussenstuk", value=f"{totaal_recht:.1f} mm")
        st.caption("De totale afstand tussen de twee bochten na montage.")

    # Visuele check (Tekstueel)
    st.info(f"📋 **Samenvatting voor zagen:**\nPak twee bochten van **{hoek} graden** (R={radius}).\nZorg dat ze beide een recht uiteinde hebben van **{lengte_per_buis:.1f} mm**.\nLas/monteer deze rechte einden tegen elkaar.")
