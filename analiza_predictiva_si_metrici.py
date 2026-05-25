import pandas as pd
import streamlit as st
import statsmodels.api as sm
from sklearn.cluster import KMeans
import plotly.express as px

def pagina_inspector_virale(df: pd.DataFrame) -> None:
    st.title("Inspector clipuri virale (loc / iloc)")
    
    st.write(" combinam loc si iloc ca sa vedem exact detaliile postarilor de top.")
    
    if 'likes' in df.columns:
        df_top = df.loc[df['likes'] > 100000]
        
        if not df_top.empty:
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
    

    c1, c2, c3 = st.columns(3)
    
   
    total_clipuri = len(df)
    medie_aprecieri = int(df['likes'].mean()) if 'likes' in df.columns and not df.empty else 0
    medie_views = int(df['plays'].mean()) if 'plays' in df.columns and not df.empty else 0
    
    c1.metric(label="Total clipuri afisate", value=total_clipuri)
    c2.metric(label="Media like-uri", value=medie_aprecieri)
    c3.metric(label="Media vizualizari", value=medie_views)

    st.write("---")
    
    maxim_distribuiri = int(df['shares'].max()) if 'shares' in df.columns and not df.empty else 0
    st.metric(label="Recordul de share-uri ptr un clip", value=maxim_distribuiri)
    st.caption("Asta ne arata care a fost cel mai distribuit clip din filtrarea curenta.")

def pagina_regresie_statsmodels(df: pd.DataFrame) -> None:
    st.title("Regresie Multipla cu Statsmodels")
    
    st.write(" regresie pt a vedea cat de mult cresc vizualizarile (plays) in functie de cate like-uri si comentarii primesti.")
    
    df_regresie = df[['likes', 'comments', 'plays']].dropna()
    
    if len(df_regresie) > 10:
        y = df_regresie['plays']
        X = df_regresie[['likes', 'comments']]
        
        X = sm.add_constant(X)
        
        try:
            model = sm.OLS(y, X).fit()
            
            st.write("### Rezumat tehnic model:")
            st.text(model.summary().tables[0].as_text())

            st.success(f"Valoarea R-squared este: {model.rsquared:.3f}. Daca e aproape de 1 inseamna ca modelul explica bine datele!")
        except Exception as eroare_model:
            st.error(f"Ceva nu a mers la model: {eroare_model}")
    else:
        st.info("minim 10 rânduri")

def pagina_clusterizare_kmeans(df: pd.DataFrame) -> None:
    st.title("Clusterizare postari cu K-Means (sklearn)")
    
    st.write("Incercam sa gasim niste tipologii de performanta in mod automat (nesupervizat).")
    st.write("Grupam clipurile bazandu-ne pe interactiune (nr de like-uri si commenturi).")
    
    k = st.slider("Alege in cate tipologii sa se imparta (K):", 2, 5, 3)
    
    date_k = df[['likes', 'comments', 'plays']].dropna()
    
    if len(date_k) > k:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        date_k['grup'] = kmeans.fit_predict(date_k[['likes', 'comments']])
        
        date_k['grup'] = date_k['grup'].astype(str)
        
        st.write(f"### Cum se prezinta cele {k} clustere detectate:")
        
        fig = px.scatter(date_k, x='likes', y='plays', color='grup',
                         title="Prastierea - vizualizari vs like-uri colorat dpa algoritm",
                         labels={"grup": "Tipologie alocata"})
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Punctele foarte departate de restul sunt 'outliers' - clipuri prea virale fata de normalitate.")
        
    else:
        st.warning("Nu aveam destule randuri filtrata pentru a face impartirea.")

    st.markdown("---")
    st.subheader("2. Regresie Logistica (scikit-learn)")
    st.write("Verificam posibilitatea de a prezice daca un videoclip va fi viral (prag teoretic de peste 500.000 vizualizari, ajustat dinamic la mediana din cauza filtrelor aplicate).")

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    reg_data = df[['likes', 'comments', 'shares', 'plays']].dropna().copy()
    if len(reg_data) > 10:
        mediana_vizualizari = reg_data['plays'].median()
        reg_data['Este_Viral'] = (reg_data['plays'] > mediana_vizualizari).astype(int)
        
        X_logistic = reg_data[['likes', 'comments', 'shares']]
        y_logistic = reg_data['Este_Viral']

        scaler = StandardScaler()
        X_scalat = scaler.fit_transform(X_logistic)

        if len(y_logistic.unique()) < 2:
           st.info("Eroare tehnica bypass: Prea puține diferențe in vizualizari pentru predicție logică. Mai adaugă rânduri.")
        else:
            log_reg = LogisticRegression(random_state=42)
            log_reg.fit(X_scalat, y_logistic)
            scor_predictie = log_reg.score(X_scalat, y_logistic)

            st.success(f"Acuratetea Regresiei Logistice de identificare a topului: {scor_predictie:.2%}")
            st.caption(f"Aplicam regresia invatand daca clipul depaseste valoarea normala a vizualizarilor ({mediana_vizualizari:,.0f}).")
    else:
        st.info("Baga mai multe date pentru antrenarea regresiei logistice (minim 10)")

