import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity } from 'react-native';
import { ClinicalAlert } from '../types';

interface ClinicalAlertModalProps {
  alert: ClinicalAlert | null;
  onDismiss: () => void;
}

export const ClinicalAlertModal: React.FC<ClinicalAlertModalProps> = ({
  alert,
  onDismiss,
}) => {
  if (!alert) return null;

  const isEmergency = alert.severity === 'EMERGENCY';
  const isCritical = alert.severity === 'CRITICAL';

  const headerColor = isEmergency ? '#DC2626' : isCritical ? '#EA580C' : '#D97706';

  return (
    <Modal visible={true} animationType="fade" transparent={true} onRequestClose={onDismiss}>
      <View style={styles.overlay}>
        <View style={styles.modalCard}>
          <View style={[styles.headerStrip, { backgroundColor: headerColor }]}>
            <Text style={styles.headerIcon}>
              {isEmergency ? '🚨' : isCritical ? '⚠️' : 'ℹ️'}
            </Text>
            <Text style={styles.headerTitle}>{alert.title}</Text>
          </View>

          <View style={styles.body}>
            <Text style={styles.description}>{alert.description}</Text>

            <View style={styles.instructionBox}>
              <Text style={styles.instructionHeading}>Pautas Médicas Inmediatas:</Text>
              <Text style={styles.instructionText}>{alert.instructions}</Text>
            </View>

            {alert.emergencyCallPrompt && (
              <TouchableOpacity
                style={styles.emergencyCallButton}
                onPress={() => alert('Marcando al servicio de emergencias médicas 112...')}
                accessibilityRole="button"
                accessibilityLabel="Llamar a emergencias médicas 112"
              >
                <Text style={styles.emergencyCallButtonText}>📞 LLAMAR AL 112 (EMERGENCIAS)</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity 
              style={[styles.dismissButton, alert.emergencyCallPrompt && styles.dismissButtonSec]} 
              onPress={onDismiss}
              accessibilityRole="button"
              accessibilityLabel="Entendido, cerrar alerta"
            >
              <Text style={[styles.dismissButtonText, alert.emergencyCallPrompt && styles.dismissButtonTextSec]}>
                HE LEÍDO Y ENTIENDO LAS INSTRUCCIONES
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    width: '100%',
    maxWidth: 420,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#E2E8F0',
  },
  headerStrip: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerIcon: {
    fontSize: 26,
    marginRight: 10,
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '900',
    flex: 1,
  },
  body: {
    padding: 20,
  },
  description: {
    fontSize: 16,
    color: '#1E293B',
    lineHeight: 22,
    fontWeight: '600',
    marginBottom: 16,
  },
  instructionBox: {
    backgroundColor: '#FEF3C7',
    borderLeftWidth: 4,
    borderLeftColor: '#D97706',
    borderRadius: 8,
    padding: 14,
    marginBottom: 20,
  },
  instructionHeading: {
    fontSize: 14,
    fontWeight: '800',
    color: '#92400E',
    marginBottom: 6,
  },
  instructionText: {
    fontSize: 15,
    color: '#78350F',
    lineHeight: 22,
    fontWeight: '500',
  },
  emergencyCallButton: {
    backgroundColor: '#DC2626',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  emergencyCallButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '900',
  },
  dismissButton: {
    backgroundColor: '#0F172A',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  dismissButtonSec: {
    backgroundColor: '#F1F5F9',
  },
  dismissButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '800',
  },
  dismissButtonTextSec: {
    color: '#475569',
  },
});

