import { useState, useEffect, useCallback } from "react";
import { api, type KC, type Edge, type Frame, type Schema, type Annotation, type QuotientResult, type MathDomain, type MathDomainEdge } from "./api";

const ALL_DEMANDS = [
  "Speaking",
  "Listening",
  "Reading",
  "Writing",
  "Interpreting a mathematical representation",
  "Producing a mathematical representation",
];

interface SidePanelProps {
  selectedNodeId: string | null;
  kcs: KC[];
  edges: Edge[];
  frame: Frame | null;
  onSelectNode: (id: string | null) => void;
  onDataChanged: () => Promise<void>;
  quotientResult: QuotientResult | null;
  mathDomains: MathDomain[];
  mathDomainEdges: MathDomainEdge[];
}

export function SidePanel({ selectedNodeId, kcs, edges, frame, onSelectNode, onDataChanged, quotientResult, mathDomains, mathDomainEdges }: SidePanelProps) {
  const [ancestors, setAncestors] = useState<string[]>([]);
  const [descendants, setDescendants] = useState<string[]>([]);
  const [schemas, setSchemas] = useState<Schema[]>([]);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [atomSet, setAtomSet] = useState<string[]>([]);
  const [convexity, setConvexity] = useState<{ status: string; missing_nodes?: string[] } | null>(null);

  // Editing state
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [mathConcepts, setMathConcepts] = useState<{ id: string; name: string }[]>([]);
  const [knownKCTypes, setKnownKCTypes] = useState<string[]>(["Skill", "Fact"]);
  const [addingNewType, setAddingNewType] = useState(false);
  const [newTypeName, setNewTypeName] = useState("");

  // Load available math concepts and known KC types once
  useEffect(() => {
    api.listMathConcepts().then(setMathConcepts).catch(() => {});
    api.listKCTypes().then((types) => {
      const all = new Set(types);
      all.add("Skill");
      all.add("Fact");
      setKnownKCTypes(Array.from(all).sort());
    }).catch(() => {});
  }, []);

  // Determine if this is a schema or domain selection
  const isSchemaSelection = selectedNodeId?.startsWith("schema-") ?? false;
  const schemaId = isSchemaSelection ? selectedNodeId!.replace("schema-", "") : null;
  const isDomainSelection = selectedNodeId?.startsWith("domain-") ?? false;
  const domainId = isDomainSelection ? selectedNodeId!.replace("domain-", "") : null;

  useEffect(() => {
    setEditingField(null);
    setError(null);
    setConfirmDelete(false);

    if (!selectedNodeId) {
      setAncestors([]);
      setDescendants([]);
      setSchemas([]);
      setAnnotations([]);
      setAtomSet([]);
      setConvexity(null);
      return;
    }

    if (isSchemaSelection && schemaId) {
      setAncestors([]);
      setDescendants([]);
      setSchemas([]);
      setAnnotations([]);
      api.getSchemaAtoms(schemaId).then(setAtomSet).catch(() => setAtomSet([]));
      api.checkConvexity(schemaId).then(setConvexity).catch(() => setConvexity(null));
      return;
    }

    if (selectedNodeId.startsWith("[")) {
      setAncestors([]);
      setDescendants([]);
      setSchemas([]);
      setAnnotations([]);
      setAtomSet([]);
      setConvexity(null);
      return;
    }

    setAtomSet([]);
    setConvexity(null);
    api.getKCAncestors(selectedNodeId).then(setAncestors).catch(() => setAncestors([]));
    api.getKCDescendants(selectedNodeId).then(setDescendants).catch(() => setDescendants([]));
    api.getKCSchemas(selectedNodeId).then(setSchemas).catch(() => setSchemas([]));
    api.getAnnotations("kc", selectedNodeId).then(setAnnotations).catch(() => setAnnotations([]));
  }, [selectedNodeId, isSchemaSelection, schemaId]);

  const saveField = useCallback(async (field: string, value: string) => {
    if (!selectedNodeId) return;
    setSaving(true);
    setError(null);
    try {
      if (field === "short_description" || field === "long_description") {
        await api.updateKC(selectedNodeId, { [field]: value });
      } else if (field === "schema_name" && schemaId) {
        await api.updateSchema(schemaId, { name: value });
      } else if (field === "schema_description" && schemaId) {
        await api.updateSchema(schemaId, { description: value });
      } else if (field === "schema_parent" && schemaId) {
        await api.updateSchema(schemaId, { parent_schema_id: value || null });
      } else if (field === "domain_name" && domainId) {
        await api.updateMathDomain(domainId, { name: value });
      } else if (field === "domain_description" && domainId) {
        await api.updateMathDomain(domainId, { description: value });
      }
      await onDataChanged();
      setEditingField(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }, [selectedNodeId, schemaId, domainId, onDataChanged]);

  const toggleDemand = useCallback(async (demand: string, currentDemands: string[]) => {
    if (!selectedNodeId) return;
    setError(null);
    const newDemands = currentDemands.includes(demand)
      ? currentDemands.filter((d) => d !== demand)
      : [...currentDemands, demand];
    try {
      await api.updateKCLanguageDemands(selectedNodeId, newDemands);
      await onDataChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [selectedNodeId, onDataChanged]);

  const handleDeleteEdge = useCallback(async (edgeId: number) => {
    setError(null);
    try {
      await api.deleteEdge(edgeId);
      await onDataChanged();
      // Re-fetch ancestors/descendants
      if (selectedNodeId) {
        api.getKCAncestors(selectedNodeId).then(setAncestors);
        api.getKCDescendants(selectedNodeId).then(setDescendants);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [selectedNodeId, onDataChanged]);

  const handleAddEdge = useCallback(async (sourceId: string, targetId: string) => {
    setError(null);
    try {
      await api.createEdge(sourceId, targetId);
      await onDataChanged();
      if (selectedNodeId) {
        api.getKCAncestors(selectedNodeId).then(setAncestors);
        api.getKCDescendants(selectedNodeId).then(setDescendants);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [selectedNodeId, onDataChanged]);

  const handleDeleteKC = useCallback(async () => {
    if (!selectedNodeId) return;
    setError(null);
    try {
      await api.deleteKC(selectedNodeId);
      onSelectNode(null);
      await onDataChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [selectedNodeId, onSelectNode, onDataChanged]);

  const handleRemoveKCFromSchema = useCallback(async (sid: string, kcId: string) => {
    setError(null);
    try {
      await api.removeKCFromSchema(sid, kcId);
      await onDataChanged();
      // Re-fetch schema data
      if (schemaId) {
        api.getSchemaAtoms(schemaId).then(setAtomSet);
        api.checkConvexity(schemaId).then(setConvexity);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [schemaId, onDataChanged]);

  const handleAddKCToSchema = useCallback(async (sid: string, kcId: string) => {
    setError(null);
    try {
      await api.addKCsToSchema(sid, [kcId]);
      await onDataChanged();
      if (schemaId) {
        api.getSchemaAtoms(schemaId).then(setAtomSet);
        api.checkConvexity(schemaId).then(setConvexity);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [schemaId, onDataChanged]);

  // Find edge ID for a given source/target pair
  const findEdgeId = (sourceId: string, targetId: string): number | null => {
    const edge = edges.find((e) => e.source_kc_id === sourceId && e.target_kc_id === targetId);
    return edge ? edge.id : null;
  };

  // Find direct predecessors (not transitive ancestors)
  const directPredecessors = selectedNodeId
    ? edges.filter((e) => e.target_kc_id === selectedNodeId).map((e) => e.source_kc_id)
    : [];

  // Find direct successors
  const directSuccessors = selectedNodeId
    ? edges.filter((e) => e.source_kc_id === selectedNodeId).map((e) => e.target_kc_id)
    : [];

  if (!selectedNodeId) {
    return (
      <div className="side-panel">
        <p className="empty-state">Click a node to see details</p>
      </div>
    );
  }

  // Inline editable text field
  const EditableField = ({ field, value, multiline }: { field: string; value: string; multiline?: boolean }) => {
    if (editingField === field) {
      return (
        <div className="editable-field">
          {multiline ? (
            <textarea
              className="edit-input"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Escape") setEditingField(null);
                if (e.key === "Enter" && e.metaKey) saveField(field, editValue);
              }}
              autoFocus
              rows={4}
            />
          ) : (
            <input
              className="edit-input"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Escape") setEditingField(null);
                if (e.key === "Enter") saveField(field, editValue);
              }}
              autoFocus
            />
          )}
          <div className="edit-actions">
            <button className="edit-save" onClick={() => saveField(field, editValue)} disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </button>
            <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
          </div>
        </div>
      );
    }
    return (
      <div
        className="editable-text"
        onClick={() => { setEditingField(field); setEditValue(value); }}
        title="Click to edit"
      >
        {value || <span style={{ color: "#aaa", fontStyle: "italic" }}>Click to add...</span>}
        <span className="edit-icon">✎</span>
      </div>
    );
  };

  // Error display
  const ErrorBanner = () =>
    error ? (
      <div className="side-panel-error">
        {error.replace(/^\d+:\s*/, "")}
        <button onClick={() => setError(null)}>✕</button>
      </div>
    ) : null;

  // Schema detail view
  if (isSchemaSelection && schemaId && frame) {
    const schema = frame.schemas.find((s) => s.id === schemaId);
    if (schema) {
      const childSchemas = frame.schemas.filter((s) => s.parent_schema_id === schemaId);
      const parentSchema = schema.parent_schema_id
        ? frame.schemas.find((s) => s.id === schema.parent_schema_id)
        : null;

      // KCs not in this schema (for adding)
      const availableKCs = kcs.filter((kc) => !schema.kc_ids.includes(kc.id));

      return (
        <div className="side-panel">
          <div className="panel-header">
            <h2>Schema: {schema.id}</h2>
            <button className="panel-close" onClick={() => onSelectNode(null)} title="Close">✕</button>
          </div>
          <ErrorBanner />

          <div className="detail-row">
            <div className="detail-label">Name</div>
            <div className="detail-value">
              <EditableField field="schema_name" value={schema.name} />
            </div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Parent Schema</div>
            <div className="detail-value">
              {editingField === "schema_parent" ? (
                <div className="add-item-form">
                  <select
                    className="edit-input"
                    autoFocus
                    defaultValue={schema.parent_schema_id || ""}
                    onChange={(e) => {
                      saveField("schema_parent", e.target.value);
                    }}
                  >
                    <option value="">— none (top-level) —</option>
                    {frame.schemas
                      .filter((s) => s.id !== schemaId)
                      .map((s) => (
                        <option key={s.id} value={s.id}>{s.id}: {s.name}</option>
                      ))}
                  </select>
                  <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
                </div>
              ) : parentSchema ? (
                <>
                  <span className="node-link" onClick={() => onSelectNode(`schema-${parentSchema.id}`)}>
                    {parentSchema.id}: {parentSchema.name}
                  </span>{" "}
                  <button className="add-btn" onClick={() => setEditingField("schema_parent")}>Change</button>
                </>
              ) : (
                <>
                  <span style={{ color: "#aaa" }}>None (top-level)</span>{" "}
                  <button className="add-btn" onClick={() => setEditingField("schema_parent")}>Set parent</button>
                </>
              )}
            </div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Description</div>
            <div className="detail-value">
              <EditableField field="schema_description" value={schema.description || ""} multiline />
            </div>
          </div>

          {childSchemas.length > 0 && (
            <div className="detail-row">
              <div className="detail-label">Child Schemas ({childSchemas.length})</div>
              <div className="detail-value node-list">
                {childSchemas.map((cs) => (
                  <div key={cs.id}>
                    <span className="node-link" onClick={() => onSelectNode(`schema-${cs.id}`)}>
                      {cs.id}: {cs.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="detail-row">
            <div className="detail-label">Direct KCs ({schema.kc_ids.length})</div>
            <div className="detail-value node-list">
              {schema.kc_ids.length === 0 ? (
                <span style={{ color: "#aaa" }}>None (has child schemas only)</span>
              ) : (
                schema.kc_ids.map((id) => {
                  const kc = kcs.find((k) => k.id === id);
                  return (
                    <div key={id} className="editable-list-item">
                      <span className="node-link" onClick={() => onSelectNode(id)}>
                        {id}
                      </span>
                      {kc && <span style={{ color: "#666" }}> — {kc.short_description}</span>}
                      <button
                        className="remove-btn"
                        onClick={() => handleRemoveKCFromSchema(schemaId, id)}
                        title="Remove from schema"
                      >✕</button>
                    </div>
                  );
                })
              )}
              {/* Add KC to schema */}
              {editingField === "add_kc_to_schema" ? (
                <div className="add-item-form">
                  <select
                    className="edit-input"
                    autoFocus
                    onChange={(e) => {
                      if (e.target.value) {
                        handleAddKCToSchema(schemaId, e.target.value);
                        setEditingField(null);
                      }
                    }}
                  >
                    <option value="">Select a KC...</option>
                    {availableKCs.map((kc) => (
                      <option key={kc.id} value={kc.id}>{kc.id}: {kc.short_description}</option>
                    ))}
                  </select>
                  <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
                </div>
              ) : (
                <button className="add-btn" onClick={() => setEditingField("add_kc_to_schema")}>+ Add KC</button>
              )}
            </div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Atom Set ({atomSet.length} KCs)</div>
            <div className="detail-value node-list" style={{ maxHeight: 200, overflowY: "auto" }}>
              {atomSet.map((id) => {
                const kc = kcs.find((k) => k.id === id);
                return (
                  <div key={id}>
                    <span className="node-link" onClick={() => onSelectNode(id)}>{id}</span>
                    {kc && <span style={{ color: "#666" }}> — {kc.short_description}</span>}
                  </div>
                );
              })}
            </div>
          </div>

          {convexity && (
            <div className="detail-row">
              <div className="detail-label">Convexity</div>
              <div className="detail-value">
                {convexity.status === "valid" ? (
                  <span className="tag" style={{ background: "#d4edda", color: "#155724" }}>Convex ✓</span>
                ) : (
                  <>
                    <span className="tag" style={{ background: "#f8d7da", color: "#721c24" }}>Not convex ✗</span>
                    {convexity.missing_nodes && (
                      <div style={{ marginTop: 4, fontSize: 11, color: "#721c24" }}>
                        Missing: {convexity.missing_nodes.map((n, i) => (
                          <span key={n}>
                            {i > 0 && ", "}
                            <span className="node-link" onClick={() => onSelectNode(n)}>{n}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Delete schema */}
          {(() => {
            // Collect all descendant schemas recursively
            const allDescendants: typeof frame.schemas = [];
            const collectDescendants = (parentId: string) => {
              for (const s of frame.schemas) {
                if (s.parent_schema_id === parentId) {
                  allDescendants.push(s);
                  collectDescendants(s.id);
                }
              }
            };
            collectDescendants(schemaId);

            const hasOwnKCs = schema.kc_ids.length > 0;
            const descendantsWithKCs = allDescendants.filter((s) => s.kc_ids.length > 0);
            const hasNonEmptyDescendants = descendantsWithKCs.length > 0;
            const hasEmptyDescendantsOnly = allDescendants.length > 0 && !hasNonEmptyDescendants;

            // Block deletion only if this schema or any descendant has KCs
            const canDelete = !hasOwnKCs && !hasNonEmptyDescendants;
            const deleteCount = 1 + allDescendants.length;

            return (
              <div className="detail-row danger-zone">
                {!canDelete ? (
                  <div style={{ fontSize: 11, color: "#999" }}>
                    Cannot delete — {hasOwnKCs ? `${schema.kc_ids.length} KC${schema.kc_ids.length !== 1 ? "s" : ""} assigned` : ""}
                    {hasOwnKCs && hasNonEmptyDescendants ? ", " : ""}
                    {hasNonEmptyDescendants ? `${descendantsWithKCs.length} non-empty child schema${descendantsWithKCs.length !== 1 ? "s" : ""}` : ""}
                  </div>
                ) : confirmDelete ? (
                  <div className="confirm-delete">
                    <span>
                      {hasEmptyDescendantsOnly
                        ? `Delete this schema and ${allDescendants.length} empty sub-schema${allDescendants.length !== 1 ? "s" : ""}? This cannot be undone.`
                        : "Delete this schema? This cannot be undone."}
                    </span>
                    <div className="confirm-actions">
                      <button
                        className="delete-confirm-btn"
                        onClick={async () => {
                          setError(null);
                          try {
                            // Delete descendants bottom-up (leaves first)
                            const reversed = [...allDescendants].reverse();
                            for (const s of reversed) {
                              await api.deleteSchema(s.id);
                            }
                            await api.deleteSchema(schemaId);
                            onSelectNode(null);
                            await onDataChanged();
                          } catch (err) {
                            setError(err instanceof Error ? err.message : String(err));
                          }
                        }}
                      >Yes, delete{deleteCount > 1 ? ` all ${deleteCount}` : ""}</button>
                      <button className="edit-cancel" onClick={() => setConfirmDelete(false)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <button className="delete-btn" onClick={() => setConfirmDelete(true)}>
                    {hasEmptyDescendantsOnly ? `Delete Schema + ${allDescendants.length} empty sub-schemas` : "Delete Schema"}
                  </button>
                )}
              </div>
            );
          })()}
        </div>
      );
    }
  }

  // Math Domain detail view
  if (isDomainSelection && domainId) {
    const domain = mathDomains.find((d) => d.id === domainId);
    if (domain) {
      // Find edges involving this domain
      const outEdges = mathDomainEdges.filter((e) => e.source_id === domainId);
      const inEdges = mathDomainEdges.filter((e) => e.target_id === domainId);
      // Count KCs linked to this domain
      const linkedKCs = kcs.filter((kc) => kc.math_contexts.some((mc) => mc.math_concept_id === domainId));

      return (
        <div className="side-panel">
          <div className="panel-header">
            <h2>{domain.name}</h2>
            <button className="panel-close" onClick={() => onSelectNode(null)} title="Close">✕</button>
          </div>
          <ErrorBanner />

          <div className="detail-row">
            <div className="detail-label">ID</div>
            <div className="detail-value">{domain.id}</div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Name</div>
            <div className="detail-value">
              <EditableField field="domain_name" value={domain.name} />
            </div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Description</div>
            <div className="detail-value">
              <EditableField field="domain_description" value={domain.description || ""} multiline />
            </div>
          </div>

          {outEdges.length > 0 && (
            <div className="detail-row">
              <div className="detail-label">Depends on ({outEdges.length})</div>
              <div className="detail-value node-list">
                {outEdges.map((e) => {
                  const target = mathDomains.find((d) => d.id === e.target_id);
                  return (
                    <div key={e.id} className="editable-list-item">
                      <span className="node-link" onClick={() => onSelectNode(`domain-${e.target_id}`)}>
                        {target ? target.name : e.target_id}
                      </span>
                      <button
                        className="remove-btn"
                        onClick={async () => {
                          setError(null);
                          try {
                            await api.deleteMathDomainEdge(e.id);
                            await onDataChanged();
                          } catch (err) {
                            setError(err instanceof Error ? err.message : String(err));
                          }
                        }}
                        title="Remove edge"
                      >✕</button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {inEdges.length > 0 && (
            <div className="detail-row">
              <div className="detail-label">Required by ({inEdges.length})</div>
              <div className="detail-value node-list">
                {inEdges.map((e) => {
                  const source = mathDomains.find((d) => d.id === e.source_id);
                  return (
                    <div key={e.id} className="editable-list-item">
                      <span className="node-link" onClick={() => onSelectNode(`domain-${e.source_id}`)}>
                        {source ? source.name : e.source_id}
                      </span>
                      <button
                        className="remove-btn"
                        onClick={async () => {
                          setError(null);
                          try {
                            await api.deleteMathDomainEdge(e.id);
                            await onDataChanged();
                          } catch (err) {
                            setError(err instanceof Error ? err.message : String(err));
                          }
                        }}
                        title="Remove edge"
                      >✕</button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="detail-row">
            <div className="detail-label">Linked KCs ({linkedKCs.length})</div>
            <div className="detail-value node-list" style={{ maxHeight: 200, overflowY: "auto" }}>
              {linkedKCs.length === 0 ? (
                <span style={{ color: "#aaa" }}>No KCs linked to this domain</span>
              ) : (
                linkedKCs.map((kc) => (
                  <div key={kc.id}>
                    <span className="node-link" onClick={() => onSelectNode(kc.id)}>
                      {kc.id}
                    </span>
                    <span style={{ color: "#666" }}> — {kc.short_description}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Delete domain */}
          <div className="detail-row danger-zone">
            {linkedKCs.length > 0 ? (
              <div style={{ fontSize: 11, color: "#999" }}>
                Cannot delete — {linkedKCs.length} KC{linkedKCs.length !== 1 ? "s" : ""} linked
              </div>
            ) : confirmDelete ? (
              <div className="confirm-delete">
                <span>Delete this domain? This cannot be undone.</span>
                <div className="confirm-actions">
                  <button
                    className="delete-confirm-btn"
                    onClick={async () => {
                      setError(null);
                      try {
                        await api.deleteMathDomain(domainId);
                        onSelectNode(null);
                        await onDataChanged();
                      } catch (err) {
                        setError(err instanceof Error ? err.message : String(err));
                      }
                    }}
                  >Yes, delete</button>
                  <button className="edit-cancel" onClick={() => setConfirmDelete(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <button className="delete-btn" onClick={() => setConfirmDelete(true)}>Delete Domain</button>
            )}
          </div>
        </div>
      );
    }
  }

  // Collapsed quotient node (read-only)
  const collapsedNode = quotientResult?.collapsed_nodes.find((c) => c.id === selectedNodeId);
  if (collapsedNode) {
    return (
      <div className="side-panel">
        <div className="panel-header">
          <h2>{collapsedNode.id}</h2>
          <button className="panel-close" onClick={() => onSelectNode(null)} title="Close">✕</button>
        </div>
        <div className="detail-row">
          <div className="detail-label">Description</div>
          <div className="detail-value">{collapsedNode.short_description}</div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Source Schema</div>
          <div className="detail-value">{collapsedNode.source_schema_id}</div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Language Demands (inherited union)</div>
          <div className="detail-value">
            {collapsedNode.language_demands.map((d) => (
              <span key={d} className="tag">{d}</span>
            ))}
          </div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Math Domains</div>
          <div className="detail-value">
            {collapsedNode.math_contexts.map((ctx) => (
              <span key={ctx.math_concept_id} className="tag math">
                {ctx.math_concept_id} ({ctx.role})
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Normal KC — editable
  const kc = kcs.find((k) => k.id === selectedNodeId);
  if (!kc) {
    return (
      <div className="side-panel">
        <p className="empty-state">KC not found: {selectedNodeId}</p>
      </div>
    );
  }

  const kcType = annotations.find((a) => a.annotation_type === "kc_type");

  return (
    <div className="side-panel">
      <div className="panel-header">
        <h2>{kc.id}</h2>
        <button className="panel-close" onClick={() => onSelectNode(null)} title="Close">✕</button>
      </div>
      <ErrorBanner />

      <div className="detail-row">
        <div className="detail-label">Short Description</div>
        <div className="detail-value">
          <EditableField field="short_description" value={kc.short_description} />
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">Long Description</div>
        <div className="detail-value">
          <EditableField field="long_description" value={kc.long_description || ""} multiline />
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">KC Type</div>
        <div className="detail-value">
          {addingNewType ? (
            <div className="new-type-input">
              <input
                type="text"
                value={newTypeName}
                onChange={(e) => setNewTypeName(e.target.value)}
                placeholder="Enter new type name"
                autoFocus
                onKeyDown={async (e) => {
                  if (e.key === "Enter" && newTypeName.trim()) {
                    const val = newTypeName.trim();
                    try {
                      if (kcType) {
                        await api.updateAnnotation(kcType.id, { content: val });
                      } else {
                        await api.createAnnotation({
                          entity_type: "kc",
                          entity_id: kc.id,
                          annotation_type: "kc_type",
                          content: val,
                        });
                      }
                      const updated = await api.getAnnotations("kc", kc.id);
                      setAnnotations(updated);
                      setKnownKCTypes((prev) => Array.from(new Set([...prev, val])).sort());
                      setAddingNewType(false);
                      setNewTypeName("");
                    } catch {
                      setError("Failed to set KC type");
                    }
                  } else if (e.key === "Escape") {
                    setAddingNewType(false);
                    setNewTypeName("");
                  }
                }}
              />
              <button className="cancel-btn" onClick={() => { setAddingNewType(false); setNewTypeName(""); }}>✕</button>
            </div>
          ) : (
            <select
              className="add-math-context-select"
              value={kcType?.content || ""}
              onChange={async (e) => {
                const val = e.target.value;
                if (val === "__new__") {
                  setAddingNewType(true);
                  return;
                }
                try {
                  if (kcType && val) {
                    await api.updateAnnotation(kcType.id, { content: val });
                  } else if (kcType && !val) {
                    await api.deleteAnnotation(kcType.id);
                  } else if (!kcType && val) {
                    await api.createAnnotation({
                      entity_type: "kc",
                      entity_id: kc.id,
                      annotation_type: "kc_type",
                      content: val,
                    });
                  }
                  const updated = await api.getAnnotations("kc", kc.id);
                  setAnnotations(updated);
                } catch {
                  setError("Failed to update KC type");
                }
              }}
            >
              <option value="">— Not set —</option>
              {knownKCTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
              <option value="__new__">+ New type...</option>
            </select>
          )}
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">Language Demands</div>
        <div className="detail-value">
          <div className="demand-checkboxes">
            {ALL_DEMANDS.map((d) => (
              <label key={d} className="demand-checkbox">
                <input
                  type="checkbox"
                  checked={kc.language_demands.includes(d)}
                  onChange={() => toggleDemand(d, kc.language_demands)}
                />
                <span>{d}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">Math Domains</div>
        <div className="detail-value">
          {kc.math_contexts.map((ctx) => (
            <span key={ctx.math_concept_id} className="tag math editable-tag">
              {ctx.math_concept_id} ({ctx.role})
              <button
                className="tag-remove"
                title="Remove math domain"
                onClick={async () => {
                  setError(null);
                  try {
                    await api.removeMathContext(kc.id, ctx.math_concept_id);
                    await onDataChanged();
                  } catch (e) {
                    setError(e instanceof Error ? e.message : String(e));
                  }
                }}
              >×</button>
            </span>
          ))}
          {(() => {
            const currentIds = new Set(kc.math_contexts.map(c => c.math_concept_id));
            const available = mathConcepts.filter(mc => !currentIds.has(mc.id));
            if (available.length === 0) return null;
            return (
              <select
                className="add-math-context-select"
                value=""
                onChange={async (e) => {
                  const mcId = e.target.value;
                  if (!mcId) return;
                  setError(null);
                  try {
                    await api.addMathContext(kc.id, mcId);
                    await onDataChanged();
                  } catch (err) {
                    setError(err instanceof Error ? err.message : String(err));
                  }
                }}
              >
                <option value="">+ Add math domain...</option>
                {available.map(mc => (
                  <option key={mc.id} value={mc.id}>{mc.name} ({mc.id})</option>
                ))}
              </select>
            );
          })()}
        </div>
      </div>

      {schemas.length > 0 && (
        <div className="detail-row">
          <div className="detail-label">Schemas ({schemas.length})</div>
          <div className="detail-value node-list">
            {schemas.map((s) => (
              <div key={s.id} className="editable-list-item">
                <span className="node-link" onClick={() => onSelectNode(`schema-${s.id}`)}>
                  {s.id}: {s.name}
                </span>
              </div>
            ))}
            {/* Move to different schema */}
            {frame && (() => {
              const currentSchemaIds = new Set(schemas.map((s) => s.id));
              const otherSchemas = frame.schemas.filter((s) => !currentSchemaIds.has(s.id));
              if (otherSchemas.length === 0) return null;
              return editingField === "move_schema" ? (
                <div className="add-item-form">
                  <select
                    className="edit-input"
                    autoFocus
                    onChange={async (e) => {
                      const targetSchemaId = e.target.value;
                      if (!targetSchemaId || !selectedNodeId) return;
                      setError(null);
                      try {
                        // Remove from all current schemas
                        for (const s of schemas) {
                          await api.removeKCFromSchema(s.id, selectedNodeId);
                        }
                        // Add to new schema
                        await api.addKCsToSchema(targetSchemaId, [selectedNodeId]);
                        await onDataChanged();
                        api.getKCSchemas(selectedNodeId).then(setSchemas);
                        setEditingField(null);
                      } catch (err) {
                        setError(err instanceof Error ? err.message : String(err));
                      }
                    }}
                  >
                    <option value="">Move to schema...</option>
                    {otherSchemas.map((s) => (
                      <option key={s.id} value={s.id}>{s.id}: {s.name}</option>
                    ))}
                  </select>
                  <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
                </div>
              ) : (
                <button className="add-btn" onClick={() => setEditingField("move_schema")}>Move to different schema...</button>
              );
            })()}
          </div>
        </div>
      )}

      <div className="detail-row">
        <div className="detail-label">
          Direct Prerequisites ({directPredecessors.length})
          <span className="detail-sublabel"> — all ancestors: {ancestors.length}</span>
        </div>
        <div className="detail-value node-list">
          {directPredecessors.length === 0 ? (
            <span style={{ color: "#aaa" }}>None (root node)</span>
          ) : (
            directPredecessors.map((id) => {
              const edgeId = findEdgeId(id, selectedNodeId!);
              const predKC = kcs.find((k) => k.id === id);
              return (
                <div key={id} className="editable-list-item">
                  <span className="node-link" onClick={() => onSelectNode(id)}>
                    {id}
                  </span>
                  {predKC && <span style={{ color: "#666" }}> — {predKC.short_description}</span>}
                  {edgeId !== null && (
                    <button
                      className="remove-btn"
                      onClick={() => handleDeleteEdge(edgeId)}
                      title="Remove this prerequisite edge"
                    >✕</button>
                  )}
                </div>
              );
            })
          )}
          {/* Add prerequisite */}
          {editingField === "add_prerequisite" ? (
            <div className="add-item-form">
              <select
                className="edit-input"
                autoFocus
                onChange={(e) => {
                  if (e.target.value) {
                    handleAddEdge(e.target.value, selectedNodeId!);
                    setEditingField(null);
                  }
                }}
              >
                <option value="">Select source KC...</option>
                {kcs
                  .filter((k) => k.id !== selectedNodeId && !directPredecessors.includes(k.id))
                  .map((k) => (
                    <option key={k.id} value={k.id}>{k.id}: {k.short_description}</option>
                  ))}
              </select>
              <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
            </div>
          ) : (
            <button className="add-btn" onClick={() => setEditingField("add_prerequisite")}>+ Add prerequisite</button>
          )}
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">
          Direct Dependents ({directSuccessors.length})
          <span className="detail-sublabel"> — all descendants: {descendants.length}</span>
        </div>
        <div className="detail-value node-list">
          {directSuccessors.length === 0 ? (
            <span style={{ color: "#aaa" }}>None (leaf node)</span>
          ) : (
            directSuccessors.map((id) => {
              const edgeId = findEdgeId(selectedNodeId!, id);
              const succKC = kcs.find((k) => k.id === id);
              return (
                <div key={id} className="editable-list-item">
                  <span className="node-link" onClick={() => onSelectNode(id)}>
                    {id}
                  </span>
                  {succKC && <span style={{ color: "#666" }}> — {succKC.short_description}</span>}
                  {edgeId !== null && (
                    <button
                      className="remove-btn"
                      onClick={() => handleDeleteEdge(edgeId)}
                      title="Remove this dependent edge"
                    >✕</button>
                  )}
                </div>
              );
            })
          )}
          {/* Add dependent */}
          {editingField === "add_dependent" ? (
            <div className="add-item-form">
              <select
                className="edit-input"
                autoFocus
                onChange={(e) => {
                  if (e.target.value) {
                    handleAddEdge(selectedNodeId!, e.target.value);
                    setEditingField(null);
                  }
                }}
              >
                <option value="">Select target KC...</option>
                {kcs
                  .filter((k) => k.id !== selectedNodeId && !directSuccessors.includes(k.id))
                  .map((k) => (
                    <option key={k.id} value={k.id}>{k.id}: {k.short_description}</option>
                  ))}
              </select>
              <button className="edit-cancel" onClick={() => setEditingField(null)}>Cancel</button>
            </div>
          ) : (
            <button className="add-btn" onClick={() => setEditingField("add_dependent")}>+ Add dependent</button>
          )}
        </div>
      </div>

      <div className="detail-row">
        <div className="detail-label">Status</div>
        <div className="detail-value">{kc.metadata_status}</div>
      </div>

      {/* Delete KC */}
      <div className="detail-row danger-zone">
        {confirmDelete ? (
          <div className="confirm-delete">
            <span>Delete this KC? This cannot be undone.</span>
            <div className="confirm-actions">
              <button className="delete-confirm-btn" onClick={handleDeleteKC}>Yes, delete</button>
              <button className="edit-cancel" onClick={() => setConfirmDelete(false)}>Cancel</button>
            </div>
          </div>
        ) : (
          <button className="delete-btn" onClick={() => setConfirmDelete(true)}>Delete KC</button>
        )}
      </div>
    </div>
  );
}
