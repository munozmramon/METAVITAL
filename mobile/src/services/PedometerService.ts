import { StepActivity } from '../types';

export class PedometerService {
  private static BASELINE_DAILY_TARGET = 4000;

  /**
   * Calculates progressive step target based on 7-day average.
   * If patient consistently reaches 4,000 steps, gently increments target by 500 steps.
   */
  public static calculateProgressiveTarget(recentDailySteps: number[]): number {
    if (recentDailySteps.length === 0) return this.BASELINE_DAILY_TARGET;
    
    const sum = recentDailySteps.reduce((acc, val) => acc + val, 0);
    const avg = sum / recentDailySteps.length;

    if (avg >= 8000) return 9000;
    if (avg >= 6000) return 7000;
    if (avg >= 4000) return 5000;
    return this.BASELINE_DAILY_TARGET;
  }

  /**
   * Generates tailored advice for postprandial walking.
   * Postprandial mild walking (10-15 min) increases GLUT4 translocation in skeletal muscle,
   * lowering postprandial glycemic excursions by 15-30% without risking hypoglycemia.
   */
  public static getPostprandialGuidance(
    lastMealTimeMinutesAgo: number,
    walksCompletedToday: number
  ): {
    shouldPrompt: boolean;
    title: string;
    message: string;
    recommendedDurationMinutes: number;
  } {
    // Ideal window is 20 to 60 minutes after finishing a main meal
    if (lastMealTimeMinutesAgo >= 20 && lastMealTimeMinutesAgo <= 75) {
      return {
        shouldPrompt: true,
        title: 'Momento Óptimo para Paseo Posprandial',
        message: 'Han pasado unos minutos desde su comida. Un paseo suave de 12-15 minutos ayudará a que sus músculos consuman la glucosa circulante y evitará picos glucémicos.',
        recommendedDurationMinutes: 15,
      };
    }

    if (walksCompletedToday < 2) {
      return {
        shouldPrompt: false,
        title: 'Meta Anti-sedentarismo',
        message: 'Tiene pendiente su paseo suave post-almuerzo o cena. ¡Cada paso suma salud cardiovascular!',
        recommendedDurationMinutes: 10,
      };
    }

    return {
      shouldPrompt: false,
      title: '¡Excelente actividad hoy!',
      message: 'Ha completado sus paseos posprandiales recomendados. Mantenga un descanso activo.',
      recommendedDurationMinutes: 10,
    };
  }
}

