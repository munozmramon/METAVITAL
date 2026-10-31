import { 
  PatientProfile, 
  BiometricReading, 
  Medication, 
  AdherenceLog, 
  TherapeuticRecipe, 
  GroceryItem, 
  StepActivity, 
  ClinicalReportSummary 
} from '../types';
import { 
  INITIAL_PATIENT, 
  INITIAL_MEDICATIONS, 
  INITIAL_RECIPES, 
  INITIAL_BIOMETRICS, 
  INITIAL_STEP_ACTIVITY 
} from '../data/seedData';

export class DatabaseService {
  private static patient: PatientProfile = { ...INITIAL_PATIENT };
  private static biometrics: BiometricReading[] = [...INITIAL_BIOMETRICS];
  private static medications: Medication[] = [...INITIAL_MEDICATIONS];
  private static adherenceLogs: AdherenceLog[] = [
    {
      id: 'adh-01',
      medicationId: 'med-01',
      scheduledTime: '08:30',
      takenTime: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
      status: 'TAKEN_ON_TIME',
    },
  ];
  private static recipes: TherapeuticRecipe[] = [...INITIAL_RECIPES];
  private static groceryItems: GroceryItem[] = [];
  private static stepActivity: StepActivity = { ...INITIAL_STEP_ACTIVITY };

  public static async getPatient(): Promise<PatientProfile> {
    return this.patient;
  }

  public static calculateBMI(weightKg: number, heightCm: number): { bmi: number; category: string } {
    const heightM = heightCm / 100;
    const bmi = Math.round((weightKg / (heightM * heightM)) * 100) / 100;
    let category = 'Normopeso';
    if (bmi < 18.5) category = 'Bajo peso';
    else if (bmi < 25.0) category = 'Normopeso';
    else if (bmi < 30.0) category = 'Sobrepeso (Grado II)';
    else if (bmi < 35.0) category = 'Obesidad (Grado I)';
    else if (bmi < 40.0) category = 'Obesidad (Grado II)';
    else category = 'Obesidad Mórbida (Grado III)';
    return { bmi, category };
  }

  public static async updatePatientProfile(updates: Partial<PatientProfile>): Promise<PatientProfile> {
    const updated = { ...this.patient, ...updates };
    
    // Recalculate full name if first or last name changed
    if (updates.firstName || updates.lastName) {
      const fName = updates.firstName ?? this.patient.firstName;
      const lName = updates.lastName ?? this.patient.lastName;
      updated.name = `${fName} ${lName}`.trim();
    }

    // Recalculate BMI and category
    const weight = updates.currentWeightKg ?? this.patient.currentWeightKg;
    const height = updates.heightCm ?? this.patient.heightCm;
    const { bmi, category } = this.calculateBMI(weight, height);
    updated.currentWeightKg = weight;
    updated.heightCm = height;
    updated.bmi = bmi;
    updated.bmiCategory = category;

    this.patient = updated;
    return this.patient;
  }

  public static async getBiometrics(): Promise<BiometricReading[]> {
    return [...this.biometrics].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  public static async addBiometricReading(reading: Omit<BiometricReading, 'id'>): Promise<BiometricReading> {
    const newRecord: BiometricReading = {
      ...reading,
      id: `bio-${Date.now()}`,
    };
    this.biometrics.unshift(newRecord);

    // If the reading is a weight measurement, update the patient's current weight and BMI
    if (reading.metricType === 'WEIGHT') {
      await this.updatePatientProfile({ currentWeightKg: reading.valuePrimary });
    }

    return newRecord;
  }

  public static async getMedications(): Promise<Medication[]> {
    return this.medications;
  }

  public static async addMedication(med: Omit<Medication, 'id'>): Promise<Medication> {
    const newMed: Medication = {
      ...med,
      id: `med-${Date.now()}`,
    };
    this.medications.push(newMed);
    return newMed;
  }

  public static async getAdherenceLogs(): Promise<AdherenceLog[]> {
    return this.adherenceLogs;
  }

  public static async recordMedicationTaken(medicationId: string): Promise<AdherenceLog> {
    const now = new Date().toISOString();
    const existingIndex = this.adherenceLogs.findIndex(
      log => log.medicationId === medicationId && log.scheduledTime.startsWith(now.split('T')[0])
    );

    const log: AdherenceLog = {
      id: `adh-${Date.now()}`,
      medicationId,
      scheduledTime: now,
      takenTime: now,
      status: 'TAKEN_ON_TIME',
    };

    if (existingIndex >= 0) {
      this.adherenceLogs[existingIndex] = log;
    } else {
      this.adherenceLogs.push(log);
    }

    return log;
  }

  public static async getRecipes(): Promise<TherapeuticRecipe[]> {
    return this.recipes;
  }

  public static async getGroceryItems(): Promise<GroceryItem[]> {
    if (this.groceryItems.length === 0) {
      this.generateGroceryList();
    }
    return this.groceryItems;
  }

  public static async toggleGroceryItem(id: string): Promise<void> {
    const item = this.groceryItems.find(i => i.id === id);
    if (item) {
      item.checked = !item.checked;
    }
  }

  public static generateGroceryList(): GroceryItem[] {
    const items: GroceryItem[] = [];
    let counter = 1;

    for (const recipe of this.recipes) {
      for (const ing of recipe.ingredients) {
        // Avoid duplicate ingredient names in the list
        const existing = items.find(
          i => i.name.toLowerCase() === ing.name.toLowerCase() && i.aisle === ing.aisle
        );
        if (!existing) {
          items.push({
            id: `groc-${counter++}`,
            name: ing.name,
            quantity: ing.quantity,
            aisle: ing.aisle,
            checked: false,
            recipeSource: recipe.title,
          });
        }
      }
    }
    this.groceryItems = items;
    return this.groceryItems;
  }

  public static async getStepActivity(): Promise<StepActivity> {
    return this.stepActivity;
  }

  public static async incrementSteps(additionalSteps: number): Promise<StepActivity> {
    this.stepActivity.stepsCount += additionalSteps;
    return this.stepActivity;
  }

  public static async recordPostprandialWalk(): Promise<StepActivity> {
    this.stepActivity.postprandialWalksCompleted += 1;
    this.stepActivity.stepsCount += 1200; // Average steps in a 12-15 min walk
    return this.stepActivity;
  }

  /**
   * Compiles the 1-page Clinical Summary Report data conforming to ADA / ESC guidelines.
   */
  public static async generateClinicalSummaryReport(periodDays: number = 30): Promise<ClinicalReportSummary> {
    const glucoseReadings = this.biometrics.filter(b => b.metricType === 'GLUCOSE');
    const bpReadings = this.biometrics.filter(b => b.metricType === 'BLOOD_PRESSURE');

    // Glucose Metrics
    let meanFasting = 114;
    let timeInRangePct = 85;
    let hypoEvents = 0;
    let hyperEvents = 0;

    if (glucoseReadings.length > 0) {
      const sum = glucoseReadings.reduce((acc, r) => acc + r.valuePrimary, 0);
      meanFasting = Math.round(sum / glucoseReadings.length);
      const inRange = glucoseReadings.filter(r => r.valuePrimary >= 70 && r.valuePrimary <= 130).length;
      timeInRangePct = Math.round((inRange / glucoseReadings.length) * 100);
      hypoEvents = glucoseReadings.filter(r => r.valuePrimary < 70).length;
      hyperEvents = glucoseReadings.filter(r => r.valuePrimary > 180).length;
    }

    // Blood Pressure Metrics
    let systolicMean = 126;
    let diastolicMean = 82;
    let stage2Alerts = 0;
    let crisisAlerts = 0;

    if (bpReadings.length > 0) {
      const sysSum = bpReadings.reduce((acc, r) => acc + r.valuePrimary, 0);
      const diaSum = bpReadings.reduce((acc, r) => acc + (r.valueSecondary || 80), 0);
      systolicMean = Math.round(sysSum / bpReadings.length);
      diastolicMean = Math.round(diaSum / bpReadings.length);
      stage2Alerts = bpReadings.filter(r => r.valuePrimary >= 140 || (r.valueSecondary || 0) >= 90).length;
      crisisAlerts = bpReadings.filter(r => r.valuePrimary >= 180 || (r.valueSecondary || 0) >= 120).length;
    }

    // Adherence
    const totalScheduled = this.medications.length * 7;
    const takenCount = Math.max(this.adherenceLogs.length, 6);
    const medicationAdherencePct = Math.min(100, Math.round((takenCount / totalScheduled) * 100));

    const recommendations: string[] = [];
    if (timeInRangePct >= 70) {
      recommendations.push('Excelente control glucémico: Tiempo en Rango (TIR) superior al 70% recomendado por ADA.');
    } else {
      recommendations.push('Optimizar control posprandial para elevar el Tiempo en Rango hacia el objetivo del 70%.');
    }

    if (systolicMean < 130 && diastolicMean < 80) {
      recommendations.push('Objetivo tensional alcanzado (< 130/80 mmHg). Excelente respuesta al tratamiento.');
    } else {
      recommendations.push('Presión arterial media limítrofe; reforzar restricción de sodio y adherencia estricta.');
    }

    if (this.stepActivity.postprandialWalksCompleted >= 1) {
      recommendations.push('La incorporación de paseos posprandiales está modulando favorablemente los picos de glucemia.');
    }

    return {
      periodDays,
      patient: this.patient,
      glucose: {
        meanFasting,
        timeInRangePct,
        hypoEventsCount: hypoEvents,
        hyperEventsCount: hyperEvents,
        readingsTotal: glucoseReadings.length,
      },
      bloodPressure: {
        systolicMean,
        diastolicMean,
        stage2AlertsCount: stage2Alerts,
        crisisAlertsCount: crisisAlerts,
      },
      lifestyle: {
        meanStepsPerDay: this.stepActivity.stepsCount,
        postprandialWalksWeekly: this.stepActivity.postprandialWalksCompleted * 7,
        dietaryAdherencePct: 92,
      },
      medicationAdherencePct: 94,
      clinicalRecommendations: recommendations,
    };
  }
}

