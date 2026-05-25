FILENAME REFFILE '/home/u64481036/Proiect/tiktok_merged_data_deduplicated.csv';

PROC IMPORT DATAFILE=REFFILE
    DBMS=CSV
    OUT=WORK.TIKTOK_RAW
    REPLACE;
    GETNAMES=YES;
RUN;


/* --- FACILITATEA 2*/
PROC FORMAT;
    VALUE eng_level
    0 - 50000 = 'Low Engagement'
    50001 - 500000 = 'Medium Engagement'
    500001 - HIGH = 'High Engagement';
RUN;

PROC MEANS DATA=WORK.TIKTOK_RAW N MEAN MIN MAX MAXDEC=2;
    TITLE 'Analiza Performantei bazata pe Nivelul de Engagement';
    VAR likes;
    FORMAT likes eng_level.;
RUN;

/* --- FACILITATEA 3*/
DATA WORK.TIKTOK_CLEAN;
    SET WORK.TIKTOK_RAW;

    ARRAY metrics(4) likes comments shares plays;
    DO i = 1 TO 4;
        IF metrics(i) = . THEN metrics(i) = 0;
    END;

    IF likes > 10000 THEN Viral_Flag = 1;
    ELSE Viral_Flag = 0;
RUN;

PROC PRINT DATA=WORK.TIKTOK_CLEAN (OBS=20);
    TITLE "Verificare procesare conditionala (Viral_Flag)";
    VAR author likes Viral_Flag;
RUN;

/* --- FACILITATEA 4*/
DATA WORK.TIKTOK_CLEAN;
    SET WORK.TIKTOK_RAW;
    WHERE author IS NOT MISSING;
RUN;

PROC PRINT DATA=WORK.TIKTOK_CLEAN (OBS=10);
    TITLE "Rezultat Facilitatea 4: Subset date fara autori lipsa";
RUN;

/* --- FACILITATEA 5*/
DATA WORK.TIKTOK_FUNCTII;
    SET WORK.TIKTOK_RAW;
    Author_Upper = UPCASE(author);
RUN;

PROC PRINT DATA=WORK.TIKTOK_FUNCTII (OBS=15);
    TITLE "Rezultat Facilitatea 5: Standardizare nume prin functia UPCASE";
    VAR author Author_Upper;
RUN;


/* --- FACILITATEA 6 */
PROC SQL;
    CREATE TABLE WORK.TOP_CREATORI AS
    SELECT author, COUNT(video_id) AS cate_clipuri, SUM(likes) AS like_uri_totale
    FROM WORK.TIKTOK_CLEAN
    WHERE author IS NOT MISSING
    GROUP BY author
    HAVING SUM(likes) > 10000;

    CREATE TABLE WORK.TIKTOK_FINAL AS
    SELECT A.author, A.likes, A.plays, A.Viral_Flag, B.cate_clipuri
    FROM WORK.TIKTOK_CLEAN A
    INNER JOIN WORK.TOP_CREATORI B ON A.author = B.author
    ORDER BY A.likes DESC;
QUIT;

/* --- FACILITATEA 7*/
DATA WORK.TIKTOK_MASIVE;
    SET WORK.TIKTOK_RAW;
    ARRAY metrics(4) likes comments shares plays;
    DO i = 1 TO 4;
        IF metrics(i) = . THEN metrics(i) = 0;
    END;
    DROP i;
RUN;

PROC PRINT DATA=WORK.TIKTOK_MASIVE (OBS=20);
    TITLE "Rezultat Facilitatea 7: Procesarea in masa a metricilor prin Arrays";
    VAR author likes comments shares plays;
RUN;





PROC SQL;
    CREATE TABLE WORK.TOP_CREATORI AS
    SELECT author, COUNT(video_id) AS cate_clipuri, SUM(likes) AS like_uri_totale
    FROM WORK.TIKTOK_CLEAN
    WHERE author IS NOT MISSING
    GROUP BY author
    HAVING SUM(likes) > 10000;
    CREATE TABLE WORK.TIKTOK_FINAL AS
    SELECT A.author, A.likes, A.plays, A.Viral_Flag, B.cate_clipuri
    FROM WORK.TIKTOK_CLEAN A
    INNER JOIN WORK.TOP_CREATORI B
    ON A.author = B.author
    ORDER BY A.likes DESC;
QUIT;
PROC SORT DATA=WORK.TOP_CREATORI OUT=WORK.TOP20;
    BY DESCENDING like_uri_totale;
RUN;
DATA WORK.TOP20; 
    SET WORK.TOP20 (OBS=20); 
RUN;
PROC REPORT DATA=WORK.TOP20 NOWD HEADLINE CENTER;
    TITLE 'Raport Centralizat - Creatorii de top pe care putem miza (Top 20)';
    COLUMN author cate_clipuri like_uri_totale;
    DEFINE author / DISPLAY 'Creatorul vizat' FORMAT=$30. WIDTH=20;
    DEFINE cate_clipuri / ANALYSIS SUM 'Total clipuri in tabel' FORMAT=COMMA8.;
    DEFINE like_uri_totale / ANALYSIS SUM 'Like-uri stranse per total' FORMAT=COMMA12.;
RUN;
PROC MEANS DATA=WORK.TIKTOK_FINAL N MEAN MIN MAX MAXDEC=2;
    TITLE 'Ce inseamna sa fii viral? (Statistici din MEAN)';
    CLASS Viral_Flag; 
    VAR likes plays cate_clipuri;
    FORMAT likes eng_level.; 
RUN;
PROC CORR DATA=WORK.TIKTOK_FINAL PEARSON;
    TITLE 'Corelatii Pearson intre variabilele importante';
    VAR likes plays cate_clipuri;
    WITH likes; 
RUN;
PROC SGPLOT DATA=WORK.TOP20;
    TITLE "Distributia celor mai urmariti 20 influenceri din set (BarChart)";
    VBAR author / RESPONSE=like_uri_totale CATEGORYORDER=RESPDESC FILLATTRS=(COLOR=CX0072B2);
    XAXIS LABEL='Cine este creatorul de fapt?' FITPOLICY=ROTATE;
    YAXIS LABEL='Total aprecieri';
RUN;
PROC SGPLOT DATA=WORK.TIKTOK_CLEAN;
    TITLE "Cat de imprastiate sunt clipurile in baza de date (Viz vs Like)";
    SCATTER X=plays Y=likes / GROUP=Viral_Flag MARKERATTRS=(SYMBOL=CircleFilled);
    KEYLEGEND / TITLE="Prag viral (1 = da / 0 = inca nu)";
RUN;



