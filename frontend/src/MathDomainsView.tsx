import { useEffect, useRef, useCallback, useState } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import dagre from "cytoscape-dagre";
import type { MathDomain, MathDomainEdge } from "./api";
import { api } from "./api";

// Register dagre layout (idempotent if already registered)
try { cytoscape.use(dagre); } catch { /* already registered */ }

const DOMAIN_COLORS: Record<string, string> = {
  "whole-numbers": "#4e79a7",
  "coordinate-plane": "#e15759",
  "integers": "#59a14f",
  "rationals": "#f28e2b",
  "irrationals": "#76b7b2",
  "reals": "#edc948",
  "number-line": "#af7aa1",
};

const DEFAULT_COLOR = "#888";

interface MathDomainsViewProps {
  domains: MathDomain[];
  domainEdges: MathDomainEdge[];
  selectedDomainId: string | null;
  onSelectDomain: (id: string | null) => void;
  onRefresh: () => Promise<void>;
}

export function MathDomainsView({
  domains,
  domainEdges,
  selectedDomainId,
  onSelectDomain,
  onRefresh,
}: MathDomainsViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const edgeTooltipRef = useRef<HTMLDivElement | null>(null);

  // Add-edge mode state
  const [addEdgeMode, setAddEdgeMode] = useState(false);
  const [edgeSource, setEdgeSource] = useState<string | null>(null);
  const [edgeError, setEdgeError] = useState<string | null>(null);

  // Add-domain form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newDomainId, setNewDomainId] = useState("");
  const [newDomainName, setNewDomainName] = useState("");
  const [newDomainDesc, setNewDomainDesc] = useState("");
  const [addError, setAddError] = useState<string | null>(null);

  const handleAddDomain = useCallback(async () => {
    if (!newDomainId.trim() || !newDomainName.trim()) return;
    setAddError(null);
    try {
      await api.createMathDomain({
        id: newDomainId.trim(),
        name: newDomainName.trim(),
        description: newDomainDesc.trim() || undefined,
      });
      setShowAddForm(false);
      setNewDomainId("");
      setNewDomainName("");
      setNewDomainDesc("");
      await onRefresh();
    } catch (e) {
      setAddError(e instanceof Error ? e.message : String(e));
    }
  }, [newDomainId, newDomainName, newDomainDesc, onRefresh]);

  const handleEdgeClick = useCallback(async (nodeId: string) => {
    if (!addEdgeMode) return;
    if (!edgeSource) {
      setEdgeSource(nodeId);
      setEdgeError(null);
    } else {
      if (nodeId === edgeSource) {
        setEdgeSource(null);
        return;
      }
      try {
        await api.createMathDomainEdge(edgeSource, nodeId);
        setAddEdgeMode(false);
        setEdgeSource(null);
        setEdgeError(null);
        await onRefresh();
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setEdgeError(msg.replace(/^\d+:\s*/, ""));
        setEdgeSource(null);
      }
    }
  }, [addEdgeMode, edgeSource, onRefresh]);

  // Build and render the graph
  useEffect(() => {
    if (!containerRef.current) return;

    const elements: ElementDefinition[] = [];

    for (const domain of domains) {
      elements.push({
        data: {
          id: domain.id,
          label: domain.name,
          color: DOMAIN_COLORS[domain.id] || DEFAULT_COLOR,
        },
      });
    }

    for (const edge of domainEdges) {
      elements.push({
        data: {
          source: edge.source_id,
          target: edge.target_id,
          id: `de-${edge.id}`,
          edgeDbId: edge.id,
        },
      });
    }

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            width: 40,
            height: 40,
            "background-color": "data(color)",
            "border-width": 2,
            "border-color": "#999",
            "font-size": "11px",
            "text-valign": "bottom",
            "text-margin-y": 6,
            color: "#333",
            "text-wrap": "wrap",
            "text-max-width": "100px",
          } as cytoscape.Css.Node,
        },
        {
          selector: "node:selected",
          style: {
            "border-width": 4,
            "border-color": "#ff6600",
          } as cytoscape.Css.Node,
        },
        {
          selector: ".edge-source",
          style: {
            "border-width": 4,
            "border-color": "#ff6600",
            "border-style": "dashed",
          } as cytoscape.Css.Node,
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#999",
            "target-arrow-color": "#999",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 1,
          } as cytoscape.Css.Edge,
        },
        {
          selector: "edge:selected",
          style: {
            "line-color": "#ff6600",
            "target-arrow-color": "#ff6600",
            width: 3,
          } as cytoscape.Css.Edge,
        },
      ],
      layout: {
        name: "dagre",
        rankDir: "TB",
        nodeSep: 60,
        rankSep: 80,
        padding: 40,
        fit: true,
      } as unknown as cytoscape.LayoutOptions,
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.3,
    });

    cy.on("tap", "node", (evt) => {
      const id = evt.target.id();
      if (addEdgeMode) {
        handleEdgeClick(id);
      } else {
        onSelectDomain(`domain-${id}`);
      }
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy) {
        if (addEdgeMode) {
          setAddEdgeMode(false);
          setEdgeSource(null);
        } else {
          onSelectDomain(null);
        }
        if (edgeTooltipRef.current) edgeTooltipRef.current.style.display = "none";
      }
    });

    // Edge click — show delete tooltip
    cy.on("tap", "edge", (evt) => {
      const edge = evt.target;
      const sourceId = edge.data("source");
      const targetId = edge.data("target");
      const dbId = edge.data("edgeDbId") as number;
      const midpoint = edge.renderedMidpoint();

      const et = edgeTooltipRef.current || document.createElement("div");
      if (!edgeTooltipRef.current) {
        et.className = "cy-edge-tooltip";
        containerRef.current!.appendChild(et);
        edgeTooltipRef.current = et;
      }

      et.innerHTML = `<span class="edge-tooltip-label">${sourceId} → ${targetId}</span>`;
      if (dbId) {
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "edge-tooltip-delete";
        deleteBtn.textContent = "Delete";
        deleteBtn.onclick = async (e) => {
          e.stopPropagation();
          try {
            await api.deleteMathDomainEdge(dbId);
            et.style.display = "none";
            await onRefresh();
          } catch (err) {
            setEdgeError(err instanceof Error ? err.message : String(err));
          }
        };
        et.appendChild(deleteBtn);
      }

      et.style.left = `${midpoint.x}px`;
      et.style.top = `${midpoint.y - 30}px`;
      et.style.display = "flex";
    });

    // Tooltip
    const tooltip = document.createElement("div");
    tooltip.className = "cy-tooltip";
    containerRef.current!.appendChild(tooltip);
    tooltipRef.current = tooltip;

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const domain = domains.find((d) => d.id === node.id());
      const desc = domain?.description || "No description";
      const pos = node.renderedPosition();
      tooltip.innerHTML = `<strong>${node.id()}</strong><br/>${desc}`;
      tooltip.style.left = `${pos.x}px`;
      tooltip.style.top = `${pos.y - 30}px`;
      tooltip.style.display = "block";
    });

    cy.on("mouseout", "node", () => {
      tooltip.style.display = "none";
    });

    cy.on("pan zoom", () => {
      tooltip.style.display = "none";
    });

    cyRef.current = cy;

    return () => {
      tooltip.remove();
      if (edgeTooltipRef.current) {
        edgeTooltipRef.current.remove();
        edgeTooltipRef.current = null;
      }
      cy.destroy();
      cyRef.current = null;
    };
  }, [domains, domainEdges, addEdgeMode, handleEdgeClick, onSelectDomain, onRefresh]);

  // Highlight selected domain and edge source
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("edge-source");

    if (edgeSource) {
      cy.getElementById(edgeSource).addClass("edge-source");
    }

    if (selectedDomainId?.startsWith("domain-")) {
      const id = selectedDomainId.replace("domain-", "");
      const node = cy.getElementById(id);
      if (node && !node.empty()) {
        node.select();
      }
    }
  }, [selectedDomainId, edgeSource]);

  return (
    <div className="math-domains-view">
      {/* Toolbar */}
      <div className="domains-toolbar">
        <button
          className={`toolbar-btn ${showAddForm ? "active" : ""}`}
          onClick={() => { setShowAddForm(!showAddForm); setAddError(null); }}
        >
          + Add Domain
        </button>
        <button
          className={`toolbar-btn ${addEdgeMode ? "active" : ""}`}
          onClick={() => {
            setAddEdgeMode(!addEdgeMode);
            setEdgeSource(null);
            setEdgeError(null);
          }}
        >
          {addEdgeMode
            ? edgeSource
              ? "Click target domain..."
              : "Click source domain..."
            : "Add Edge"}
        </button>
        {addEdgeMode && (
          <button className="toolbar-btn cancel" onClick={() => { setAddEdgeMode(false); setEdgeSource(null); setEdgeError(null); }}>
            Cancel
          </button>
        )}
      </div>

      {/* Add domain form */}
      {showAddForm && (
        <div className="add-domain-form">
          <input
            type="text"
            placeholder="Domain ID (e.g., number-line)"
            value={newDomainId}
            onChange={(e) => setNewDomainId(e.target.value)}
            className="domain-input"
          />
          <input
            type="text"
            placeholder="Display name"
            value={newDomainName}
            onChange={(e) => setNewDomainName(e.target.value)}
            className="domain-input"
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newDomainDesc}
            onChange={(e) => setNewDomainDesc(e.target.value)}
            className="domain-input"
          />
          <div className="form-actions">
            <button
              className="toolbar-btn create"
              disabled={!newDomainId.trim() || !newDomainName.trim()}
              onClick={handleAddDomain}
            >
              Create
            </button>
            <button className="toolbar-btn cancel" onClick={() => setShowAddForm(false)}>Cancel</button>
          </div>
          {addError && (
            <div className="domain-error">{addError.replace(/^\d+:\s*/, "")}</div>
          )}
        </div>
      )}

      {/* Edge error */}
      {edgeError && (
        <div className="domain-error-banner">
          {edgeError}
          <button onClick={() => setEdgeError(null)}>Dismiss</button>
        </div>
      )}

      {/* Graph */}
      <div ref={containerRef} className="cy-container" />
    </div>
  );
}
