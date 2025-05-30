import streamlit as st
import pandas as pd

st.title("Renten-Ausgaben-Optimierer (Euro, Inflation)")

st.sidebar.header("Passen Sie Ihre Parameter an:")

aktuelles_alter = st.sidebar.number_input("Aktuelles Alter", min_value=20, max_value=95, value=50)
rentenalter = st.sidebar.number_input("Rentenalter", min_value=aktuelles_alter+1, max_value=100, value=55)
sterbealter = st.sidebar.number_input("Sterbealter", min_value=rentenalter+1, max_value=120, value=100)
start_depot = st.sidebar.number_input("Startkapital (€)", min_value=0, step=10000, value=1_500_000)
zins = st.sidebar.number_input("Jährlicher Zinssatz (%)", min_value=0.0, max_value=20.0, value=4.0) / 100
arbeitseinkommen = st.sidebar.number_input("Einkommen während Arbeit (monatlich €)", min_value=0, step=500, value=6_000)
renten_einkommen = st.sidebar.number_input("Einkommen in Rente (monatlich €)", min_value=0, step=500, value=3_000)
inflation = st.sidebar.number_input("Jährliche Inflationsrate (%)", min_value=0.0, max_value=10.0, value=2.0) / 100

st.write("### Anleitung")
st.write(
    "Passen Sie die Parameter in der Seitenleiste an. Das Programm berechnet die optimale monatliche Startausgabe (in Euro), "
    "damit Ihr Depot zum gewählten Sterbealter auf null sinkt, und zeigt den Depotverlauf als Diagramm. "
    "Alle Zuflüsse und Ausgaben werden jährlich um die Inflationsrate erhöht."
)

# Optimierung
low = 0
high = start_depot * 2  # Obergrenze für jährliche Ausgaben
tolerance = 1
optimale_ausgabe = None
endverlauf = []

for _ in range(100):
    ausgabe = (low + high) / 2
    depot = start_depot
    verlauf = []
    adj_arbeitseinkommen = arbeitseinkommen * 12
    adj_renten_einkommen = renten_einkommen * 12
    adj_ausgabe = ausgabe
    for alter in range(aktuelles_alter + 1, sterbealter + 1):
        zufluss = adj_arbeitseinkommen if alter < rentenalter else adj_renten_einkommen
        depot = depot * (1 + zins) + zufluss - adj_ausgabe
        verlauf.append({
            "Alter": alter,
            "Monatliche Ausgabe (€)": adj_ausgabe / 12,
            "Jährlicher Zufluss (€)": zufluss,
            "Depotwert am Jahresende (€)": depot
        })
        # Inflation für das nächste Jahr anwenden
        adj_arbeitseinkommen *= (1 + inflation)
        adj_renten_einkommen *= (1 + inflation)
        adj_ausgabe *= (1 + inflation)
    if abs(depot) <= tolerance:
        optimale_ausgabe = ausgabe
        endverlauf = verlauf.copy()
        break
    elif depot > 0:
        low = ausgabe
        endverlauf = verlauf.copy()
    else:
        high = ausgabe

if optimale_ausgabe is not None:
    st.success(f"Optimale monatliche Startausgabe: **€{optimale_ausgabe/12:,.2f}** (steigt jährlich mit Inflation)")
else:
    st.warning("Es konnte kein optimaler Ausgabewert gefunden werden. Bitte passen Sie die Parameter an.")

df = pd.DataFrame(endverlauf)
st.line_chart(df.set_index("Alter")["Depotwert am Jahresende (€)"])

st.write("### Jährliche Übersicht: Ausgabe, Zufluss und Depotwert")
st.dataframe(df.style.format({
    "Monatliche Ausgabe (€)": "€{:.2f}",
    "Jährlicher Zufluss (€)": "€{:.2f}",
    "Depotwert am Jahresende (€)": "€{:.2f}"
}))
