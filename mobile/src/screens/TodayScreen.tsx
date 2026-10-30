import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  StyleSheet, 
  TouchableOpacity,
  Modal,
  TextInput
} from 'react-native';
import { AccessibleCard } from '../components/AccessibleCard';
import { BiometricCaptureModal } from '../components/BiometricCaptureModal';
import { MedicationItem } from '../components/MedicationItem';
import { ClinicalAlertModal } from '../components/ClinicalAlertModal';
import { DatabaseService } from '../services/DatabaseService';
import { ClinicalEngine } from '../services/ClinicalEngine';
import { PedometerService } from '../services/PedometerService';
import { 
  MetricType, 
  MeasurementContext, 
  BiometricReading, 
  Medication, 
  AdherenceLog, 
  StepActivity, 
  ClinicalAlert,
  PatientProfile
} from '../types';

export const TodayScreen: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false);
  const [activeMetricType, setActiveMetricType] = useState<MetricType>('GLUCOSE');
  const [activeAlert, setActiveAlert] = useState<ClinicalAlert | null>(null);

  const [patient, setPatient] = useState<PatientProfile | null>(null);
  const [biometrics, setBiometrics] = useState<BiometricReading[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [adherenceLogs, setAdherenceLogs] = useState<AdherenceLog[]>([]);
  const [stepActivity, setStepActivity] = useState<StepActivity | null>(null);

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [formFirstName, setFormFirstName] = useState('');
  const [formLastName, setFormLastName] = useState('');
  const [formAge, setFormAge] = useState('');
  const [formHeight, setFormHeight] = useState('');
  const [formWeight, setFormWeight] = useState('');

  const loadData = async () => {
    const pat = await DatabaseService.getPatient();
    const bios = await DatabaseService.getBiometrics();
    const meds = await DatabaseService.getMedications();
    const adhs = await DatabaseService.getAdherenceLogs();
    const steps = await DatabaseService.getStepActivity();

    setPatient(pat);
    setBiometrics(bios);
    setMedications(meds);
    setAdherenceLogs(adhs);
    setStepActivity(steps);

    setFormFirstName(pat.firstName);
    setFormLastName(pat.lastName);
    setFormAge(pat.age.toString());
    setFormHeight(pat.heightCm.toString());
    setFormWeight(pat.currentWeightKg.toString());
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenCapture = (type: MetricType) => {
    setActiveMetricType(type);
    setModalVisible(true);
  };

  const handleSaveProfile = async () => {
    const updated = await DatabaseService.updatePatientProfile({
      firstName: formFirstName,
      lastName: formLastName,
      age: parseInt(formAge, 10) || patient?.age,
      heightCm: parseFloat(formHeight) || patient?.heightCm,
      currentWeightKg: parseFloat(formWeight) || patient?.currentWeightKg,
    });
    setPatient(updated);
    setIsEditingProfile(false);
  };

  const handleConfirmReading = async (
    type: MetricType,
    primary: number,
    secondary?: number,
    context?: MeasurementContext
  ) => {
    const newReading = await DatabaseService.addBiometricReading({
      patientId: 'pat-001',
      metricType: type,
      valuePrimary: primary,
      valueSecondary: secondary,
      context: context || 'FASTING',
      captureMethod: 'OCR_CAMERA',
      timestamp: new Date().toISOString(),
      isAlert: false,
    });

    // Evaluate with Clinical Rule Engine
    let alert: ClinicalAlert | null = null;
    if (type === 'GLUCOSE') {
      alert = ClinicalEngine.evaluateGlucose(newReading);
    } else if (type === 'BLOOD_PRESSURE') {
      alert = ClinicalEngine.evaluateBloodPressure(newReading);
    }

    if (alert) {
      newReading.isAlert = true;
      setActiveAlert(alert);
    }

    loadData();
  };

  const handleTakeMedication = async (medicationId: string) => {
    await DatabaseService.recordMedicationTaken(medicationId);
    loadData();
  };

  const handleRecordWalk = async () => {
    const updated = await DatabaseService.recordPostprandialWalk();
    setStepActivity({ ...updated });
  };

  const latestGlucose = biometrics.find(b => b.metricType === 'GLUCOSE');
  const latestBP = biometrics.find(b => b.metricType === 'BLOOD_PRESSURE');

  const pedometerGuidance = PedometerService.getPostprandialGuidance(
    30, 
    stepActivity?.postprandialWalksCompleted || 0
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header Bar */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerGreeting}>
            Hola, {patient?.firstName || 'Ramón'}
          </Text>
          <Text style={styles.headerDate}>
            {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}
          </Text>
        </View>
        <TouchableOpacity 
          style={styles.profileBadgeBtn}
          onPress={() => setIsEditingProfile(true)}
          accessibilityLabel="Editar ficha y datos del paciente"
        >
          <Text style={styles.profileBadgeBtnText}>👤 Mi Ficha</Text>
        </TouchableOpacity>
      </View>

      {/* TARJETA 0: DATOS DE LA PERSONA Y ESTADO PONDERAL */}
      <AccessibleCard
        title={`${patient?.name || 'Ramón García Fernández'}`}
        subtitle={`Edad: ${patient?.age || 58} años • Estatura: ${patient?.heightCm || 172} cm`}
        badgeText={patient?.bmiCategory || 'Sobrepeso'}
        badgeColor={patient && patient.bmi < 25 ? '#16A34A' : '#EA580C'}
      >
        <View style={styles.profileSummaryRow}>
          <View style={styles.profileSummaryCol}>
            <Text style={styles.profileMetricLabel}>Peso Actual:</Text>
            <Text style={styles.profileMetricVal}>{patient?.currentWeightKg || 84.5} kg</Text>
          </View>
          <View style={styles.profileSummaryCol}>
            <Text style={styles.profileMetricLabel}>Índice Masa Corporal:</Text>
            <Text style={styles.profileMetricVal}>IMC {patient?.bmi || 28.56}</Text>
          </View>
        </View>

        <View style={styles.profileBtnRow}>
          <TouchableOpacity
            style={styles.scalePhotoBtn}
            onPress={() => handleOpenCapture('WEIGHT')}
            accessibilityRole="button"
            accessibilityLabel="Fotografiar báscula para registrar peso y recalcular IMC"
          >
            <Text style={styles.scalePhotoBtnText}>📸 FOTO BÁSCULA (ACTUALIZAR)</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.editProfileBtn}
            onPress={() => setIsEditingProfile(true)}
            accessibilityRole="button"
            accessibilityLabel="Editar datos personales"
          >
            <Text style={styles.editProfileBtnText}>✏️ EDITAR DATOS</Text>
          </TouchableOpacity>
        </View>
      </AccessibleCard>

      {/* TARJETA 1: ENTRADA BIOMÉTRICA CON HARDWARE NATIVO (OCR EN 2 TOQUES) */}
      <AccessibleCard 
        title="Mediciones del Día" 
        subtitle="Fotografíe la pantalla de su aparato para lectura automática"
        badgeText="OCR Local"
        badgeColor="#0D6EFD"
      >
        <View style={styles.biometricButtonRow}>
          <TouchableOpacity
            style={[styles.bioActionButton, styles.bioGlucoseBtn]}
            onPress={() => handleOpenCapture('GLUCOSE')}
            accessibilityRole="button"
            accessibilityLabel="Fotografiar glucómetro"
          >
            <Text style={styles.bioBtnIcon}>🩸</Text>
            <Text style={styles.bioBtnTitle}>GLUCÓMETRO</Text>
            <Text style={styles.bioBtnSub}>
              {latestGlucose ? `${latestGlucose.valuePrimary} mg/dL` : '114 mg/dL'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.bioActionButton, styles.bioBpBtn]}
            onPress={() => handleOpenCapture('BLOOD_PRESSURE')}
            accessibilityRole="button"
            accessibilityLabel="Fotografiar tensiómetro digital"
          >
            <Text style={styles.bioBtnIcon}>💓</Text>
            <Text style={styles.bioBtnTitle}>TENSIÓMETRO</Text>
            <Text style={styles.bioBtnSub}>
              {latestBP ? `${latestBP.valuePrimary}/${latestBP.valueSecondary} mmHg` : '124/82 mmHg'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.bioActionButton, styles.bioScaleBtn]}
            onPress={() => handleOpenCapture('WEIGHT')}
            accessibilityRole="button"
            accessibilityLabel="Fotografiar báscula digital"
          >
            <Text style={styles.bioBtnIcon}>⚖️</Text>
            <Text style={styles.bioBtnTitle}>BÁSCULA</Text>
            <Text style={styles.bioBtnSub}>
              {patient?.currentWeightKg || 84.5} kg
            </Text>
          </TouchableOpacity>
        </View>
      </AccessibleCard>

      {/* TARJETA 2: GESTOR DE MEDICACIÓN Y ADHERENCIA */}
      <AccessibleCard
        title="Medicación Pautada"
        subtitle="Confirme sus tomas con un solo toque de pantalla"
        badgeText="Adherencia"
        badgeColor="#16A34A"
      >
        {medications.map((med) => {
          const isTaken = adherenceLogs.some(
            (log) => log.medicationId === med.id && log.status === 'TAKEN_ON_TIME'
          );
          return (
            <MedicationItem
              key={med.id}
              medication={med}
              isTaken={isTaken}
              onTakeDose={handleTakeMedication}
            />
          );
        })}
      </AccessibleCard>

      {/* TARJETA 3: SENSORES DE MOVIMIENTO & PASEOS POSPRANDIALES */}
      <AccessibleCard
        title="Actividad Anti-sedentarismo"
        subtitle="Modulación de glucemia mediante caminata pasiva"
        badgeText="Podómetro"
        badgeColor="#8B5CF6"
      >
        <View style={styles.stepsStatsBox}>
          <View style={styles.stepNumbers}>
            <Text style={styles.stepCurrentText}>{stepActivity?.stepsCount.toLocaleString()} </Text>
            <Text style={styles.stepTargetText}>/ {stepActivity?.targetSteps.toLocaleString()} pasos</Text>
          </View>
          <Text style={styles.stepPct}>
            {stepActivity ? Math.min(100, Math.round((stepActivity.stepsCount / stepActivity.targetSteps) * 100)) : 0}%
          </Text>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressBarBg}>
          <View 
            style={[
              styles.progressBarActive, 
              { 
                width: `${Math.min(100, ((stepActivity?.stepsCount || 0) / (stepActivity?.targetSteps || 4000)) * 100)}%` 
              }
            ]} 
          />
        </View>

        <View style={styles.postprandialAdviceBox}>
          <Text style={styles.postprandialTitle}>💡 {pedometerGuidance.title}</Text>
          <Text style={styles.postprandialDesc}>{pedometerGuidance.message}</Text>
          <TouchableOpacity 
            style={styles.walkButton} 
            onPress={handleRecordWalk}
            accessibilityRole="button"
            accessibilityLabel="Registrar paseo suave posprandial de 15 minutos"
          >
            <Text style={styles.walkButtonText}>👟 HE DADO UN PASEO DE 15 MIN</Text>
          </TouchableOpacity>
        </View>
      </AccessibleCard>

      {/* TARJETA 4: PRÓXIMA COMIDA CARDIOPROTECTORA */}
      <AccessibleCard
        title="Chef Terapéutico: Almuerzo"
        subtitle="Baja carga glucémica y rico en Omega-3"
      >
        <Text style={styles.recipePreviewTitle}>Salmón Salvaje con Brócoli al Vapor y AOVE</Text>
        <Text style={styles.recipePreviewStats}>⏱ 12 min • 4.8g Fibra Soluble • &lt; 150 mg Sodio</Text>
        <Text style={styles.recipeStepHighlight}>
          1. Cortar el brócoli y cocinar 8 min al vapor con el salmón. Aliñar con AOVE.
        </Text>
      </AccessibleCard>

      {/* Modal para Editar Datos Personales y Ponderales */}
      <Modal visible={isEditingProfile} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.profileModalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Datos Personales y Ponderales</Text>
              <TouchableOpacity onPress={() => setIsEditingProfile(false)}>
                <Text style={styles.closeBtn}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView>
              <Text style={styles.inputLabel}>Nombre:</Text>
              <TextInput
                style={styles.textInput}
                value={formFirstName}
                onChangeText={setFormFirstName}
                placeholder="Nombre"
              />

              <Text style={styles.inputLabel}>Apellidos:</Text>
              <TextInput
                style={styles.textInput}
                value={formLastName}
                onChangeText={setFormLastName}
                placeholder="Apellidos"
              />

              <View style={styles.formRow}>
                <View style={styles.formCol}>
                  <Text style={styles.inputLabel}>Edad (años):</Text>
                  <TextInput
                    style={styles.textInput}
                    value={formAge}
                    onChangeText={setFormAge}
                    keyboardType="numeric"
                  />
                </View>
                <View style={styles.formCol}>
                  <Text style={styles.inputLabel}>Estatura (cm):</Text>
                  <TextInput
                    style={styles.textInput}
                    value={formHeight}
                    onChangeText={setFormHeight}
                    keyboardType="numeric"
                  />
                </View>
              </View>

              <Text style={styles.inputLabel}>Peso Actual (kg):</Text>
              <TextInput
                style={styles.textInput}
                value={formWeight}
                onChangeText={setFormWeight}
                keyboardType="decimal-pad"
              />
              <Text style={styles.helperText}>
                * Nota: Puede actualizar el peso automáticamente fotografiando su báscula.
              </Text>

              <TouchableOpacity style={styles.saveProfileBtn} onPress={handleSaveProfile}>
                <Text style={styles.saveProfileBtnText}>GUARDAR DATOS</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Modales */}
      <BiometricCaptureModal
        visible={modalVisible}
        metricType={activeMetricType}
        onClose={() => setModalVisible(false)}
        onConfirmReading={handleConfirmReading}
      />

      <ClinicalAlertModal
        alert={activeAlert}
        onDismiss={() => setActiveAlert(null)}
      />
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  headerGreeting: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
  },
  headerDate: {
    fontSize: 14,
    color: '#64748B',
    textTransform: 'capitalize',
    marginTop: 2,
    fontWeight: '600',
  },
  statusIndicator: {
    backgroundColor: '#DCFCE7',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '800',
    color: '#166534',
  },
  profileBadgeBtn: {
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  profileBadgeBtnText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0D6EFD',
  },
  profileSummaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  profileSummaryCol: {
    flex: 1,
  },
  profileMetricLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  profileMetricVal: {
    fontSize: 18,
    fontWeight: '900',
    color: '#0F172A',
    marginTop: 2,
  },
  profileBtnRow: {
    flexDirection: 'row',
    gap: 8,
  },
  scalePhotoBtn: {
    flex: 1.3,
    backgroundColor: '#16A34A',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  scalePhotoBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 12,
  },
  editProfileBtn: {
    flex: 1,
    backgroundColor: '#0F172A',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  editProfileBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 12,
  },
  biometricButtonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  bioActionButton: {
    flex: 1,
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
  },
  bioGlucoseBtn: {
    backgroundColor: '#EFF6FF',
    borderColor: '#BFDBFE',
  },
  bioBpBtn: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FECACA',
  },
  bioScaleBtn: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  bioBtnIcon: {
    fontSize: 32,
    marginBottom: 6,
  },
  bioBtnTitle: {
    fontSize: 14,
    fontWeight: '900',
    color: '#0F172A',
    marginBottom: 4,
  },
  bioBtnSub: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
  },
  stepsStatsBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  stepNumbers: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  stepCurrentText: {
    fontSize: 28,
    fontWeight: '900',
    color: '#0F172A',
  },
  stepTargetText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#64748B',
  },
  stepPct: {
    fontSize: 18,
    fontWeight: '800',
    color: '#8B5CF6',
  },
  progressBarBg: {
    height: 12,
    backgroundColor: '#E2E8F0',
    borderRadius: 6,
    overflow: 'hidden',
    marginBottom: 16,
  },
  progressBarActive: {
    height: '100%',
    backgroundColor: '#8B5CF6',
  },
  postprandialAdviceBox: {
    backgroundColor: '#F3E8FF',
    padding: 14,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#8B5CF6',
  },
  postprandialTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#6B21A8',
    marginBottom: 4,
  },
  postprandialDesc: {
    fontSize: 13,
    color: '#581C87',
    lineHeight: 18,
    marginBottom: 10,
  },
  walkButton: {
    backgroundColor: '#6B21A8',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  walkButtonText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 13,
  },
  recipePreviewTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 4,
  },
  recipePreviewStats: {
    fontSize: 12,
    fontWeight: '700',
    color: '#166534',
    marginBottom: 8,
  },
  recipeStepHighlight: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.75)',
    justifyContent: 'flex-end',
  },
  profileModalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '85%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  closeBtn: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#64748B',
    padding: 6,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
    marginTop: 10,
    marginBottom: 4,
  },
  textInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1.5,
    borderColor: '#CBD5E1',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: '#0F172A',
  },
  formRow: {
    flexDirection: 'row',
    gap: 12,
  },
  formCol: {
    flex: 1,
  },
  helperText: {
    fontSize: 12,
    color: '#64748B',
    fontStyle: 'italic',
    marginTop: 6,
    marginBottom: 14,
  },
  saveProfileBtn: {
    backgroundColor: '#0D6EFD',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  saveProfileBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
  },
});

