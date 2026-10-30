import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { GroceryItem, SupermarketAisle } from '../types';

interface GroceryAisleListProps {
  items: GroceryItem[];
  onToggleItem: (id: string) => void;
}

const AISLE_METADATA: Record<SupermarketAisle, { title: string; icon: string; clinicalRationale: string }> = {
  FRUITS_VEGETABLES: {
    title: 'Frutas y Verduras Frescas',
    icon: '🥦',
    clinicalRationale: 'Aporte de fibra soluble, antioxidantes y potasio para control tensional.',
  },
  FISH_LEAN_MEAT: {
    title: 'Pescadería y Carnicería Magra',
    icon: '🐟',
    clinicalRationale: 'Omega-3 (EPA/DHA) para reducir triglicéridos e inflamación endotelial.',
  },
  LEGUMES_WHOLE_GRAINS: {
    title: 'Legumbres y Granos Enteros',
    icon: '🥣',
    clinicalRationale: 'Betaglucanos y almidón resistente que amortiguan picos glucémicos.',
  },
  HEALTHY_FATS: {
    title: 'Grasas Cardioprotectoras (AOVE y Frutos Secos)',
    icon: '🫒',
    clinicalRationale: 'Ácido oleico monoinsaturado para elevar c-HDL y mejorar perfil lipídico.',
  },
};

export const GroceryAisleList: React.FC<GroceryAisleListProps> = ({
  items,
  onToggleItem,
}) => {
  const aisles: SupermarketAisle[] = [
    'FRUITS_VEGETABLES',
    'FISH_LEAN_MEAT',
    'LEGUMES_WHOLE_GRAINS',
    'HEALTHY_FATS',
  ];

  return (
    <View style={styles.container}>
      {aisles.map((aisleKey) => {
        const meta = AISLE_METADATA[aisleKey];
        const aisleItems = items.filter((i) => i.aisle === aisleKey);

        if (aisleItems.length === 0) return null;

        return (
          <View key={aisleKey} style={styles.aisleSection}>
            <View style={styles.aisleHeader}>
              <Text style={styles.aisleIcon}>{meta.icon}</Text>
              <View style={styles.aisleTitleBox}>
                <Text style={styles.aisleTitle}>{meta.title}</Text>
                <Text style={styles.aisleRationale}>{meta.clinicalRationale}</Text>
              </View>
            </View>

            <View style={styles.itemsList}>
              {aisleItems.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.itemRow, item.checked && styles.itemRowChecked]}
                  onPress={() => onToggleItem(item.id)}
                  accessibilityRole="checkbox"
                  accessibilityState={{ checked: item.checked }}
                  accessibilityLabel={`${item.name}, ${item.quantity}. ${item.checked ? 'Comprado' : 'Pendiente'}`}
                  activeOpacity={0.7}
                >
                  <View style={[styles.checkbox, item.checked && styles.checkboxChecked]}>
                    {item.checked ? <Text style={styles.checkmark}>✓</Text> : null}
                  </View>
                  <View style={styles.itemTextBox}>
                    <Text style={[styles.itemName, item.checked && styles.itemNameChecked]}>
                      {item.name}
                    </Text>
                    <Text style={styles.itemQty}>{item.quantity}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        );
      })}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 4,
  },
  aisleSection: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#E2E8F0',
    padding: 14,
    marginBottom: 14,
  },
  aisleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1.5,
    borderBottomColor: '#F1F5F9',
    paddingBottom: 10,
    marginBottom: 10,
  },
  aisleIcon: {
    fontSize: 26,
    marginRight: 10,
  },
  aisleTitleBox: {
    flex: 1,
  },
  aisleTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  aisleRationale: {
    fontSize: 12,
    color: '#64748B',
    marginTop: 2,
    fontWeight: '500',
  },
  itemsList: {
    marginTop: 4,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderRadius: 8,
    marginVertical: 2,
  },
  itemRowChecked: {
    backgroundColor: '#F8FAFC',
    opacity: 0.6,
  },
  checkbox: {
    width: 28,
    height: 28,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#94A3B8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  checkboxChecked: {
    backgroundColor: '#16A34A',
    borderColor: '#16A34A',
  },
  checkmark: {
    color: '#FFFFFF',
    fontWeight: '900',
    fontSize: 16,
  },
  itemTextBox: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemName: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1E293B',
  },
  itemNameChecked: {
    textDecorationLine: 'line-through',
    color: '#94A3B8',
  },
  itemQty: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },
});

