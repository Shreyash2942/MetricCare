WITH infection_cases AS (
    SELECT
        c.patientid,
        c.code
    FROM silvercondition c
    WHERE c.code IN ('E11.9', 'I10', 'J45.909', 'M54.5', 'F32.9')
),
inpatient_encounter AS (
    SELECT
        e.patientid,
        e.encounterid
    FROM silverencounter e
    WHERE
        encountertype ='Inpatient'
)

SELECT
    i.code AS infaction_type,
    COUNT(i.patientid) AS patient_with_infaction,
    COUNT(ie.patientid) AS number_of_inpatient,
    COUNT(i.patientid)*1000/((SELECT COUNT(patientid) FROM inpatient_encounter)) AS infaction_rate_per_1000
FROM
    inpatient_encounter ie
LEFT JOIN
    infection_cases i
    on ie.patientid=i.patientid
GROUP BY
    i.code
