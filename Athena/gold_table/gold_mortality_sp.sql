WITH patinet_condition AS (
    SELECT
        e.patientid,
        e.encounterid,
        e.participantstartperiod,
        e.participantendperiod,
        e.encountertype,
        c.code
    FROM
        silverencounter e
    JOIN silvercondition c
    ON e.patientid = c.patientid
    WHERE
        e.encountertype='Inpatient'
),
mortality AS (
    SELECT
        p.patient_id,
        c.code,
        CASE
            WHEN p.deceaseddatetime IS NOT NULL
                AND date_diff('day',p.deceaseddatetime,c.participantstartperiod)<=5478
            THEN 1 ELSE 0
        END AS dath_in_15years,
        date_diff('day',p.deceaseddatetime,c.participantstartperiod) AS date_diff_in_dath
    FROM
        silverpatients p
    JOIN
        patinet_condition c
    ON
        p.patient_id=c.patientid
)

SELECT
    code,
    count(*) AS total_case,
    sum(dath_in_15years) AS total_daths_in_15_years,
    (sum(dath_in_15years)*100/count(*)) AS mortality_rate
FROM mortality
group by code


