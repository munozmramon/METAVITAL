/**
 * METAVITAL Notification & Critical Alarm Service
 * Manages persistent critical alerts for medication schedules and smart postprandial walk timers.
 */

import { Medication } from '../types';

export interface ScheduledAlarm {
  id: string;
  type: 'MEDICATION' | 'POSTPRANDIAL_WALK';
  targetTime: string; // ISO string or HH:MM
  title: string;
  message: string;
  isCritical: boolean;
  isActive: boolean;
}

export class NotificationAlarmService {
  private static activeAlarms: ScheduledAlarm[] = [];

  /**
   * Configures persistent alarms for daily medication intakes.
   * On mobile hardware, maps to iOS UNNotificationRequest (Critical Alert) / Android NotificationChannel (IMPORTANCE_HIGH).
   */
  public static scheduleMedicationAlarms(medications: Medication[]): ScheduledAlarm[] {
    const scheduled: ScheduledAlarm[] = [];

    for (const med of medications) {
      if (!med.isActive) continue;

      const alarm: ScheduledAlarm = {
        id: `alarm-med-${med.id}`,
        type: 'MEDICATION',
        targetTime: med.scheduledTime,
        title: `⏰ Toma de ${med.genericName} (${med.doseMg} mg)`,
        message: `${med.instructions}. Confirme su toma en METAVITAL con 1 solo toque.`,
        isCritical: true, // Bypass Do Not Disturb for vital cardiovascular therapy
        isActive: true,
      };

      scheduled.push(alarm);
    }

    this.activeAlarms = [...this.activeAlarms.filter(a => a.type !== 'MEDICATION'), ...scheduled];
    return scheduled;
  }

  /**
   * Schedules a smart reminder for skeletal muscle glucose clearance 30 minutes after a meal.
   */
  public static schedulePostprandialWalkReminder(
    mealName: string = 'la comida',
    delayMinutes: number = 30
  ): ScheduledAlarm {
    const fireDate = new Date(Date.now() + delayMinutes * 60 * 1000);
    const timeStr = fireDate.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

    const alarm: ScheduledAlarm = {
      id: `alarm-walk-${Date.now()}`,
      type: 'POSTPRANDIAL_WALK',
      targetTime: timeStr,
      title: '👟 Momento Óptimo para su Paseo Posprandial',
      message: `Han transcurrido ${delayMinutes} minutos desde ${mealName}. Una caminata suave de 12-15 minutos favorecerá el transporte no insulino-dependiente de glucosa (GLUT4), amortiguando el pico glucémico.`,
      isCritical: false,
      isActive: true,
    };

    this.activeAlarms.push(alarm);
    return alarm;
  }

  public static getActiveAlarms(): ScheduledAlarm[] {
    return this.activeAlarms;
  }

  public static cancelAlarm(id: string): void {
    this.activeAlarms = this.activeAlarms.filter(a => a.id !== id);
  }
}

