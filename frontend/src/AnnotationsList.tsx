import type { Annotation } from "./api";

const TYPE_LABELS: Record<string, string> = {
  rationale: "Rationale",
  provenance: "Provenance",
  editorial_note: "Note",
  open_question: "Open question",
  proposed_revision: "Proposed revision",
};

const TYPE_COLORS: Record<string, { bg: string; fg: string }> = {
  rationale: { bg: "#dbeafe", fg: "#1e40af" },
  provenance: { bg: "#e5e7eb", fg: "#374151" },
  editorial_note: { bg: "#ede9fe", fg: "#5b21b6" },
  open_question: { bg: "#fef3c7", fg: "#92400e" },
  proposed_revision: { bg: "#fce7f3", fg: "#9d174d" },
};

function formatDate(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toISOString().slice(0, 10);
}

/** Renders an entity's annotations (excluding kc_type, which is shown as the KC
 *  Type field). Resolved open questions stay visible as history, marked resolved. */
export function AnnotationsList({ annotations, label }: { annotations: Annotation[]; label?: string }) {
  const visible = annotations.filter((a) => a.annotation_type !== "kc_type");
  if (visible.length === 0) return null;
  return (
    <div className="detail-row">
      <div className="detail-label">{label ?? "Notes & History"} ({visible.length})</div>
      <div className="detail-value annotation-list">
        {visible.map((a) => {
          const resolved = a.annotation_type === "open_question" && !!a.resolved_at;
          const colors = resolved
            ? { bg: "#e5e7eb", fg: "#6b7280" }
            : TYPE_COLORS[a.annotation_type] ?? { bg: "#e5e7eb", fg: "#374151" };
          const meta = [a.author, formatDate(a.created_at)].filter(Boolean).join(" · ");
          return (
            <div key={a.id} className="annotation-item">
              <span className="tag" style={{ background: colors.bg, color: colors.fg }}>
                {TYPE_LABELS[a.annotation_type] ?? a.annotation_type}
                {resolved ? " — resolved" : ""}
              </span>
              {resolved && formatDate(a.resolved_at) && (
                <span className="annotation-meta"> {formatDate(a.resolved_at)}</span>
              )}
              <div className="annotation-content">{a.content}</div>
              {meta && <div className="annotation-meta">{meta}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
