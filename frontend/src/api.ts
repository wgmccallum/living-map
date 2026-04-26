const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
}

// Types
export interface KC {
  id: string;
  short_description: string;
  long_description: string | null;
  is_quotient_node: boolean;
  metadata_status: string;
  language_demands: string[];
  math_contexts: { math_concept_id: string; role: string }[];
  created_at: string;
}

export interface Edge {
  id: number;
  source_kc_id: string;
  target_kc_id: string;
}

export interface Schema {
  id: string;
  frame_id: string;
  name: string;
  description: string | null;
  parent_schema_id: string | null;
  kc_ids: string[];
}

export interface Frame {
  id: string;
  name: string;
  description: string | null;
  frame_type: string;
  is_reference: boolean;
  schemas: Schema[];
}

export interface Annotation {
  id: number;
  entity_type: string;
  entity_id: string;
  annotation_type: string;
  content: string;
}

export interface ConvexityViolation {
  schema_id: string;
  missing_nodes: string[];
}

export interface LaminarityViolation {
  schema_a: string;
  schema_b: string;
  overlap: string[];
  a_only: string[];
  b_only: string[];
}

export interface ValidationCheck {
  status: string;
  violations?: ConvexityViolation[] | LaminarityViolation[] | unknown[];
  cycles?: string[][];
  schema_dag_edges?: [string, string][];
}

export interface ValidationReport {
  frame_id: string;
  valid: boolean;
  checks: Record<string, ValidationCheck>;
}

export interface QuotientResult {
  quotient_dag: { nodes: string[]; edges: [string, string][] };
  collapsed_nodes: {
    id: string;
    source_schema_id: string;
    short_description: string;
    language_demands: string[];
    math_contexts: { math_concept_id: string; role: string }[];
  }[];
  updated_schemas: Record<string, string[]>;
  schemas_collapsed: string[];
  original_node_count: number;
  quotient_node_count: number;
  original_edge_count: number;
  quotient_edge_count: number;
}

export interface MathDomain {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface MathDomainEdge {
  id: number;
  source_id: string;
  target_id: string;
  created_at: string;
}

export interface Stats {
  knowledge_map: {
    node_count: number;
    edge_count: number;
    connected_components: number;
    longest_path_length: number;
  };
  math_structure_map: {
    node_count: number;
    edge_count: number;
  };
}

// API functions
export const api = {
  listKCs: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return get<KC[]>(`/kcs${qs}`);
  },
  getKC: (id: string) => get<KC>(`/kcs/${encodeURIComponent(id)}`),
  getKCAncestors: (id: string) => get<string[]>(`/kcs/${encodeURIComponent(id)}/ancestors`),
  getKCDescendants: (id: string) => get<string[]>(`/kcs/${encodeURIComponent(id)}/descendants`),
  getKCSchemas: (frameId: string, kcId: string) =>
    get<Schema[]>(`/frames/${encodeURIComponent(frameId)}/kcs/${encodeURIComponent(kcId)}/schemas`),

  listEdges: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return get<Edge[]>(`/edges${qs}`);
  },

  listFrames: () => get<Frame[]>("/frames"),
  getFrame: (id: string) => get<Frame>(`/frames/${encodeURIComponent(id)}`),
  listSchemas: (frameId: string) =>
    get<Schema[]>(`/frames/${encodeURIComponent(frameId)}/schemas`),
  getSchemaAtoms: (frameId: string, id: string) =>
    get<string[]>(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(id)}/atoms`),
  checkConvexity: (frameId: string, id: string) =>
    get<{ status: string; missing_nodes?: string[] }>(
      `/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(id)}/check-convexity`
    ),

  validateFrame: (frameId: string) =>
    post<ValidationReport>(`/frames/${encodeURIComponent(frameId)}/validate`, {}),
  computeQuotient: (frameId: string, schemaIds: string[]) =>
    post<QuotientResult>(`/frames/${encodeURIComponent(frameId)}/quotient`, {
      schema_ids: schemaIds,
    }),
  getSchemaDAG: (frameId: string) =>
    get<{ edges: [string, string][] }>(`/frames/${encodeURIComponent(frameId)}/schema-dag`),

  getAnnotations: (entityType: string, entityId: string) =>
    get<Annotation[]>(
      `/annotations?entity_type=${encodeURIComponent(entityType)}&entity_id=${encodeURIComponent(entityId)}`
    ),

  getStats: () => get<Stats>("/stats"),

  // Mutations
  createKC: (data: { id: string; short_description: string; long_description?: string; language_demands?: string[] }) =>
    post<KC>("/kcs", data),
  updateKC: (id: string, data: { short_description?: string; long_description?: string }) =>
    patch<KC>(`/kcs/${encodeURIComponent(id)}`, data),
  deleteKC: (id: string) => del(`/kcs/${encodeURIComponent(id)}`),
  updateKCLanguageDemands: (id: string, demands: string[]) =>
    patch<KC>(`/kcs/${encodeURIComponent(id)}/language-demands`, { language_demands: demands }),
  addMathContext: (kcId: string, mathConceptId: string, role: string = "primary") =>
    post<KC>(`/kcs/${encodeURIComponent(kcId)}/math-contexts`, { math_concept_id: mathConceptId, role }),
  removeMathContext: (kcId: string, mathConceptId: string) =>
    del(`/kcs/${encodeURIComponent(kcId)}/math-contexts/${encodeURIComponent(mathConceptId)}`),
  listMathConcepts: () => get<{ id: string; name: string; description: string | null }[]>("/math-concepts"),

  createEdge: (source: string, target: string) =>
    post<Edge>("/edges", { source_kc_id: source, target_kc_id: target }),
  deleteEdge: (edgeId: number) => del(`/edges/${edgeId}`),

  createSchema: (
    frameId: string,
    data: { id: string; name: string; description?: string; parent_schema_id?: string | null },
  ) => post<Schema>(`/frames/${encodeURIComponent(frameId)}/schemas`, data),
  updateSchema: (frameId: string, id: string, data: { name?: string; description?: string; parent_schema_id?: string | null }) =>
    patch<Schema>(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(id)}`, data),
  deleteSchema: (frameId: string, id: string) =>
    del(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(id)}`),
  addKCsToSchema: (frameId: string, schemaId: string, kcIds: string[]) =>
    post<void>(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(schemaId)}/kcs`, { kc_ids: kcIds }),
  removeKCFromSchema: (frameId: string, schemaId: string, kcId: string) =>
    del(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(schemaId)}/kcs/${encodeURIComponent(kcId)}`),
  getNextKCId: (frameId: string, schemaId: string) =>
    get<{ next_id: string }>(`/frames/${encodeURIComponent(frameId)}/schemas/${encodeURIComponent(schemaId)}/next-kc-id`),
  forkFrame: (
    sourceFrameId: string,
    data: { id: string; name: string; description?: string },
  ) => post<Frame>(`/frames/${encodeURIComponent(sourceFrameId)}/fork`, data),

  // Math Domains CRUD
  listMathDomains: () => get<MathDomain[]>("/math-concepts"),
  createMathDomain: (data: { id: string; name: string; description?: string }) =>
    post<MathDomain>("/math-concepts", data),
  updateMathDomain: (id: string, data: { name?: string; description?: string }) =>
    patch<MathDomain>(`/math-concepts/${encodeURIComponent(id)}`, data),
  deleteMathDomain: (id: string) => del(`/math-concepts/${encodeURIComponent(id)}`),
  getMathDomainKCs: (id: string) => get<KC[]>(`/math-concepts/${encodeURIComponent(id)}/kcs`),

  listKCTypes: () => get<string[]>("/kc-types"),

  // Annotations
  createAnnotation: (data: { entity_type: string; entity_id: string; annotation_type: string; content: string }) =>
    post<Annotation>("/annotations", data),
  updateAnnotation: (id: number, data: { content?: string; resolved_at?: string | null }) =>
    patch<Annotation>(`/annotations/${id}`, data),
  deleteAnnotation: (id: number) => del(`/annotations/${id}`),

  // Math Domain Edges
  listMathDomainEdges: () => get<MathDomainEdge[]>("/math-concept-edges"),
  createMathDomainEdge: (sourceId: string, targetId: string) =>
    post<MathDomainEdge>("/math-concept-edges", { source_id: sourceId, target_id: targetId }),
  deleteMathDomainEdge: (edgeId: number) => del(`/math-concept-edges/${edgeId}`),

  // Topology Diagnostics
  diagnoseTopology: (frameId: string) =>
    post<TopologyDiagnosticsResponse>(
      `/frames/${encodeURIComponent(frameId)}/topology/diagnose`, {}),
  diagnoseTopologyWithScenario: (frameId: string, scenario: LearnerScenarioPayload) =>
    post<TopologyDiagnosticsResponse>(
      `/frames/${encodeURIComponent(frameId)}/topology/diagnose-scenario`, scenario),
};

// Topology Diagnostics types

export interface SuggestedAction {
  label: string;
  action_type: string;
  payload: Record<string, unknown>;
}

export interface TopologyIssue {
  id: string;
  issue_type: string;
  severity: string;
  summary: string;
  involved_kcs: string[];
  involved_schemas: string[];
  extra: Record<string, unknown>;
  suggested_actions: SuggestedAction[];
}

export interface TopologyDiagnosticsResponse {
  frame_id: string;
  issues: TopologyIssue[];
  summary: Record<string, number>;
  scenario_name: string | null;
}

export interface LearnerScenarioPayload {
  name: string;
  theta: number;
  mastery_functions: Array<{
    vertex_id: string;
    breakpoints: Array<{ time: number; value: number }>;
  }>;
  long_h1_threshold_ratio?: number;
}
