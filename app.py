from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tiktok_merged_data_deduplicated.csv"

NUMERIC_COLUMNS = ["likes", "comments", "shares", "plays", "views"]
TEXT_COLUMNS = ["author", "description", "hashtags", "music", "video_url"]
DATE_COLUMNS = ["create_time", "fetch_time", "posted_time"]


st.set_page_config(
    page_title="TrendTok Solutions",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
            median_value = cleaned[column].median()
            if pd.notna(median_value):
                cleaned[column] = cleaned[column].fillna(median_value)
            else:
                cleaned[column] = cleaned[column].fillna(0)

    for column in TEXT_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").fillna("unknown")

    for column in DATE_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    if "author" in cleaned.columns:
        cleaned = cleaned[cleaned["author"].notna()]

    return cleaned


def add_scaled_column(df: pd.DataFrame, column: str = "plays") -> pd.DataFrame:
    scaled = df.copy()

    if column not in scaled.columns:
        return scaled

    series = pd.to_numeric(scaled[column], errors="coerce")
    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        scaled[f"{column}_scaled"] = 0.0
    else:
        scaled[f"{column}_scaled"] = (series - min_value) / (max_value - min_value)

    return scaled


def prepare_data() -> pd.DataFrame:
    raw_data = load_data()
    cleaned_data = clean_data(raw_data)
    return add_scaled_column(cleaned_data, "plays")


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    author_options = ["Toti autorii"] + sorted(df["author"].dropna().astype(str).unique().tolist())
    selected_author = st.sidebar.selectbox("Autor", author_options)

    likes_min = int(df["likes"].min()) if "likes" in df.columns else 0
    likes_max = int(df["likes"].max()) if "likes" in df.columns else 0
    selected_likes = st.sidebar.slider("Minimum aprecieri (likes)", likes_min, likes_max, likes_min)

    if "plays_scaled" in df.columns:
        play_min = float(df["plays_scaled"].min())
        play_max = float(df["plays_scaled"].max())
        selected_play_range = st.sidebar.slider(
            "Interval vizualizari scalate",
            min_value=play_min,
            max_value=play_max,
            value=(play_min, play_max),
        )
    else:
        selected_play_range = None

    filtered = df.copy()
    if selected_author != "Toti autorii":
        filtered = filtered[filtered["author"] == selected_author]
    if "likes" in filtered.columns:
        filtered = filtered[filtered["likes"] >= selected_likes]
    if selected_play_range is not None:
        filtered = filtered[
            (filtered["plays_scaled"] >= selected_play_range[0])
            & (filtered["plays_scaled"] <= selected_play_range[1])
        ]

    return filtered


def render_overview_page(df: pd.DataFrame) -> None:
    st.title("TrendTok Solutions")
    st.subheader("Dashboard general")

    col1, col2, col3 = st.columns(3)
    col1.metric("Postari", f"{len(df):,}".replace(",", "."))
    col2.metric("Autori unici", f"{df['author'].nunique():,}".replace(",", ".") if "author" in df.columns else "0")
    col3.metric("Total aprecieri", f"{int(df['likes'].sum()):,}".replace(",", ".") if "likes" in df.columns else "0")

    st.write("### Mostra de date")
    st.dataframe(df.head(20), use_container_width=True)

    if {"author", "likes"}.issubset(df.columns):
        top_authors = df.groupby("author", as_index=False)["likes"].sum().sort_values("likes", ascending=False).head(10)
        st.write("### Top autori dupa aprecieri")
        st.bar_chart(top_authors.set_index("author")["likes"])

    if {"create_time", "likes"}.issubset(df.columns):
        time_series = df.dropna(subset=["create_time"]).copy()
        if not time_series.empty:
            time_series["date_only"] = time_series["create_time"].dt.date
            daily_likes = time_series.groupby("date_only", as_index=True)["likes"].sum().tail(30)
            st.write("### Evolutie zilnica aprecieri")
            st.line_chart(daily_likes)


def render_data_quality_page(df: pd.DataFrame) -> None:
    st.title("Calitatea datelor")

    missing_before = load_data().isna().sum().sort_values(ascending=False)
    missing_after = df.isna().sum().sort_values(ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Valori lipsa inainte de curatare")
        st.dataframe(missing_before[missing_before > 0].rename("missing_before"), use_container_width=True)
    with col2:
        st.write("### Valori lipsa dupa curatare")
        st.dataframe(missing_after[missing_after > 0].rename("missing_after"), use_container_width=True)

    st.write("### Coloane numerice si scalare")
    preview_columns = [column for column in ["plays", "plays_scaled", "likes"] if column in df.columns]
    st.dataframe(df[preview_columns].head(20), use_container_width=True)

    if "plays" in df.columns and "likes" in df.columns:
        corr_frame = df[["plays", "likes", "comments", "shares"]].copy()
        st.write("### Corelatii intre variabile numerice")
        st.dataframe(corr_frame.corr(numeric_only=True), use_container_width=True)


def render_author_analysis_page(df: pd.DataFrame) -> None:
    st.title("Analiza autorilor")

    if "author" not in df.columns:
        st.info("Coloana 'author' nu este disponibila in setul de date.")
        return

    author_stats = (
        df.groupby("author", as_index=False)
        .agg(
            posts=("video_id", "count") if "video_id" in df.columns else ("author", "count"),
            total_likes=("likes", "sum") if "likes" in df.columns else ("author", "count"),
            average_plays=("plays", "mean") if "plays" in df.columns else ("author", "count"),
        )
        .sort_values(["total_likes", "posts"], ascending=False)
    )

    st.write("### Statistici agregate pe autor")
    st.dataframe(author_stats.head(20), use_container_width=True)

    if "average_plays" in author_stats.columns:
        st.write("### Top autori dupa media de vizualizari")
        st.bar_chart(author_stats.set_index("author")["average_plays"].head(15))


def render_post_analysis_page(df: pd.DataFrame) -> None:
    st.title("Analiza postarilor")

    if "plays_scaled" in df.columns:
        st.write("### Distributia valorii scalate pentru vizualizari (plays)")
        st.bar_chart(df["plays_scaled"].head(50))

    if {"likes", "comments", "shares"}.issubset(df.columns):
        engagement = df[["likes", "comments", "shares"]].sum().sort_values(ascending=False)
        st.write("### Agregare simpla a indicatorilor de interactiune")
        st.bar_chart(engagement)

    if {"description", "likes"}.issubset(df.columns):
        top_posts = df.sort_values("likes", ascending=False).loc[:, ["description", "likes"]].head(10)
        st.write("### Cele mai apreciate postari")
        st.dataframe(top_posts, use_container_width=True)


def render_row_inspector_page(df: pd.DataFrame) -> None:
    st.title("Inspector randuri")

    if df.empty:
        st.info("Nu exista randuri disponibile in urma filtrarii.")
        return

    max_index = len(df) - 1
    row_index = st.slider("Selecteaza indexul randului", 0, max_index, 0)

    st.write("### Rezultat folosind 'loc'")
    st.dataframe(df.loc[[df.index[row_index]]], use_container_width=True)

    st.write("### Rezultat folosind 'iloc'")
    st.dataframe(df.iloc[[row_index]], use_container_width=True)

    st.write("### Detalii complete rand selectat")
    selected_row = df.iloc[row_index]
    st.json({key: (None if pd.isna(value) else str(value)) for key, value in selected_row.to_dict().items()})


def render_summary_page(df: pd.DataFrame) -> None:
    st.title("Metrici recapitulative")

    if df.empty:
        st.info("Nu exista date disponibile pentru rezumat.")
        return

    summary = pd.DataFrame(
        {
            "metrica": ["randuri", "coloane", "media_aprecieri", "mediana_aprecieri", "media_vizualizari", "mediana_vizualizari"],
            "valoare": [
                len(df),
                df.shape[1],
                float(df["likes"].mean()) if "likes" in df.columns else 0.0,
                float(df["likes"].median()) if "likes" in df.columns else 0.0,
                float(df["plays"].mean()) if "plays" in df.columns else 0.0,
                float(df["plays"].median()) if "plays" in df.columns else 0.0,
            ],
        }
    )

    st.dataframe(summary, use_container_width=True)
    if {"author", "likes"}.issubset(df.columns):
        author_totals = df.groupby("author", as_index=False)["likes"].sum().sort_values("likes", ascending=False).head(10)
        st.write("### Total aprecieri per autor")
        st.bar_chart(author_totals.set_index("author")["likes"])


def render_statistical_modeling_page(df: pd.DataFrame) -> None:
    st.title("Modelare statistica (Statsmodels)")

    if {"likes", "comments", "shares", "plays"}.issubset(df.columns):
        st.write("### Regresie Liniara Multipla (OLS)")
        st.write("Se prezice numarul de vizualizari ('plays') in functie de 'likes', 'comments' si 'shares'.")
        
        # Prepare data for regression
        data = df[["likes", "comments", "shares", "plays"]].dropna()
        if len(data) > 10:
            X = data[["likes", "comments", "shares"]]
            y = data["plays"]
            X = sm.add_constant(X)
            
            try:
                model = sm.OLS(y, X).fit()
                st.text(model.summary().as_text())
                
                st.write("### Esantion predictii model")
                data["vizualizari_prezise"] = model.predict(X)
                st.dataframe(data[["plays", "vizualizari_prezise", "likes"]].head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Eroare la antrenarea modelului: {e}")
        else:
            st.info("Nu exista suficiente date valide pentru regresie.")
            

def render_machine_learning_page(df: pd.DataFrame) -> None:
    st.title("Machine learning (Scikit-Learn)")

    if {"likes", "comments", "shares"}.issubset(df.columns):
        st.write("### Gruparea cu K-Means (Clustering)")
        st.write("Postarile sunt grupate in functie de gradul de interactiune (angajament).")
        
        k_clusters = st.slider("Selecteaza numarul de grupuri (K)", 2, 6, 3)
        
        data = df[["likes", "comments", "shares"]].dropna()
        if len(data) > 10:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)
            
            kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init='auto')
            data["cluster"] = kmeans.fit_predict(scaled_data)
            
            st.write(f"### Distributia grupurilor pentru K={k_clusters}")
            
            if "plays" in df.columns:
                data["plays"] = df["plays"].loc[data.index]
                fig = px.scatter(
                    data, x="likes", y="plays", color=data["cluster"].astype(str),
                    title="Grupuri: Aprecieri vs Vizualizari",
                    labels={"color": "ID Grup"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.write("### Mediile metricilor per grup")
            cluster_centers = data.groupby("cluster").mean()
            st.dataframe(cluster_centers, use_container_width=True)
        else:
            st.info("Sunt necesare mai multe date pentru clustere.")

def main() -> None:
    st.sidebar.title("TrendTok Solutions")
    st.sidebar.caption("Structura proiectului pentru Pachete Software")

    page = st.sidebar.radio(
        "Meniu navigare",
        [
            "General (Overview)", 
            "Calitatea datelor", 
            "Analiza autorilor", 
            "Analiza postarilor", 
            "Inspector randuri", 
            "Machine learning",
            "Modele statistice",
            "Metrici recapitulative"
        ],
    )

    data = prepare_data()
    filtered_data = filter_data(data)

    if page == "General (Overview)":
        render_overview_page(filtered_data)
    elif page == "Calitatea datelor":
        render_data_quality_page(filtered_data)
    elif page == "Analiza autorilor":
        render_author_analysis_page(filtered_data)
    elif page == "Analiza postarilor":
        render_post_analysis_page(filtered_data)
    elif page == "Inspector randuri":
        render_row_inspector_page(filtered_data)
    elif page == "Machine learning":
        render_machine_learning_page(filtered_data)
    elif page == "Modele statistice":
        render_statistical_modeling_page(filtered_data)
    else:
        render_summary_page(filtered_data)


if __name__ == "__main__":
    main()