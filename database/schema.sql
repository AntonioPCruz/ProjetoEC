-- 1. Main Disease table
CREATE TABLE IF NOT EXISTS diseases (
    disease_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- 2. Symptoms and their severity weights
CREATE TABLE IF NOT EXISTS symptoms (
    symptom_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    severity_weight INT
);

-- 3. Mapping Disease to Symptoms (Many-to-Many)
CREATE TABLE IF NOT EXISTS disease_symptoms (
    disease_id INT REFERENCES diseases(disease_id),
    symptom_id INT REFERENCES symptoms(symptom_id),
    PRIMARY KEY (disease_id, symptom_id)
);

-- 4. Precautions for each disease
CREATE TABLE IF NOT EXISTS disease_precautions (
    precaution_id SERIAL PRIMARY KEY,
    disease_id INT REFERENCES diseases(disease_id),
    precaution TEXT NOT NULL
);

-- Tabela para Estatísticas Globais de Saúde
CREATE TABLE IF NOT EXISTS global_health_stats (
    stat_id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    disease_name VARCHAR(255) NOT NULL,
    disease_category VARCHAR(100),
    prevalence_rate DECIMAL(5,2),
    incidence_rate DECIMAL(5,2),
    mortality_rate DECIMAL(5,2),
    age_group VARCHAR(50),
    gender VARCHAR(20),
    population_affected INT,
    healthcare_access_pct DECIMAL(5,2),
    doctors_per_1000 DECIMAL(5,2),
    hospital_beds_per_1000 DECIMAL(5,2),
    treatment_type VARCHAR(100),
    average_treatment_cost_usd DECIMAL(12,2),
    availability_vaccines_treatment VARCHAR(10),
    recovery_rate DECIMAL(5,2),
    dalys INT,
    improvement_5yr_pct DECIMAL(5,2),
    per_capita_income_usd DECIMAL(12,2),
    education_index DECIMAL(4,3),
    urbanization_rate_pct DECIMAL(5,2),
    -- Unique constraint para evitar duplicados se correres o script várias vezes
    UNIQUE(country, year, disease_name, age_group, gender)
);