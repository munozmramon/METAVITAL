# METAVITAL: Documento de Arquitectura de Software y Seguridad

## 1. Visión General
**METAVITAL** es una plataforma móvil nativa para la gestión integral del síndrome metabólico (diabetes tipo 2/prediabetes, hipertensión arterial, dislipemia aterogénica, sobrepeso y sedentarismo).
Diseñada bajo el paradigma **Offline-First**, **Edge-AI** y **Zero-Knowledge Privacy**, garantiza operatividad total sin conexión a internet y máxima protección de datos de salud (PHI).

---

## 2. Diagrama de Arquitectura

```
+---------------------------------------------------------------------------------+
|                              CAPA DISPOSITIVO (EDGE)                            |
|                                                                                 |
|  [ Vistas Accesibles (WCAG AAA) ]                                               |
|  - Hoy (2-tap entry)                                                            |
|  - Mis Métricas (TIR 70-130)                                                    |
|  - Nutrición & Compra (Pasillos)                                                |
|  - Informe Médico (PDF 1 pág)                                                   |
|          |                                                                      |
|          v                                                                      |
|  [ Motor de Reglas Clínicas Local ] <---> [ OCR Engine Local (ML Kit / Vision) ]|
|  (Triage ADA / ESC en < 50ms)             (Lectura LCD 7 segmentos sin cloud)  |
|          |                                                                      |
|          v                                                                      |
|  [ Base de Datos Local Cifrada: SQLCipher AES-256 ]                             |
|  (Clave gestionada en iOS Keychain / Android Hardware Keystore)                 |
+---------------------------------------+-----------------------------------------+
                                        | (Sincronización TLS 1.3 / mTLS)
                                        v
+---------------------------------------------------------------------------------+
|                                 CAPA CLOUD BACKEND                              |
|                                                                                 |
|  [ API Gateway (Envoy / Kong) ] -> WAF + Rate Limiter                           |
|          |                                                                      |
|          v                                                                      |
|  [ FastAPI Core Microservices ]                                                 |
|  - Ingesta biométrica disociada (PII / PHI separados)                           |
|  - Compilador de Informes Médicos PDF/A-1a                                      |
|  - Motor de Correlación Farmacológica Avanzada                                  |
|          |                                                                      |
|          v                                                                      |
|  [ PostgreSQL 16 + Citus ]                                                      |
|  (Cifrado en reposo TDE, Row Level Security, Auditoría inmutable append-only)   |
+---------------------------------------------------------------------------------+
```

---

## 3. Componentes Clave

### 3.1 Motor de Reconocimiento Óptico (OCR) On-Device
* **Tecnología:** Google ML Kit Text Recognition v2 (Android) y Apple Vision (iOS).
* **Preprocesamiento:** Umbralización adaptativa (*Adaptive Binarization*), corrección de perspectiva de pantalla LCD/OLED y filtro morfológico para dígitos de 7 segmentos.
* **Algoritmo de Extracción Determinista:**
  * Si detecta sufijo `mg/dL` o número único entre 20 y 600 $\rightarrow$ `GLUCOSE`.
  * Si detecta patrón de 2 o 3 valores apilados o barra `/` (ej. 120/80 con pulso 72) $\rightarrow$ `BLOOD_PRESSURE` (Sistólica, Diastólica y Pulso).
* **Privacidad:** La captura de la cámara nunca se transmite al servidor; solo viajan los números extraídos y validados tras la confirmación táctil del paciente.

### 3.2 Sensor Pasivo de Pasos y Paseos Posprandiales
* **Tecnología:** `CMPedometer` (iOS) y `SensorManager.SENSOR_TYPE_STEP_COUNTER` (Android) con *hardware batching* que no despierta la CPU principal, consumiendo menos del 1% de batería por día.
* **Lógica Posprandial:** Detecta la ventana de 20 a 75 minutos post-comida y sugiere un paseo suave de 10-15 minutos, modulando la translocación de transportadores GLUT4 no dependientes de insulina para mitigar la excursión glucémica.

### 3.3 Seguridad, Cifrado y Cumplimiento Normativo (HIPAA / RGPD)
1. **Pseudonimización Estricta (RGPD Art. 32):** El identificador del paciente en la base de datos de salud es un hash `Argon2id` disociado de sus datos identificativos civiles (PII).
2. **Cifrado en Reposo:** Cifrado simétrico de página completa `AES-256-CBC` mediante SQLCipher en el dispositivo móvil y `TDE` con llaves rotadas en PostgreSQL.
3. **Cifrado en Tránsito:** TLS 1.3 con *Certificate Pinning* en la aplicación cliente para erradicar vectores MitM.
4. **Pistas de Auditoría:** Inmutables, con firma SHA-256 por cada acceso médico al informe del paciente.

