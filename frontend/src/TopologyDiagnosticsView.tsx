import { useEffect, useState, useMemo } from "react";
import { api, type KC, type Edge, type Frame, type TopologyIssue,
         type TopologyDiagnosticsResponse } from "./api";
import { DAGView } from "./DAGView";

interface TopologyDiagnosticsViewProps {
  frame: Frame | null;
  kcs: KC[];
  edges: Edge[];
  onNavigateToKC: (kcId: string) => void;
}

const ISSUE_TYPE_LABELS: Record<string, string> = {
  permanent_h1: "Cycle without integration",
  permanent_h0: "Disconnected component",
  antichain_schema: "Antichain schema",
  long_h1: "Long-lived structural hole",
};

const ISSUE_TYPE_DESCRIPTIONS: Record<string, string> = {
  permanent_h1:
    "A loop of pairwise prereq-connected KCs with no schema declaring them as an integrated whole. " +
    "Either create a schema grouping these KCs, or mark the cycle as an intentional gap.",
  permanent_h0:
    "A cluster of KCs with no prereq edges to the rest of the frame. Either bridge with a new edge, " +
    "create a connecting schema, or mark as intentional.",
  antichain_schema:
    "A schema whose KCs have no internal prereq edges — they're parallel modalities of the same skill, " +
    "or they need explicit edges to capture their integration.",
  long_h1:
    "A structural hole that persists for a long time during the learner's trajectory — a pedagogical bottleneck.",
};

const SEVERITY_COLORS: Record<string, string> = {
  high: "#e15759",
  medium: "#f28e2b",
  low: "#edc948",
  info: "#4a90d9",
};

export function TopologyDiagnosticsView({
  frame,
  kcs,
  edges,
  onNavigateToKC,
}: TopologyDiagnosticsViewProps) {
  const [data, setData] = useState<TopologyDiagnosticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  // Run diagnostics whenever frame changes
  useEffect(() => {
    if (!frame) {
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .diagnoseTopology(frame.id)
      .then((res) => {
        setData(res);
        if (res.issues.length > 0) setSelectedIssueId(res.issues[0].id);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : String(e))
      )
      .finally(() => setLoading(false));
  }, [frame?.id]);

  const filteredIssues = useMemo(() => {
    if (!data) return [];
    return data.issues.filter((issue) => {
      if (typeFilter !== "all" && issue.issue_type !== typeFilter) return false;
      if (severityFilter !== "all" && issue.severity !== severityFilter) return false;
      return true;
    });
  }, [data, typeFilter, severityFilter]);

  const selectedIssue = useMemo(() => {
    if (!data || !selectedIssueId) return null;
    return data.issues.find((i) => i.id === selectedIssueId) ?? null;
  }, [data, selectedIssueId]);

  // Compute the subgraph KCs/edges for the selected issue
  const subgraphData = useMemo(() => {
    if (!selectedIssue) return { kcs: [], edges: [] };
    const involvedSet = new Set(selectedIssue.involved_kcs);
    const subKCs = kcs.filter((kc) => involvedSet.has(kc.id));
    const subEdges = edges.filter(
      (e) => involvedSet.has(e.source_kc_id) && involvedSet.has(e.target_kc_id)
    );
    return { kcs: subKCs, edges: subEdges };
  }, [selectedIssue, kcs, edges]);

  if (!frame) {
    return (
      <div className="topology-empty">
        <p>Select a frame to run topology diagnostics.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="topology-empty">
        <p>Computing diagnostics for {frame.id}…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="topology-empty">
        <p style={{ color: "#e15759" }}>Error: {error}</p>
        <button
          className="toolbar-btn"
          onClick={() => {
            setError(null);
            setLoading(true);
            api.diagnoseTopology(frame.id)
              .then(setData)
              .catch((e) => setError(e instanceof Error ? e.message : String(e)))
              .finally(() => setLoading(false));
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  const issueTypes = Object.keys(ISSUE_TYPE_LABELS);
  const severities = ["high", "medium", "low", "info"];

  return (
    <div className="topology-diagnostics-view">
      {/* Top header with summary */}
      <div className="topology-header">
        <h3>Topology Diagnostics — {frame.name ?? frame.id}</h3>
        <div className="topology-summary">
          {data.summary.total ? (
            <>
              <strong>{data.summary.total}</strong> issues:{" "}
              {issueTypes.map((t) =>
                data.summary[t] ? (
                  <span key={t} className="summary-pill">
                    {data.summary[t]} {ISSUE_TYPE_LABELS[t]}
                  </span>
                ) : null
              )}
            </>
          ) : (
            <span style={{ color: "#666" }}>No issues found.</span>
          )}
        </div>
        <div className="topology-filters">
          <label>
            Type:{" "}
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="all">All ({data.issues.length})</option>
              {issueTypes.map((t) =>
                data.summary[t] ? (
                  <option key={t} value={t}>
                    {ISSUE_TYPE_LABELS[t]} ({data.summary[t]})
                  </option>
                ) : null
              )}
            </select>
          </label>
          <label>
            Severity:{" "}
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">All</option>
              {severities.map((s) =>
                data.summary[`severity:${s}`] ? (
                  <option key={s} value={s}>
                    {s} ({data.summary[`severity:${s}`]})
                  </option>
                ) : null
              )}
            </select>
          </label>
        </div>
      </div>

      {/* Two-column body: issue list + detail */}
      <div className="topology-body">
        <div className="issue-list">
          {filteredIssues.length === 0 && (
            <p style={{ padding: "16px", color: "#666" }}>
              No issues match the current filters.
            </p>
          )}
          {filteredIssues.map((issue) => (
            <IssueCard
              key={issue.id}
              issue={issue}
              selected={issue.id === selectedIssueId}
              onClick={() => setSelectedIssueId(issue.id)}
            />
          ))}
        </div>

        <div className="issue-detail-pane">
          {selectedIssue ? (
            <IssueDetail
              issue={selectedIssue}
              frame={frame}
              subgraphKCs={subgraphData.kcs}
              subgraphEdges={subgraphData.edges}
              onNavigateToKC={onNavigateToKC}
            />
          ) : (
            <p style={{ padding: "24px", color: "#666" }}>
              Select an issue to see details.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Issue card (in the list) ──

function IssueCard({
  issue,
  selected,
  onClick,
}: {
  issue: TopologyIssue;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <div
      className={`issue-card ${selected ? "selected" : ""}`}
      onClick={onClick}
    >
      <div className="issue-card-header">
        <span
          className="severity-pill"
          style={{ backgroundColor: SEVERITY_COLORS[issue.severity] || "#999" }}
          title={`Severity: ${issue.severity}`}
        >
          {issue.severity}
        </span>
        <span className="issue-type-label">
          {ISSUE_TYPE_LABELS[issue.issue_type] || issue.issue_type}
        </span>
      </div>
      <div className="issue-card-summary">{issue.summary}</div>
      {issue.involved_kcs.length > 0 && (
        <div className="issue-card-chips">
          {issue.involved_kcs.slice(0, 6).map((kc) => (
            <span key={kc} className="kc-chip">
              {kc}
            </span>
          ))}
          {issue.involved_kcs.length > 6 && (
            <span className="kc-chip more">
              +{issue.involved_kcs.length - 6}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

// ── Issue detail pane ──

function IssueDetail({
  issue,
  frame,
  subgraphKCs,
  subgraphEdges,
  onNavigateToKC,
}: {
  issue: TopologyIssue;
  frame: Frame;
  subgraphKCs: KC[];
  subgraphEdges: Edge[];
  onNavigateToKC: (kcId: string) => void;
}) {
  return (
    <div className="issue-detail">
      <div className="issue-detail-header">
        <span
          className="severity-pill"
          style={{ backgroundColor: SEVERITY_COLORS[issue.severity] || "#999" }}
        >
          {issue.severity}
        </span>
        <h4>{ISSUE_TYPE_LABELS[issue.issue_type] || issue.issue_type}</h4>
      </div>

      <p className="issue-detail-summary">{issue.summary}</p>
      <p className="issue-detail-help">
        {ISSUE_TYPE_DESCRIPTIONS[issue.issue_type]}
      </p>

      {/* Embedded subgraph for issues with KCs */}
      {subgraphKCs.length > 0 && (
        <div className="issue-subgraph">
          <div className="issue-subgraph-label">Local subgraph:</div>
          <div className="issue-subgraph-container">
            <DAGView
              kcs={subgraphKCs}
              edges={subgraphEdges}
              frame={frame}
              colorMode="schema"
              showSchemaOverlay={false}
              selectedNodeId={null}
              onSelectNode={(id) => id && onNavigateToKC(id)}
              filteredKCIds={null}
              quotientResult={null}
              collapsedSchemaIds={new Set()}
            />
          </div>
        </div>
      )}

      {/* Involved KCs as clickable chips */}
      {issue.involved_kcs.length > 0 && (
        <div className="issue-detail-row">
          <div className="issue-detail-label">Involved KCs:</div>
          <div className="issue-detail-chips">
            {issue.involved_kcs.map((kc) => (
              <button
                key={kc}
                className="kc-chip clickable"
                onClick={() => onNavigateToKC(kc)}
                title="Click to view in Knowledge Map"
              >
                {kc}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Involved schemas */}
      {issue.involved_schemas.length > 0 && (
        <div className="issue-detail-row">
          <div className="issue-detail-label">Involved schemas:</div>
          <div className="issue-detail-chips">
            {issue.involved_schemas.map((s) => (
              <span key={s} className="schema-chip">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Type-specific extra info */}
      {issue.issue_type === "permanent_h1" && Array.isArray(issue.extra.cycle_edges) && (
        <div className="issue-detail-row">
          <div className="issue-detail-label">Cycle edges:</div>
          <div className="cycle-edges">
            {(issue.extra.cycle_edges as [string, string][]).map(
              ([s, t], i) => (
                <span key={i} className="cycle-edge">
                  {s} → {t}
                </span>
              )
            )}
          </div>
        </div>
      )}

      {issue.issue_type === "long_h1" && (
        <div className="issue-detail-row">
          <div className="issue-detail-label">Time window:</div>
          <span>
            t = {Number(issue.extra.birth).toFixed(2)} →{" "}
            {Number(issue.extra.death).toFixed(2)} (lifetime{" "}
            {Number(issue.extra.lifetime).toFixed(2)})
          </span>
        </div>
      )}

      {/* Suggested actions */}
      {issue.suggested_actions.length > 0 && (
        <div className="issue-actions">
          <div className="issue-detail-label">Suggested actions:</div>
          <div className="issue-actions-list">
            {issue.suggested_actions.map((action, i) => (
              <button
                key={i}
                className={`action-btn action-${action.action_type}`}
                onClick={() => handleAction(action, onNavigateToKC)}
                title={action.action_type}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function handleAction(
  action: { label: string; action_type: string; payload: Record<string, unknown> },
  onNavigateToKC: (kcId: string) => void
) {
  // For v1: most actions just inform. The "create_schema" action could
  // copy the proposed atom set to the clipboard for the user to paste
  // into the schema editor.
  if (action.action_type === "create_schema" && action.payload.atom_kcs) {
    const atoms = (action.payload.atom_kcs as string[]).join(", ");
    const parent = action.payload.parent_schema_id || "(no parent)";
    const name = action.payload.suggested_name || "(unnamed)";
    alert(
      `Proposed schema:\n\n` +
        `Name: ${name}\n` +
        `Parent: ${parent}\n` +
        `Atoms: ${atoms}\n\n` +
        `(Use the Knowledge Map view to create the schema and add these KCs.)`
    );
    return;
  }
  if (action.action_type === "create_edge" && action.payload.source_candidates) {
    const cands = action.payload.source_candidates as string[];
    alert(
      `Suggested edge endpoints: ${cands.join(", ")}\n\n` +
        `(Use the Knowledge Map view's "Add Edge" tool to create an edge.)`
    );
    return;
  }
  if (action.action_type === "annotate") {
    alert(
      `${action.label}\n\nDismissal/annotation persistence is not yet wired up. ` +
        `For now this is informational.`
    );
    return;
  }
  // Default: navigate to the first involved KC
  if (action.payload.atom_kcs) {
    const atoms = action.payload.atom_kcs as string[];
    if (atoms.length > 0) onNavigateToKC(atoms[0]);
  }
}
