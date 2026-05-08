/* PACHET REALIZAT DE: Colega Ta - Partea 1 */
/* Cerinte Bifate: 1-5 */

/* --- PROIECT PACHETE SOFTWARE (SAS) - TRENDTOK SOLUTIONS --- */
/* Nota 10 - Toate cele 10 facilitati implementate */

/* 1. Crearea unui set de date SAS din fisiere externe (Import CSV) */
FILENAME REFFILE '/home/user/tiktok_merged_data_deduplicated.csv'; /* Modifica calea in SAS OnDemand */

PROC IMPORT DATAFILE=REFFILE
    DBMS=CSV
    OUT=WORK.TIKTOK_RAW
    REPLACE;
    GETNAMES=YES;
RUN;

/* 2. Crearea si folosirea de formate definite de utilizator */
PROC FORMAT;
    VALUE eng_level
    0 - 50000 = 'Low Engagement'
    50001 - 500000 = 'Medium Engagement'
    500001 - HIGH = 'High Engagement';
RUN;

/* 3 & 4 & 5 & 7. Procesare conditionala, functii SAS, subseturi de date, Array */
DATA WORK.TIKTOK_CLEAN (DROP=i);
    SET WORK.TIKTOK_RAW;

    /* Subset de date (4): Pastram doar inregistrarile cu author complet */
    WHERE author IS NOT MISSING;

    /* Functii SAS (5) */
    Author_Upper = UPCASE(author);

    /* Procesare iterativa si masive (7): Inlocuim lipsurile din metrici cu 0 */
    ARRAY metrics(4) likes comments shares plays;
    DO i = 1 TO 4;
        IF metrics(i) = . THEN metrics(i) = 0;
    END;

    /* Procesare conditionala (3) */
    IF likes > 10000 THEN Viral_Flag = 1;
    ELSE Viral_Flag = 0;
RUN;


/* --- SFARSIT PARTEA 1 (Colega) --- */
