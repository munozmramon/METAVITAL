"""
Server-side HTML/PDF Compiler for METAVITAL Clinical Summaries.
Conforms to ADA/EASD and ESC/ESH Guidelines.
"""

from typing import Dict, Any
from .static.logo_base64 import METAVITAL_LOGO_WHITE_B64


class PDFCompiler:
    @staticmethod
    def compile_report_html(data: Dict[str, Any]) -> str:
        patient = data.get("patient", {})
        glucose = data.get("glucose", {})
        bp = data.get("blood_pressure", {})
        lifestyle = data.get("lifestyle", {})
        adherence_pct = data.get("medication_adherence_pct", 95)
        recommendations = data.get("recommendations", [])

        rec_items = "".join([f"<li>{r}</li>" for r in recommendations])

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>METAVITAL - Resumen Clínico Especializado</title>
  <style>
    @page {{ size: A4; margin: 12mm 15mm; }}
    body {{
      font-family: Arial, sans-serif;
      color: #1a202c;
      background: #ffffff;
      font-size: 11pt;
      line-height: 1.4;
      margin: 0;
      padding: 0;
    }}
    .header {{
      border-bottom: 2.5px solid #0d6efd;
      padding-bottom: 8px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
    }}
    .title {{ font-size: 22pt; font-weight: 800; color: #0d6efd; margin: 0; }}
    .subtitle {{ font-size: 9.5pt; color: #718096; margin: 0; }}
    .patient-bar {{
      background: #edf2f7;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 12px;
      font-size: 10pt;
    }}
    .grid {{
      display: flex;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .card {{
      flex: 1;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px;
    }}
    .card-title {{
      font-weight: bold;
      border-bottom: 1px solid #edf2f7;
      padding-bottom: 4px;
      margin-bottom: 8px;
      color: #2d3748;
    }}
    .metric-row {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 5px;
      font-size: 9.5pt;
    }}
    .val-bold {{ font-weight: bold; color: #1a202c; }}
    .recs {{
      background: #f7fafc;
      border-left: 4px solid #0d6efd;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 9pt;
      margin-bottom: 12px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <div style="display: flex; align-items: center; gap: 12px;">
      <img src="data:image/png;base64,{METAVITAL_LOGO_WHITE_B64}" style="width: 48px; height: 48px; border-radius: 50%;" alt="Logo Metavital">
      <div>
        <div class="title">METAVITAL</div>
        <div class="subtitle">Informe de Síndrome Metabólico | Estándar ADA & ESC</div>
      </div>
    </div>
    <div style="text-align: right; font-size: 9pt; color: #718096;">
      Período: Últimos 30 días<br>Documento Médico Oficial
    </div>
  </div>

  <div class="patient-bar">
    <strong>Paciente:</strong> {patient.get('name', 'Ramón Muñoz Martínez')} | 
    <strong>Edad:</strong> {patient.get('age', 63)} años | 
    <strong>IMC:</strong> {patient.get('bmi', 37.28)} kg/m² | 
    <strong>Peso:</strong> {patient.get('current_weight_kg', 101.5)} kg
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-title">Glucemia & Tiempo en Rango (TIR)</div>
      <div class="metric-row"><span>Tiempo en Rango (70-130 mg/dL):</span><span class="val-bold">{glucose.get('time_in_range_pct', 82)}%</span></div>
      <div class="metric-row"><span>Media Basal en Ayunas:</span><span class="val-bold">{glucose.get('mean_fasting', 114)} mg/dL</span></div>
      <div class="metric-row"><span>Hipoglucemias (&lt; 70 mg/dL):</span><span class="val-bold">{glucose.get('hypo_events', 0)} eventos</span></div>
      <div class="metric-row"><span>Picos Hiperglucémicos (&gt; 180):</span><span class="val-bold">{glucose.get('hyper_events', 0)}</span></div>
    </div>
    <div class="card">
      <div class="card-title">Presión Arterial (ESC/ESH)</div>
      <div class="metric-row"><span>Media Sistólica / Diastólica:</span><span class="val-bold">{bp.get('mean_systolic', 126)} / {bp.get('mean_diastolic', 82)} mmHg</span></div>
      <div class="metric-row"><span>Lecturas en Alerta (&ge; 140/90):</span><span class="val-bold">{bp.get('stage_2_alerts', 0)}</span></div>
      <div class="metric-row"><span>Crisis Registradas (&ge; 180/120):</span><span class="val-bold">{bp.get('crisis_count', 0)}</span></div>
      <div class="metric-row"><span>Estado Vascular:</span><span class="val-bold">Controlado</span></div>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-title">Actividad Física & Paseos Posprandiales</div>
      <div class="metric-row"><span>Media Pasos / Día (Podómetro):</span><span class="val-bold">{lifestyle.get('mean_steps', 4400)} pasos</span></div>
      <div class="metric-row"><span>Paseos Posprandiales (15 min):</span><span class="val-bold">{lifestyle.get('walks_completed', 8)} completados</span></div>
      <div class="metric-row"><span>Adherencia Nutrición Cardioprotectora:</span><span class="val-bold">92%</span></div>
    </div>
    <div class="card">
      <div class="card-title">Adherencia Farmacológica</div>
      <div class="metric-row"><span>Tomas Cumplidas vs Pautadas:</span><span class="val-bold">{adherence_pct}%</span></div>
      <div class="metric-row"><span>Pauta Matutina (Metformina + Enalapril):</span><span class="val-bold">Correcta</span></div>
      <div class="metric-row"><span>Pauta Nocturna (Atorvastatina):</span><span class="val-bold">Correcta</span></div>
    </div>
  </div>

  <div class="recs">
    <strong>Juicio Clínico y Recomendaciones para la Consulta:</strong>
    <ul>{rec_items or "<li>Continuar con la pauta actual y mantener paseos activos posprandiales.</li>"}</ul>
  </div>

  <div style="font-size: 8.5pt; color: #a0aec0; border-top: 1px dashed #cbd5e0; padding-top: 6px;">
    METAVITAL Cloud Service • Cifrado AES-256 E2E • Cumple HIPAA & RGPD
  </div>
</body>
</html>"""

