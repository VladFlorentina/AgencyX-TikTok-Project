# PACHET REALIZAT DE: [Numele Tau]
# Cerinte Bifate: 7 (loc/iloc), 9 (scikit-learn), 10 (statsmodels), 11 (metrici specifice)

import pandas as pd
import streamlit as st
import statsmodels.api as sm
from sklearn.cluster import KMeans
import plotly.express as px

def pagina_inspector_virale(df: pd.DataFrame) -> None:
    st.title("Inspector clipuri virale (loc / iloc)")
    
    st.write("Aici combinam loc si iloc ca sa vedem exact detaliile postarilor de top.")
    
    if 'likes' in df.columns:
        # luam doar clipurile care au facut peste 100k like-uri 
        df_top = df.loc[df['likes'] > 100000]
        
        if not df_top.empty:
            # pastrez doar primele 3 randuri cu iloc dupa ce le sortez
            top_3_clipuri = df_top.sort_values(by="likes", ascending=False).iloc[0:3]
            st.write("### Top 3 clipuri virale din dataset:")
            st.dataframe(top_3_clipuri[['author', 'description', 'likes', 'plays']], use_container_width=True)
            
            st.write("Si aici detaliile in format JSON pentru locul 1 ca sa vedem toate coloanele:")
            st.json(top_3_clipuri.iloc[0].to_dict())
        else:
            st.info("Setul filtrat nu are clipuri cu atat de multe like-uri (peste 100k).")
    else:
        st.warning("Coloana de aprecieri nu a fost gasita.")

def pagina_metrici_generale(df: pd.DataFrame) -> None:
    st.title("Metrice de performanta")
    
    st.write("Cativa indicatori calculati rapid ca sa ne facem o idee despre datasetul afisat.")
    
    # impartim frumos pe coloane
    c1, c2, c3 = st.columns(3)
    
    # calcule simple
    total_clipuri = len(df)
    medie_aprecieri = int(df['likes'].mean()) if 'likes' in df.columns and not df.empty else 0
    medie_views = int(df['plays'].mean()) if 'plays' in df.columns and not df.empty else 0
    
    # afisare cu widgetul de metrici din streamlit (bifam cerinta 11)
    c1.metric(label="Total clipuri afisate", value=total_clipuri)
    c2.metric(label="Media like-uri", value=medie_aprecieri)
    c3.metric(label="Media vizualizari", value=medie_views)

    st.write("---")
    
    maxim_distribuiri = int(df['shares'].max()) if 'shares' in df.columns and not df.empty else 0
    st.metric(label="Recordul de share-uri ptr un clip", value=maxim_distribuiri)
    st.caption("Asta ne arata care a fost cel mai distribuit clip din filtrarea curenta.")

def pagina_regresie_statsmodels(df: pd.DataFrame) -> None:
    st.title("Regresie Multipla cu Statsmodels")
    
    st.write("Am facut aici o regresie sa vad cat de mult cresc vizualizarile (plays) in functie de cate like-uri si comentarii primesti.")
    
    # pregatesc datele fara na-uri ca altfel crapa
    df_regresie = df[['likes', 'comments', 'plays']].dropna()
    
    if len(df_regresie) > 10:
        # y reprezinta ce vrem sa aflam, X variabilele care influenteaza
        y = df_regresie['plays']
        X = df_regresie[['likes', 'comments']]
        
        # trebuie pus manual constanta la statsmodels (asa am facut la seminar)
        X = sm.add_constant(X)
        
        try:
            # bam, antrenam modelul
            model = sm.OLS(y, X).fit()
            
            st.write("### Rezumat tehnic model:")
            # afisez doar primele detalii din output sa nu umplu ecranul aiurea
            st.text(model.summary().as_text()[:800] + "\n\n[...] am taiat restul tabelului ca sa arate mai curat pe ecran")
            
            st.success(f"Valoarea R-squared este: {model.rsquared:.3f}. Daca e aproape de 1 inseamna ca modelul explica bine datele!")
        except Exception as eroare_model:
            st.error(f"Ceva nu a mers la model: {eroare_model}")
    else:
        st.info("Baga mai multe date ca sa se poata antrena regresia (minim 10 rânduri)")

def pagina_clusterizare_kmeans(df: pd.DataFrame) -> None:
    st.title("Clusterizare postari cu K-Means (sklearn)")
    
    st.write("Incercam sa gasim niste tipologii de performanta in mod automat (nesupervizat).")
    st.write("Grupam clipurile bazandu-ne pe interactiune (nr de like-uri si commenturi).")
    
    # las userul sa aleaga in cate grupuri sa se faca impărțeala
    k = st.slider("Alege in cate tipologii sa se imparta (K):", 2, 5, 3)
    
    date_k = df[['likes', 'comments', 'plays']].dropna()
    
    if len(date_k) > k:
        # rulez kmeans
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        date_k['grup'] = kmeans.fit_predict(date_k[['likes', 'comments']])
        
        # il fac string ca plot-ul sa ii dea culori distincte (categorice, nu continue)
        date_k['grup'] = date_k['grup'].astype(str)
        
        st.write(f"### Cum se prezinta cele {k} clustere detectate:")
        
        fig = px.scatter(date_k, x='likes', y='plays', color='grup',
                         title="Prastierea - vizualizari vs like-uri colorat dpa algoritm",
                         labels={"grup": "Tipologie alocata"})
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Punctele foarte departate de restul sunt 'outliers' - clipuri prea virale fata de normalitate.")
        
    else:
        st.warning("Nu aveam destule randuri filtrata pentru a face impartirea.")
