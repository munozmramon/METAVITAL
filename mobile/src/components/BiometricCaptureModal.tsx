import React, { useState } from 'react';
import { 
  View, 
  Text, 
  Modal, 
  StyleSheet, 
  TouchableOpacity, 
  ActivityIndicator, 
  TextInput 
} from 'react-native';
import { MetricType, MeasurementContext } from '../types';
import { OCRService } from '../services/OCRService';

interface BiometricCaptureModalProps {
  visible: boolean;
  metricType: MetricType;
  onClose: () => void;
  onConfirmReading: (
    metricType: MetricType, 
    primary: number, 
    secondary?: number, 
    context?: MeasurementContext
  ) => void;
}

export const BiometricCaptureModal: React.FC<BiometricCaptureModalProps> = ({
  visible,
  metricType,
  onClose,
  onConfirmReading,
}) => {
  const [step, setStep] = useState<'CAPTURE' | 'PROCESSING' | 'CONFIRM'>('CAPTURE');
  const [primaryValue, setPrimaryValue] = useState<number>(metricType === 'GLUCOSE' ? 114 : 124);
  const [secondaryValue, setSecondaryValue] = useState<number>(metricType === 'BLOOD_PRESSURE' ? 82 : 0);
  const [context, setContext] = useState<MeasurementContext>('FASTING');
  const [confidence, setConfidence] = useState<number>(0.96);

  const isGlucose = metricType === 'GLUCOSE';
  const isWeight = metricType === 'WEIGHT';
  const isBP = metricType === 'BLOOD_PRESSURE';

  const modalTitle = isGlucose 
    ? 'Escaneo de Glucómetro' 
    : isWeight 
    ? 'Escaneo de Báscula Digital' 
    : 'Escaneo de Tensiómetro';

  const targetPrompt = isGlucose
    ? 'Encuadre la pantalla del glucómetro aquí'
    : isWeight
    ? 'Encuadre la pantalla digital de la báscula aquí'
    : 'Encuadre la pantalla del tensiómetro digital aquí';

  const targetSub = isGlucose
    ? 'Detección óptica automática (mg/dL)'
    : isWeight
    ? 'Detección óptica de peso corporal (kg) y recálculo de IMC'
    : 'Detección óptica de presión (mmHg) y pulso';

  const handleSimulateOCRScan = async () => {
    setStep('PROCESSING');
    
    // Simulate optical scanning with ML Kit
    setTimeout(async () => {
      const result = await OCRService.processDevicePhoto('mock_frame.jpg', metricType);
      setPrimaryValue(result.primaryValue);
      if (result.secondaryValue) setSecondaryValue(result.secondaryValue);
      setConfidence(result.confidence);
      setStep('CONFIRM');
    }, 400);
  };

  const handleSave = () => {
    onConfirmReading(
      metricType, 
      primaryValue, 
      isGlucose ? undefined : secondaryValue, 
      context
    );
    setStep('CAPTURE');
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.modalContent}>
          {/* Header */}
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>
              {modalTitle}
            </Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          {step === 'CAPTURE' && (
            <View style={styles.stepContainer}>
              <View style={styles.cameraViewport}>
                <View style={styles.scanTargetBox}>
                  <Text style={styles.targetInstruction}>
                    {targetPrompt}
                  </Text>
                  <Text style={styles.targetSub}>
                    {targetSub}
                  </Text>
                </View>
              </View>

              <TouchableOpacity 
                style={styles.primaryActionButton} 
                onPress={handleSimulateOCRScan}
                accessibilityRole="button"
                accessibilityLabel="Fotografiar pantalla y extraer valor"
              >
                <Text style={styles.primaryActionButtonText}>
                  📸 FOTOGRAFIAR PANTALLA
                </Text>
              </TouchableOpacity>
            </View>
          )}

          {step === 'PROCESSING' && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#0D6EFD" />
              <Text style={styles.loadingText}>Procesando pantalla digital con OCR local...</Text>
              <Text style={styles.loadingSub}>Verificación en el dispositivo (100% privado y seguro)</Text>
            </View>
          )}

          {step === 'CONFIRM' && (
            <View style={styles.stepContainer}>
              <View style={styles.detectionNotice}>
                <Text style={styles.detectionNoticeText}>
                  ✓ Valor extraído con {Math.round(confidence * 100)}% de precisión óptica
                </Text>
              </View>

              {isGlucose ? (
                <View style={styles.valueDisplayBox}>
                  <Text style={styles.valueLabel}>Glucemia detectada:</Text>
                  <View style={styles.numberRow}>
                    <TextInput
                      style={styles.largeInput}
                      value={primaryValue.toString()}
                      onChangeText={(val) => setPrimaryValue(parseFloat(val) || 0)}
                      keyboardType="numeric"
                      accessibilityLabel="Valor de glucosa en mg por decilitro"
                    />
                    <Text style={styles.unitText}>mg/dL</Text>
                  </View>
                </View>
              ) : isWeight ? (
                <View style={styles.valueDisplayBox}>
                  <Text style={styles.valueLabel}>Peso detectado en báscula:</Text>
                  <View style={styles.numberRow}>
                    <TextInput
                      style={styles.largeInput}
                      value={primaryValue.toString()}
                      onChangeText={(val) => setPrimaryValue(parseFloat(val) || 0)}
                      keyboardType="decimal-pad"
                      accessibilityLabel="Valor de peso en kilogramos"
                    />
                    <Text style={styles.unitText}>kg</Text>
                  </View>
                  <Text style={styles.subtext}>Se recalculará automáticamente su IMC</Text>
                </View>
              ) : (
                <View style={styles.valueDisplayBox}>
                  <Text style={styles.valueLabel}>Presión Arterial detectada:</Text>
                  <View style={styles.numberRow}>
                    <TextInput
                      style={styles.largeInput}
                      value={primaryValue.toString()}
                      onChangeText={(val) => setPrimaryValue(parseInt(val, 10) || 0)}
                      keyboardType="numeric"
                    />
                    <Text style={styles.slashText}>/</Text>
                    <TextInput
                      style={styles.largeInput}
                      value={secondaryValue.toString()}
                      onChangeText={(val) => setSecondaryValue(parseInt(val, 10) || 0)}
                      keyboardType="numeric"
                    />
                    <Text style={styles.unitText}>mmHg</Text>
                  </View>
                  <Text style={styles.subtext}>Sistólica / Diastólica</Text>
                </View>
              )}

              {/* Context Selector: 1-touch */}
              <View style={styles.contextContainer}>
                <Text style={styles.contextLabel}>Momento de la medición:</Text>
                <View style={styles.contextRow}>
                  <TouchableOpacity
                    style={[styles.contextChip, context === 'FASTING' && styles.contextChipActive]}
                    onPress={() => setContext('FASTING')}
                  >
                    <Text style={[styles.contextChipText, context === 'FASTING' && styles.contextChipTextActive]}>
                      En Ayunas
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.contextChip, context === 'POSTPRANDIAL' && styles.contextChipActive]}
                    onPress={() => setContext('POSTPRANDIAL')}
                  >
                    <Text style={[styles.contextChipText, context === 'POSTPRANDIAL' && styles.contextChipTextActive]}>
                      Post-comida
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.contextChip, context === 'RANDOM' && styles.contextChipActive]}
                    onPress={() => setContext('RANDOM')}
                  >
                    <Text style={[styles.contextChipText, context === 'RANDOM' && styles.contextChipTextActive]}>
                      Casual
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* Confirm Button: 2nd tap of the whole flow */}
              <TouchableOpacity 
                style={styles.confirmButton} 
                onPress={handleSave}
                accessibilityRole="button"
                accessibilityLabel="Confirmar y registrar medición"
              >
                <Text style={styles.confirmButtonText}>✓ CONFIRMAR Y GUARDAR</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.75)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    minHeight: 460,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0F172A',
  },
  closeButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#F1F5F9',
  },
  closeButtonText: {
    fontSize: 18,
    color: '#475569',
    fontWeight: '700',
  },
  stepContainer: {
    flex: 1,
  },
  cameraViewport: {
    height: 220,
    backgroundColor: '#0F172A',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    marginBottom: 20,
  },
  scanTargetBox: {
    borderWidth: 2.5,
    borderColor: '#38BDF8',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    width: '90%',
  },
  targetInstruction: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 6,
  },
  targetSub: {
    color: '#94A3B8',
    fontSize: 12,
    textAlign: 'center',
  },
  primaryActionButton: {
    backgroundColor: '#0D6EFD',
    borderRadius: 14,
    paddingVertical: 18,
    alignItems: 'center',
    minHeight: 56,
  },
  primaryActionButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '800',
  },
  loadingContainer: {
    paddingVertical: 60,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 18,
    fontSize: 16,
    fontWeight: '700',
    color: '#0F172A',
  },
  loadingSub: {
    marginTop: 6,
    fontSize: 13,
    color: '#64748B',
  },
  detectionNotice: {
    backgroundColor: '#DCFCE7',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  detectionNoticeText: {
    color: '#166534',
    fontWeight: '700',
    fontSize: 14,
  },
  valueDisplayBox: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1.5,
    borderColor: '#CBD5E1',
    borderRadius: 16,
    padding: 18,
    alignItems: 'center',
    marginBottom: 16,
  },
  valueLabel: {
    fontSize: 15,
    color: '#475569',
    fontWeight: '600',
    marginBottom: 8,
  },
  numberRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  largeInput: {
    fontSize: 44,
    fontWeight: '900',
    color: '#0F172A',
    minWidth: 80,
    textAlign: 'center',
    borderBottomWidth: 2,
    borderBottomColor: '#0D6EFD',
  },
  slashText: {
    fontSize: 40,
    fontWeight: '600',
    color: '#94A3B8',
    marginHorizontal: 8,
  },
  unitText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#475569',
    marginLeft: 10,
  },
  subtext: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 4,
  },
  contextContainer: {
    marginBottom: 20,
  },
  contextLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 8,
  },
  contextRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  contextChip: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 6,
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    marginHorizontal: 3,
    alignItems: 'center',
  },
  contextChipActive: {
    backgroundColor: '#0D6EFD',
  },
  contextChipText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
  },
  contextChipTextActive: {
    color: '#FFFFFF',
  },
  confirmButton: {
    backgroundColor: '#16A34A',
    borderRadius: 14,
    paddingVertical: 18,
    alignItems: 'center',
    minHeight: 56,
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '800',
  },
});

