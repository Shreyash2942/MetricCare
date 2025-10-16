CREATE TABLE IF NOT EXISTS mc_de_4_takeo_shreyash.gold_readmission_rate
WITH (
  format = 'PARQUET',
  external_location = 's3://mc-de-4-takeo-project/shreyash/database/goldtable/gold_readmission_rate'
) AS(
    SELECT
        patientid,
        encounterid,
        participantstartperiod,
        participantendperiod,
        date_diff('day',
            LAG(participantendperiod) over (partition BY patientid order by participantendperiod),
            participantstartperiod
        ) as days_since_last_discharge,
        CASE
            WHEN date_diff('day',
                LAG(participantendperiod) over (partition BY patientid order by participantendperiod),
                participantstartperiod
            ) >=30 THEN TRUE ELSE FALSE
            END as is_readmission
        FROM silverencounter
);


SELECT * FROM gold_readmission_rate;

SELECT patientid,
    count(patientid)*100 AS num_time_readmission
    FROM gold_readmission_rate
    WHERE is_readmission=TRUE
    GROUP BY patientid;

with patient_encouter AS (
    SELECT patientid,count(patientid) as patient_count FROM gold_readmission_rate GROUP by patientid
)SELECT g.patientid,
    (count(g.patientid)*100/MAX(e.patient_count)) AS patient_readmission_rate
    FROM gold_readmission_rate g join patient_encouter e
    on g.patientid=e.patientid
    WHERE g.is_readmission=TRUE
    GROUP BY g.patientid;
