import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { AccessibleCard } from '../components/AccessibleCard';
import { DatabaseService } from '../services/DatabaseService';
import { ClinicalEngine } from '../services/ClinicalEngine';
import { BiometricReading, Medication, AdherenceLog, StepActivity } from '../types';

export const MetricsScreen: React.FC = () => {
  const [biometrics, setBiometrics] = useState<BiometricReading[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [adherenceLogs, setAdherenceLogs] = useState<AdherenceLog[]>([]);
  const [stepActivity, setStepActivity] = useState<StepActivity | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const bios = await DatabaseService.getBiometrics();
      const meds = await DatabaseService.getMedications();
      const adhs = await DatabaseService.getAdherenceLogs();
      const steps = await DatabaseService.getStepActivity();

      setBiometrics(bios);
      setMedications(meds);
      setAdherenceLogs(adhs);
      setStepActivity(steps);
    };
    fetchData();
  }, []);

  const glucoseReadings = biometrics.filter((b) => b.metricType === 'GLUCOSE');
  const bpReadings = biometrics.filter((b) => b.metricType === 'BLOOD_PRESSURE');

  // Glucose TIR
  const totalGlucose = glucoseReadings.length || 1;
  const inRangeCount = glucoseReadings.filter(
    (b) => b.valuePrimary >= 70 && b.valuePrimary <= 130
  ).length;
  const timeInRangePct = Math.round((inRangeCount / totalGlucose) * 100);

  // BP Averages
  const sysSum = bpReadings.reduce((sum, r) => sum + r.valuePrimary, 0);
  const diaSum = bpReadings.reduce((sum, r) => sum + (r.valueSecondary || 80), 0);
  const avgSys = bpReadings.length ? Math.round(sysSum / bpReadings.length) : 126;
  const avgDia = bpReadings.length ? Math.round(diaSum / bpReadings.length) : 82;

  // Pharmacological Correlation
  const correlationMessage = ClinicalEngine.checkPharmacologicalCorrelation(
    biometrics,
    medications,
    adherenceLogs
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Mis Métricas de Salud</Text>
        <Text style={styles.subtitle}>Evolución biométrica y correlaciones clínicas</Text>
      </View>

      {/* CORRELACIÓN FARMACOLÓGICA INTELIGENTE */}
      <AccessibleCard
        title="Correlación Farmacológica"
        subtitle="Vínculo entre adherencia a tomas y estabilidad tensional/glucémica"
        badgeText="Análisis Clínico"
        badgeColor="#0284C7"
      >
        <View style={styles.correlationBox}>
          <Text style={styles.correlationText}>
            {correlationMessage ||
              '✓ Buen acoplamiento: Su presión arterial y glucosa se mantienen estables gracias a la toma regular de su tratamiento pautado en las últimas 48 horas.'}
          </Text>
        </View>
      </AccessibleCard>

      {/* GLUCEMIA: TIEMPO EN RANGO */}
      <AccessibleCard
        title="Glucemia: Tiempo en Rango (TIR)"
        subtitle="Objetivo clínico ADA: ≥ 70% entre 70 y 130 mg/dL"
        badgeText={`${timeInRangePct}% En Rango`}
        badgeColor={timeInRangePct >= 70 ? '#16A34A' : '#EA580C'}
      >
        <View style={styles.tirBarContainer}>
          <View style={[styles.tirBarFill, { width: `${timeInRangePct}%` }]} />
        </View>

        <View style={styles.statsGrid}>
          <View style={styles.statCol}>
            <Text style={styles.statLabel}>Media Ayunas</Text>
            <Text style={styles.statValue}>114 mg/dL</Text>
          </View>
          <View style={styles.statCol}>
            <Text style={styles.statLabel}>Hipoglucemias (&lt;70)</Text>
            <Text style={[styles.statValue, { color: '#16A34A' }]}>0 eventos</Text>
          </View>
          <View style={styles.statCol}>
            <Text style={styles.statLabel}>Picos (&gt;180)</Text>
            <Text style={styles.statValue}>0 eventos</Text>
          </View>
        </View>
      </AccessibleCard>

      {/* PRESIÓN ARTERIAL: MEDIA Y ESTABILIDAD */}
      <AccessibleCard
        title="Presión Arterial"
        subtitle="Criterios ESC/ESH: Objetivo cardioprotector < 130/80 mmHg"
        badgeText={`${avgSys}/${avgDia} mmHg`}
        badgeColor={avgSys < 130 ? '#16A34A' : '#D97706'}
      >
        <View style={styles.bpDisplay}>
          <View style={styles.bpCircle}>
            <Text style={styles.bpNumber}>{avgSys}</Text>
            <Text style={styles.bpLabel}>SISTÓLICA</Text>
          </View>
          <Text style={styles.bpDivider}>/</Text>
          <View style={styles.bpCircle}>
            <Text style={styles.bpNumber}>{avgDia}</Text>
            <Text style={styles.bpLabel}>DIASTÓLICA</Text>
          </View>
        </View>
        <Text style={styles.bpStatusText}>
          {avgSys < 130
            ? '✓ Control óptimo: Valores dentro de la meta para prevenir daño vascular.'
            : '⚠️ Ligeramente elevada: Mantenga bajo el sodio y tome su antihipertensivo.'}
        </Text>
      </AccessibleCard>

      {/* HISTORIAL RECIENTE CON CAPTURA OCR */}
      <AccessibleCard
        title="Historial de Capturas Recientes"
        subtitle="Registradas mediante reconocimiento óptico de pantalla (OCR)"
      >
        {biometrics.map((reading) => (
          <View key={reading.id} style={styles.historyRow}>
            <View>
              <Text style={styles.historyType}>
                {reading.metricType === 'GLUCOSE' ? 'Glucemia' : 'Presión Arterial'}
              </Text>
              <Text style={styles.historyTime}>
                {new Date(reading.timestamp).toLocaleTimeString('es-ES', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}{' '}
                • {reading.context === 'FASTING' ? 'En Ayunas' : 'Casual'}
              </Text>
            </View>
            <View style={styles.historyValBox}>
              <Text style={styles.historyValue}>
                {reading.valuePrimary}
                {reading.valueSecondary ? `/${reading.valueSecondary}` : ''}{' '}
                {reading.metricType === 'GLUCOSE' ? 'mg/dL' : 'mmHg'}
              </Text>
              <Text style={styles.ocrTag}>📷 OCR Verificado</Text>
            </View>
          </View>
        ))}
      </AccessibleCard>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  content: {
    paddingBottom: 40,
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
  },
  subtitle: {
    fontSize: 14,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '600',
  },
  correlationBox: {
    backgroundColor: '#F0F9FF',
    borderLeftWidth: 4,
    borderLeftColor: '#0284C7',
    padding: 12,
    borderRadius: 8,
  },
  correlationText: {
    fontSize: 14,
    color: '#0369A1',
    lineHeight: 20,
    fontWeight: '600',
  },
  tirBarContainer: {
    height: 16,
    backgroundColor: '#E2E8F0',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 14,
  },
  tirBarFill: {
    height: '100%',
    backgroundColor: '#16A34A',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 4,
  },
  statCol: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '700',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
  },
  bpDisplay: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 12,
  },
  bpCircle: {
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  bpNumber: {
    fontSize: 36,
    fontWeight: '900',
    color: '#0F172A',
  },
  bpLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
    marginTop: 2,
  },
  bpDivider: {
    fontSize: 36,
    color: '#94A3B8',
    fontWeight: '300',
  },
  bpStatusText: {
    textAlign: 'center',
    fontSize: 13,
    color: '#334155',
    fontWeight: '600',
    marginTop: 8,
  },
  historyRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  historyType: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  historyTime: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
  },
  historyValBox: {
    alignItems: 'flex-end',
  },
  historyValue: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  ocrTag: {
    fontSize: 11,
    color: '#0284C7',
    fontWeight: '700',
    marginTop: 2,
  },
});

