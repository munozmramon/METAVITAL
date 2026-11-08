/**
 * METAVITAL - Data Backup & Local Persistence Service (JavaScript Runtime)
 * Cumplimiento de Salvaguarda de Datos PWA Offline-First (Target Sénior)
 * Soporte JSON + CSV estructurado e IndexedDB
 */

const DB_NAME = 'metavital_offline_db';
const DB_VERSION = 1;
const STORE_NAME = 'readings';

function openIndexedDB() {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('IndexedDB no soportado en este navegador.'));
      return;
    }
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = function(e) {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
    request.onsuccess = function() { resolve(request.result); };
    request.onerror = function() { reject(request.error); };
  });
}

function saveRecordToIndexedDB(record) {
  try {
    openIndexedDB().then(db => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      store.put(record);
    }).catch(err => {
      console.warn('[IndexedDB] Warning guardando:', err);
    });
  } catch(e) {}
}

function exportUserDataToJSON() {
  const patientData = (typeof window.patient !== 'undefined')
    ? window.patient
    : {
        firstName: 'Usuario',
        lastName: 'Local',
        fullName: 'Usuario Local',
        age: 60,
        heightCm: 170,
        weightKg: 75.0,
        clinicalProfile: 'STANDARD',
        targetGlucoseMin: 70,
        targetGlucoseMax: 130,
        targetSystolicMax: 130,
        targetDiastolicMax: 80,
        bmi: 25.9,
        bmiCategory: 'Normopeso'
      };

  const measurements = (typeof window.measurementHistory !== 'undefined' && Array.isArray(window.measurementHistory))
    ? window.measurementHistory
    : [];

  let stepsHistory = {};
  try {
    const rawSteps = localStorage.getItem('metavital_steps_history_v2');
    if (rawSteps) stepsHistory = JSON.parse(rawSteps);
  } catch (e) {
    console.warn('[BackupService] Error al leer steps history:', e);
  }

  let dietLogs = {};
  try {
    const rawDiet = localStorage.getItem('metavital_diet_logs');
    if (rawDiet) dietLogs = JSON.parse(rawDiet);
  } catch (e) {
    console.warn('[BackupService] Error al leer diet logs:', e);
  }

  const userPlan = localStorage.getItem('metavital_user_plan') || 'free';

  const payload = {
    schemaVersion: '1.0',
    app: 'METAVITAL',
    exportedAt: new Date().toISOString(),
    environment: 'PWA-Offline',
    patient: patientData,
    measurements: measurements,
    stepsHistory: stepsHistory,
    dietLogs: dietLogs,
    userPlan: userPlan
  };

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const dateStr = new Date().toISOString().split('T')[0];
  const safeName = (patientData.fullName || 'Paciente').replace(/\s+/g, '_');
  a.href = url;
  a.download = 'METAVITAL_CopiaSeguridad_' + safeName + '_' + dateStr + '.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  try {
    localStorage.setItem('metavital_last_backup_date', Date.now().toString());
  } catch (e) {}

  const banner = document.getElementById('clinical-alert-banner');
  if (banner) {
    banner.classList.add('show');
    const titleEl = document.getElementById('alert-title');
    const msgEl = document.getElementById('alert-msg');
    if (titleEl) titleEl.innerText = '✓ COPIA JSON DESCARGADA';
    if (msgEl) msgEl.innerText = 'Sus constantes y perfil se han guardado en un archivo JSON en su dispositivo.';
    setTimeout(() => banner.classList.remove('show'), 4500);
  }

  return payload;
}

function exportUserDataToCSV() {
  const patientData = (typeof window.patient !== 'undefined') ? window.patient : {};
  const measurements = (typeof window.measurementHistory !== 'undefined' && Array.isArray(window.measurementHistory))
    ? window.measurementHistory
    : [];

  const headers = ['ID', 'Fecha_Registro', 'Tipo', 'Parametro', 'Valor', 'Estado_Clinico', 'Paciente'];
  const rows = measurements.map(function(m) {
    return [
      m.id,
      '"' + (m.date || '') + '"',
      m.type,
      '"' + (m.label || '') + '"',
      '"' + (m.value || '') + '"',
      '"' + (m.status || '') + '"',
      '"' + (patientData.fullName || 'Paciente') + '"'
    ];
  });

  const csvContent = '\uFEFF' + [headers.join(';'), ...rows.map(r => r.join(';'))].join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const dateStr = new Date().toISOString().split('T')[0];
  const safeName = (patientData.fullName || 'Paciente').replace(/\s+/g, '_');
  a.href = url;
  a.download = 'METAVITAL_Constantes_' + safeName + '_' + dateStr + '.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  try {
    localStorage.setItem('metavital_last_backup_date', Date.now().toString());
  } catch (e) {}

  const banner = document.getElementById('clinical-alert-banner');
  if (banner) {
    banner.classList.add('show');
    const titleEl = document.getElementById('alert-title');
    const msgEl = document.getElementById('alert-msg');
    if (titleEl) titleEl.innerText = '✓ COPIA CSV DESCARGADA';
    if (msgEl) msgEl.innerText = 'Historial exportado en CSV para abrir en Excel o compartir.';
    setTimeout(() => banner.classList.remove('show'), 4500);
  }
}

function importUserDataFromJSON(file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('No se seleccionó ningún archivo de respaldo.'));
      return;
    }

    const reader = new FileReader();
    reader.onload = function(event) {
      try {
        const text = event.target.result;
        const data = JSON.parse(text);

        if (!data || data.app !== 'METAVITAL' || !Array.isArray(data.measurements)) {
          throw new Error('El archivo no tiene el formato válido de copia de seguridad de METAVITAL.');
        }

        if (data.patient && typeof window.patient !== 'undefined') {
          Object.assign(window.patient, data.patient);
          if (typeof window.updateProfileUI === 'function') {
            window.updateProfileUI();
          }
        }

        if (Array.isArray(data.measurements)) {
          window.measurementHistory = data.measurements;
          if (typeof window.renderMeasurementHistory === 'function') {
            window.renderMeasurementHistory();
          }
          data.measurements.forEach(m => saveRecordToIndexedDB(m));
        }

        if (data.stepsHistory) {
          localStorage.setItem('metavital_steps_history_v2', JSON.stringify(data.stepsHistory));
          if (typeof window.stepsDailyHistory !== 'undefined') {
            window.stepsDailyHistory = data.stepsHistory;
          }
        }

        if (data.dietLogs) {
          localStorage.setItem('metavital_diet_logs', JSON.stringify(data.dietLogs));
        }

        localStorage.setItem('metavital_last_backup_date', Date.now().toString());

        const banner = document.getElementById('clinical-alert-banner');
        if (banner) {
          banner.classList.add('show');
          const titleEl = document.getElementById('alert-title');
          const msgEl = document.getElementById('alert-msg');
          if (titleEl) titleEl.innerText = '✓ COPIA RESTAURADA CON ÉXITO';
          if (msgEl) msgEl.innerText = 'Se han recuperado ' + data.measurements.length + ' constantes históricas y sus datos clínicos.';
          setTimeout(() => banner.classList.remove('show'), 4500);
        }

        resolve(true);
      } catch (err) {
        alert('Error al restaurar copia: ' + err.message);
        reject(err);
      }
    };
    reader.onerror = function() { reject(new Error('Error al leer el archivo.')); };
    reader.readAsText(file);
  });
}

function handleRestoreBackupFile(input) {
  if (input && input.files && input.files[0]) {
    importUserDataFromJSON(input.files[0]).then(() => {
      input.value = '';
    }).catch(err => {
      console.error(err);
      input.value = '';
    });
  }
}

function checkWeeklyBackupReminder() {
  try {
    const isFree = (typeof getUserPlan === 'function') ? (getUserPlan() === 'free') : true;
    if (!isFree) return;

    const lastBackup = localStorage.getItem('metavital_last_backup_date');
    const now = Date.now();
    const SEVEN_DAYS = 7 * 24 * 60 * 60 * 1000;

    if (!lastBackup || (now - parseInt(lastBackup, 10)) > SEVEN_DAYS) {
      const banner = document.getElementById('backup-weekly-reminder-banner');
      if (banner) banner.style.display = 'block';
    }
  } catch (e) {}
}

function dismissBackupReminder() {
  const banner = document.getElementById('backup-weekly-reminder-banner');
  if (banner) banner.style.display = 'none';
  try {
    localStorage.setItem('metavital_last_backup_date', Date.now().toString());
  } catch (e) {}
}

window.exportUserDataToJSON = exportUserDataToJSON;
window.exportUserDataToCSV = exportUserDataToCSV;
window.importUserDataFromJSON = importUserDataFromJSON;
window.handleRestoreBackupFile = handleRestoreBackupFile;
window.checkWeeklyBackupReminder = checkWeeklyBackupReminder;
window.dismissBackupReminder = dismissBackupReminder;
window.saveRecordToIndexedDB = saveRecordToIndexedDB;
