import { 
  BiometricReading, 
  ClinicalAlert, 
  AdherenceLog, 
  Medication 
} from '../types';

export class ClinicalEngine {
  /**
   * Evaluates a glucose reading according to American Diabetes Association (ADA) guidelines.
   */
  public static evaluateGlucose(
    reading: BiometricReading
  ): ClinicalAlert | null {
    const value = reading.valuePrimary;

    if (value < 54) {
      return {
        id: `alert-glu-${Date.now()}`,
        severity: 'EMERGENCY',
        title: 'HIPOGLUCEMIA GRAVE (< 54 mg/dL)',
        description: `Lectura de ${value} mg/dL registrada. Existe riesgo inminente de deterioro neurológico.`,
        instructions: 
          'Tome de inmediato 15 gramos de glucosa de acción rápida (1 cucharada de miel, 150 ml de zumo o 3 terrones de azúcar). No se administre insulina. Si experimenta confusión, solicite auxilio médico inmediato.',
        requiresImmediateAction: true,
        emergencyCallPrompt: true,
        familyContactPrompt: true,
        timestamp: new Date().toISOString(),
      };
    }

    if (value < 70) {
      return {
        id: `alert-glu-${Date.now()}`,
        severity: 'CRITICAL',
        title: 'HIPOGLUCEMIA LEVE/MODERADA (< 70 mg/dL)',
        description: `Lectura de ${value} mg/dL registrada.`,
        instructions: 
          'Regla de los 15: Tome 15g de carbohidratos simples (medio vaso de zumo o agua con azúcar). Descanse sentado 15 minutos y vuelva a medir su glucosa con el glucómetro.',
        requiresImmediateAction: true,
        emergencyCallPrompt: false,
        familyContactPrompt: false,
        timestamp: new Date().toISOString(),
      };
    }

    if (value > 300) {
      return {
        id: `alert-glu-${Date.now()}`,
        severity: 'CRITICAL',
        title: 'HIPERGLUCEMIA SEVERA (> 300 mg/dL)',
        description: `Lectura de ${value} mg/dL registrada.`,
        instructions: 
          'Beba 2-3 vasos de agua sin azúcar. Verifique si ha olvidado su medicación antidiabética. Si nota náuseas, dolor abdominal o dificultad respiratoria, acuda a urgencias.',
        requiresImmediateAction: true,
        emergencyCallPrompt: false,
        familyContactPrompt: true,
        timestamp: new Date().toISOString(),
      };
    }

    if (reading.context === 'FASTING' && value > 140) {
      return {
        id: `alert-glu-${Date.now()}`,
        severity: 'WARNING',
        title: 'GLUCEMIA BASAL ELEVADA (> 140 mg/dL)',
        description: `Su nivel de glucosa en ayunas (${value} mg/dL) se sitúa por encima del rango óptimo (70-130 mg/dL).`,
        instructions: 
          'Priorice un desayuno sin azúcares libres ni harinas refinadas. Programe un paseo suave de 15 minutos después de desayunar.',
        requiresImmediateAction: false,
        emergencyCallPrompt: false,
        familyContactPrompt: false,
        timestamp: new Date().toISOString(),
      };
    }

    return null;
  }

  /**
   * Evaluates blood pressure reading according to European Society of Cardiology (ESC/ESH) guidelines.
   */
  public static evaluateBloodPressure(
    reading: BiometricReading,
    hasSymptoms: boolean = false
  ): ClinicalAlert | null {
    const sys = reading.valuePrimary;
    const dia = reading.valueSecondary || 0;

    // Hypertensive crisis (>= 180 or >= 120)
    if (sys >= 180 || dia >= 120) {
      if (hasSymptoms) {
        return {
          id: `alert-bp-${Date.now()}`,
          severity: 'EMERGENCY',
          title: 'EMERGENCIA HIPERTENSIVA (Sistólica ≥ 180 o Diastólica ≥ 120 con síntomas)',
          description: `Registro crítico: ${sys}/${dia} mmHg con sintomatología asociada.`,
          instructions: 
            'Riesgo cardiovascular agudo. Llame al 112 o trasládese al servicio de urgencias hospitalario más cercano de inmediato.',
          requiresImmediateAction: true,
          emergencyCallPrompt: true,
          familyContactPrompt: true,
          timestamp: new Date().toISOString(),
        };
      }

      return {
        id: `alert-bp-${Date.now()}`,
        severity: 'CRITICAL',
        title: 'URGENCIA HIPERTENSIVA (Sistólica ≥ 180 o Diastólica ≥ 120)',
        description: `Registro crítico de ${sys}/${dia} mmHg.`,
        instructions: 
          'Permanezca en reposo sentado en un ambiente tranquilo y sin ruidos durante 15 minutos sin cruzar las piernas. Repita la medición. Si persiste en este nivel, contacte con su médico de guardia.',
        requiresImmediateAction: true,
        emergencyCallPrompt: false,
        familyContactPrompt: false,
        timestamp: new Date().toISOString(),
      };
    }

    // Stage 1 or 2 Hypertension (> 140 or > 90)
    if (sys >= 140 || dia >= 90) {
      return {
        id: `alert-bp-${Date.now()}`,
        severity: 'WARNING',
        title: 'PRESIÓN ARTERIAL ELEVADA (≥ 140/90 mmHg)',
        description: `Presión actual: ${sys}/${dia} mmHg (Por encima del objetivo cardioprotector < 130/80 mmHg).`,
        instructions: 
          'Compruebe si ha tomado su medicación antihipertensiva pautada de hoy. Limite estrictamente el consumo de sal en las próximas comidas y evite el café o bebidas estimulantes.',
        requiresImmediateAction: false,
        emergencyCallPrompt: false,
        familyContactPrompt: false,
        timestamp: new Date().toISOString(),
      };
    }

    // Hypotension (< 90/60)
    if (sys < 90 || dia < 60) {
      return {
        id: `alert-bp-${Date.now()}`,
        severity: 'WARNING',
        title: 'HIPOTENSIÓN ARTERIAL (< 90/60 mmHg)',
        description: `Presión baja detectada: ${sys}/${dia} mmHg.`,
        instructions: 
          'Tome un vaso de agua o una infusión ligera. Si siente mareo o inestabilidad, túmbese con las piernas ligeramente elevadas para favorecer el retorno venoso.',
        requiresImmediateAction: false,
        emergencyCallPrompt: false,
        familyContactPrompt: false,
        timestamp: new Date().toISOString(),
      };
    }

    return null;
  }

  /**
   * Analyzes cross-correlation between medication adherence in the past 24-48 hours
   * and current blood pressure / glucose deviations.
   */
  public static checkPharmacologicalCorrelation(
    recentReadings: BiometricReading[],
    medications: Medication[],
    adherenceLogs: AdherenceLog[]
  ): string | null {
    const past48Hours = Date.now() - 48 * 60 * 60 * 1000;
    
    // Check missed antihypertensive
    const antihypertensive = medications.filter(m => m.therapeuticClass === 'ANTIHYPERTENSIVE');
    const missedAntihypertensives = adherenceLogs.filter(log => {
      const isAntiHyp = antihypertensive.some(m => m.id === log.medicationId);
      const isRecent = new Date(log.scheduledTime).getTime() >= past48Hours;
      return isAntiHyp && isRecent && (log.status === 'MISSED' || log.status === 'SKIPPED');
    });

    const recentHighBP = recentReadings.find(r => 
      r.metricType === 'BLOOD_PRESSURE' && 
      r.valuePrimary >= 140 && 
      new Date(r.timestamp).getTime() >= past48Hours
    );

    if (missedAntihypertensives.length > 0 && recentHighBP) {
      return `Se detecta un repunte en su presión arterial (${recentHighBP.valuePrimary}/${recentHighBP.valueSecondary || 0} mmHg) tras haber omitido dosis de su tratamiento antihipertensivo en las últimas 48 horas. No duplique la siguiente dosis; continúe con la pauta ordinaria prescrita.`;
    }

    // Check missed antidiabetic
    const antidiabetics = medications.filter(m => m.therapeuticClass === 'ANTIDIABETIC');
    const missedAntidiabetics = adherenceLogs.filter(log => {
      const isAntiDia = antidiabetics.some(m => m.id === log.medicationId);
      const isRecent = new Date(log.scheduledTime).getTime() >= past48Hours;
      return isAntiDia && isRecent && (log.status === 'MISSED' || log.status === 'SKIPPED');
    });

    const recentHighGlucose = recentReadings.find(r =>
      r.metricType === 'GLUCOSE' &&
      r.valuePrimary > 150 &&
      new Date(r.timestamp).getTime() >= past48Hours
    );

    if (missedAntidiabetics.length > 0 && recentHighGlucose) {
      return `Se observa una glucemia elevada (${recentHighGlucose.valuePrimary} mg/dL) vinculada a dosis pendientes de su medicación antidiabética. Mantenga hidratación adecuada y retome su pauta habitual en la próxima toma.`;
    }

    return null;
  }
}

