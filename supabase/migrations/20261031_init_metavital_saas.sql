-- ========================================================
-- METAVITAL SAAS: MIGRACIÓN INICIAL COMPLETA (POSTGRESQL + RLS)
-- ========================================================

-- 1. Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabla de Perfiles Públicos (vinculada a auth.users de Supabase)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT,
    birth_date DATE,
    height_cm NUMERIC(5,2),
    assigned_doctor_name TEXT DEFAULT 'Dr. Nicolás Cobo Fernández',
    assigned_doctor_phone TEXT DEFAULT '+34 600 000 000',
    assigned_doctor_email TEXT,
    assigned_center TEXT DEFAULT 'Hospital Universitario de Jaén / C.S. Baeza',
    medical_notes TEXT,
    subscription_status TEXT DEFAULT 'active' CHECK (subscription_status IN ('inactive', 'active', 'past_due', 'trial', 'cancelled')),
    stripe_customer_id TEXT UNIQUE,
    stripe_subscription_id TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Tabla de Mediciones Biométricas Diarias (Glucosa, Tensión, Peso, Pasos)
CREATE TABLE IF NOT EXISTS public.biometric_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL CHECK (metric_type IN ('GLUCOSE', 'BP', 'WEIGHT', 'STEPS')),
    val_primary NUMERIC(7,2) NOT NULL, -- Glucosa (mg/dL), Sistólica (mmHg), Peso (kg), Pasos
    val_secondary NUMERIC(7,2),         -- Diastólica (mmHg) para BP
    val_tertiary NUMERIC(7,2),          -- Pulso (lpm)
    notes TEXT,
    device_source TEXT DEFAULT 'manual', -- 'manual', 'camera_ocr', 'bluetooth'
    measured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Pautas de Medicación y Registro de Tomas
CREATE TABLE IF NOT EXISTS public.medication_prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    drug_name TEXT NOT NULL,
    active_ingredient TEXT,
    dosage TEXT NOT NULL,
    schedule_time TIME NOT NULL,
    timing_label TEXT NOT NULL, -- 'Desayuno', 'Comida', 'Cena', 'Noche'
    is_active BOOLEAN DEFAULT TRUE,
    clinical_purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.medication_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    prescription_id UUID REFERENCES public.medication_prescriptions(id) ON DELETE CASCADE,
    taken_at TIMESTAMPTZ DEFAULT NOW(),
    date_logged DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'taken' CHECK (status IN ('taken', 'skipped', 'delayed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Diario de Ingesta Real y Auditoría Nutricional
CREATE TABLE IF NOT EXISTS public.daily_food_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    day_name TEXT NOT NULL, -- 'lunes', 'martes', etc.
    desayuno_text TEXT,
    comida_text TEXT,
    cena_text TEXT,
    audit_status TEXT CHECK (audit_status IN ('green', 'yellow', 'red')),
    audit_score INTEGER,
    audit_feedback JSONB, -- Factores protectores, alertas potasio/azúcar/sodio
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, log_date)
);

-- 6. Informes Médicos Mensuales Generados
CREATE TABLE IF NOT EXISTS public.monthly_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    period_month INTEGER NOT NULL,
    period_year INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    download_token UUID DEFAULT uuid_generate_v4(),
    token_expires_at TIMESTAMPTZ,
    sent_to_doctor_at TIMESTAMPTZ,
    doctor_email_sent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================================
-- ROW LEVEL SECURITY (RLS) - AISLAMIENTO TOTAL ENTRE USUARIOS
-- ========================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.biometric_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medication_prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medication_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_food_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.monthly_reports ENABLE ROW LEVEL SECURITY;

-- Políticas de Acceso Exclusivo por Usuario (auth.uid() = user_id)
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users manage own biometrics" ON public.biometric_readings;
CREATE POLICY "Users manage own biometrics" ON public.biometric_readings
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users manage own medications" ON public.medication_prescriptions;
CREATE POLICY "Users manage own medications" ON public.medication_prescriptions
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users manage own medication logs" ON public.medication_logs;
CREATE POLICY "Users manage own medication logs" ON public.medication_logs
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users manage own food logs" ON public.daily_food_logs;
CREATE POLICY "Users manage own food logs" ON public.daily_food_logs
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users view own reports" ON public.monthly_reports;
CREATE POLICY "Users view own reports" ON public.monthly_reports
    FOR SELECT USING (auth.uid() = user_id);

-- Trigger automático para crear perfil cuando un usuario se registra en Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, email, subscription_status)
  VALUES (
    new.id,
    COALESCE(new.raw_user_meta_data->>'full_name', 'Paciente MetaVital'),
    new.email,
    'active'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

