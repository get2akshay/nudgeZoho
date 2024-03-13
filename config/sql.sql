/* SELECT
                ts/1000 AS time,
                str_v,
                (('x' || REPLACE(LEFT(str_v, 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS x_axis,
                (('x' || REPLACE(SUBSTRING(str_v FROM 10 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS y_axis,
                (('x' || REPLACE(SUBSTRING(str_v FROM 19 FOR 8), '-', ''))::bit(32)::integer * 9.8 * 0.00390625) AS z_axis
            FROM
                ts_kv
            WHERE
                entity_id = '58a03740-7caf-11ee-9304-e17cb189e218'
            AND key = 53
            LIMIT 1 */

SELECT
    most_common_entity_id
    FROM (
        SELECT
            entity_id AS most_common_entity_id,
            ROW_NUMBER() OVER (PARTITION BY str_v ORDER BY COUNT(*) DESC) AS rn
        FROM
            ts_kv
        WHERE
            str_v SIMILAR TO '00:8c:10:30:01:4c'
        GROUP BY
            str_v, entity_id
    ) AS subquery
    WHERE
        rn = 1
    LIMIT 2

