"""
METAVITAL Interactive Web Simulator
Provides a high-fidelity interactive simulation of the mobile application
running directly in any desktop or mobile browser.
"""

def get_simulator_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>METAVITAL - Simulador de Experiencia Móvil</title>
  <style>
    :root {
      --primary: #0D6EFD;
      --primary-dark: #0A58CA;
      --success: #16A34A;
      --warning: #D97706;
      --danger: #DC2626;
      --bg: #F8FAFC;
      --card-bg: #FFFFFF;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --border: #E2E8F0;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }

    /* Mobile Device Frame */
    .phone-wrapper {
      width: 100%;
      max-width: 420px;
      height: 870px;
      background: #FFFFFF;
      border-radius: 42px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), 0 0 0 12px #334155;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }

    /* Status Bar */
    .status-bar {
      height: 34px;
      background: #FFFFFF;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 24px;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      border-bottom: 1px solid #F1F5F9;
    }

    /* App Screen Container */
    .screen-content {
      flex: 1;
      overflow-y: auto;
      background: var(--bg);
      padding: 16px;
    }

    /* Bottom Navigation Bar (4 tabs) */
    .bottom-nav {
      height: 72px;
      background: #FFFFFF;
      border-top: 1.5px solid var(--border);
      display: flex;
      justify-content: space-around;
      align-items: center;
      padding: 0 8px;
    }

    .nav-btn {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px 0;
      border-radius: 12px;
      transition: all 0.2s;
    }

    .nav-btn.active {
      background: #EFF6FF;
    }

    .nav-icon {
      font-size: 22px;
      margin-bottom: 3px;
    }

    .nav-label {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
    }

    .nav-btn.active .nav-label {
      color: var(--primary);
      font-weight: 900;
    }

    /* Cards */
    .card {
      background: var(--card-bg);
      border-radius: 16px;
      padding: 16px;
      margin-bottom: 14px;
      border: 1.5px solid var(--border);
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }

    .card-title {
      font-size: 17px;
      font-weight: 800;
      color: var(--text-main);
    }

    .card-subtitle {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .badge {
      font-size: 11px;
      font-weight: 800;
      padding: 4px 8px;
      border-radius: 6px;
      color: #FFFFFF;
      text-transform: uppercase;
    }

    /* Profile Card Header */
    .profile-card {
      background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
      border: 2px solid #E2E8F0;
    }

    .profile-stats-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      background: #F1F5F9;
      padding: 12px;
      border-radius: 12px;
      margin: 10px 0;
    }

    .profile-stat-box {
      font-size: 12px;
      color: var(--text-muted);
    }

    .profile-stat-box strong {
      display: block;
      font-size: 16px;
      color: var(--text-main);
      font-weight: 900;
      margin-top: 2px;
    }

    .btn-row-profile {
      display: flex;
      gap: 8px;
    }

    .btn-scale-quick {
      flex: 1.3;
      background: var(--success);
      color: #FFFFFF;
      border: none;
      padding: 10px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 12px;
      cursor: pointer;
    }

    .btn-edit-profile {
      flex: 1;
      background: var(--text-main);
      color: #FFFFFF;
      border: none;
      padding: 10px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 12px;
      cursor: pointer;
    }

    /* Biometric Action Buttons (3 buttons) */
    .btn-action-row {
      display: flex;
      gap: 8px;
    }

    .btn-bio {
      flex: 1;
      background: #EFF6FF;
      border: 2px solid #BFDBFE;
      border-radius: 14px;
      padding: 12px 6px;
      text-align: center;
      cursor: pointer;
      transition: transform 0.1s;
    }

    .btn-bio:active {
      transform: scale(0.97);
    }

    .btn-bio-red {
      background: #FEF2F2;
      border-color: #FECACA;
    }

    .btn-bio-green {
      background: #F0FDF4;
      border-color: #BBF7D0;
    }

    .btn-bio-icon {
      font-size: 26px;
      margin-bottom: 4px;
    }

    .btn-bio-title {
      font-size: 12px;
      font-weight: 900;
      color: var(--text-main);
    }

    .btn-bio-val {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Medication Item */
    .med-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #F8FAFC;
      border: 1.5px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 8px;
    }

    .med-item.taken {
      background: #F0FDF4;
      border-color: #BBF7D0;
    }

    .med-info h4 {
      font-size: 15px;
      color: var(--text-main);
      font-weight: 800;
    }

    .med-info p {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .btn-take {
      background: var(--primary);
      color: #FFFFFF;
      border: none;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 13px;
      cursor: pointer;
    }

    .btn-take.done {
      background: #DCFCE7;
      color: var(--success);
      cursor: default;
    }

    /* Progress bar */
    .progress-bg {
      height: 10px;
      background: #E2E8F0;
      border-radius: 5px;
      overflow: hidden;
      margin: 8px 0;
    }

    .progress-fill {
      height: 100%;
      background: #8B5CF6;
      width: 71%;
      transition: width 0.3s;
    }

    /* Modal Overlay */
    .modal-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 23, 42, 0.75);
      display: none;
      justify-content: flex-end;
      z-index: 100;
    }

    .modal-box {
      background: #FFFFFF;
      width: 100%;
      border-radius: 28px 28px 0 0;
      padding: 24px;
      animation: slideUp 0.25s ease-out;
      max-height: 85%;
      overflow-y: auto;
    }

    @keyframes slideUp {
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    }

    /* Camera viewport simulator */
    .camera-frame {
      height: 180px;
      background: #0F172A;
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      margin-bottom: 16px;
      border: 2px dashed #38BDF8;
      color: #FFFFFF;
      text-align: center;
      padding: 10px;
    }

    .camera-frame h3 {
      font-size: 15px;
      margin-bottom: 4px;
    }

    .camera-frame p {
      font-size: 12px;
      color: #94A3B8;
    }

    .btn-primary {
      width: 100%;
      background: var(--primary);
      color: #FFFFFF;
      border: none;
      padding: 14px;
      border-radius: 12px;
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
    }

    .btn-success {
      background: var(--success);
    }

    /* Form Controls */
    .form-group {
      margin-bottom: 12px;
    }

    .form-group label {
      display: block;
      font-size: 13px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 4px;
    }

    .form-control {
      width: 100%;
      padding: 10px 12px;
      border: 1.5px solid var(--border);
      border-radius: 8px;
      font-size: 14px;
      color: var(--text-main);
      background: #F8FAFC;
    }

    .form-row-2 {
      display: flex;
      gap: 10px;
    }

    /* Grocery list styling */
    .aisle-group {
      margin-bottom: 14px;
      background: #FFFFFF;
      border: 1.5px solid var(--border);
      border-radius: 12px;
      padding: 12px;
    }

    .aisle-head {
      font-size: 14px;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .grocery-row {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid #F1F5F9;
      cursor: pointer;
    }

    .grocery-row:last-child {
      border-bottom: none;
    }

    .grocery-row.checked span {
      text-decoration: line-through;
      color: #94A3B8;
    }

    /* Alert Banner */
    .alert-banner {
      background: #FEF3C7;
      border-left: 4px solid #D97706;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 14px;
      display: none;
    }

    .alert-banner.show {
      display: block;
    }

    .alert-banner h5 {
      color: #92400E;
      font-size: 14px;
      font-weight: 800;
      margin-bottom: 4px;
    }

    .alert-banner p {
      color: #78350F;
      font-size: 12.5px;
      line-height: 17px;
    }
  </style>
</head>
<body>

  <div class="phone-wrapper">
    <!-- Status Bar -->
    <div class="status-bar">
      <span>09:41</span>
      <span>METAVITAL 4G 🔋 98%</span>
    </div>

    <!-- Active Screen: Hoy -->
    <div id="tab-hoy" class="screen-content tab-view">
      <!-- Clinical Alert Container -->
      <div id="clinical-alert-banner" class="alert-banner">
        <h5 id="alert-title">⚠️ ALERTA CLÍNICA</h5>
        <p id="alert-msg">Instrucciones inmediatas.</p>
      </div>

      <!-- TARJETA 0: DATOS DE LA PERSONA Y ESTADO PONDERAL -->
      <div class="card profile-card">
        <div class="card-header">
          <div>
            <div id="card-fullname" class="card-title">Ramón García Fernández</div>
            <div id="card-subdetails" class="card-subtitle">58 años • Estatura: 172 cm</div>
          </div>
          <span id="badge-bmi-category" class="badge" style="background: var(--warning);">Sobrepeso</span>
        </div>

        <div class="profile-stats-grid">
          <div class="profile-stat-box">
            <span>Peso Actual:</span>
            <strong><span id="disp-profile-weight">84.5</span> kg</strong>
          </div>
          <div class="profile-stat-box">
            <span>Índice Masa Corporal:</span>
            <strong>IMC <span id="disp-profile-bmi">28.56</span></strong>
          </div>
        </div>

        <div class="btn-row-profile">
          <button class="btn-scale-quick" onclick="openCaptureModal('WEIGHT')">
            📸 FOTO BÁSCULA
          </button>
          <button class="btn-edit-profile" onclick="openProfileModal()">
            ✏️ EDITAR DATOS
          </button>
        </div>
      </div>

      <!-- Tarjeta 1: Mediciones del Día con OCR en 2 toques (3 botones) -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Mediciones del Día</div>
            <div class="card-subtitle">Fotografíe la pantalla de su aparato en 2 toques</div>
          </div>
          <span class="badge" style="background: var(--primary);">OCR Local</span>
        </div>
        <div class="btn-action-row">
          <div class="btn-bio" onclick="openCaptureModal('GLUCOSE')">
            <div class="btn-bio-icon">🩸</div>
            <div class="btn-bio-title">GLUCÓMETRO</div>
            <div id="disp-glucose" class="btn-bio-val">114 mg/dL</div>
          </div>
          <div class="btn-bio btn-bio-red" onclick="openCaptureModal('BP')">
            <div class="btn-bio-icon">💓</div>
            <div class="btn-bio-title">TENSIÓMETRO</div>
            <div id="disp-bp" class="btn-bio-val">124/82 mmHg</div>
          </div>
          <div class="btn-bio btn-bio-green" onclick="openCaptureModal('WEIGHT')">
            <div class="btn-bio-icon">⚖️</div>
            <div class="btn-bio-title">BÁSCULA</div>
            <div id="disp-scale-btn" class="btn-bio-val">84.5 kg</div>
          </div>
        </div>
      </div>

      <!-- Tarjeta 2: Medicación con confirmación 1 toque -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Medicación Pautada</div>
            <div class="card-subtitle">Confirme sus tomas con un solo toque</div>
          </div>
          <span class="badge" style="background: var(--success);">Adherencia</span>
        </div>
        
        <div id="med-1" class="med-item taken">
          <div class="med-info">
            <h4>Metformina 850 mg</h4>
            <p>⏰ 08:30 • Con el desayuno</p>
          </div>
          <button class="btn-take done">✓ TOMADA</button>
        </div>

        <div id="med-2" class="med-item">
          <div class="med-info">
            <h4>Enalapril 20 mg</h4>
            <p>⏰ 09:00 • Con agua</p>
          </div>
          <button id="btn-take-2" class="btn-take" onclick="takeMedication('med-2', 'btn-take-2')">TOMAR</button>
        </div>
      </div>

      <!-- Tarjeta 3: Pasos pasivos & Paseo posprandial -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Meta Anti-sedentarismo</div>
            <div class="card-subtitle">Modula picos glucémicos con caminatas suaves</div>
          </div>
          <span class="badge" style="background: #8B5CF6;">Podómetro</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <h2 id="step-count-text" style="color:var(--text-main); font-weight:900;">2.850 <span style="font-size:14px; color:var(--text-muted); font-weight:600;">/ 4.000 pasos</span></h2>
          <span id="step-pct-text" style="font-weight:800; color:#8B5CF6;">71%</span>
        </div>
        <div class="progress-bg">
          <div id="step-progress-bar" class="progress-fill" style="width: 71%;"></div>
        </div>
        <div style="background:#F3E8FF; padding:10px; border-radius:8px; margin-top:8px;">
          <p style="font-size:12px; color:#581C87; line-height:16px;">
            💡 <strong>Paseo posprandial:</strong> Caminar 10-15 min post-comida amortigua las excursiones glucémicas.
          </p>
          <button style="width:100%; margin-top:8px; background:#6B21A8; color:#fff; border:none; padding:8px; border-radius:6px; font-weight:800; font-size:12px; cursor:pointer;" onclick="recordPostprandialWalk()">
            👟 HE DADO UN PASEO DE 15 MIN (+1.200 PASOS)
          </button>
        </div>
      </div>
    </div>

    <!-- Active Screen: Métricas -->
    <div id="tab-metricas" class="screen-content tab-view" style="display:none;">
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Control Ponderal e IMC</div>
            <div class="card-subtitle">Evolución del peso corporal</div>
          </div>
          <span id="badge-metric-bmi" class="badge" style="background:var(--warning);">IMC 28.56</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; margin-top:4px;">
          <div>Peso actual: <strong id="disp-metric-weight">84.5 kg</strong></div>
          <div>Estatura: <strong id="disp-metric-height">172 cm</strong></div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Glucemia: Tiempo en Rango</div>
            <div class="card-subtitle">Meta ADA: &ge; 70% entre 70 y 130 mg/dL</div>
          </div>
          <span class="badge" style="background:var(--success);">TIR: 85%</span>
        </div>
        <div class="progress-bg">
          <div class="progress-fill" style="width: 85%; background:var(--success);"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; margin-top:10px;">
          <div>Media Basal: <strong>114 mg/dL</strong></div>
          <div>Hipoglucemias: <strong style="color:var(--success);">0</strong></div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Presión Arterial (ESC/ESH)</div>
            <div class="card-subtitle">Meta cardioprotectora: &lt; 130/80 mmHg</div>
          </div>
          <span class="badge" style="background:var(--success);">124/82 mmHg</span>
        </div>
        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
          Control hemodinámico óptimo sin registros &ge; 140/90 en las últimas 72h.
        </p>
      </div>

      <div class="card" style="background:#F0F9FF; border-left:4px solid #0284C7;">
        <div class="card-title" style="color:#0369A1; font-size:15px;">Correlación Farmacológica</div>
        <p style="font-size:12.5px; color:#0369A1; line-height:17px; margin-top:4px;">
          ✓ Excelente respuesta: Su presión arterial y glucemia se mantienen estables por cumplimiento de sus tomas pautadas.
        </p>
      </div>
    </div>

    <!-- Active Screen: Nutrición & Compra -->
    <div id="tab-nutricion" class="screen-content tab-view" style="display:none;">
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Chef Terapéutico (4 pasos)</div>
            <div class="card-subtitle">Salmón al vapor con brócoli y AOVE</div>
          </div>
          <span class="badge" style="background:var(--success);">Omega-3</span>
        </div>
        <ol style="margin-left:18px; font-size:13px; color:#334155; line-height:20px;">
          <li>Cortar brócoli en ramilletes pequeños.</li>
          <li>Colocar salmón y brócoli en estuche de vapor o sartén.</li>
          <li>Cocinar 8 min al vapor a fuego medio.</li>
          <li>Aliñar con 1 cda de Aceite de Oliva Virgen Extra y limón.</li>
        </ol>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Lista de la Compra por Pasillos</div>
            <div class="card-subtitle">Evita compras compulsivas de ultraprocesados</div>
          </div>
        </div>

        <div class="aisle-group">
          <div class="aisle-head">🥦 Frutas y Verduras Frescas</div>
          <div class="grocery-row" onclick="toggleGrocery(this)">
            <input type="checkbox"> <span>Brócoli fresco (500 g)</span>
          </div>
          <div class="grocery-row" onclick="toggleGrocery(this)">
            <input type="checkbox"> <span>Espinacas tiernas (1 kg)</span>
          </div>
        </div>

        <div class="aisle-group">
          <div class="aisle-head">🐟 Pescadería y Carnicería Magra</div>
          <div class="grocery-row" onclick="toggleGrocery(this)">
            <input type="checkbox"> <span>Lomos de Salmón fresco (Omega-3)</span>
          </div>
        </div>

        <div class="aisle-group">
          <div class="aisle-head">🫒 Grasas Cardioprotectoras</div>
          <div class="grocery-row" onclick="toggleGrocery(this)">
            <input type="checkbox"> <span>Aceite de Oliva Virgen Extra (AOVE)</span>
          </div>
          <div class="grocery-row" onclick="toggleGrocery(this)">
            <input type="checkbox"> <span>Nueces crudas sin sal (200 g)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Screen: Informe Médico -->
    <div id="tab-informe" class="screen-content tab-view" style="display:none;">
      <div class="card" style="border:2px solid var(--primary);">
        <div class="card-header">
          <div>
            <div class="card-title">Informe Clínico (1 Página)</div>
            <div class="card-subtitle">Estructurado para Endocrinología y Medicina Interna</div>
          </div>
        </div>
        <p style="font-size:13px; color:var(--text-muted); line-height:18px; margin-bottom:12px;">
          Resumen ejecutivo con filiación completa, Tiempo en Rango (TIR), medias tensionales, adherencia farmacológica y evolución ponderal.
        </p>
        <button class="btn-primary" onclick="downloadReport()">
          📄 DESCARGAR / VER INFORME PDF
        </button>
      </div>

      <div class="card" style="font-size:13px;">
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Paciente:</span> <strong id="report-patient-name">Ramón García Fernández</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Edad y Talla:</span> <strong id="report-patient-age-height">58 años • 172 cm</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Peso e IMC:</span> <strong id="report-patient-weight-bmi">84.5 kg • IMC 28.56</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Glucemia TIR:</span> <strong style="color:var(--success);">85% en objetivo</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Presión Media:</span> <strong>124/82 mmHg</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0;">
          <span>Adherencia Fármacos:</span> <strong style="color:var(--primary);">96% tomas cumplidas</strong>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation Bar -->
    <div class="bottom-nav">
      <button class="nav-btn active" onclick="switchTab('tab-hoy', this)">
        <span class="nav-icon">☀️</span>
        <span class="nav-label">Hoy</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-metricas', this)">
        <span class="nav-icon">📈</span>
        <span class="nav-label">Métricas</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-nutricion', this)">
        <span class="nav-icon">🥗</span>
        <span class="nav-label">Nutrición</span>
      </button>
      <button class="nav-btn" onclick="switchTab('tab-informe', this)">
        <span class="nav-icon">📋</span>
        <span class="nav-label">Informe</span>
      </button>
    </div>

    <!-- Modal de Captura OCR (Simulación de 2 toques: Glucómetro, Tensiómetro, Báscula) -->
    <div id="capture-modal" class="modal-overlay">
      <div class="modal-box">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h3 id="modal-title" style="font-size:18px; font-weight:800;">Captura OCR</h3>
          <span style="cursor:pointer; font-size:20px; font-weight:bold;" onclick="closeCaptureModal()">✕</span>
        </div>

        <div id="view-snap">
          <div class="camera-frame">
            <h3 id="camera-prompt">Encuadre la pantalla aquí</h3>
            <p id="camera-subtext">El algoritmo extraerá automáticamente los números</p>
          </div>
          <button class="btn-primary" onclick="simulateSnap()">
            📸 1. CAPTURAR PANTALLA
          </button>
        </div>

        <div id="view-confirm" style="display:none;">
          <div style="background:#DCFCE7; padding:10px; border-radius:8px; margin-bottom:12px; font-size:13px; color:#166534; font-weight:700;">
            ✓ Valor detectado con 98% de precisión óptica
          </div>
          <div style="text-align:center; padding:14px; background:#F8FAFC; border-radius:12px; margin-bottom:14px; border:1.5px solid var(--border);">
            <div id="detected-val" style="font-size:42px; font-weight:900; color:var(--text-main);">84.2</div>
            <div id="detected-unit" style="font-size:14px; font-weight:700; color:var(--text-muted);">kg (Báscula Digital)</div>
          </div>
          <button class="btn-primary btn-success" onclick="saveReading()">
            ✓ 2. CONFIRMAR Y GUARDAR
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Editar Datos Personales y Ponderales -->
    <div id="profile-modal" class="modal-overlay">
      <div class="modal-box">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
          <h3 style="font-size:18px; font-weight:800; color:var(--text-main);">Ficha de la Persona</h3>
          <span style="cursor:pointer; font-size:20px; font-weight:bold;" onclick="closeProfileModal()">✕</span>
        </div>

        <div class="form-group">
          <label>Nombre:</label>
          <input id="input-first-name" class="form-control" type="text" value="Ramón">
        </div>

        <div class="form-group">
          <label>Apellidos:</label>
          <input id="input-last-name" class="form-control" type="text" value="García Fernández">
        </div>

        <div class="form-row-2">
          <div class="form-group" style="flex:1;">
            <label>Edad (años):</label>
            <input id="input-age" class="form-control" type="number" value="58">
          </div>
          <div class="form-group" style="flex:1;">
            <label>Estatura (cm):</label>
            <input id="input-height" class="form-control" type="number" value="172">
          </div>
        </div>

        <div class="form-group">
          <label>Peso Actual (kg):</label>
          <input id="input-weight" class="form-control" type="number" step="0.1" value="84.5">
          <p style="font-size:11.5px; color:var(--text-muted); margin-top:4px;">
            * Consejo: También puede subir el peso directamente con una foto de la báscula.
          </p>
        </div>

        <button class="btn-primary" onclick="saveProfileData()" style="margin-top:10px;">
          GUARDAR DATOS PERSONALES
        </button>
      </div>
    </div>
  </div>

  <script>
    // Global Patient State
    let patient = {
      firstName: "Ramón",
      lastName: "García Fernández",
      fullName: "Ramón García Fernández",
      age: 58,
      heightCm: 172.0,
      weightKg: 84.5,
      bmi: 28.56,
      bmiCategory: "Sobrepeso (Grado II)"
    };

    let currentMetric = 'GLUCOSE';
    let steps = 2850;

    function calculateBmi(weight, height) {
      const hM = height / 100.0;
      const bmi = Math.round((weight / (hM * hM)) * 100) / 100;
      let cat = "Normopeso";
      if (bmi < 18.5) cat = "Bajo peso";
      else if (bmi < 25.0) cat = "Normopeso";
      else if (bmi < 30.0) cat = "Sobrepeso (Grado II)";
      else if (bmi < 35.0) cat = "Obesidad (Grado I)";
      else if (bmi < 40.0) cat = "Obesidad (Grado II)";
      else cat = "Obesidad Mórbida (Grado III)";
      return { bmi, cat };
    }

    function updateProfileUI() {
      const { bmi, cat } = calculateBmi(patient.weightKg, patient.heightCm);
      patient.bmi = bmi;
      patient.bmiCategory = cat;

      document.getElementById('card-fullname').innerText = patient.fullName;
      document.getElementById('card-subdetails').innerText = patient.age + ' años • Estatura: ' + patient.heightCm + ' cm';
      document.getElementById('disp-profile-weight').innerText = patient.weightKg;
      document.getElementById('disp-profile-bmi').innerText = patient.bmi;
      document.getElementById('disp-scale-btn').innerText = patient.weightKg + ' kg';
      document.getElementById('badge-bmi-category').innerText = patient.bmiCategory;
      document.getElementById('badge-bmi-category').style.background = patient.bmi < 25 ? 'var(--success)' : 'var(--warning)';

      // Update Métricas tab
      document.getElementById('disp-metric-weight').innerText = patient.weightKg + ' kg';
      document.getElementById('disp-metric-height').innerText = patient.heightCm + ' cm';
      document.getElementById('badge-metric-bmi').innerText = 'IMC ' + patient.bmi;

      // Update Informe tab
      document.getElementById('report-patient-name').innerText = patient.fullName;
      document.getElementById('report-patient-age-height').innerText = patient.age + ' años • ' + patient.heightCm + ' cm';
      document.getElementById('report-patient-weight-bmi').innerText = patient.weightKg + ' kg • IMC ' + patient.bmi;

      // Notify backend if available
      fetch('/api/v1/patient', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: patient.firstName,
          last_name: patient.lastName,
          age: patient.age,
          height_cm: patient.heightCm,
          current_weight_kg: patient.weightKg
        })
      }).catch(() => {});
    }

    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-view').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).style.display = 'block';
      btn.classList.add('active');
    }

    function openCaptureModal(type) {
      currentMetric = type;
      if (type === 'GLUCOSE') {
        document.getElementById('modal-title').innerText = 'Glucómetro Digital';
        document.getElementById('camera-prompt').innerText = 'Encuadre la pantalla del Glucómetro';
        document.getElementById('camera-subtext').innerText = 'Extracción automática de mg/dL';
      } else if (type === 'BP') {
        document.getElementById('modal-title').innerText = 'Tensiómetro Digital';
        document.getElementById('camera-prompt').innerText = 'Encuadre la pantalla del Tensiómetro';
        document.getElementById('camera-subtext').innerText = 'Extracción de Sistólica/Diastólica en mmHg';
      } else if (type === 'WEIGHT') {
        document.getElementById('modal-title').innerText = 'Báscula Digital de Peso';
        document.getElementById('camera-prompt').innerText = 'Encuadre la pantalla de la Báscula';
        document.getElementById('camera-subtext').innerText = 'Extracción óptica de peso en kg y cálculo de IMC';
      }

      document.getElementById('view-snap').style.display = 'block';
      document.getElementById('view-confirm').style.display = 'none';
      document.getElementById('capture-modal').style.display = 'flex';
    }

    function closeCaptureModal() {
      document.getElementById('capture-modal').style.display = 'none';
    }

    function openProfileModal() {
      document.getElementById('input-first-name').value = patient.firstName;
      document.getElementById('input-last-name').value = patient.lastName;
      document.getElementById('input-age').value = patient.age;
      document.getElementById('input-height').value = patient.heightCm;
      document.getElementById('input-weight').value = patient.weightKg;
      document.getElementById('profile-modal').style.display = 'flex';
    }

    function closeProfileModal() {
      document.getElementById('profile-modal').style.display = 'none';
    }

    function saveProfileData() {
      patient.firstName = document.getElementById('input-first-name').value.trim() || patient.firstName;
      patient.lastName = document.getElementById('input-last-name').value.trim() || patient.lastName;
      patient.fullName = patient.firstName + ' ' + patient.lastName;
      patient.age = parseInt(document.getElementById('input-age').value, 10) || patient.age;
      patient.heightCm = parseFloat(document.getElementById('input-height').value) || patient.heightCm;
      patient.weightKg = parseFloat(document.getElementById('input-weight').value) || patient.weightKg;

      updateProfileUI();
      closeProfileModal();

      const banner = document.getElementById('clinical-alert-banner');
      banner.classList.add('show');
      document.getElementById('alert-title').innerText = '✓ DATOS ACTUALIZADOS';
      document.getElementById('alert-msg').innerText = 'Ficha actualizada: ' + patient.fullName + ' • IMC recalculado: ' + patient.bmi;
      setTimeout(() => banner.classList.remove('show'), 3500);
    }

    function simulateSnap() {
      document.getElementById('view-snap').style.display = 'none';
      document.getElementById('view-confirm').style.display = 'block';
      if (currentMetric === 'GLUCOSE') {
        document.getElementById('detected-val').innerText = '112';
        document.getElementById('detected-unit').innerText = 'mg/dL (Glucosa en Ayunas)';
      } else if (currentMetric === 'BP') {
        document.getElementById('detected-val').innerText = '122/80';
        document.getElementById('detected-unit').innerText = 'mmHg (Sistólica / Diastólica)';
      } else if (currentMetric === 'WEIGHT') {
        document.getElementById('detected-val').innerText = '84.1';
        document.getElementById('detected-unit').innerText = 'kg (Foto de Báscula Digital)';
      }
    }

    function saveReading() {
      if (currentMetric === 'GLUCOSE') {
        document.getElementById('disp-glucose').innerText = '112 mg/dL';
      } else if (currentMetric === 'BP') {
        document.getElementById('disp-bp').innerText = '122/80 mmHg';
      } else if (currentMetric === 'WEIGHT') {
        patient.weightKg = 84.1;
        updateProfileUI();
      }
      closeCaptureModal();
      
      const banner = document.getElementById('clinical-alert-banner');
      banner.classList.add('show');
      document.getElementById('alert-title').innerText = '✓ REGISTRO GUARDADO';
      document.getElementById('alert-msg').innerText = currentMetric === 'WEIGHT' 
        ? 'Peso de 84.1 kg guardado desde foto de la báscula. IMC actualizado a ' + patient.bmi + '.'
        : 'Su medición está dentro de la meta clínica de control vascular.';
      setTimeout(() => banner.classList.remove('show'), 4000);
    }

    function takeMedication(itemId, btnId) {
      document.getElementById(itemId).classList.add('taken');
      const btn = document.getElementById(btnId);
      btn.classList.add('done');
      btn.innerText = '✓ TOMADA';
      btn.onclick = null;
    }

    function recordPostprandialWalk() {
      steps += 1200;
      document.getElementById('step-count-text').innerHTML = steps.toLocaleString() + ' <span style="font-size:14px; color:var(--text-muted); font-weight:600;">/ 4.000 pasos</span>';
      const pct = Math.min(100, Math.round((steps / 4000) * 100));
      document.getElementById('step-pct-text').innerText = pct + '%';
      document.getElementById('step-progress-bar').style.width = pct + '%';
      alert('¡Excelente! Ha completado su paseo posprandial de 15 min (+1.200 pasos). Ayudando a que sus músculos consuman la glucosa circulante.');
    }

    function toggleGrocery(row) {
      row.classList.toggle('checked');
      const chk = row.querySelector('input');
      chk.checked = !chk.checked;
    }

    function downloadReport() {
      window.open('/api/v1/reports/pdf-html', '_blank');
    }

    // Initialize UI on load
    updateProfileUI();
  </script>
</body>
</html>
"""
