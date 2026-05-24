FILENAME REFFILE '/home/user/tiktok_merged_data_deduplicated.csv';

PROC IMPORT DATAFILE=REFFILE
    DBMS=CSV
    OUT=WORK.TIKTOK_RAW
    REPLACE;
    GETNAMES=YES;
RUN;

PROC FORMAT;
    VALUE eng_level
    0 - 50000 = 'Low Engagement'
    50001 - 500000 = 'Medium Engagement'
    500001 - HIGH = 'High Engagement';
RUN;

DATA WORK.TIKTOK_CLEAN (DROP=i);
    SET WORK.TIKTOK_RAW;

    WHERE author IS NOT MISSING;

    Author_Upper = UPCASE(author);

    ARRAY metrics(4) likes comments shares plays;
    DO i = 1 TO 4;
        IF metrics(i) = . THEN metrics(i) = 0;
    END;

    IF likes > 10000 THEN Viral_Flag = 1;
    ELSE Viral_Flag = 0;
RUN;
