// Mirrors app/domain/schemas/* on the backend. Kept hand-in-sync;
// OpenAPI-generated client types remain a candidate for a later pass.

export type CEFRLevel = "A1" | "A2" | "B1" | "B2" | "C1" | "C2";

export interface UserRead {
  id: string;
  email: string;
  full_name: string;
  native_language: string;
  target_language: string;
  cefr_level: CEFRLevel;
  is_active: boolean;
  is_superuser: boolean;
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

// --- Recommendation Engine, ML, Analytics ---
// Every field below is `null`/empty exactly where the backend has no real
// data yet for that user (see docs/ARCHITECTURE.md).

export interface SkillScores {
  grammar: number | null;
  vocabulary: number | null;
  speaking: number | null;
}

export interface TopicRanking {
  topic_id: string;
  topic_name: string;
  mistake_count: number;
  accuracy: number | null;
}

export interface PredictedMilestone {
  topics_remaining: number;
  projected_date: string;
}

export interface MotivationMessage {
  headline: string;
  body: string;
  suggested_minutes: number;
}

export interface DashboardSummary {
  cefr_level: CEFRLevel;
  member_since: string;
  current_streak_days: number;
  longest_streak_days: number;
  total_study_minutes: number;
  weekly_study_minutes: number;
  last_12_weeks: DailyMinutes[];
  skill_scores: SkillScores;
  weakest_topics: TopicRanking[];
  strongest_topics: TopicRanking[];
  predicted_milestone: PredictedMilestone | null;
  consistency_score: number | null;
  best_study_day: string | null;
  vocab_at_risk_count: number;
  motivation_message: MotivationMessage | null;
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

// --- Learning Engine ---

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

// --- AI Tutor, Assessment, Memory ---

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

// Recommendation Engine — internal content only (grammar topics + vocabulary),
// ranked by real data. No podcasts/articles: no real content source exists.
export interface RecommendedVocab {
  id: string;
  german: string;
  english: string;
  retention_probability: number;
  reason: string;
}

export interface RecommendedTopic {
  topic_id: string;
  topic_name: string;
  reason: string;
}

export interface RecommendationResult {
  vocab: RecommendedVocab[];
  topics: RecommendedTopic[];
}

// --- Conversation Mode (speech) ---
// Grammar/vocabulary scores are real (Claude-scored). Pronunciation/fluency
// have no real signal yet, so they're never sent by the API at all — the
// frontend renders them as locked via the same `LockedInsights` component
// the dashboard uses, rather than the API faking a number.

export interface SpeechTurnRead {
  id: string;
  role: MessageRole;
  text: string;
  grammar_score: number | null;
  vocabulary_score: number | null;
  feedback: string | null;
  created_at: string;
}

export interface SpeechConversationSummary {
  id: string;
  created_at: string;
  turn_count: number;
  last_turn_preview: string | null;
}

export interface SpeechConversationRead {
  id: string;
  created_at: string;
  turns: SpeechTurnRead[];
}

export interface SubmitTurnResponse {
  conversation_id: string;
  user_turn: SpeechTurnRead;
  assistant_turn: SpeechTurnRead;
}

// --- Admin panel ---
// Every field here is real data, a real reachability check, or a zero/empty
// value where no data exists yet (see docs/ARCHITECTURE.md).

export interface ServiceStatus {
  name: string;
  reachable: boolean;
}

export interface SystemHealth {
  services: ServiceStatus[];
  anthropic_configured: boolean;
  sentry_configured: boolean;
  otel_configured: boolean;
  whisper_model_cached: boolean;
  piper_model_cached: boolean;
}

export interface AgentUsageTotals {
  agent_name: string;
  call_count: number;
  input_tokens: number;
  output_tokens: number;
}

export interface LLMUsageSummary {
  by_agent: AgentUsageTotals[];
}

export interface SessionActivity {
  sessions_today: number;
  sessions_this_week: number;
  active_users_this_week: number;
}

export interface ErrorLogEntryRead {
  id: string;
  created_at: string;
  method: string;
  path: string;
  exception_type: string;
  message: string;
}
