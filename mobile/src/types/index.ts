export type MetricType = 'GLUCOSE' | 'BLOOD_PRESSURE' | 'WEIGHT' | 'STEPS';

export type MeasurementContext = 'FASTING' | 'POSTPRANDIAL' | 'RANDOM' | 'BEDTIME';

export type CaptureMethod = 'OCR_CAMERA' | 'MANUAL' | 'BLUETOOTH_NATIVE';

export type AlertSeverity = 'NORMAL' | 'WARNING' | 'CRITICAL' | 'EMERGENCY';

export interface BiometricReading {
  id: string;
  patientId: string;
  metricType: MetricType;
  valuePrimary: number; // mg/dL for glucose, Systolic mmHg for BP
  valueSecondary?: number; // Diastolic mmHg for BP
  valueTertiary?: number; // Heart rate (bpm)
  context: MeasurementContext;
  captureMethod: CaptureMethod;
  timestamp: string; // ISO string
  isAlert: boolean;
  alertNotes?: string;
}

export interface Medication {
  id: string;
  brandName: string;
  genericName: string;
  doseMg: number;
  therapeuticClass: 'ANTIDIABETIC' | 'ANTIHYPERTENSIVE' | 'STATIN_LIPID' | 'OTHER';
  scheduledTime: string; // "09:00"
  instructions: string;
  photoUrl?: string;
  isActive: boolean;
}

export interface AdherenceLog {
  id: string;
  medicationId: string;
  scheduledTime: string;
  takenTime?: string;
  status: 'TAKEN_ON_TIME' | 'TAKEN_LATE' | 'MISSED' | 'SKIPPED';
  notes?: string;
}

export interface StepActivity {
  date: string; // YYYY-MM-DD
  stepsCount: number;
  targetSteps: number; // starts at 4000
  postprandialWalksCompleted: number; // target: 2-3 walks of 10-15 mins
  activeMinutes: number;
}

export interface TherapeuticRecipe {
  id: string;
  title: string;
  mealType: 'BREAKFAST' | 'LUNCH' | 'DINNER' | 'SNACK';
  glycemicLoad: 'VERY_LOW' | 'LOW' | 'MEDIUM';
  sodiumMg: number;
  solubleFiberG: number;
  omega3Rich: boolean;
  prepTimeMinutes: number;
  steps: [string, string, string] | [string, string, string, string]; // strictly max 4 steps
  ingredients: {
    name: string;
    quantity: string;
    aisle: SupermarketAisle;
  }[];
}

export type SupermarketAisle = 
  | 'FRUITS_VEGETABLES' 
  | 'FISH_LEAN_MEAT' 
  | 'LEGUMES_WHOLE_GRAINS' 
  | 'HEALTHY_FATS';

export interface GroceryItem {
  id: string;
  name: string;
  quantity: string;
  aisle: SupermarketAisle;
  checked: boolean;
  recipeSource?: string;
}

export interface ClinicalAlert {
  id: string;
  severity: AlertSeverity;
  title: string;
  description: string;
  instructions: string;
  requiresImmediateAction: boolean;
  emergencyCallPrompt: boolean;
  familyContactPrompt: boolean;
  timestamp: string;
}

export interface PatientProfile {
  id: string;
  name: string;
  age: number;
  gender: 'MALE' | 'FEMALE';
  heightCm: number;
  currentWeightKg: number;
  bmi: number;
  targetGlucoseMin: number; // default 70
  targetGlucoseMax: number; // default 130
  targetSystolicMax: number; // default 130
  targetDiastolicMax: number; // default 80
}

export interface ClinicalReportSummary {
  periodDays: number;
  patient: PatientProfile;
  glucose: {
    meanFasting: number;
    timeInRangePct: number; // 70-130 mg/dL
    hypoEventsCount: number; // < 70
    hyperEventsCount: number; // > 180
    readingsTotal: number;
  };
  bloodPressure: {
    systolicMean: number;
    diastolicMean: number;
    stage2AlertsCount: number; // >= 140/90
    crisisAlertsCount: number; // >= 180/120
  };
  lifestyle: {
    meanStepsPerDay: number;
    postprandialWalksWeekly: number;
    dietaryAdherencePct: number;
  };
  medicationAdherencePct: number;
  clinicalRecommendations: string[];
}

