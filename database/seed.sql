-- =====================================================================
-- METAVITAL Seed Data: Sample Patient, Metrics, Meds, Recipes
-- =====================================================================

INSERT INTO patients (id, medical_record_hash, birth_date, gender, height_cm, baseline_weight_kg)
VALUES ('a1b2c3d4-e5f6-7890-1234-56789abcdef0', 'hash_sha256_patient_ramon_munoz_001', '1963-04-12', 'MALE', 165.0, 101.5)
ON CONFLICT (id) DO NOTHING;

INSERT INTO medications (id, patient_id, commercial_name, active_ingredient, dose_mg, therapeutic_class, scheduled_time, instructions)
VALUES 
('b1b2c3d4-e5f6-7890-1234-56789abcdef1', 'a1b2c3d4-e5f6-7890-1234-56789abcdef0', 'Dianben', 'Metformina', 850, 'ANTIDIABETIC', '08:30:00', 'Junto con el desayuno.'),
('b1b2c3d4-e5f6-7890-1234-56789abcdef2', 'a1b2c3d4-e5f6-7890-1234-56789abcdef0', 'Renitec', 'Enalapril', 20, 'ANTIHYPERTENSIVE', '09:00:00', 'Con un vaso de agua.'),
('b1b2c3d4-e5f6-7890-1234-56789abcdef3', 'a1b2c3d4-e5f6-7890-1234-56789abcdef0', 'Cardyl', 'Atorvastatina', 20, 'STATIN_LIPID', '21:30:00', 'Por la noche tras cenar.')
ON CONFLICT (id) DO NOTHING;

INSERT INTO therapeutic_recipes (id, title, meal_type, glycemic_load_score, sodium_mg, soluble_fiber_g, omega3_rich, prep_time_minutes, step_1, step_2, step_3, step_4)
VALUES
('c1b2c3d4-e5f6-7890-1234-56789abcdef1', 'Salmón Salvaje con Brócoli al Vapor y AOVE', 'LUNCH', 'VERY_LOW', 120, 4.8, TRUE, 12,
 'Cortar el brócoli en ramilletes pequeños.',
 'Disponer brócoli y salmón en estuche de vapor o sartén con tapa.',
 'Cocinar al vapor 8 minutos a fuego medio.',
 'Servir aliñado con una cucharada de Aceite de Oliva Virgen Extra y limón.'),
('c1b2c3d4-e5f6-7890-1234-56789abcdef2', 'Salteado Mediterráneo de Garbanzos con Espinacas', 'LUNCH', 'LOW', 180, 7.5, FALSE, 10,
 'Enjuagar garbanzos cocidos bajo el grifo para retirar exceso de sodio.',
 'Dorar un ajo laminado en una sartén con AOVE durante 1 minuto.',
 'Añadir espinacas frescas hasta que reduzcan de volumen.',
 'Saltear los garbanzos con pimentón dulce durante 3 minutos.')
ON CONFLICT (id) DO NOTHING;

