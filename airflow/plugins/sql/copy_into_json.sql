USE ROLE {{ params.role }};
USE WAREHOUSE {{ params.warehouse }};
USE SCHEMA {{ params.database }}.{{ params.schema }};
COPY INTO JSON_RAW(JSON_DATA, FILENAME, LOAD_DATE)
FROM (
    SELECT T.*,
        METADATA$FILENAME,
        regexp_substr(
            METADATA$FILENAME,
            '([0-9]{4}-[0-9]{2}-[0-9]{2})'
        ) as LOAD_DATE
    FROM @BESTBUY_STAGE/bestbuy/products/categories T
)
PATTERN = '.*/{{ ds }}.json'
FILE_FORMAT = BESTBUY_JSON_FILE_FORMAT;