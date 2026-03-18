/**
 * HábitosFam – frontend/scripts/types.ts
 * Shared interfaces for the TypeScript migration.
 */

export interface MicroHabit {
    id?: number;
    habit_id?: number;
    description: string;
    description_es?: string;
    order: number;
}

export interface Habit {
    id?: number;
    profile_id?: number;
    key: string;
    name: string;
    description: string;
    motivation: string;
    icon: string;
    category: string;
    stars: number;
    order: number;
    micro_habits?: MicroHabit[];
}

export interface RewardTier {
    id?: number;
    profile_id?: number;
    min_stars: number;
    reward: number;
}

export interface Profile {
    id?: number;
    slug: string;
    name: string;
    age: number;
    avatar: string;
    theme: string;
    pin: string;
    base_weekly_reward: number;
    full_weekly_reward: number;
    monthly_min_pct: number;
    monthly_reward_desc: string;
    is_admin?: boolean;
    is_active?: boolean;
    balance?: number;
    unlocked_themes_json?: string;
    unlocked_avatars_json?: string;
    habits?: Habit[];
    reward_tiers?: RewardTier[];
}

export interface AppSettings {
    currency: string;
    app_name: string;
    streak_days: number;
    streak_bonus_pct: number;
}

export interface LogEntry {
    date: string;
    completed_count: number;
    total: number;
    pct: number;
    day_done: boolean;
}

export interface HealthInfo {
    status: string;
    db_engine: string;
    profiles: number;
    total_day_logs: number;
}
