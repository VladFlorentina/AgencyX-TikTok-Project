# TrendTok Solutions

## Despre proiect

Acest proiect analizeaza performanta postarilor si a autorilor de pe TikTok pentru o agentie fictiva de marketing numita TrendTok Solutions.
Scopul este sa identificam ce tipuri de continut si ce autori au cele mai bune rezultate, astfel incat agentia sa poata lua decizii de business mai bune.

Proiectul are doua componente:
- aplicatie interactiva in Python, realizata cu Streamlit;
- scripturi SAS pentru analiza si raportare.

## Datele folosite

Fisierul principal de lucru este `data/tiktok_merged_data_deduplicated.csv`.
Contine informatii despre postari, autori, aprecieri, comentarii, distribuiri, vizualizari, hashtag-uri si alte atribute utile pentru analiza.

## Ce am implementat in Python

Aplicatia Streamlit din `app.py` include mai multe functionalitati cerute in PDF:
- structura multi-pagina;
- filtre interactive cu widget-uri;
- import CSV cu pandas;
- tratarea valorilor lipsa;
- scalarea variabilei `plays`;
- agregari si grupuri cu pandas;
- accesarea datelor cu `loc` si `iloc`;
- grafice dinamice;
- clusterizare cu scikit-learn;
- regresie multipla cu statsmodels;
- afisarea de metrici generale.

Aplicatia este gandita ca un dashboard de analiza pentru TrendTok Solutions:
- pagina de overview prezinta sumarul general;
- pagina de calitate a datelor arata valorile lipsa si corelatiile;
- pagina de analiza a autorilor compara performanta creatorilor;
- pagina de analiza a postarilor prezinta distributii si top postari;
- pagina de inspector randuri permite vizualizarea cu `loc` si `iloc`;
- pagina de machine learning grupeaza postarile cu K-Means;
- pagina de modele statistice foloseste OLS pentru a estima vizualizarile.

## Ce am implementat in SAS

Fisierul `sas_academy_script.sas` contine exemple pentru cerintele SAS din proiect:
- import de date din fisier extern;
- formate definite de utilizator;
- procesare conditionala si iterativa;
- subseturi de date;
- functii SAS;
- combinarea seturilor de date prin SQL;
- utilizarea masivelor;
- raportare;
- statistici descriptive;
- grafice.

## Cum rulezi proiectul Python

1. Activeaza mediul virtual local:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Porneste aplicatia Streamlit:

```powershell
python -m streamlit run app.py
```

## Cum rulezi partea SAS

1. Deschide SAS Studio sau SAS OnDemand for Academics.
2. Incarca fisierul CSV in mediul SAS.
3. Deschide `sas_academy_script.sas` si adapteaza calea catre fisier.
4. Ruleaza scriptul si salveaza output-urile pentru documentatie.

## Structura proiectului

- `app.py` - aplicatia principala Streamlit;
- `requirements.txt` - dependinte Python;
- `data/` - fisierul CSV cu datele TikTok;
- `sas_academy_script.sas` - scriptul SAS;
- `Cerinte seminar Pachete Software 2026 - INFO.pdf` - cerintele seminarului.

## Observatii

