from analiza_predictiva_si_metrici import (
    pagina_inspector_virale,
    pagina_metrici_generale,
    pagina_regresie_statsmodels,
    pagina_clusterizare_kmeans
)

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


def main() -> None:
    st.sidebar.title("TrendTok Solutions")
    st.sidebar.caption("Proiect Pachete Software (11 Facilitati Python)")

    st.sidebar.header("Modul 1: Analiza Descriptiva")
    page_1 = st.sidebar.radio(
        "Sectiunea de baza (Colega):",
        ["General (Overview)", "Calitatea datelor", "Analiza autorilor", "Analiza postarilor"]
    )
    
    st.sidebar.header("Modul 2: Analiza Statistica")
    page_2 = st.sidebar.radio(
        "Sectiunea de varf (Tu):",
        ["Nimic selectat", "Inspector Virale (loc/iloc)", "Metrici Actuale", "Regresie (Statsmodels)", "Tipologii (K-Means)"]
    )

    data = prepare_data()
    filtered_data = filter_data(data)
    
    st.sidebar.markdown("---")
    
    if page_1 == "General (Overview)": render_overview_page(filtered_data)
    if page_1 == "Calitatea datelor": render_data_quality_page(filtered_data)
    if page_1 == "Analiza autorilor": render_author_analysis_page(filtered_data)
    if page_1 == "Analiza postarilor": render_post_analysis_page(filtered_data)
    
    if page_2 != "Nimic selectat":
        st.markdown("---")
        if page_2 == "Inspector Virale (loc/iloc)": pagina_inspector_virale(filtered_data)
        if page_2 == "Metrici Actuale": pagina_metrici_generale(filtered_data)
        if page_2 == "Regresie (Statsmodels)": pagina_regresie_statsmodels(filtered_data)
        if page_2 == "Tipologii (K-Means)": pagina_clusterizare_kmeans(filtered_data)

if __name__ == "__main__":
    main()
