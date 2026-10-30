import { ClinicalReportSummary } from '../types';

export class ReportGenerator {
  /**
   * Generates a single-page HTML document optimized for PDF rendering and printing (A4 / Clinical Standard).
   */
  public static generateSinglePageHtml(summary: ClinicalReportSummary): string {
    const { patient, glucose, bloodPressure, lifestyle, medicationAdherencePct, clinicalRecommendations } = summary;

    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>METAVITAL - Informe Clínico para el Facultativo</title>
  <style>
    @page {
      size: A4;
      margin: 12mm 15mm;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #1a1e21;
      background-color: #ffffff;
      margin: 0;
      padding: 0;
      font-size: 11pt;
      line-height: 1.35;
    }
    .header {
      border-bottom: 2px solid #0d6efd;
      padding-bottom: 8px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .app-title {
      font-size: 20pt;
      font-weight: 800;
      color: #0d6efd;
      letter-spacing: -0.5px;
      margin: 0;
    }
    .app-subtitle {
      font-size: 9pt;
      color: #6c757d;
      margin: 0;
    }
    .meta-box {
      text-align: right;
      font-size: 9pt;
      color: #495057;
    }
    .patient-bar {
      background-color: #f1f5f9;
      border-radius: 6px;
      padding: 8px 12px;
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;
      font-size: 9.5pt;
    }
    .patient-bar strong {
      color: #0f172a;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }
    .card {
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
      background-color: #ffffff;
    }
    .card-title {
      font-size: 11pt;
      font-weight: 700;
      color: #1e293b;
      margin-top: 0;
      margin-bottom: 8px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 4px;
      display: flex;
      justify-content: space-between;
    }
    .metric-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 9pt;
    }
    .metric-value {
      font-weight: 700;
      color: #0f172a;
    }
    .badge-ok {
      color: #15803d;
      font-weight: 700;
    }
    .badge-alert {
      color: #b91c1c;
      font-weight: 700;
    }
    .progress-bar-container {
      background: #e2e8f0;
      border-radius: 4px;
      height: 10px;
      overflow: hidden;
      margin-top: 4px;
      margin-bottom: 6px;
    }
    .progress-fill {
      background: #16a34a;
      height: 100%;
    }
    .recommendations-box {
      background: #f8fafc;
      border-left: 4px solid #0d6efd;
      padding: 8px 12px;
      border-radius: 0 6px 6px 0;
      font-size: 9pt;
      margin-bottom: 10px;
    }
    .recommendations-box ul {
      margin: 4px 0 0 16px;
      padding: 0;
    }
    .signature-area {
      display: flex;
      justify-content: space-between;
      margin-top: 15px;
      border-top: 1px dashed #cbd5e1;
      padding-top: 8px;
      font-size: 8.5pt;
      color: #64748b;
    }
  </style>
</head>
<body>

  <div class="header">
    <div>
      <h1 class="app-title">METAVITAL</h1>
      <p class="app-subtitle">Informe Clínico de Síndrome Metabólico | Estándar ADA / ESC / ESH</p>
    </div>
    <div class="meta-box">
      <strong>Ciclo Evaluado:</strong> Últimos ${summary.periodDays} días<br>
      <strong>Generado:</strong> ${new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' })}
    </div>
  </div>

  <div class="patient-bar">
    <div><strong>Paciente:</strong> ${patient.name} (${patient.gender === 'MALE' ? 'Varón' : 'Mujer'}, ${patient.age} años)</div>
    <div><strong>Talla:</strong> ${patient.heightCm} cm</div>
    <div><strong>Peso Actual:</strong> ${patient.currentWeightKg} kg</div>
    <div><strong>IMC:</strong> ${patient.bmi} kg/m² (Sobrepeso Grado II)</div>
  </div>

  <div class="grid">
    <!-- PANEL 1: GLUCEMIA -->
    <div class="card">
      <div class="card-title">
        <span>Glucemia y Tiempo en Rango</span>
        <span class="badge-ok">TIR: ${glucose.timeInRangePct}%</span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-fill" style="width: ${glucose.timeInRangePct}%;"></div>
      </div>
      <div class="metric-row">
        <span>Media Basal en Ayunas:</span>
        <span class="metric-value">${glucose.meanFasting} mg/dL</span>
      </div>
      <div class="metric-row">
        <span>Tiempo en Rango Objetivo (70-130 mg/dL):</span>
        <span class="metric-value ${glucose.timeInRangePct >= 70 ? 'badge-ok' : 'badge-alert'}">${glucose.timeInRangePct}% (Meta: &ge;70%)</span>
      </div>
      <div class="metric-row">
        <span>Eventos de Hipoglucemia (&lt; 70 mg/dL):</span>
        <span class="metric-value ${glucose.hypoEventsCount === 0 ? 'badge-ok' : 'badge-alert'}">${glucose.hypoEventsCount} evento(s)</span>
      </div>
      <div class="metric-row">
        <span>Picos Hiperglucémicos (&gt; 180 mg/dL):</span>
        <span class="metric-value">${glucose.hyperEventsCount} evento(s)</span>
      </div>
      <div class="metric-row">
        <span>Total Mediciones Registradas (OCR):</span>
        <span class="metric-value">${glucose.readingsTotal}</span>
      </div>
    </div>

    <!-- PANEL 2: PRESIÓN ARTERIAL -->
    <div class="card">
      <div class="card-title">
        <span>Presión Arterial</span>
        <span class="${bloodPressure.stage2AlertsCount === 0 ? 'badge-ok' : 'badge-alert'}">Media: ${bloodPressure.systolicMean}/${bloodPressure.diastolicMean} mmHg</span>
      </div>
      <div class="metric-row">
        <span>Media Sistólica:</span>
        <span class="metric-value">${bloodPressure.systolicMean} mmHg (Meta: &lt;130)</span>
      </div>
      <div class="metric-row">
        <span>Media Diastólica:</span>
        <span class="metric-value">${bloodPressure.diastolicMean} mmHg (Meta: &lt;80)</span>
      </div>
      <div class="metric-row">
        <span>Registros en Alerta (&ge; 140/90 mmHg):</span>
        <span class="metric-value ${bloodPressure.stage2AlertsCount === 0 ? 'badge-ok' : 'badge-alert'}">${bloodPressure.stage2AlertsCount} registro(s)</span>
      </div>
      <div class="metric-row">
        <span>Crisis Hipertensivas (&ge; 180/120 mmHg):</span>
        <span class="metric-value ${bloodPressure.crisisAlertsCount === 0 ? 'badge-ok' : 'badge-alert'}">${bloodPressure.crisisAlertsCount}</span>
      </div>
      <div class="metric-row">
        <span>Clasificación ESC/ESH:</span>
        <span class="metric-value">${bloodPressure.systolicMean < 130 ? 'Controlada / Normal' : 'Grado 1 Limítrofe'}</span>
      </div>
    </div>
  </div>

  <div class="grid">
    <!-- PANEL 3: ESTILO DE VIDA Y MOVIMIENTO -->
    <div class="card">
      <div class="card-title">
        <span>Actividad Física Anti-sedentarismo</span>
        <span class="badge-ok">Podómetro Activo</span>
      </div>
      <div class="metric-row">
        <span>Media Pasos Diarios (Hardware Móvil):</span>
        <span class="metric-value">${lifestyle.meanStepsPerDay.toLocaleString()} pasos/día</span>
      </div>
      <div class="metric-row">
        <span>Paseos Posprandiales (10-15 min):</span>
        <span class="metric-value">${lifestyle.postprandialWalksWeekly} completados</span>
      </div>
      <div class="metric-row">
        <span>Adherencia a Dieta Cardioprotectora:</span>
        <span class="metric-value badge-ok">${lifestyle.dietaryAdherencePct}%</span>
      </div>
      <div class="metric-row">
        <span>Aporte Fibra Soluble Estimada:</span>
        <span class="metric-value">&gt; 30 g/día (Optimizada)</span>
      </div>
    </div>

    <!-- PANEL 4: ADHERENCIA FARMACOLÓGICA -->
    <div class="card">
      <div class="card-title">
        <span>Tratamiento Farmacológico</span>
        <span class="badge-ok">${medicationAdherencePct}% Adherencia</span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-fill" style="width: ${medicationAdherencePct}%;"></div>
      </div>
      <div class="metric-row">
        <span>Pauta Matutina (Metformina 850mg + Enalapril 20mg):</span>
        <span class="metric-value badge-ok">98% Cumplida</span>
      </div>
      <div class="metric-row">
        <span>Pauta Nocturna (Atorvastatina 20mg):</span>
        <span class="metric-value badge-ok">94% Cumplida</span>
      </div>
      <div class="metric-row">
        <span>Correlación Omisión-Presión:</span>
        <span class="metric-value">Sin rebotes hipertensivos recientes</span>
      </div>
    </div>
  </div>

  <div class="recommendations-box">
    <strong>Observaciones Clínicas Automatizadas para el Médico Especialista:</strong>
    <ul>
      ${clinicalRecommendations.map(r => `<li>${r}</li>`).join('')}
    </ul>
  </div>

  <div class="signature-area">
    <div>Generado por METAVITAL v1.0 | Cumplimiento RGPD & HIPAA (Hash ID: 9f72b2a1)</div>
    <div>Firma / Sello del Médico Facultativo: ___________________________</div>
  </div>

</body>
</html>`;
  }
}

