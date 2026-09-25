export interface AuthUser {
  id: number;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export type ChartType = "bar" | "line" | "pie" | "scatter" | "grouped_bar" | "table" | "none";

export interface ChartConfig {
  type: ChartType;
  x?: string | null;
  y?: string | null;
  series?: string[] | null;
  title: string;
}

export interface ChatMetadata {
  status: "ok" | "clarification_needed" | "unanswerable" | "error";
  execution_ms?: number | null;
  row_count?: number | null;
}

export interface ChatResponse {
  answer: string;
  sql?: string | null;
  data: Record<string, unknown>[];
  columns: string[];
  chart?: ChartConfig | null;
  metadata: ChatMetadata;
  clarification_options?: string[] | null;
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
}

export interface HistoryItem {
  id: number;
  conversation_id: string;
  question: string;
  sql?: string | null;
  answer?: string | null;
  chart_type?: string | null;
  status: string;
  created_at: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
}

export interface DashboardMetrics {
  total_sales: number;
  total_profit: number;
  total_orders: number;
  total_customers: number;
  average_order_value: number;
}

export interface DashboardResponse {
  metrics: DashboardMetrics;
  sales_over_time: Record<string, unknown>[];
  sales_by_region: Record<string, unknown>[];
  sales_by_category: Record<string, unknown>[];
  top_products: Record<string, unknown>[];
}

export interface SchemaColumn {
  name: string;
  type: string;
}

export interface SchemaTable {
  name: string;
  columns: SchemaColumn[];
}

export interface DatabaseSchema {
  tables: SchemaTable[];
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  table_name: string;
  row_count: number;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  truncated: boolean;
}

/** A single turn in the chat transcript, as rendered by the UI (not the wire format). */
export interface ChatTurn {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  isError?: boolean;
  createdAt: string;
}
