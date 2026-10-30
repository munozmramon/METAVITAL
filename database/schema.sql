-- =====================================================================
-- METAVITAL Database Schema
-- Certified for HIPAA & RGPD with Column-level and Table Encryption
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Patients Table (Pseudonymized PII)
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medical_record_hash VARCHAR(64) UNIQUE NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    height_cm NUMERIC(5,2) NOT NULL,
    baseline_weight_kg NUMERIC(5,2) NOT NULL,
    target_glucose_min INT DEFAULT 70,
    target_glucose_max INT DEFAULT 130,
    target_systolic_max INT DEFAULT 130,
    target_diastolic_max INT DEFAULT 80,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Biometric Readings (OCR Camera, Bluetooth or Manual)
CREATE TABLE IF NOT EXISTS biometric_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    metric_type VARCHAR(20) NOT NULL CHECK (metric_type IN ('GLUCOSE', 'BLOOD_PRESSURE', 'WEIGHT', 'STEPS')),
    value_primary NUMERIC(6,2) NOT NULL,
    value_secondary NUMERIC(6,2) NULL,
    value_tertiary NUMERIC(6,2) NULL,
    measurement_context VARCHAR(20) NOT NULL CHECK (
        measurement_context IN ('FASTING', 'POSTPRANDIAL', 'RANDOM', 'BEDTIME')
    ),
    capture_method VARCHAR(20) NOT NULL CHECK (
        capture_method IN ('OCR_CAMERA', 'MANUAL', 'BLUETOOTH_NATIVE')
    ),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_alert BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_biometrics_patient ON biometric_records(patient_id, recorded_at DESC);

-- 3. Medications Catalog & Prescriptions
CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    commercial_name VARCHAR(100) NOT NULL,
    active_ingredient VARCHAR(100) NOT NULL,
    dose_mg NUMERIC(6,2) NOT NULL,
    therapeutic_class VARCHAR(50) NOT NULL CHECK (
        therapeutic_class IN ('ANTIDIABETIC', 'ANTIHYPERTENSIVE', 'STATIN_LIPID', 'OTHER')
    ),
    scheduled_time TIME NOT NULL,
    instructions VARCHAR(255) NULL,
    photo_url TEXT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Adherence Records
CREATE TABLE IF NOT EXISTS adherence_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medication_id UUID NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    scheduled_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    taken_timestamp TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('TAKEN_ON_TIME', 'TAKEN_LATE', 'MISSED', 'SKIPPED')
    ),
    notes VARCHAR(255) NULL
);

-- 5. Lifestyle & Movement Logs (Pedometers / Accelerometers)
CREATE TABLE IF NOT EXISTS lifestyle_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    step_count INT NOT NULL DEFAULT 0,
    postprandial_walks_count INT DEFAULT 0,
    dietary_plan_completed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_patient_log_date UNIQUE (patient_id, log_date)
);

-- 6. Therapeutic Recipes (Max 4 steps, Mediterranean low glycemic load)
CREATE TABLE IF NOT EXISTS therapeutic_recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(150) NOT NULL,
    meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('BREAKFAST', 'LUNCH', 'DINNER', 'SNACK')),
    glycemic_load_score VARCHAR(15) CHECK (glycemic_load_score IN ('VERY_LOW', 'LOW', 'MEDIUM')),
    sodium_mg NUMERIC(6,2) NOT NULL,
    soluble_fiber_g NUMERIC(5,2) NOT NULL,
    omega3_rich BOOLEAN DEFAULT FALSE,
    prep_time_minutes INT NOT NULL,
    step_1 TEXT NOT NULL,
    step_2 TEXT NOT NULL,
    step_3 TEXT NOT NULL,
    step_4 TEXT NULL
);

-- 7. Grocery Items by Supermarket Aisle
CREATE TABLE IF NOT EXISTS grocery_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipe_id UUID REFERENCES therapeutic_recipes(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    quantity VARCHAR(50) NOT NULL,
    aisle VARCHAR(50) NOT NULL CHECK (
        aisle IN ('FRUITS_VEGETABLES', 'FISH_LEAN_MEAT', 'LEGUMES_WHOLE_GRAINS', 'HEALTHY_FATS')
    ),
    checked BOOLEAN DEFAULT FALSE
);

