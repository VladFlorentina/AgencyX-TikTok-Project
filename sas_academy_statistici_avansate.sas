                        
/* Ce am facut eu: Partea de curatare cu SQL, grafice si testari  */
/*                         (Cerintele 6-10)                       */


/* Aici ne bazam pe setul WORK.TIKTOK_CLEAN pe care l-a facut ea  */
/* si care contine baza filtrata si fara na-uri.                  */

/* 6. Utilizarea PROC SQL pentru a uni niste date sumarizate      */
PROC SQL;
    /* Dintr-un foc, fac un tabel simplu sa vad creatorii buni    */
    /* Cei care au postat si strans decent de multe likeuri       */
    CREATE TABLE WORK.TOP_CREATORI AS
    SELECT author, COUNT(video_id) AS cate_clipuri, SUM(likes) AS like_uri_totale
    FROM WORK.TIKTOK_CLEAN
    WHERE author IS NOT MISSING
    GROUP BY author
    HAVING SUM(likes) > 10000;

    /* Aici combin tabelul abia facut inapoi cu baza de la colega */
    /* practic un INNER JOIN bazat pe nume autor (cerinta bifata) */
    CREATE TABLE WORK.TIKTOK_FINAL AS
    SELECT A.author, A.likes, A.plays, A.Viral_Flag, B.cate_clipuri
    FROM WORK.TIKTOK_CLEAN A
    INNER JOIN WORK.TOP_CREATORI B
    ON A.author = B.author
    ORDER BY A.likes DESC;
QUIT;


/* 8. Proceduri de raportare (PROC REPORT pe care o aratam in pdf)*/
PROC REPORT DATA=WORK.TOP_CREATORI NOWD HEADLINE CENTER;
    TITLE 'Raport Centralizat - Creatorii de top pe care putem miza';
    COLUMN author cate_clipuri like_uri_totale;
    
    /* formatari sa dea bine la ochii profului, cum ne-a aratat    */
    DEFINE author / DISPLAY 'Creatorul vizat' FORMAT=$30. WIDTH=20;
    DEFINE cate_clipuri / ANALYSIS SUM 'Total clipuri in tabel' FORMAT=COMMA8.;
    DEFINE like_uri_totale / ANALYSIS SUM 'Like-uri stranse per total' FORMAT=COMMA12.;
RUN;


/* 9. Proceduri statistice (am ales MEANS si CORR, minim 2 sa fie)*/

/* Prima chestie: calculam valorile de top/avg in fc de viral      */
PROC MEANS DATA=WORK.TIKTOK_FINAL N MEAN MIN MAX MAXDEC=2;
    TITLE 'Ce inseamna sa fii viral? (Statistici din MEAN)';
    CLASS Viral_Flag; /* Asta grupeaza statistica dupa variabila asta  */
    VAR likes plays cate_clipuri;
    FORMAT likes eng_level.; /* CERINTA 2: folosirea formatului definit de colega */
RUN;

/* A doua: sa ne dam seama de unde trag aprecierile                */
PROC CORR DATA=WORK.TIKTOK_FINAL PEARSON;
    TITLE 'Corelatii Pearson intre variabilele importante';
    VAR likes plays cate_clipuri;
    WITH likes; /* Testez influenta fata de numarul de aprecieri   */
RUN;


/* 10. Generarea de Grafice (PROC SGPLOT) normal si combinat      */

/* Primul este un grafic de bare normal. Setam culori ca sa atraga atetntia */
PROC SGPLOT DATA=WORK.TOP_CREATORI;
    TITLE "Distributia celor mai urmariti influenceri din set (BarChart)";
    VBAR author / RESPONSE=like_uri_totale CATEGORYORDER=RESPDESC FILLATTRS=(COLOR=CX0072B2);
    XAXIS LABEL='Cine este creatorul de fapt?';
    YAXIS LABEL='Total aprecieri';
RUN;

/* Al doilea e scatterplot. E bun pt regressia de la punctul de python */
PROC SGPLOT DATA=WORK.TIKTOK_CLEAN;
    TITLE "Cat de imprastiate sunt clipurile in baza de date (Viz vs Like)";
    SCATTER X=plays Y=likes / GROUP=Viral_Flag MARKERATTRS=(SYMBOL=CircleFilled);
    KEYLEGEND / TITLE="Prag viral (1 = da / 0 = inca nu)";
RUN;

