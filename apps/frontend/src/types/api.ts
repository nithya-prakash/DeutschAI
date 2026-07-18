// Mirrors app/domain/schemas/* on the backend. Kept hand-in-sync for now;
// Phase 6 adds OpenAPI-generated client types so this file can be deleted.

export type CEFRLevel = "A1" | "A2" | "B1" | "B2" | "C1" | "C2";

export interface UserRead {
  id: string;
  email: string;
  full_name: string;
  native_language: string;
  target_language: string;
  cefr_level: CEFRLevel;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface DailyMinutes {
  date: string;
  minutes: number;
}

export interface DashboardSummary {
  cefr_level: CEFRLevel;
  member_since: string;
  current_streak_days: number;
  longest_streak_days: number;
  total_study_minutes: number;
  weekly_study_minutes: number;
  last_12_weeks: DailyMinutes[];
  locked_insights: string[];
}

export interface StudySessionCreate {
  duration_minutes: number;
  note?: string;
}

export interface StudySessionRead {
  id: string;
  studied_on: string;
  duration_minutes: number;
  note: string | null;
}

export interface ApiError {
  detail: string;
}

// --- Phase 2: Learning Engine ---

export type TopicCategory = "grammar" | "everyday_topic";
export type TopicStatus = "not_started" | "in_progress" | "mastered";

export interface TopicRead {
  id: string;
  category: TopicCategory;
  name: string;
  order_index: number;
  status: TopicStatus;
}

export interface VocabularyItemCreate {
  german: string;
  english: string;
  example_sentence?: string;
}

export interface VocabularyItemRead {
  id: string;
  german: string;
  english: string;
  example_sentence: string | null;
  repetitions: number;
  next_review_date: string;
  last_reviewed_at: string | null;
  is_due: boolean;
}

/** Mirrors app.services.spaced_repetition.ReviewQuality. */
export const REVIEW_QUALITY = {
  again: 1,
  hard: 3,
  good: 4,
  easy: 5,
} as const;

export interface PlanBlock {
  activity: string;
  minutes: number;
  reason: string;
}

export interface DailyPlan {
  generated_for: string;
  available_minutes: number;
  vocab_due_count: number;
  weak_topic_count: number;
  blocks: PlanBlock[];
}

// --- Phase 3: AI Tutor, Assessment, Memory ---

export interface AskTutorRequest {
  question: string;
  conversation_id?: string;
}

export interface TutorAnswer {
  conversation_id: string;
  answer: string;
  sources: string[];
}

export type MessageRole = "user" | "assistant";

export interface MessageRead {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  message_count: number;
  last_message_preview: string | null;
}

export interface ConversationRead {
  id: string;
  created_at: string;
  messages: MessageRead[];
}

export interface QuizQuestionRead {
  id: string;
  topic_id: string;
  topic_name: string;
  question: string;
  options: string[];
}

export interface QuizAttemptResult {
  is_correct: boolean;
  correct_option_index: number;
  explanation: string;
}

export type MemoryType = "mistake" | "forgotten_word" | "pronunciation_issue" | "note";

export interface MemoryRead {
  id: string;
  memory_type: MemoryType;
  content: string;
  related_topic_name: string | null;
  created_at: string;
}
