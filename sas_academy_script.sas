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

/* 6. Combinarea seturilor de date (PROC SQL / INNER JOIN) */
/* Cream un dataset agregat cu autorii principali si ii facem join inapoi cu dataset-ul mare */
PROC SQL;
    CREATE TABLE WORK.AUTHOR_STATS AS
    SELECT author, COUNT(video_id) AS total_videos, SUM(likes) AS total_likes
    FROM WORK.TIKTOK_CLEAN
    GROUP BY author
    HAVING total_likes > 100000;

    CREATE TABLE WORK.TIKTOK_COMBINED AS
    SELECT a.*, b.total_videos
    FROM WORK.TIKTOK_CLEAN a
    INNER JOIN WORK.AUTHOR_STATS b
    ON a.author = b.author;
QUIT;

/* 8. Utilizarea de proceduri pentru raportare */
PROC REPORT DATA=WORK.AUTHOR_STATS NOWD HEADLINE CENTER;
    TITLE 'Top Authors Report (Likes > 100K)';
    COLUMN author total_videos total_likes;
    DEFINE author / DISPLAY 'Content Author' WIDTH=30;
    DEFINE total_videos / ANALYSIS SUM 'No. of Posts';
    DEFINE total_likes / ANALYSIS SUM 'Total Likes' FORMAT=COMMA12.;
RUN;

/* 9. Proceduri statistice (PROC FREQ, PROC CORR, PROC MEANS) */
PROC FREQ DATA=WORK.TIKTOK_CLEAN;
    TITLE 'Engagement Levels Frequency';
    TABLES likes / NOCUM;
    FORMAT likes eng_level.; /* Aplicarea formatului punctul 2 */
RUN;

PROC CORR DATA=WORK.TIKTOK_CLEAN;
    TITLE 'Correlation Between Engagement Metrics';
    VAR likes comments shares plays;
RUN;

PROC MEANS DATA=WORK.TIKTOK_CLEAN N MEAN MIN MAX;
    TITLE 'General Metrics Analytics';
    VAR likes comments shares plays;
    CLASS Viral_Flag; /* Segmentare baza pe IF-ul de la punctul 3 */
RUN;

/* 10. Generarea de grafice (PROC SGPLOT) */
PROC SGPLOT DATA=WORK.TIKTOK_CLEAN;
    TITLE 'Scatter Plot: Likes vs Plays Distribution by Viral Status';
    SCATTER X=plays Y=likes / GROUP=Viral_Flag;
    XAXIS LABEL='Total Plays';
    YAXIS LABEL='Total Likes';
RUN;

PROC SGPLOT DATA=WORK.AUTHOR_STATS;
    TITLE 'Bar Chart: Top Authors by Total Likes';
    VBAR author / RESPONSE=total_likes CATEGORYORDER=RESPDESC;
RUN;
