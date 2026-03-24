import { useEffect, useRef, useCallback, useImperativeHandle, forwardRef } from "react";
import cytoscape, { type Core, type ElementDefinition, type Position } from "cytoscape";
import dagre from "cytoscape-dagre";
import type { KC, Edge, Frame, QuotientResult } from "./api";

// Register dagre layout
cytoscape.use(dagre);

// Color palettes
const SCHEMA_COLORS = [
  "#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
  "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac",
  "#86bcb6", "#8cd17d", "#b6992d", "#499894", "#d37295",
  "#a0cbe8", "#ffbe7d", "#8b8b8b", "#d4a6c8", "#fabfd2",
  "#d7b5a6", "#79706e", "#b9ca5d", "#f1ce63", "#a1d99b",
  "#c9b2d6", "#ff9896", "#e7969c", "#7b4173", "#ad494a",
];

const DEMAND_COLORS: Record<string, string> = {
  "Speaking": "#4e79a7",
  "Listening": "#f28e2b",
  "Reading": "#e15759",
  "Writing": "#76b7b2",
  "Interpreting a mathematical representation": "#59a14f",
  "Producing a mathematical representation": "#edc948",
};

const CATEGORY_COLORS: Record<string, string> = {
  "SUB": "#4e79a7",
  "CNM": "#e15759",
  "COP": "#59a14f",
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

interface DAGViewProps {
  kcs: KC[];
  edges: Edge[];
  frame: Frame | null;
  colorMode: string;
  showSchemaOverlay: boolean;
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
  onDeleteEdge?: (edgeId: number) => void;
  addEdgeMode?: boolean;
  edgeSource?: string | null;
  onEdgeNodeClick?: (nodeId: string) => void;
  filteredKCIds: Set<string> | null;
  quotientResult: QuotientResult | null;
  collapsedSchemaIds: Set<string>;
}

export interface DAGViewHandle {
  resetLayout: () => void;
}

export const DAGView = forwardRef<DAGViewHandle, DAGViewProps>(function DAGView({
  kcs,
  edges,
  frame,
  colorMode,
  showSchemaOverlay,
  selectedNodeId,
  onSelectNode,
  filteredKCIds,
  onDeleteEdge,
  addEdgeMode,
  edgeSource,
  onEdgeNodeClick,
  quotientResult,
  collapsedSchemaIds,
}, ref) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const edgeTooltipRef = useRef<HTMLDivElement | null>(null);

  // Refs for interactive props — changes to these should NOT trigger a graph rebuild
  const addEdgeModeRef = useRef(addEdgeMode);
  addEdgeModeRef.current = addEdgeMode;
  const edgeSourceRef = useRef(edgeSource);
  edgeSourceRef.current = edgeSource;
  const onEdgeNodeClickRef = useRef(onEdgeNodeClick);
  onEdgeNodeClickRef.current = onEdgeNodeClick;
  const onDeleteEdgeRef = useRef(onDeleteEdge);
  onDeleteEdgeRef.current = onDeleteEdge;
  const onSelectNodeRef = useRef(onSelectNode);
  onSelectNodeRef.current = onSelectNode;
  const edgesRef = useRef(edges);
  edgesRef.current = edges;

  // Cache node positions so they survive graph rebuilds
  const savedPositions = useRef<Map<string, Position>>(new Map());

  // Expose resetLayout to parent
  useImperativeHandle(ref, () => ({
    resetLayout: () => {
      savedPositions.current.clear();
      const cy = cyRef.current;
      if (cy) {
        (cy.layout({
          name: "dagre",
          rankDir: "TB",
          nodeSep: 20,
          rankSep: 40,
          edgeSep: 8,
          padding: 20,
          fit: true,
        } as unknown as cytoscape.LayoutOptions)).run();
      }
    },
  }), []);

  // Build schema color map
  const schemaColorMap = useRef(new Map<string, string>());
  useEffect(() => {
    if (!frame) return;
    const map = new Map<string, string>();
    frame.schemas.forEach((s, i) => {
      map.set(s.id, SCHEMA_COLORS[i % SCHEMA_COLORS.length]);
    });
    schemaColorMap.current = map;
  }, [frame]);

  const getNodeColor = useCallback(
    (kc: KC): string => {
      if (colorMode === "language_demand") {
        const d = kc.language_demands[0];
        return d ? (DEMAND_COLORS[d] || "#888") : "#888";
      }
      if (colorMode === "math_concept") {
        const mc = kc.math_contexts[0];
        return mc ? (MATH_CONCEPT_COLORS[mc.math_concept_id] || "#888") : "#888";
      }
      if (colorMode === "category") {
        const prefix = kc.id.split("-")[0];
        return CATEGORY_COLORS[prefix] || "#888";
      }
      // schema mode
      if (frame) {
        for (const s of frame.schemas) {
          if (s.kc_ids.includes(kc.id)) {
            return schemaColorMap.current.get(s.id) || "#888";
          }
        }
      }
      return "#888";
    },
    [colorMode, frame]
  );

  // Build and render the graph
  useEffect(() => {
    if (!containerRef.current || kcs.length === 0) return;

    const elements: ElementDefinition[] = [];

    if (quotientResult) {
      // Quotient view
      const kcMap = new Map(kcs.map((kc) => [kc.id, kc]));
      const quotientNodes = new Set(quotientResult.quotient_dag.nodes);

      // Build schema overlay for uncollapsed schemas
      // updated_schemas maps schema_id -> list of node IDs (KCs or collapsed nodes) still in that schema
      const schemaMembers = new Map<string, Set<string>>();
      if (showSchemaOverlay && frame && quotientResult.updated_schemas) {
        for (const schema of frame.schemas) {
          // Skip schemas that were collapsed
          if (collapsedSchemaIds.has(schema.id)) continue;
          const members = quotientResult.updated_schemas[schema.id];
          if (!members || members.length === 0) continue;
          // Only include members that are actually in the quotient DAG
          const validMembers = members.filter((m) => quotientNodes.has(m));
          if (validMembers.length === 0) continue;
          schemaMembers.set(schema.id, new Set(validMembers));
          elements.push({
            data: {
              id: `schema-${schema.id}`,
              label: `${schema.id}: ${schema.name}`,
              isSchema: true,
            },
          });
        }
      }

      for (const nodeId of quotientResult.quotient_dag.nodes) {
        const collapsed = quotientResult.collapsed_nodes.find((c) => c.id === nodeId);

        // Find parent schema for this node
        let parent: string | undefined;
        if (showSchemaOverlay && frame) {
          for (const [schemaId, members] of schemaMembers) {
            if (members.has(nodeId)) {
              parent = `schema-${schemaId}`;
              break;
            }
          }
        }

        if (collapsed) {
          elements.push({
            data: {
              id: nodeId,
              label: collapsed.short_description,
              isCollapsed: true,
              demands: collapsed.language_demands.join(", "),
              parent,
            },
          });
        } else {
          const kc = kcMap.get(nodeId);
          elements.push({
            data: {
              id: nodeId,
              label: kc ? kc.short_description : nodeId,
              color: kc ? getNodeColor(kc) : "#888",
              parent,
            },
          });
        }
      }

      for (const [source, target] of quotientResult.quotient_dag.edges) {
        elements.push({
          data: { source, target, id: `e-${source}-${target}` },
        });
      }
    } else {
      // Normal view — add compound nodes for schemas if overlay is on
      if (showSchemaOverlay && frame) {
        // Build a map of schema_id -> parent_schema_id for nesting
        const schemaMap = new Map(frame.schemas.map((s) => [s.id, s]));

        // Add ALL schemas that have either direct KCs or child schemas as compound nodes
        const schemasWithChildren = new Set<string>();
        for (const s of frame.schemas) {
          if (s.parent_schema_id && schemaMap.has(s.parent_schema_id)) {
            schemasWithChildren.add(s.parent_schema_id);
          }
        }

        for (const schema of frame.schemas) {
          if (schema.kc_ids.length > 0 || schemasWithChildren.has(schema.id)) {
            // If this schema has a parent schema in the frame, nest it
            let schemaParent: string | undefined;
            if (schema.parent_schema_id && schemaMap.has(schema.parent_schema_id)) {
              schemaParent = `schema-${schema.parent_schema_id}`;
            }
            elements.push({
              data: {
                id: `schema-${schema.id}`,
                label: `${schema.id}: ${schema.name}`,
                isSchema: true,
                parent: schemaParent,
              },
            });
          }
        }
      }

      for (const kc of kcs) {
        const dimmed = filteredKCIds && !filteredKCIds.has(kc.id);
        let parent: string | undefined;

        if (showSchemaOverlay && frame) {
          // Find the most specific (leaf) schema containing this KC
          // i.e. the schema that directly lists this KC (not via a child)
          for (const s of frame.schemas) {
            if (s.kc_ids.includes(kc.id)) {
              parent = `schema-${s.id}`;
              break;
            }
          }
        }

        elements.push({
          data: {
            id: kc.id,
            label: kc.short_description,
            color: getNodeColor(kc),
            dimmed: dimmed ? "yes" : "no",
            parent,
          },
        });
      }

      for (const edge of edges) {
        elements.push({
          data: {
            source: edge.source_kc_id,
            target: edge.target_kc_id,
            id: `e-${edge.id}`,
          },
        });
      }
    }

    // Save positions from previous instance before destroying
    if (cyRef.current) {
      cyRef.current.nodes().forEach((node) => {
        if (!node.isParent()) {
          savedPositions.current.set(node.id(), { ...node.position() });
        }
      });
      cyRef.current.destroy();
    }

    // Decide layout: use saved positions if we have them for most nodes, otherwise dagre
    const nodeIds = elements.filter((el) => el.data.id && !el.data.source && !el.data.isSchema).map((el) => el.data.id!);
    const hasPositions = nodeIds.length > 0 && nodeIds.filter((id) => savedPositions.current.has(id)).length >= nodeIds.length * 0.5;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "",
            width: 20,
            height: 20,
            "background-color": "data(color)",
            "border-width": 1,
            "border-color": "#999",
          } as cytoscape.Css.Node,
        },
        {
          selector: "node[dimmed = 'yes']",
          style: { opacity: 0.2 },
        },
        {
          selector: "node[?isCollapsed]",
          style: {
            label: "",
            shape: "round-rectangle" as cytoscape.Css.NodeShape,
            width: 30,
            height: 30,
            "background-color": "#4a90d9",
            "border-width": 2,
            "border-color": "#2a5f9e",
          } as cytoscape.Css.Node,
        },
        {
          selector: ":parent",
          style: {
            "background-opacity": 0.08,
            "background-color": "#4a90d9",
            "border-width": 1.5,
            "border-color": "#4a90d9",
            "border-opacity": 0.4,
            label: "data(label)",
            "font-size": "9px",
            color: "#4a90d9",
            "text-valign": "top",
            "text-halign": "center",
            "text-margin-y": -6,
            "padding": "12px",
          } as cytoscape.Css.Node,
        },
        {
          selector: "node:selected",
          style: {
            "border-width": 3,
            "border-color": "#ff6600",
            "background-color": "#ff6600",
            color: "#fff",
          } as cytoscape.Css.Node,
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#bbb",
            "target-arrow-color": "#bbb",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 0.8,
          } as cytoscape.Css.Edge,
        },
        {
          selector: "edge:selected",
          style: {
            "line-color": "#ff6600",
            "target-arrow-color": "#ff6600",
            width: 2.5,
          } as cytoscape.Css.Edge,
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
          selector: ".highlighted",
          style: {
            "border-width": 2.5,
            "border-color": "#ff6600",
          } as cytoscape.Css.Node,
        },
        {
          selector: ".ancestor",
          style: {
            "border-width": 2,
            "border-color": "#e15759",
            "background-color": "#fdd",
          } as cytoscape.Css.Node,
        },
        {
          selector: ".descendant",
          style: {
            "border-width": 2,
            "border-color": "#59a14f",
            "background-color": "#dfd",
          } as cytoscape.Css.Node,
        },
      ],
      layout: hasPositions
        ? {
            name: "preset",
            positions: (node: cytoscape.NodeSingular) => {
              const pos = savedPositions.current.get(node.id());
              return pos || { x: 0, y: 0 };
            },
            fit: true,
            padding: 20,
          } as unknown as cytoscape.LayoutOptions
        : {
            name: "dagre",
            rankDir: "TB",
            nodeSep: 20,
            rankSep: 40,
            edgeSep: 8,
            padding: 20,
            fit: true,
          } as unknown as cytoscape.LayoutOptions,
      minZoom: 0.05,
      maxZoom: 5,
      wheelSensitivity: 0.3,
    });

    cy.on("tap", "node", (evt) => {
      const id = evt.target.id();
      if (addEdgeModeRef.current && onEdgeNodeClickRef.current) {
        onEdgeNodeClickRef.current(id);
      } else {
        onSelectNodeRef.current(id);
      }
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy) {
        onSelectNodeRef.current(null);
        if (edgeTooltipRef.current) edgeTooltipRef.current.style.display = "none";
      }
    });

    // Edge click — show delete tooltip
    cy.on("tap", "edge", (evt) => {
      const edge = evt.target;
      const sourceId = edge.data("source");
      const targetId = edge.data("target");
      const midpoint = edge.renderedMidpoint();

      const et = edgeTooltipRef.current || document.createElement("div");
      if (!edgeTooltipRef.current) {
        et.className = "cy-edge-tooltip";
        containerRef.current!.appendChild(et);
        edgeTooltipRef.current = et;
      }

      // Find the edge ID from the edges prop via ref
      const matchingEdge = edgesRef.current.find(
        (e) => e.source_kc_id === sourceId && e.target_kc_id === targetId
      );

      et.innerHTML = `<span class="edge-tooltip-label">${sourceId} → ${targetId}</span>`;
      if (matchingEdge && onDeleteEdgeRef.current) {
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "edge-tooltip-delete";
        deleteBtn.textContent = "Delete";
        deleteBtn.onclick = (e) => {
          e.stopPropagation();
          onDeleteEdgeRef.current!(matchingEdge.id);
          et.style.display = "none";
        };
        et.appendChild(deleteBtn);
      }

      et.style.left = `${midpoint.x}px`;
      et.style.top = `${midpoint.y - 30}px`;
      et.style.display = "flex";
    });

    // Hover tooltip
    const tooltip = document.createElement("div");
    tooltip.className = "cy-tooltip";
    containerRef.current!.appendChild(tooltip);
    tooltipRef.current = tooltip;

    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      if (node.id().startsWith("schema-")) return;
      const label = node.data("label") || node.id();
      const pos = node.renderedPosition();
      tooltip.textContent = `${node.id()}: ${label}`;
      tooltip.style.left = `${pos.x}px`;
      tooltip.style.top = `${pos.y - 20}px`;
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
  }, [kcs, edges, frame, colorMode, showSchemaOverlay, getNodeColor, filteredKCIds, quotientResult, collapsedSchemaIds]);

  // Highlight selected node's ancestors and descendants
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("highlighted ancestor descendant edge-source");

    if (edgeSource) {
      cy.getElementById(edgeSource).addClass("edge-source");
    }

    if (!selectedNodeId) return;
    const node = cy.getElementById(selectedNodeId);
    if (!node || node.empty()) return;

    node.select();

    // Highlight predecessors (ancestors in DAG)
    const predecessors = node.predecessors("node");
    predecessors.addClass("ancestor");

    // Highlight successors (descendants in DAG)
    const successors = node.successors("node");
    successors.addClass("descendant");
  }, [selectedNodeId, edgeSource]);

  return <div ref={containerRef} className="cy-container" />;
});
