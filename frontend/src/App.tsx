import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { api, type KC, type Edge, type Frame, type Schema, type Stats, type ValidationReport, type QuotientResult, type ConvexityViolation, type LaminarityViolation, type MathDomain, type MathDomainEdge } from "./api";
import { DAGView, type DAGViewHandle } from "./DAGView";
import { MathDomainsView } from "./MathDomainsView";
import { TopologyDiagnosticsView } from "./TopologyDiagnosticsView";
import { SidePanel } from "./SidePanel";

type ActiveView = "kc" | "domains" | "topology";

type ColorMode = "language_demand" | "schema" | "category" | "math_concept";

const DEMAND_COLORS: Record<string, string> = {
  "Speaking": "#4e79a7",
  "Listening": "#f28e2b",
  "Reading": "#e15759",
  "Writing": "#76b7b2",
  "Interpreting a mathematical representation": "#59a14f",
  "Producing a mathematical representation": "#edc948",
};

const MATH_CONCEPT_COLORS: Record<string, string> = {
  "whole-numbers": "#4e79a7",
  "coordinate-plane": "#e15759",
  "integers": "#59a14f",
  "rationals": "#f28e2b",
  "irrationals": "#76b7b2",
  "reals": "#edc948",
  "number-line": "#af7aa1",
};

function computeAtomSet(schemaId: string, schemas: Schema[]): Set<string> {
  const schema = schemas.find((s) => s.id === schemaId);
  if (!schema) return new Set();
  const result = new Set(schema.kc_ids);
  for (const child of schemas.filter((s) => s.parent_schema_id === schemaId)) {
    for (const id of computeAtomSet(child.id, schemas)) result.add(id);
  }
  return result;
}

function parseQuotientError(msg: string): string {
  // Backend returns errors like:
  // "400: Schema CNM-8300 is not convex. Missing nodes: ['CNM-532', 'CNM-533', ...]"
  // "400: Schemas X and Y are not laminar — they partially overlap. Overlap: ['...']"
  // Strip the HTTP status prefix
  const cleaned = msg.replace(/^\d+:\s*/, "");

  // Try to extract detail from JSON error body
  try {
    const parsed = JSON.parse(cleaned);
    if (parsed.detail) return parsed.detail;
  } catch {
    // not JSON, use as-is
  }

  return cleaned;
}

export function App() {
  const [kcs, setKCs] = useState<KC[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [frames, setFrames] = useState<Frame[]>([]);
  const [activeFrame, setActiveFrame] = useState<Frame | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [validation, setValidation] = useState<ValidationReport | null>(null);

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [colorMode, setColorMode] = useState<ColorMode>("schema");
  const [showSchemaOverlay, setShowSchemaOverlay] = useState(true);
  const [showValidationDetail, setShowValidationDetail] = useState(false);
  const [showOnlyActiveFrame, setShowOnlyActiveFrame] = useState(true);
  const [selectedSchemaId, setSelectedSchemaId] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<ActiveView>("kc");
  const [mathDomains, setMathDomains] = useState<MathDomain[]>([]);
  const [mathDomainEdges, setMathDomainEdges] = useState<MathDomainEdge[]>([]);

  const dagViewRef = useRef<DAGViewHandle>(null);

  // Add KC / Add Edge state
  const [showAddKCForm, setShowAddKCForm] = useState(false);
  const [newKCSchemaId, setNewKCSchemaId] = useState("");
  const [newKCId, setNewKCId] = useState("");
  const [newKCDesc, setNewKCDesc] = useState("");
  const [addKCError, setAddKCError] = useState<string | null>(null);
  const [addEdgeMode, setAddEdgeMode] = useState(false);
  const [edgeSource, setEdgeSource] = useState<string | null>(null);
  const [addEdgeError, setAddEdgeError] = useState<string | null>(null);

  // Add Schema state
  const [showAddSchemaForm, setShowAddSchemaForm] = useState(false);
  const [newSchemaId, setNewSchemaId] = useState("");
  const [newSchemaName, setNewSchemaName] = useState("");
  const [newSchemaDesc, setNewSchemaDesc] = useState("");
  const [newSchemaParentId, setNewSchemaParentId] = useState<string>("");
  const [newSchemaKCs, setNewSchemaKCs] = useState<Set<string>>(new Set());
  const [newSchemaKCFilter, setNewSchemaKCFilter] = useState("");
  const [addSchemaError, setAddSchemaError] = useState<string | null>(null);

  const resetAddSchemaForm = () => {
    setShowAddSchemaForm(false);
    setNewSchemaId("");
    setNewSchemaName("");
    setNewSchemaDesc("");
    setNewSchemaParentId("");
    setNewSchemaKCs(new Set());
    setNewSchemaKCFilter("");
    setAddSchemaError(null);
  };

  // Quotient state
  const [quotientSchemaIds, setQuotientSchemaIds] = useState<Set<string>>(new Set());
  const [pendingSchemaIds, setPendingSchemaIds] = useState<Set<string>>(new Set());
  const [quotientResult, setQuotientResult] = useState<QuotientResult | null>(null);
  const [quotientError, setQuotientError] = useState<string | null>(null);
  const [isQuotientView, setIsQuotientView] = useState(false);

  // Load initial data
  useEffect(() => {
    Promise.all([
      api.listKCs({ limit: "1000" }),
      api.listEdges({ limit: "1000" }),
      api.listFrames(),
      api.getStats(),
      api.listMathDomains(),
      api.listMathDomainEdges(),
    ]).then(([kcs, edges, frames, stats, domains, domainEdges]) => {
      setKCs(kcs);
      setEdges(edges);
      setFrames(frames);
      setStats(stats);
      setMathDomains(domains);
      setMathDomainEdges(domainEdges);
      if (frames.length > 0) {
        const ref = frames.find((f) => f.is_reference) || frames[0];
        setActiveFrame(ref);
      }
    });
  }, []);

  // Refresh all data from backend
  const refreshData = useCallback(async () => {
    const [newKCs, newEdges, newFrames, newStats, newDomains, newDomainEdges] = await Promise.all([
      api.listKCs({ limit: "1000" }),
      api.listEdges({ limit: "1000" }),
      api.listFrames(),
      api.getStats(),
      api.listMathDomains(),
      api.listMathDomainEdges(),
    ]);
    setKCs(newKCs);
    setEdges(newEdges);
    setFrames(newFrames);
    setStats(newStats);
    setMathDomains(newDomains);
    setMathDomainEdges(newDomainEdges);
    // Update active frame with fresh data
    if (activeFrame) {
      const updated = newFrames.find((f) => f.id === activeFrame.id);
      if (updated) {
        setActiveFrame(updated);
        api.validateFrame(updated.id).then(setValidation);
      }
    }
  }, [activeFrame]);

  // Validate frame when it changes
  useEffect(() => {
    if (activeFrame) {
      api.validateFrame(activeFrame.id).then(setValidation);
    }
  }, [activeFrame?.id]);

  const handleComputeQuotient = useCallback(async () => {
    if (!activeFrame) return;
    // Merge pending selections into committed set, expanding to include all child schemas
    const allIds = new Set([...quotientSchemaIds, ...pendingSchemaIds]);
    // Recursively add all descendant schemas of selected schemas
    let changed = true;
    while (changed) {
      changed = false;
      for (const s of activeFrame.schemas) {
        if (s.parent_schema_id && allIds.has(s.parent_schema_id) && !allIds.has(s.id)) {
          allIds.add(s.id);
          changed = true;
        }
      }
    }
    if (allIds.size === 0) return;
    try {
      const result = await api.computeQuotient(activeFrame.id, [...allIds]);
      setQuotientResult(result);
      setQuotientSchemaIds(allIds);
      setPendingSchemaIds(new Set());
      setQuotientError(null);
      setIsQuotientView(true);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setQuotientError(msg);
    }
  }, [activeFrame, quotientSchemaIds, pendingSchemaIds]);

  const handleResetQuotient = useCallback(() => {
    setQuotientResult(null);
    setQuotientError(null);
    setIsQuotientView(false);
    setQuotientSchemaIds(new Set());
    setPendingSchemaIds(new Set());
  }, []);

  const togglePendingSchema = useCallback((schemaId: string) => {
    if (!activeFrame) return;
    setPendingSchemaIds((prev) => {
      const next = new Set(prev);
      const adding = !next.has(schemaId);
      // Collect this schema and all descendants
      const affected = new Set<string>([schemaId]);
      let changed = true;
      while (changed) {
        changed = false;
        for (const s of activeFrame.schemas) {
          if (s.parent_schema_id && affected.has(s.parent_schema_id) && !affected.has(s.id)) {
            affected.add(s.id);
            changed = true;
          }
        }
      }
      for (const id of affected) {
        if (adding) next.add(id);
        else next.delete(id);
      }
      return next;
    });
  }, [activeFrame]);

  // Compute KCs in active frame (for frame filtering)
  const frameKCIds = (() => {
    if (!showOnlyActiveFrame || !activeFrame) return null;
    const ids = new Set<string>();
    for (const s of activeFrame.schemas) {
      for (const kcId of s.kc_ids) {
        ids.add(kcId);
      }
    }
    return ids;
  })();

  // Apply frame filter
  const frameFilteredKCs = frameKCIds ? kcs.filter((kc) => frameKCIds.has(kc.id)) : kcs;
  const frameFilteredEdges = frameKCIds
    ? edges.filter((e) => frameKCIds.has(e.source_kc_id) && frameKCIds.has(e.target_kc_id))
    : edges;

  // Apply schema filter
  const schemaAtoms = useMemo(() => {
    if (!selectedSchemaId || !activeFrame) return null;
    return computeAtomSet(selectedSchemaId, activeFrame.schemas);
  }, [selectedSchemaId, activeFrame]);

  const baseKCs = schemaAtoms ? frameFilteredKCs.filter((kc) => schemaAtoms.has(kc.id)) : frameFilteredKCs;
  const baseEdges = schemaAtoms
    ? frameFilteredEdges.filter((e) => schemaAtoms.has(e.source_kc_id) && schemaAtoms.has(e.target_kc_id))
    : frameFilteredEdges;

  // Filter KCs by search
  const filteredKCs = searchQuery
    ? baseKCs.filter(
        (kc) =>
          kc.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          kc.short_description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : baseKCs;

  const filteredKCIds = searchQuery ? new Set(filteredKCs.map((k) => k.id)) : null;

  return (
    <div className="app-layout">
      {/* Left: Control Panel */}
      <div className="control-panel">
        <h1>Living Map</h1>

        <div className="search-bar">
          <input
            type="text"
            placeholder="Search KCs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Frame selector */}
        <div className="control-section">
          <h3>Frame</h3>
          <select
            value={activeFrame?.id || ""}
            onChange={(e) => {
              const f = frames.find((fr) => fr.id === e.target.value);
              if (f) { setActiveFrame(f); handleResetQuotient(); setSelectedSchemaId(null); }
            }}
          >
            {frames.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        </div>

        {/* Color coding */}
        <div className="control-section">
          <h3>Color by</h3>
          <select
            value={colorMode}
            onChange={(e) => setColorMode(e.target.value as ColorMode)}
          >
            <option value="schema">Schema membership</option>
            <option value="language_demand">Language demand</option>
            <option value="math_concept">Math domain</option>
            <option value="category">Category (prefix)</option>
          </select>
          {colorMode === "language_demand" && (
            <div className="legend">
              {Object.entries(DEMAND_COLORS).map(([name, color]) => (
                <div key={name} className="legend-item">
                  <span className="legend-swatch" style={{ background: color }} />
                  <span className="legend-label">{name}</span>
                </div>
              ))}
              <div className="legend-item">
                <span className="legend-swatch" style={{ background: "#888" }} />
                <span className="legend-label">None</span>
              </div>
            </div>
          )}
          {colorMode === "math_concept" && (
            <div className="legend">
              {(() => {
                // Dynamically build legend from KCs actually present
                const concepts = new Set<string>();
                for (const kc of baseKCs) {
                  for (const mc of kc.math_contexts) {
                    concepts.add(mc.math_concept_id);
                  }
                }
                return [...concepts].sort().map((id) => (
                  <div key={id} className="legend-item">
                    <span className="legend-swatch" style={{ background: MATH_CONCEPT_COLORS[id] || "#888" }} />
                    <span className="legend-label">{id.replace(/-/g, " ")}</span>
                  </div>
                ));
              })()}
              <div className="legend-item">
                <span className="legend-swatch" style={{ background: "#888" }} />
                <span className="legend-label">None</span>
              </div>
            </div>
          )}
        </div>

        {/* Display toggles */}
        <div className="control-section">
          <h3>Display</h3>
          <label>
            <input
              type="checkbox"
              checked={showSchemaOverlay}
              onChange={(e) => setShowSchemaOverlay(e.target.checked)}
            />
            Show schema boundaries
          </label>
          <label>
            <input
              type="checkbox"
              checked={showOnlyActiveFrame}
              onChange={(e) => setShowOnlyActiveFrame(e.target.checked)}
            />
            Show only active frame
          </label>
          {activeFrame && (
            <div style={{ marginTop: 8 }}>
              <label style={{ fontSize: 13, fontWeight: 500 }}>Schema filter</label>
              <select
                value={selectedSchemaId || ""}
                onChange={(e) => setSelectedSchemaId(e.target.value || null)}
                style={{ width: "100%", marginTop: 4 }}
              >
                <option value="">All schemas</option>
                {(() => {
                  const schemas = activeFrame.schemas;
                  const byParent = new Map<string | null, typeof schemas>();
                  for (const s of schemas) {
                    const key = s.parent_schema_id && schemas.some((p) => p.id === s.parent_schema_id) ? s.parent_schema_id : null;
                    if (!byParent.has(key)) byParent.set(key, []);
                    byParent.get(key)!.push(s);
                  }
                  for (const children of byParent.values()) children.sort((a, b) => a.id.localeCompare(b.id));
                  const ordered: { schema: typeof schemas[0]; depth: number }[] = [];
                  const walk = (parentId: string | null, depth: number) => {
                    for (const s of byParent.get(parentId) || []) {
                      ordered.push({ schema: s, depth });
                      walk(s.id, depth + 1);
                    }
                  };
                  walk(null, 0);
                  return ordered.map(({ schema: s, depth }) => (
                    <option key={s.id} value={s.id}>
                      {"\u00A0\u00A0".repeat(depth)}{s.id}: {s.name}
                    </option>
                  ));
                })()}
              </select>
            </div>
          )}
        </div>

        {/* Quotient controls */}
        {activeFrame && (
          <div className="control-section">
            <h3>{isQuotientView ? "Quotient — collapse more schemas" : "Quotient — select schemas to collapse"}</h3>

            {/* Summary of already-collapsed schemas */}
            {isQuotientView && quotientResult && (
              <div className="quotient-summary">
                <div className="quotient-stats">
                  {quotientResult.original_node_count} → {quotientResult.quotient_node_count} nodes
                </div>
                <div style={{ marginBottom: 8 }}>
                  {quotientResult.collapsed_nodes.map((c) => (
                    <div key={c.id} className="collapsed-tag">
                      ✓ {c.short_description}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Schema selection list — excludes already-collapsed */}
            <div className="schema-list">
              {(() => {
                // Build a tree-ordered flat list with depth
                const schemas = activeFrame.schemas;
                const byParent = new Map<string | null, typeof schemas>();
                for (const s of schemas) {
                  const key = s.parent_schema_id && schemas.some(p => p.id === s.parent_schema_id) ? s.parent_schema_id : null;
                  if (!byParent.has(key)) byParent.set(key, []);
                  byParent.get(key)!.push(s);
                }
                // Sort children alphabetically within each group
                for (const children of byParent.values()) children.sort((a, b) => a.id.localeCompare(b.id));
                const ordered: { schema: typeof schemas[0]; depth: number }[] = [];
                const walk = (parentId: string | null, depth: number) => {
                  for (const s of byParent.get(parentId) || []) {
                    ordered.push({ schema: s, depth });
                    walk(s.id, depth + 1);
                  }
                };
                walk(null, 0);
                return ordered;
              })()
                .filter(({ schema: s }) => !quotientSchemaIds.has(s.id))
                .map(({ schema: s, depth }) => (
                  <label
                    key={s.id}
                    className="schema-item"
                    style={{ paddingLeft: depth * 16 }}
                  >
                    <input
                      type="checkbox"
                      checked={pendingSchemaIds.has(s.id)}
                      onChange={() => togglePendingSchema(s.id)}
                    />
                    <span title={s.name}>{s.id}: {s.name}</span>
                  </label>
                ))}
            </div>
            <button
              className="quotient-btn"
              disabled={pendingSchemaIds.size === 0}
              onClick={handleComputeQuotient}
            >
              {isQuotientView
                ? `Collapse ${pendingSchemaIds.size} more`
                : `Compute Quotient (${pendingSchemaIds.size} schemas)`}
            </button>
            {quotientError && (
              <div className="quotient-error">
                <div className="quotient-error-title">Quotient failed</div>
                <div className="quotient-error-body">{parseQuotientError(quotientError)}</div>
                <button className="quotient-error-dismiss" onClick={() => setQuotientError(null)}>Dismiss</button>
              </div>
            )}
            {isQuotientView && (
              <button className="reset-btn" onClick={handleResetQuotient}>
                Reset to original DAG
              </button>
            )}
          </div>
        )}

        {/* Empty Schemas */}
        {activeFrame && (() => {
          const emptySchemas = activeFrame.schemas.filter((s) => {
            const hasKCs = s.kc_ids.length > 0;
            const hasChildren = activeFrame.schemas.some((c) => c.parent_schema_id === s.id);
            return !hasKCs && !hasChildren;
          });
          if (emptySchemas.length === 0) return null;
          return (
            <div className="control-section">
              <h3>Empty Schemas ({emptySchemas.length})</h3>
              <div className="schema-list" style={{ maxHeight: 150, overflowY: "auto" }}>
                {emptySchemas.map((s) => (
                  <div
                    key={s.id}
                    className="schema-item empty-schema-item"
                    onClick={() => setSelectedNodeId(`schema-${s.id}`)}
                    style={{ cursor: "pointer" }}
                  >
                    <span className="empty-schema-dot" />
                    <span title={s.name}>{s.id}: {s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}

        {/* Stats */}
        {stats && (
          <div className="stats-bar">
            {stats.knowledge_map.node_count} KCs · {stats.knowledge_map.edge_count} edges · {" "}
            {stats.knowledge_map.connected_components} components · longest path: {stats.knowledge_map.longest_path_length}
          </div>
        )}
      </div>

      {/* Center: Graph */}
      <div className="graph-area">
        {/* View toggle tabs */}
        <div className="view-tabs">
          <button
            className={`view-tab ${activeView === "kc" ? "active" : ""}`}
            onClick={() => { setActiveView("kc"); setSelectedNodeId(null); }}
          >
            Knowledge Map
          </button>
          <button
            className={`view-tab ${activeView === "domains" ? "active" : ""}`}
            onClick={() => { setActiveView("domains"); setSelectedNodeId(null); }}
          >
            Math Domains
          </button>
          <button
            className={`view-tab ${activeView === "topology" ? "active" : ""}`}
            onClick={() => { setActiveView("topology"); setSelectedNodeId(null); }}
          >
            Topology
          </button>
        </div>

        {activeView === "kc" && validation && (
          <div className="validation-panel-wrapper">
            <div
              className={`validation-badge ${validation.valid ? "valid" : "invalid"}`}
              onClick={() => setShowValidationDetail((v) => !v)}
              style={{ cursor: "pointer" }}
              title="Click for details"
            >
              {validation.valid ? "Frame valid ✓" : "Frame has violations ✗"}
              <span style={{ marginLeft: 6, fontSize: 10 }}>{showValidationDetail ? "▲" : "▼"}</span>
            </div>
            {showValidationDetail && (
              <div className="validation-detail">
                {Object.entries(validation.checks).map(([name, check]) => {
                  const label = name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
                  return (
                    <div key={name} className="validation-check">
                      <div className="validation-check-header">
                        <span className={`check-status ${check.status}`}>
                          {check.status === "valid" ? "✓" : "✗"}
                        </span>
                        {label}
                      </div>
                      {check.status === "violation" && name === "schema_convexity" && check.violations && (
                        <div className="violation-details">
                          {(check.violations as ConvexityViolation[]).map((v) => (
                            <div key={v.schema_id} className="violation-item">
                              <strong>{v.schema_id}</strong> is missing nodes:{" "}
                              {v.missing_nodes.map((n, i) => (
                                <span key={n}>
                                  {i > 0 && ", "}
                                  <span className="node-link" onClick={() => { setSelectedNodeId(n); setShowValidationDetail(false); }}>{n}</span>
                                </span>
                              ))}
                            </div>
                          ))}
                        </div>
                      )}
                      {check.status === "violation" && name === "laminarity" && check.violations && (
                        <div className="violation-details">
                          {(check.violations as LaminarityViolation[]).map((v, i) => (
                            <div key={i} className="violation-item">
                              <strong>{v.schema_a}</strong> and <strong>{v.schema_b}</strong> partially overlap
                              <div style={{ fontSize: 11, color: "#666", marginTop: 2 }}>
                                Overlap: {v.overlap.join(", ")}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      {check.status === "violation" && name === "frame_acyclicity" && check.cycles && (
                        <div className="violation-details">
                          {check.cycles.map((cycle, i) => (
                            <div key={i} className="violation-item">
                              Cycle: {cycle.join(" → ")} → {cycle[0]}
                            </div>
                          ))}
                        </div>
                      )}
                      {check.status === "violation" && name === "downward_closure" && check.violations && (
                        <div className="violation-details">
                          {(check.violations as { missing: string; parent: string }[]).map((v, i) => (
                            <div key={i} className="violation-item">
                              Schema <strong>{v.missing}</strong> (child of {v.parent}) is missing from frame
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Knowledge Map toolbar */}
        {activeView === "kc" && (
          <div className="km-toolbar">
            <button
              className={`toolbar-btn ${showAddKCForm ? "active" : ""}`}
              onClick={() => { setShowAddKCForm(!showAddKCForm); setAddKCError(null); }}
            >
              + Add KC
            </button>
            <button
              className={`toolbar-btn ${showAddSchemaForm ? "active" : ""}`}
              onClick={() => {
                if (showAddSchemaForm) {
                  resetAddSchemaForm();
                } else {
                  setShowAddSchemaForm(true);
                  setAddSchemaError(null);
                }
              }}
            >
              + Add Schema
            </button>
            <button
              className={`toolbar-btn ${addEdgeMode ? "active" : ""}`}
              onClick={() => {
                setAddEdgeMode(!addEdgeMode);
                setEdgeSource(null);
                setAddEdgeError(null);
              }}
            >
              {addEdgeMode
                ? edgeSource
                  ? "Click target KC..."
                  : "Click source KC..."
                : "Add Edge"}
            </button>
            {addEdgeMode && (
              <button className="toolbar-btn cancel" onClick={() => { setAddEdgeMode(false); setEdgeSource(null); setAddEdgeError(null); }}>
                Cancel
              </button>
            )}
            <button
              className="toolbar-btn"
              onClick={() => dagViewRef.current?.resetLayout()}
              title="Re-run automatic layout"
            >
              Reset Layout
            </button>
            {showAddKCForm && (
              <div className="add-domain-form">
                <label className="form-label">Schema</label>
                <select
                  className="domain-input"
                  value={newKCSchemaId}
                  onChange={async (e) => {
                    const schemaId = e.target.value;
                    setNewKCSchemaId(schemaId);
                    setNewKCId("");
                    if (schemaId) {
                      try {
                        const { next_id } = await api.getNextKCId(schemaId);
                        setNewKCId(next_id);
                      } catch {
                        setNewKCId("");
                      }
                    }
                  }}
                >
                  <option value="">Select a schema...</option>
                  {activeFrame?.schemas.map((s) => (
                    <option key={s.id} value={s.id}>{s.id}: {s.name}</option>
                  ))}
                </select>
                {newKCId && (
                  <div className="generated-id">
                    ID: <strong>{newKCId}</strong>
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Short description"
                  value={newKCDesc}
                  onChange={(e) => setNewKCDesc(e.target.value)}
                  className="domain-input"
                />
                <div className="form-actions">
                  <button
                    className="toolbar-btn create"
                    disabled={!newKCId || !newKCDesc.trim()}
                    onClick={async () => {
                      setAddKCError(null);
                      try {
                        await api.createKC({ id: newKCId, short_description: newKCDesc.trim() });
                        // Also add to the selected schema
                        if (newKCSchemaId) {
                          await api.addKCsToSchema(newKCSchemaId, [newKCId]);
                        }
                        setShowAddKCForm(false);
                        setNewKCSchemaId("");
                        setNewKCId("");
                        setNewKCDesc("");
                        await refreshData();
                      } catch (e) {
                        setAddKCError(e instanceof Error ? e.message : String(e));
                      }
                    }}
                  >
                    Create
                  </button>
                  <button className="toolbar-btn cancel" onClick={() => { setShowAddKCForm(false); setNewKCSchemaId(""); setNewKCId(""); setNewKCDesc(""); }}>Cancel</button>
                </div>
                {addKCError && <div className="domain-error">{addKCError}</div>}
              </div>
            )}
            {showAddSchemaForm && activeFrame && (
              <div className="add-domain-form add-schema-form">
                <label className="form-label">Schema ID</label>
                <input
                  type="text"
                  placeholder="e.g. CNM-8240"
                  value={newSchemaId}
                  onChange={(e) => setNewSchemaId(e.target.value)}
                  className="domain-input"
                />
                <label className="form-label">Name</label>
                <input
                  type="text"
                  placeholder="Schema name"
                  value={newSchemaName}
                  onChange={(e) => setNewSchemaName(e.target.value)}
                  className="domain-input"
                />
                <label className="form-label">Description (optional)</label>
                <textarea
                  placeholder="Schema description"
                  value={newSchemaDesc}
                  onChange={(e) => setNewSchemaDesc(e.target.value)}
                  className="domain-input"
                  rows={2}
                />
                <label className="form-label">Parent schema (optional)</label>
                <select
                  className="domain-input"
                  value={newSchemaParentId}
                  onChange={(e) => setNewSchemaParentId(e.target.value)}
                >
                  <option value="">— none (top-level) —</option>
                  {activeFrame.schemas.map((s) => (
                    <option key={s.id} value={s.id}>{s.id}: {s.name}</option>
                  ))}
                </select>
                <label className="form-label">
                  KCs to include ({newSchemaKCs.size} selected)
                </label>
                <input
                  type="text"
                  placeholder="Filter KCs..."
                  value={newSchemaKCFilter}
                  onChange={(e) => setNewSchemaKCFilter(e.target.value)}
                  className="domain-input"
                />
                <div className="schema-kc-list">
                  {frameFilteredKCs
                    .filter((kc) => {
                      const q = newSchemaKCFilter.toLowerCase();
                      if (!q) return true;
                      return (
                        kc.id.toLowerCase().includes(q) ||
                        kc.short_description.toLowerCase().includes(q)
                      );
                    })
                    .map((kc) => (
                      <label key={kc.id} className="schema-kc-row">
                        <input
                          type="checkbox"
                          checked={newSchemaKCs.has(kc.id)}
                          onChange={(e) => {
                            const next = new Set(newSchemaKCs);
                            if (e.target.checked) next.add(kc.id);
                            else next.delete(kc.id);
                            setNewSchemaKCs(next);
                          }}
                        />
                        <span className="schema-kc-id">{kc.id}</span>
                        <span className="schema-kc-desc">{kc.short_description}</span>
                      </label>
                    ))}
                </div>
                <div className="form-actions">
                  <button
                    className="toolbar-btn create"
                    disabled={!newSchemaId.trim() || !newSchemaName.trim()}
                    onClick={async () => {
                      setAddSchemaError(null);
                      try {
                        await api.createSchema(activeFrame.id, {
                          id: newSchemaId.trim(),
                          name: newSchemaName.trim(),
                          description: newSchemaDesc.trim() || undefined,
                          parent_schema_id: newSchemaParentId || null,
                        });
                        if (newSchemaKCs.size > 0) {
                          await api.addKCsToSchema(newSchemaId.trim(), Array.from(newSchemaKCs));
                        }
                        resetAddSchemaForm();
                        await refreshData();
                      } catch (e) {
                        const msg = e instanceof Error ? e.message : String(e);
                        setAddSchemaError(msg.replace(/^\d+:\s*/, ""));
                      }
                    }}
                  >
                    Create
                  </button>
                  <button className="toolbar-btn cancel" onClick={resetAddSchemaForm}>Cancel</button>
                </div>
                {addSchemaError && <div className="domain-error">{addSchemaError}</div>}
              </div>
            )}
            {addEdgeError && (
              <div className="domain-error-banner">
                {addEdgeError}
                <button onClick={() => setAddEdgeError(null)}>Dismiss</button>
              </div>
            )}
          </div>
        )}

        {activeView === "kc" && (
          <DAGView
            ref={dagViewRef}
            kcs={baseKCs}
            edges={baseEdges}
            frame={activeFrame}
            colorMode={colorMode}
            showSchemaOverlay={showSchemaOverlay}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
            onDeleteEdge={async (edgeId) => {
              await api.deleteEdge(edgeId);
              await refreshData();
            }}
            addEdgeMode={addEdgeMode}
            edgeSource={edgeSource}
            onEdgeNodeClick={async (nodeId) => {
              if (!edgeSource) {
                setEdgeSource(nodeId);
                setAddEdgeError(null);
              } else {
                if (nodeId === edgeSource) {
                  setEdgeSource(null);
                  return;
                }
                try {
                  await api.createEdge(edgeSource, nodeId);
                  setAddEdgeMode(false);
                  setEdgeSource(null);
                  setAddEdgeError(null);
                  await refreshData();
                } catch (e) {
                  const msg = e instanceof Error ? e.message : String(e);
                  setAddEdgeError(msg.replace(/^\d+:\s*/, ""));
                  setEdgeSource(null);
                }
              }
            }}
            filteredKCIds={filteredKCIds}
            quotientResult={isQuotientView ? quotientResult : null}
            collapsedSchemaIds={quotientSchemaIds}
          />
        )}
        {activeView === "domains" && (
          <MathDomainsView
            domains={mathDomains}
            domainEdges={mathDomainEdges}
            selectedDomainId={selectedNodeId}
            onSelectDomain={setSelectedNodeId}
            onRefresh={refreshData}
          />
        )}
        {activeView === "topology" && (
          <TopologyDiagnosticsView
            frame={activeFrame}
            kcs={kcs}
            edges={edges}
            onNavigateToKC={(kcId) => {
              setActiveView("kc");
              setSelectedNodeId(kcId);
            }}
          />
        )}
      </div>

      {/* Right: Side Panel */}
      <SidePanel
        selectedNodeId={selectedNodeId}
        kcs={kcs}
        edges={edges}
        frame={activeFrame}
        onSelectNode={setSelectedNodeId}
        onDataChanged={refreshData}
        quotientResult={isQuotientView ? quotientResult : null}
        mathDomains={mathDomains}
        mathDomainEdges={mathDomainEdges}
      />
    </div>
  );
}
