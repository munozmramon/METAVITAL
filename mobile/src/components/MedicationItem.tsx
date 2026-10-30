import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Medication } from '../types';

interface MedicationItemProps {
  medication: Medication;
  isTaken: boolean;
  onTakeDose: (medicationId: string) => void;
}

export const MedicationItem: React.FC<MedicationItemProps> = ({
  medication,
  isTaken,
  onTakeDose,
}) => {
  return (
    <View style={[styles.container, isTaken && styles.containerTaken]}>
      <View style={styles.infoCol}>
        <View style={styles.timeBadge}>
          <Text style={styles.timeBadgeText}>⏰ {medication.scheduledTime}</Text>
        </View>
        <Text style={styles.medName}>
          {medication.genericName} {medication.doseMg} mg
        </Text>
        <Text style={styles.brandName}>
          ({medication.brandName}) • {medication.instructions}
        </Text>
      </View>

      <TouchableOpacity
        style={[styles.actionButton, isTaken ? styles.actionButtonTaken : styles.actionButtonPending]}
        onPress={() => !isTaken && onTakeDose(medication.id)}
        disabled={isTaken}
        accessibilityRole="button"
        accessibilityLabel={
          isTaken
            ? `${medication.genericName} ya tomada`
            : `Confirmar toma de ${medication.genericName} con un toque`
        }
      >
        <Text style={[styles.actionButtonText, isTaken && styles.actionButtonTextTaken]}>
          {isTaken ? '✓ TOMADA' : 'TOMAR'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    borderRadius: 12,
    padding: 14,
    marginVertical: 6,
  },
  containerTaken: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  infoCol: {
    flex: 1,
    paddingRight: 10,
  },
  timeBadge: {
    backgroundColor: '#E2E8F0',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginBottom: 4,
  },
  timeBadgeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  medName: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0F172A',
  },
  brandName: {
    fontSize: 13,
    color: '#64748B',
    marginTop: 2,
  },
  actionButton: {
    minWidth: 95,
    minHeight: 48,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 12,
  },
  actionButtonPending: {
    backgroundColor: '#0D6EFD',
  },
  actionButtonTaken: {
    backgroundColor: '#DCFCE7',
    borderWidth: 1,
    borderColor: '#86EFAC',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  actionButtonTextTaken: {
    color: '#15803D',
  },
});

