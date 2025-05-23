SET SQL_SAFE_UPDATES = 0;
CREATE TABLE resume_matcher_data.jobs_data AS
SELECT *, 'Business Analyst' AS job_type FROM resume_matcher_data.business_analyst_jobs
UNION ALL
SELECT *, 'Data Analyst' AS job_type FROM resume_matcher_data.data_analyst_jobs
UNION ALL
SELECT *, 'Data Engineer' AS job_type FROM resume_matcher_data.data_engineer_jobs
UNION ALL
SELECT *, 'Data Scientist' AS job_type FROM resume_matcher_data.data_scientist_jobs;

CREATE TABLE resume_matcher_data.job_data (
    id int,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    salary VARCHAR(255),
    required_skills VARCHAR(255),
    job_type VARCHAR(255),
    url VARCHAR(2083)
);

INSERT INTO resume_matcher_data.job_data (id, title, company, location, salary, required_skills, job_type, url)
SELECT id, title, company, location, salary, required_skills, job_type, url FROM resume_matcher_data.all_jobs;

DROP TABLE resume_matcher_data.all_jobs;

SELECT count(*)
FROM resume_matcher_data.all_jobs
WHERE  TRIM(required_skills) = "";


UPDATE resume_matcher_data.all_jobs
SET required_skills = 'Unknown'
WHERE TRIM(required_skills) = "";

ALTER TABLE resume_matcher_data.all_jobs
ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE resume_matcher_data.job_data
ADD state VARCHAR(50);

UPDATE resume_matcher_data.job_data
SET state = 
    CASE 
        WHEN location LIKE '%, %' THEN SUBSTRING_INDEX(location, ', ', -1)
        ELSE SUBSTRING_INDEX(location, ',', -1)
    END;

UPDATE resume_matcher_data.job_data
SET state = 'US'
WHERE state = 'United States';

SELECT *
FROM resume_matcher_data.job_data;