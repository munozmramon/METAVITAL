/**
 * METAVITAL - Data Backup & Local Persistence Service
 * Cumplimiento de Salvaguarda de Datos PWA Offline (Target Sénior / Plan Local)
 * Previene la pérdida de constantes históricas por purga de almacenamiento (Safari ITP / Chrome)
 */

export interface PatientProfile {
  firstName: string;
  lastName: string;
  fullName: string;
  age: number;
  heightCm: number;
  weightKg: number;
  clinicalProfile: string;
  targetGlucoseMin: number;
  targetGlucoseMax: number;
  targetSystolicMax: number;
  targetDiastolicMax: number;
  bmi: number;
  bmiCategory: string;
}

export interface MeasurementRecord {
  id: number | string;
  type: 'GLUCOSE' | 'BP' | 'WEIGHT' | 'STEPS' | string;
  icon?: string;
  label: string;
  value: string;
  date: string;
  day?: string;
  numVal?: number;
  numValDia?: number;
  status: string;
  badgeColor?: string;
}

export interface MetavitalBackupPayload {
  schemaVersion: '1.0';
  app: 'METAVITAL';
  exportedAt: string;
  environment: 'PWA-Offline' | 'Cloud';
  patient: Partial<PatientProfile>;
  measurements: MeasurementRecord[];
  stepsHistory?: Record<string, any>;
  dietLogs?: Record<string, any>;
  userPlan?: string;
}

/**
 * Recopila y exporta las constantes del usuario a un archivo JSON legible y descargable
 */
export function exportUserDataToJSON(): MetavitalBackupPayload {
  // 1. Obtener perfil del paciente
  const patientData: Partial<PatientProfile> = (typeof (window as any).patient !== 'undefined')
    ? (window as any).patient
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

  // 2. Obtener historial de mediciones
  const measurements: MeasurementRecord[] = (typeof (window as any).measurementHistory !== 'undefined' && Array.isArray((window as any).measurementHistory))
    ? (window as any).measurementHistory
    : [];

  // 3. Obtener pasos diarios y dietas desde LocalStorage
  let stepsHistory: Record<string, any> = {};
  try {
    const rawSteps = localStorage.getItem('metavital_steps_history_v2');
    if (rawSteps) stepsHistory = JSON.parse(rawSteps);
  } catch (e) {
    console.warn('[BackupService] Error al leer steps history:', e);
  }

  let dietLogs: Record<string, any> = {};
  try {
    const rawDiet = localStorage.getItem('metavital_diet_logs');
    if (rawDiet) dietLogs = JSON.parse(rawDiet);
  } catch (e) {
    console.warn('[BackupService] Error al leer diet logs:', e);
  }

  const userPlan = localStorage.getItem('metavital_user_plan') || 'free';

  const payload: MetavitalBackupPayload = {
    schemaVersion: '1.0',
    app: 'METAVITAL',
    exportedAt: new Date().toISOString(),
    environment: 'PWA-Offline',
    patient: patientData,
    measurements,
    stepsHistory,
    dietLogs,
    userPlan
  };

  // Generar y disparar descarga en el navegador
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const dateStr = new Date().toISOString().split('T')[0];
  const safeName = (patientData.fullName || 'Paciente').replace(/\s+/g, '_');
  a.href = url;
  a.download = `METAVITAL_CopiaSeguridad_${safeName}_${dateStr}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  // Guardar marca temporal para el recordatorio de 7 días
  try {
    localStorage.setItem('metavital_last_backup_date', Date.now().toString());
  } catch (e) {}

  return payload;
}

/**
 * Valida y restaura una copia de seguridad JSON previamente exportada
 */
export async function importUserDataFromJSON(file: File): Promise<boolean> {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('No se seleccionó ningún archivo de respaldo.'));
      return;
    }

    const reader = new FileReader();
    reader.onload = (event: ProgressEvent<FileReader>) => {
      try {
        const text = event.target?.result as string;
        const data = JSON.parse(text) as MetavitalBackupPayload;

        // Validación de cabecera de integridad
        if (!data || data.app !== 'METAVITAL' || !Array.isArray(data.measurements)) {
          throw new Error('El archivo no tiene el formato válido de copia de seguridad de METAVITAL.');
        }

        // 1. Restaurar paciente
        if (data.patient && typeof (window as any).patient !== 'undefined') {
          Object.assign((window as any).patient, data.patient);
          if (typeof (window as any).updateProfileUI === 'function') {
            (window as any).updateProfileUI();
          }
        }

        // 2. Restaurar historial de constantes
        if (Array.isArray(data.measurements)) {
          (window as any).measurementHistory = data.measurements;
          if (typeof (window as any).renderMeasurementHistory === 'function') {
            (window as any).renderMeasurementHistory();
          }
        }

        // 3. Restaurar pasos y dietas en LocalStorage
        if (data.stepsHistory) {
          localStorage.setItem('metavital_steps_history_v2', JSON.stringify(data.stepsHistory));
          if (typeof (window as any).stepsDailyHistory !== 'undefined') {
            (window as any).stepsDailyHistory = data.stepsHistory;
          }
        }

        if (data.dietLogs) {
          localStorage.setItem('metavital_diet_logs', JSON.stringify(data.dietLogs));
        }

        // Registrar restauración exitosa
        localStorage.setItem('metavital_last_backup_date', Date.now().toString());
        resolve(true);
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Error al leer el archivo en el dispositivo.'));
    reader.readAsText(file);
  });
}
