# TrendTok Solutions

## Despre proiect

TrendTok Solutions este un proiect de analiză a performanței postărilor și autorilor de pe TikTok, realizat pentru o agenție fictivă de marketing.

Scopul proiectului este identificarea tipurilor de conținut și a autorilor cu cele mai bune rezultate, astfel încât datele să poată susține decizii de business mai bine argumentate.

## Proiect realizat în echipă

Acesta este un proiect universitar dezvoltat împreună cu [Mădălina Crăiniceanu](https://github.com/madalinacrainiceanu) și [Vlad Florentina](https://github.com/VladFlorentina), cu o contribuție egală de 50% din partea fiecărui membru al echipei.

## Componentele proiectului

Proiectul are două componente principale:

- o aplicație interactivă în Python, realizată cu Streamlit;
- scripturi SAS pentru procesarea, analiza și raportarea datelor.

## Datele folosite

Setul principal de date este disponibil în:

```text
data/tiktok_merged_data_deduplicated.csv
```

Acesta conține informații despre postări, autori, aprecieri, comentarii, distribuiri, vizualizări, hashtag-uri, muzică și alte atribute utile pentru analiză.

## Aplicația Python

Aplicația Streamlit include:

- dashboard general cu indicatori și grafice;
- filtre interactive pentru autori și performanța postărilor;
- analiză a calității datelor și a valorilor lipsă;
- agregări și statistici pe autori;
- analiză a postărilor și a indicatorilor de interacțiune;
- vizualizări dinamice cu Plotly;
- inspector pentru postări virale folosind `loc` și `iloc`;
- metrici generale pentru setul de date filtrat;
- regresie multiplă cu Statsmodels;
- clusterizare K-Means pentru identificarea tipologiilor de postări;
- regresie logistică pentru clasificarea postărilor în funcție de performanță.

## Componenta SAS

Scripturile SAS acoperă mai multe operații de analiză și raportare, printre care:

- importul datelor din fișiere externe;
- procesare condițională și iterativă;
- subseturi de date și funcții SAS;
- combinarea seturilor de date prin SQL;
- utilizarea masivelor;
- statistici descriptive și raportare;
- generarea de grafice.

## Contribuții în cadrul echipei

Proiectul a fost dezvoltat în mod colaborativ, prin contribuția egală a ambilor membri ai echipei.

- **Mădălina Crăiniceanu** a lucrat la modulul de analiză predictivă și metrici din `analiza_predictiva_si_metrici.py`, inclusiv la funcționalitățile pentru metrici generale, regresie și clusterizare, precum și la scriptul SAS pentru statistici avansate.
- **Vlad Florentina** a lucrat la aplicația Streamlit, prelucrarea și analiza inițială a setului de date, vizualizările dashboard-ului și componentele SAS pentru analiza și raportarea datelor.

## Tehnologii

- Python
- Pandas
- Streamlit
- Plotly
- Scikit-learn
- Statsmodels
- SAS

## Instalare și rulare

### Aplicația Python

Instalează dependențele:

```powershell
pip install -r requirements.txt
```

Pornește dashboard-ul Streamlit:

```powershell
python -m streamlit run app.py
```

### Scripturile SAS

1. Deschide SAS Studio sau SAS OnDemand for Academics.
2. Încarcă fișierul CSV în mediul SAS.
3. Deschide scriptul SAS dorit.
4. Adaptează calea către fișierul de date, dacă este necesar.
5. Rulează scriptul și salvează rezultatele pentru documentație.

## Structura proiectului

```text
AgencyX-TikTok-Project/
├── data/                               # Setul de date TikTok
├── word/                               # Documentație și materiale ale proiectului
├── app.py                              # Aplicația Streamlit
├── analiza_predictiva_si_metrici.py    # Analize predictive și metrici
├── requirements.txt                    # Dependențe Python
├── sas_academy_script.sas              # Script SAS principal
├── sas_academy_statistici_avansate.sas # Statistici SAS avansate
└── README.md
```

## Licență

Proiectul este disponibil sub licența MIT.
