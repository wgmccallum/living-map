"""AI service for the Moderated Bulk Add pipeline.

Provides prompt-driven AI capabilities for each workflow stage:
grain-size review, KC formulation, prerequisite proposals,
schema proposals, and mathematical correctness checks.

Requires ANTHROPIC_API_KEY environment variable to be set.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

# Lazy-import anthropic to avoid hard failure at import time
_client = None
_MODEL = "claude-sonnet-4-20250514"


def _get_client():
    global _client
    if _client is None:
        try:
            import anthropic
        except ImportError:
            raise RuntimeError(
                "The 'anthropic' package is required for AI features. "
                "Install it with: pip install anthropic"
            )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Get an API key from https://console.anthropic.com and set it: "
                "export ANTHROPIC_API_KEY=sk-ant-..."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _call_claude(system: str, user: str, max_tokens: int = 4096) -> str:
    """Call Claude and return the text response."""
    client = _get_client()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def _extract_json(text: str) -> dict | list:
    """Extract JSON from a Claude response that may contain markdown fences."""
    # Try to find JSON in code blocks first
    match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text)
    if match:
        return json.loads(match.group(1))
    # Try parsing the whole response
    # Find first [ or { and last ] or }
    start = min(
        (text.find(c) for c in "[{" if text.find(c) >= 0),
        default=-1,
    )
    if start >= 0:
        end = max(
            (text.rfind(c) for c in "]}" if text.rfind(c) >= 0),
            default=-1,
        )
        if end > start:
            return json.loads(text[start : end + 1])
    raise ValueError(f"Could not extract JSON from response: {text[:200]}...")


# ═══════════════════════════════════════════════════════
# System prompts
# ═══════════════════════════════════════════════════════

_SYSTEM_BASE = """You are an expert in K-12 mathematics education and curriculum design, \
working as part of the Living Map project — a system for building a fine-grained \
directed acyclic graph (DAG) of mathematical knowledge components (KCs).

A KC is a single, testable unit of mathematical knowledge. It has:
- A behavioral definition: what a student can do (prompt/context + expected response)
- Language demands: which modalities are required (Speaking, Listening, Reading, Writing, \
Interpreting a mathematical representation, Producing a mathematical representation)
- A KC type annotation: Fact, Skill, Definition, Principle, or Skill Subtype

Your job is to help decompose standards and curriculum content into well-formed KCs."""


# ═══════════════════════════════════════════════════════
# Grain-Size Review (Stage 2)
# ═══════════════════════════════════════════════════════

def grain_review(kcs: list[dict], existing_kcs: list[dict] | None = None) -> list[dict]:
    """Generate grain-size review questions for a batch of proposed KCs.

    Args:
        kcs: List of staged KC dicts (id, source_text, source_reference, etc.)
        existing_kcs: Optional list of existing KCs for calibration

    Returns:
        List of dicts, one per KC, with:
        - kc_id: the staged KC ID
        - analysis: grain-size assessment
        - recommendation: 'keep', 'split', or 'merge'
        - split_suggestions: list of suggested sub-KCs if splitting
        - merge_target: ID to merge with if merging
        - questions: list of specific questions for the reviewer
    """
    kc_descriptions = "\n\n".join(
        f"[{kc['id']}] Source: {kc.get('source_reference', 'unknown')}\n"
        f"Text: {kc.get('source_text', kc.get('short_description', ''))}"
        for kc in kcs
    )

    calibration = ""
    if existing_kcs:
        samples = existing_kcs[:10]
        calibration = "\n\nHere are some existing KCs for grain-size calibration:\n" + "\n".join(
            f"- {kc.get('id', '')}: {kc.get('short_description', '')}"
            for kc in samples
        )

    user_msg = f"""Analyze the grain size of these proposed knowledge components. \
For each one, determine whether it represents a single testable idea or whether \
it should be split into multiple KCs (or merged with a related one).

A well-sized KC:
- Describes ONE testable mathematical behavior
- Can be assessed with a single task or prompt
- Is neither too broad (covering multiple distinct ideas) nor too narrow (a trivial sub-step)

Proposed KCs:

{kc_descriptions}{calibration}

Respond with a JSON array. For each KC:
{{
  "kc_id": "the staged KC ID",
  "analysis": "Brief explanation of your grain-size assessment",
  "recommendation": "keep" | "split" | "merge",
  "split_suggestions": ["description of sub-KC 1", "description of sub-KC 2"],
  "merge_target": "ID of KC to merge with, if applicable",
  "questions": ["Specific question for the reviewer about this KC's grain size"]
}}"""

    response = _call_claude(_SYSTEM_BASE, user_msg)
    return _extract_json(response)


# ═══════════════════════════════════════════════════════
# Grain-Size Conversation (interactive follow-up)
# ═══════════════════════════════════════════════════════


def grain_review_chat(
    kc: dict,
    all_session_kcs: list[dict],
    conversation_history: list[dict],
    existing_kcs: list[dict] | None = None,
) -> str:
    """Continue a conversation about a KC's grain size.

    Args:
        kc: The specific KC under discussion
        all_session_kcs: All staged KCs in the session (for batch context)
        conversation_history: List of {role, content} message dicts
        existing_kcs: Optional committed KCs for calibration

    Returns:
        The AI's text response (free-form, not JSON)
    """
    other_kcs = [k for k in all_session_kcs if k.get("id") != kc.get("id")]
    other_kc_lines = "\n".join(
        f"  [{k['id']}] ({k.get('source_reference', '')}): "
        f"{k.get('source_text', k.get('short_description', ''))[:120]}"
        for k in other_kcs
    )

    calibration = ""
    if existing_kcs:
        samples = existing_kcs[:10]
        calibration = "\n\nExisting committed KCs for grain-size calibration:\n" + "\n".join(
            f"  - {kc_ex.get('id', '')}: {kc_ex.get('short_description', '')}"
            for kc_ex in samples
        )

    system = _SYSTEM_BASE + f"""

You are in an interactive discussion with an expert reviewer about the grain size \
of a specific KC. The reviewer may ask you to clarify your reasoning, reconsider \
your assessment, or explore alternatives (splitting, merging, keeping as-is). \
Be conversational but precise. Reference specific mathematical content when \
explaining your reasoning. Keep responses focused and concise.

When you and the reviewer reach agreement on a concrete action (split, merge, or approve), \
include an ACTION block at the end of your response in exactly this format:

For a split:
[ACTION:split]
- First child KC description
- Second child KC description
[/ACTION]

For approving the grain size as-is:
[ACTION:approve]
[/ACTION]

Only include the ACTION block when you are confident the reviewer has agreed. \
Do not include it when you are still discussing or asking questions.

KC under discussion:
  [{kc['id']}] Source: {kc.get('source_reference', 'unknown')}
  Text: {kc.get('source_text', kc.get('short_description', ''))}
  Status: {kc.get('stage_status', 'unknown')}
  {f"Short description: {kc['short_description']}" if kc.get('short_description') else ""}

Other KCs in this batch (for context):
{other_kc_lines if other_kc_lines else '  (none)'}
{calibration}"""

    client = _get_client()

    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_history
    ]

    response = client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        system=system,
        messages=messages,
    )
    text = response.content[0].text
    action = _parse_conversation_action(text)
    return text, action


def _parse_conversation_action(text: str) -> dict | None:
    """Extract an [ACTION:type]...[/ACTION] block from AI response text."""
    import re
    m = re.search(r'\[ACTION:(\w+)\](.*?)\[/ACTION\]', text, re.DOTALL)
    if not m:
        return None
    action_type = m.group(1).strip().lower()
    body = m.group(2).strip()

    if action_type == "split":
        children = [
            line.lstrip("- ").strip()
            for line in body.splitlines()
            if line.strip() and line.strip() != "-"
        ]
        if children:
            return {"type": "split", "children": children}
    elif action_type == "approve":
        return {"type": "approve"}
    return None


# ═══════════════════════════════════════════════════════
# KC Formulation (Stage 3)
# ═══════════════════════════════════════════════════════

def formulate_kcs(kcs: list[dict], existing_kcs: list[dict] | None = None) -> list[dict]:
    """Generate full KC descriptions for grain-approved KCs.

    Args:
        kcs: List of staged KC dicts that have passed grain review
        existing_kcs: Optional list of existing KCs for voice calibration

    Returns:
        List of dicts with proposed formulations:
        - kc_id: the staged KC ID
        - short_description: concise behavioral definition
        - long_description: detailed prompt/context + expected response
        - language_demands: list of applicable modalities
        - kc_type: Fact, Skill, Definition, Principle, or Skill Subtype
        - math_concepts: list of {name, role} for mathematical context
        - correctness_note: any mathematical concerns
    """
    kc_descriptions = "\n\n".join(
        f"[{kc['id']}] Source ref: {kc.get('source_reference', 'unknown')}\n"
        f"Source text: {kc.get('source_text', '')}"
        for kc in kcs
    )

    calibration = ""
    if existing_kcs:
        samples = existing_kcs[:8]
        calibration = "\n\nExisting KCs for voice and style calibration:\n" + "\n".join(
            f"- {kc.get('id', '')}: {kc.get('short_description', '')} "
            f"[{', '.join(kc.get('language_demands', []))}]"
            for kc in samples
        )

    user_msg = f"""Write proper KC formulations for each of these approved content items. \
Each KC needs a behavioral definition: what can the student do?

The short_description should be a concise statement (1 sentence).
The long_description should specify the prompt/context and expected response — \
what you would ask a student and what a correct response looks like.

Language demands (choose all that apply):
- Speaking, Listening, Reading, Writing
- Interpreting a mathematical representation
- Producing a mathematical representation

KC types: Fact, Skill, Definition, Principle, Skill Subtype

Items to formulate:

{kc_descriptions}{calibration}

Respond with a JSON array. For each KC:
{{
  "kc_id": "the staged KC ID",
  "short_description": "Concise behavioral definition",
  "long_description": "Detailed: prompt/context + expected response",
  "language_demands": ["Speaking", "Reading"],
  "kc_type": "Skill",
  "math_concepts": [{{"name": "concept name", "role": "primary"}}],
  "correctness_note": "Any mathematical concerns, or null if none"
}}"""

    response = _call_claude(_SYSTEM_BASE, user_msg, max_tokens=8192)
    return _extract_json(response)


# ═══════════════════════════════════════════════════════
# Prerequisite Proposals (Stage 4)
# ═══════════════════════════════════════════════════════

def propose_prerequisites(kcs: list[dict], existing_edges: list[dict] | None = None) -> list[dict]:
    """Propose prerequisite edges for formulated KCs.

    Args:
        kcs: List of formulated staged KC dicts
        existing_edges: Already-confirmed edges in this session

    Returns:
        List of proposed edge dicts:
        - source_kc_id: prerequisite KC
        - target_kc_id: KC that depends on the prerequisite
        - reasoning: explanation of why this edge exists
        - confidence: 'high', 'medium', or 'low'
    """
    kc_descriptions = "\n".join(
        f"[{kc['id']}]: {kc.get('short_description', kc.get('source_text', ''))}"
        for kc in kcs
    )

    existing_edge_str = ""
    if existing_edges:
        existing_edge_str = "\n\nAlready-confirmed edges:\n" + "\n".join(
            f"  {e['source_kc_id']} → {e['target_kc_id']}"
            for e in existing_edges
        )

    user_msg = f"""Analyze these KCs and propose prerequisite relationships between them.

An edge A → B means "A is a prerequisite for B" — a student must have KC A \
before they can acquire KC B. Only propose edges where there is a genuine \
logical or mathematical dependency, not just a typical instructional sequence.

KCs:

{kc_descriptions}{existing_edge_str}

For each proposed edge, explain your reasoning. Rate your confidence:
- high: clear mathematical dependency
- medium: strong pedagogical argument
- low: plausible but debatable

Also identify any gaps — KCs that seem to need a prerequisite that doesn't \
exist in this set. Flag these separately.

Respond with a JSON object:
{{
  "edges": [
    {{
      "source_kc_id": "prerequisite KC ID",
      "target_kc_id": "dependent KC ID",
      "reasoning": "Why A is prerequisite for B",
      "confidence": "high"
    }}
  ],
  "gaps": [
    {{
      "needed_for": "KC ID that needs a missing prerequisite",
      "description": "What the missing prerequisite KC would cover",
      "reasoning": "Why this gap exists"
    }}
  ]
}}"""

    response = _call_claude(_SYSTEM_BASE, user_msg, max_tokens=8192)
    return _extract_json(response)


# ═══════════════════════════════════════════════════════
# Schema Proposals (Stage 5)
# ═══════════════════════════════════════════════════════

def propose_schemas(kcs: list[dict], edges: list[dict]) -> list[dict]:
    """Propose schema groupings for edge-confirmed KCs.

    Args:
        kcs: List of edge-confirmed staged KC dicts
        edges: Confirmed edges between these KCs

    Returns:
        List of proposed schema dicts:
        - name: schema name
        - description: what this schema covers
        - kc_ids: list of KC IDs in this schema
        - parent_schema: name of parent schema if nested, null otherwise
    """
    kc_descriptions = "\n".join(
        f"[{kc['id']}]: {kc.get('short_description', kc.get('source_text', ''))}"
        for kc in kcs
    )
    edge_str = "\n".join(
        f"  {e['source_kc_id']} → {e['target_kc_id']}"
        for e in edges
    )

    user_msg = f"""Organize these KCs into a HIERARCHICAL schema structure. A schema is a \
coherent bundle of KCs that form a meaningful unit.

CRITICAL RULES:
1. HIERARCHY IS REQUIRED. Create parent schemas that group related child schemas together. \
For example, if you have child schemas "Counting On" (3 KCs) and "Making Ten" (4 KCs), \
they should both be children of a parent schema "Addition Strategies."
2. Parent schemas have kc_ids: [] (empty). KCs are listed ONLY on leaf (child) schemas. \
A parent's membership is the union of its children — never list KCs on a parent.
3. Every leaf schema must have at least 3 KCs. If a KC doesn't fit into a group of 3+, \
put it in the "unassigned" list instead.
4. Schemas must be CONVEX: if KC A and KC C are in the schema, and A → B → C in the \
prerequisite graph, then B must be in the schema too.
5. Aim for 2-4 parent schemas, each with 2-4 child schemas of 3-8 KCs.

Example structure for a fractions topic:
  Parent: "Understanding Fractions" (kc_ids: [], parent_schema: null)
    Child: "Unit Fractions" (kc_ids: [F1, F2, F3], parent_schema: "Understanding Fractions")
    Child: "Comparing Fractions" (kc_ids: [F4, F5, F6], parent_schema: "Understanding Fractions")
  Parent: "Fraction Operations" (kc_ids: [], parent_schema: null)
    Child: "Adding Fractions" (kc_ids: [F7, F8, F9, F10], parent_schema: "Fraction Operations")

KCs:
{kc_descriptions}

Prerequisite edges:
{edge_str}

Respond with a JSON object:
{{
  "schemas": [
    {{
      "name": "Schema name",
      "description": "What this schema covers",
      "kc_ids": [],
      "parent_schema": null
    }},
    {{
      "name": "Child schema name",
      "description": "...",
      "kc_ids": ["KC-1", "KC-2", "KC-3"],
      "parent_schema": "Schema name"
    }}
  ],
  "unassigned": ["KC-X"]
}}"""

    response = _call_claude(_SYSTEM_BASE, user_msg)
    return _extract_json(response)


# ═══════════════════════════════════════════════════════
# Correctness Check
# ═══════════════════════════════════════════════════════

def correctness_check(kcs: list[dict]) -> list[dict]:
    """Run mathematical correctness assessment on KCs.

    Args:
        kcs: List of staged KC dicts to check

    Returns:
        List of dicts:
        - kc_id: the staged KC ID
        - is_correct: boolean
        - issues: list of concerns (empty if correct)
        - suggestions: suggested fixes if issues found
    """
    kc_descriptions = "\n\n".join(
        f"[{kc['id']}]\n"
        f"Short: {kc.get('short_description', '(not yet formulated)')}\n"
        f"Long: {kc.get('long_description', '(not yet formulated)')}\n"
        f"Source: {kc.get('source_text', '')}"
        for kc in kcs
    )

    user_msg = f"""Review these knowledge components for mathematical correctness.

For each KC, check:
1. Is the mathematical content accurate?
2. Does it describe a single coherent idea (not conflating distinct concepts)?
3. Is the behavioral definition testable — could you write an assessment item for it?
4. Are there any ambiguities or imprecisions in the mathematical language?

KCs to review:

{kc_descriptions}

Respond with a JSON array:
[
  {{
    "kc_id": "the staged KC ID",
    "is_correct": true,
    "issues": [],
    "suggestions": []
  }}
]"""

    response = _call_claude(_SYSTEM_BASE, user_msg)
    return _extract_json(response)


# ═══════════════════════════════════════════════════════
# Availability check
# ═══════════════════════════════════════════════════════

def is_available() -> tuple[bool, str]:
    """Check if AI service is available (API key configured, package installed)."""
    try:
        import anthropic
    except ImportError:
        return False, "The 'anthropic' package is not installed"
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return False, "ANTHROPIC_API_KEY environment variable is not set"
    return True, "AI service is available"
