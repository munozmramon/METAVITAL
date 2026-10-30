import React, { useState } from 'react';
import { 
  SafeAreaView, 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  StatusBar 
} from 'react-native';
import { TodayScreen } from './screens/TodayScreen';
import { MetricsScreen } from './screens/MetricsScreen';
import { NutritionScreen } from './screens/NutritionScreen';
import { DoctorReportScreen } from './screens/DoctorReportScreen';

type TabKey = 'TODAY' | 'METRICS' | 'NUTRITION' | 'REPORT';

interface TabConfig {
  key: TabKey;
  label: string;
  icon: string;
}

const TABS: TabConfig[] = [
  { key: 'TODAY', label: 'Hoy', icon: '☀️' },
  { key: 'METRICS', label: 'Mis Métricas', icon: '📈' },
  { key: 'NUTRITION', label: 'Nutrición', icon: '🥗' },
  { key: 'REPORT', label: 'Informe', icon: '📋' },
];

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('TODAY');

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'TODAY':
        return <TodayScreen />;
      case 'METRICS':
        return <MetricsScreen />;
      case 'NUTRITION':
        return <NutritionScreen />;
      case 'REPORT':
        return <DoctorReportScreen />;
      default:
        return <TodayScreen />;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      {/* Active Screen Body */}
      <View style={styles.screenContainer}>
        {renderActiveScreen()}
      </View>

      {/* Accessible Bottom Navigation Bar (4 tabs strictly) */}
      <View style={styles.bottomNav} accessibilityRole="tablist">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <TouchableOpacity
              key={tab.key}
              style={[styles.navTab, isActive && styles.navTabActive]}
              onPress={() => setActiveTab(tab.key)}
              accessibilityRole="tab"
              accessibilityState={{ selected: isActive }}
              accessibilityLabel={`Pestaña ${tab.label}`}
              activeOpacity={0.8}
            >
              <Text style={styles.tabIcon}>{tab.icon}</Text>
              <Text style={[styles.tabLabel, isActive && styles.tabLabelActive]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  screenContainer: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  bottomNav: {
    flexDirection: 'row',
    height: 72,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1.5,
    borderTopColor: '#E2E8F0',
    paddingHorizontal: 8,
    paddingBottom: 6,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  navTab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 12,
  },
  navTabActive: {
    backgroundColor: '#EFF6FF',
  },
  tabIcon: {
    fontSize: 22,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
  },
  tabLabelActive: {
    color: '#0D6EFD',
    fontWeight: '900',
  },
});

export default App;

