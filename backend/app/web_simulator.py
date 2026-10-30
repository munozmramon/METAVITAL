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
      max-width: 412px;
      height: 840px;
      background: #FFFFFF;
      border-radius: 40px;
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

    /* Buttons */
    .btn-action-row {
      display: flex;
      gap: 10px;
    }

    .btn-bio {
      flex: 1;
      background: #EFF6FF;
      border: 2px solid #BFDBFE;
      border-radius: 14px;
      padding: 14px 10px;
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

    .btn-bio-icon {
      font-size: 28px;
      margin-bottom: 4px;
    }

    .btn-bio-title {
      font-size: 13px;
      font-weight: 800;
      color: var(--text-main);
    }

    .btn-bio-val {
      font-size: 12px;
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

      <!-- Tarjeta 1: Mediciones con OCR en 2 toques -->
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
          Resumen ejecutivo con Tiempo en Rango (TIR), medias tensionales, adherencia farmacológica y pasos pasivos.
        </p>
        <button class="btn-primary" onclick="downloadReport()">
          📄 DESCARGAR / VER INFORME PDF
        </button>
      </div>

      <div class="card" style="font-size:13px;">
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>Paciente:</span> <strong>Ramón (58 años)</strong>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9;">
          <span>IMC Actual:</span> <strong>28.5 kg/m² (-1.2 kg)</strong>
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

    <!-- Modal de Captura OCR (Simulación de 2 toques) -->
    <div id="capture-modal" class="modal-overlay">
      <div class="modal-box">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h3 id="modal-title" style="font-size:18px; font-weight:800;">Captura OCR</h3>
          <span style="cursor:pointer; font-size:20px; font-weight:bold;" onclick="closeCaptureModal()">✕</span>
        </div>

        <div id="view-snap">
          <div class="camera-frame">
            <h3 id="camera-prompt">Encuadre la pantalla aquí</h3>
            <p>El algoritmo extraerá automáticamente los números</p>
          </div>
          <button class="btn-primary" onclick="simulateSnap()">
            📸 1. CAPTURAR PANTALLA
          </button>
        </div>

        <div id="view-confirm" style="display:none;">
          <div style="background:#DCFCE7; padding:10px; border-radius:8px; margin-bottom:12px; font-size:13px; color:#166534; font-weight:700;">
            ✓ Valor detectado con 97% de precisión óptica
          </div>
          <div style="text-align:center; padding:14px; background:#F8FAFC; border-radius:12px; margin-bottom:14px; border:1.5px solid var(--border);">
            <div id="detected-val" style="font-size:42px; font-weight:900; color:var(--text-main);">118</div>
            <div id="detected-unit" style="font-size:14px; font-weight:700; color:var(--text-muted);">mg/dL (Glucemia)</div>
          </div>
          <button class="btn-primary btn-success" onclick="saveReading()">
            ✓ 2. CONFIRMAR Y GUARDAR
          </button>
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentMetric = 'GLUCOSE';
    let steps = 2850;

    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-view').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).style.display = 'block';
      btn.classList.add('active');
    }

    function openCaptureModal(type) {
      currentMetric = type;
      document.getElementById('modal-title').innerText = type === 'GLUCOSE' ? 'Glucómetro Digital' : 'Tensiómetro Digital';
      document.getElementById('camera-prompt').innerText = type === 'GLUCOSE' ? 'Encuadre la pantalla del Glucómetro' : 'Encuadre la pantalla del Tensiómetro';
      document.getElementById('view-snap').style.display = 'block';
      document.getElementById('view-confirm').style.display = 'none';
      document.getElementById('capture-modal').style.display = 'flex';
    }

    function closeCaptureModal() {
      document.getElementById('capture-modal').style.display = 'none';
    }

    function simulateSnap() {
      document.getElementById('view-snap').style.display = 'none';
      document.getElementById('view-confirm').style.display = 'block';
      if (currentMetric === 'GLUCOSE') {
        document.getElementById('detected-val').innerText = '112';
        document.getElementById('detected-unit').innerText = 'mg/dL (Glucosa en Ayunas)';
      } else {
        document.getElementById('detected-val').innerText = '122/80';
        document.getElementById('detected-unit').innerText = 'mmHg (Sistólica / Diastólica)';
      }
    }

    function saveReading() {
      if (currentMetric === 'GLUCOSE') {
        document.getElementById('disp-glucose').innerText = '112 mg/dL';
      } else {
        document.getElementById('disp-bp').innerText = '122/80 mmHg';
      }
      closeCaptureModal();
      
      // Clinical alert simulation test
      const banner = document.getElementById('clinical-alert-banner');
      banner.classList.add('show');
      document.getElementById('alert-title').innerText = '✓ REGISTRO VALIDADO';
      document.getElementById('alert-msg').innerText = 'Su medición está dentro de la meta clínica (70-130 mg/dL y <130/80 mmHg).';
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
  </script>
</body>
</html>
"""
