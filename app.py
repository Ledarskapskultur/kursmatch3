import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kursmatchare", layout="wide")

if 'kurser' not in st.session_state:
    st.session_state.kurser = None
if 'deltagare_info' not in st.session_state:
    st.session_state.deltagare_info = []

menu = st.sidebar.radio("Navigera", ["Filuppladdning", "Matchning och filtrering"])

if menu == "Filuppladdning":
    st.title("Ladda upp kursfil")
    uploaded_file = st.file_uploader("Ladda upp Excel-fil med kurser", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            expected_cols = ["Vecka", "Anläggning", "Arrangör", "Pris"]
            if not all(col in df.columns for col in expected_cols):
                st.error(f"Excel-filen måste innehålla följande kolumner: {', '.join(expected_cols)}")
            else:
                df["Pris"] = pd.to_numeric(df["Pris"], errors="coerce")
                df["Vecka"] = pd.to_numeric(df["Vecka"], errors="coerce")
                st.session_state.kurser = df
                st.success("Filen har laddats upp och kurserna är sparade!")
        except Exception as e:
            st.error(f"Fel vid läsning av Excel-fil: {e}")

elif menu == "Matchning och filtrering":
    st.title("Kursmatchare: UGL-utbildningar")

    st.sidebar.header("Deltagarens information")
    kund_namn = st.sidebar.text_input("Namn")
    kund_epost = st.sidebar.text_input("E-post")
    kund_telefon = st.sidebar.text_input("Telefon")

    st.sidebar.header("Filtrera på kurs")
    val_vecka = st.sidebar.text_input("Vecka (valfri, skriv t.ex. 12)")
    val_maxpris = st.sidebar.number_input("Maxpris (SEK)", min_value=0, value=20000, step=500)

    if st.session_state.kurser is not None:
        df = st.session_state.kurser.copy()
        df_filtered = df.copy()

        if val_vecka:
            try:
                vecka = int(val_vecka)
                df_filtered = df_filtered[df_filtered["Vecka"] == vecka]
            except ValueError:
                st.warning("Vänligen ange en giltig veckonummer.")

        df_filtered = df_filtered[df_filtered["Pris"] <= val_maxpris]

        if st.button("Spara deltagarinformation + matchade kurser"):
            for _, row in df_filtered.iterrows():
                st.session_state.deltagare_info.append({
                    "Namn": kund_namn,
                    "E-post": kund_epost,
                    "Telefon": kund_telefon,
                    "Vecka": row["Vecka"],
                    "Anläggning": row["Anläggning"],
                    "Pris": row["Pris"]
                })
            st.success("Informationen är sparad!")

        st.subheader("Matchade kurser")
        st.write(f"Antal träffar efter filter: {len(df_filtered)}")
        st.dataframe(df_filtered.reset_index(drop=True))

        st.subheader("Alla uppladdade kurser")
        st.write(f"Totalt antal kurser i filen: {len(df)}")
        st.dataframe(df.reset_index(drop=True))

        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Ladda ner matchade kurser som CSV",
            data=csv,
            file_name="matchade_kurser.csv",
            mime="text/csv"
        )

        if st.session_state.deltagare_info:
            st.subheader("Sparad deltagarinformation")
            deltagar_df = pd.DataFrame(st.session_state.deltagare_info)
            st.dataframe(deltagar_df)

    else:
        st.info("Ingen kursfil har laddats upp ännu. Gå till 'Filuppladdning' först.")
