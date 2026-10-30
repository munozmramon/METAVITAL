import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { AccessibleCard } from '../components/AccessibleCard';
import { GroceryAisleList } from '../components/GroceryAisleList';
import { DatabaseService } from '../services/DatabaseService';
import { TherapeuticRecipe, GroceryItem } from '../types';

export const NutritionScreen: React.FC = () => {
  const [recipes, setRecipes] = useState<TherapeuticRecipe[]>([]);
  const [groceryItems, setGroceryItems] = useState<GroceryItem[]>([]);
  const [selectedRecipeIndex, setSelectedRecipeIndex] = useState<number>(0);
  const [showGroceryList, setShowGroceryList] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      const recs = await DatabaseService.getRecipes();
      const grocs = await DatabaseService.getGroceryItems();
      setRecipes(recs);
      setGroceryItems(grocs);
    };
    load();
  }, []);

  const handleGenerateList = () => {
    const items = DatabaseService.generateGroceryList();
    setGroceryItems([...items]);
    setShowGroceryList(true);
  };

  const handleToggleGrocery = async (id: string) => {
    await DatabaseService.toggleGroceryItem(id);
    const updated = await DatabaseService.getGroceryItems();
    setGroceryItems([...updated]);
  };

  const currentRecipe = recipes[selectedRecipeIndex];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Nutrición Cardioprotectora</Text>
        <Text style={styles.subtitle}>
          Dieta Mediterránea terapéutica de baja carga glucémica y &lt; 4 pasos
        </Text>
      </View>

      {/* RECETARIO TERAPÉUTICO (MÁXIMO 4 PASOS) */}
      {currentRecipe && (
        <AccessibleCard
          title={currentRecipe.title}
          subtitle={`Tiempo: ${currentRecipe.prepTimeMinutes} min • Fibra soluble: ${currentRecipe.solubleFiberG}g`}
          badgeText={currentRecipe.glycemicLoad === 'VERY_LOW' ? 'Muy Baja Carga' : 'Baja Carga'}
          badgeColor="#16A34A"
        >
          {/* Selector de Recetas */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.recipeNav}>
            {recipes.map((rec, idx) => (
              <TouchableOpacity
                key={rec.id}
                style={[
                  styles.recipeTab,
                  selectedRecipeIndex === idx && styles.recipeTabActive,
                ]}
                onPress={() => setSelectedRecipeIndex(idx)}
              >
                <Text
                  style={[
                    styles.recipeTabText,
                    selectedRecipeIndex === idx && styles.recipeTabTextActive,
                  ]}
                >
                  {rec.mealType === 'BREAKFAST'
                    ? 'Desayuno'
                    : rec.mealType === 'LUNCH'
                    ? 'Almuerzo'
                    : 'Cena'}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {/* Pasos Culinarios Simples (Máximo 4) */}
          <View style={styles.stepsContainer}>
            <Text style={styles.stepsHeading}>Pasos de Elaboración Rápida:</Text>
            {currentRecipe.steps.map((stepText, idx) => (
              <View key={idx} style={styles.stepRow}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepBadgeText}>{idx + 1}</Text>
                </View>
                <Text style={styles.stepText}>{stepText}</Text>
              </View>
            ))}
          </View>

          {/* Ingredientes de la Receta */}
          <View style={styles.ingredientsSummary}>
            <Text style={styles.ingredientsTitle}>Ingredientes Cotidianos:</Text>
            {currentRecipe.ingredients.map((ing, i) => (
              <Text key={i} style={styles.ingItem}>
                • {ing.name} ({ing.quantity})
              </Text>
            ))}
          </View>
        </AccessibleCard>
      )}

      {/* BOTÓN GENERADOR DE LISTA DE LA COMPRA */}
      <View style={styles.buttonWrapper}>
        <TouchableOpacity
          style={styles.generateButton}
          onPress={handleGenerateList}
          accessibilityRole="button"
          accessibilityLabel="Generar lista de la compra organizada por pasillos de supermercado"
        >
          <Text style={styles.generateButtonText}>
            🛒 GENERAR LISTA DE LA COMPRA INTELIGENTE
          </Text>
        </TouchableOpacity>
      </View>

      {/* LISTA DE LA COMPRA ORGANIZADA POR PASILLOS */}
      {showGroceryList && (
        <AccessibleCard
          title="Lista de la Compra Cardioprotectora"
          subtitle="Organizada por pasillos para evitar compras compulsivas de ultraprocesados"
          badgeText="Supermercado"
          badgeColor="#8B5CF6"
        >
          <GroceryAisleList
            items={groceryItems}
            onToggleItem={handleToggleGrocery}
          />
        </AccessibleCard>
      )}
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
  recipeNav: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  recipeTab: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
    marginRight: 8,
  },
  recipeTabActive: {
    backgroundColor: '#0D6EFD',
  },
  recipeTabText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
  },
  recipeTabTextActive: {
    color: '#FFFFFF',
  },
  stepsContainer: {
    marginBottom: 16,
  },
  stepsHeading: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 10,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  stepBadge: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    marginTop: 2,
  },
  stepBadgeText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '900',
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
    fontWeight: '500',
  },
  ingredientsSummary: {
    backgroundColor: '#F8FAFC',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  ingredientsTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#475569',
    marginBottom: 6,
  },
  ingItem: {
    fontSize: 13,
    color: '#334155',
    marginBottom: 2,
  },
  buttonWrapper: {
    paddingHorizontal: 16,
    marginVertical: 10,
  },
  generateButton: {
    backgroundColor: '#16A34A',
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: 'center',
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
});

