import streamlit as st
import pandas as pd

# ----------------- FUNZIONE HTML -----------------
def generate_html(descrizione, immagine):
    return f'''
<p>{descrizione}</p>
<div style="text-align:center;">
    <img src="{immagine}" alt="Immagine prodotto" />
</div>
'''

def generate_breve_descrizione(descrizione_breve, scheda_tecnica, scheda_sicurezza):
    return f'''
<p>{descrizione_breve}</p>
<span style="font-size: 10pt;">Prezzo comprensivo di contributo ambientale CONOU</span>
<b>Specifiche tecniche:</b>
<ul>
    <li><a href="{scheda_tecnica}" target="_blank" rel="noopener">Scheda tecnica prodotto (PDF)</a></li>
    <li><a href="{scheda_sicurezza}" target="_blank" rel="noopener">Scheda sicurezza (PDF)</a></li>
</ul>
'''

def process_formato(sku, formato):
    try:
        f = float(formato)
    except:
        return formato
    if 1 <= f <= 6:
        return f"{int(f)}Lx{int(f)}"
    elif f == 20:
        return "Tanica da 20L"
    elif f == 205:
        return "Fusto da 205L"
    elif "Tan" in sku:
        return f"Tanica da {int(f)}L"
    else:
        return f"{int(f)}L"

# ----------------- STREAMLIT -----------------
st.title("Generatore Listino WooCommerce")

uploaded_file = st.file_uploader("Carica il file Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file:
    # Lettura file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ----------------- NORMALIZZAZIONE COLONNE -----------------
    df.columns = df.columns.str.strip()         # rimuove spazi iniziali/finali
    df.columns = df.columns.str.replace('\n','')  # rimuove eventuali line-break
    df.columns = df.columns.str.replace('\xa0','') # rimuove spazi non-breaking

    st.write("Colonne trovate nel file:")
    st.write(df.columns.tolist())

    # ----------------- CREAZIONE DATAFRAME WC -----------------
    wc_df = pd.DataFrame()

    # Colonne principali
    wc_df['SKU'] = df['Sku']
    wc_df['NOME'] = "Olio Motore " + df['Viscosità'].astype(str) + " " + df['Nome olio'].astype(str) + " " + df['Marca'].astype(str)

    # BREVE_DESCRIZIONE HTML
    wc_df['BREVE_DESCRIZIONE'] = df.apply(lambda x: generate_breve_descrizione(
        x['Descrizione breve'], x['Scheda tecnica'], x['Scheda sicurezza']), axis=1)

    # DESCRIZIONE HTML
    wc_df['DESCRIZIONE'] = df.apply(lambda x: generate_html(
        x['Descrizione'], x['Img 7'] if pd.notna(x['Img 7']) else ""), axis=1)

    # Prezzi
    wc_df['PREZZO_LISTINO'] = df['Prezzo Marketplace']
    wc_df['PREZZO_IN_OFFERTA'] = ""

    # Categorie e tag
    wc_df['CATEGORIE'] = "Olio motore auto"
    wc_df['TAG'] = df['ACEA'].astype(str) + ", " + df['Viscosità'].astype(str) + ", " + df['Formato (L)'].astype(str)

    # Immagini
    img_cols = ['Img 1','Img 2','Img 3','Img 4','Img 5','Img 6','Img 7']
    wc_df['IMMAGINE'] = df[img_cols].apply(lambda x: ",".join([i for i in x if pd.notna(i)]), axis=1)

    # Download nomi/url
    wc_df['DOWNLOAD_NOMI'] = ""
    wc_df['DOWNLOAD_URL'] = ""

    # Attributi
    wc_df['ATTRIBUTO_Viscosità'] = df['Viscosità']
    wc_df['ATTRIBUTO_Predefinito_Viscosità'] = "Si"
    wc_df['ATTRIBUTO_Acea'] = df['ACEA']
    wc_df['ATTRIBUTO_Predefinito_Acea'] = "Si"
    wc_df['ATTRIBUTO_Marca'] = df['Marca']
    wc_df['ATTRIBUTO_Predefinito_Marca'] = "Si"
    wc_df['ATTRIBUTO_Utilizzo'] = df['Utilizzo']
    wc_df['ATTRIBUTO_Predefinito_Utilizzo'] = "Si"
    wc_df['ATTRIBUTO_Formato'] = df.apply(lambda x: process_formato(x['Sku'], x['Formato (L)']), axis=1)
    wc_df['ATTRIBUTO_Predefinito_Formato'] = "Si"

    st.write("Anteprima dati WooCommerce:")
    st.dataframe(wc_df.head())

    # Bottone download CSV
    csv = wc_df.to_csv(index=False)
    st.download_button(
        label="Scarica CSV WooCommerce",
        data=csv,
        file_name='listino_woocommerce.csv',
        mime='text/csv'
    )
