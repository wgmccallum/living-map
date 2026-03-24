"""Pydantic models for API request/response bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Knowledge Components ---

class MathContextLink(BaseModel):
    math_concept_id: str
    role: str = "primary"


class KCCreate(BaseModel):
    id: str
    short_description: str
    long_description: str | None = None
    language_demands: list[str] = Field(default_factory=list)
    math_contexts: list[MathContextLink] = Field(default_factory=list)


class KCUpdate(BaseModel):
    short_description: str | None = None
    long_description: str | None = None
    metadata_status: str | None = None


class KCResponse(BaseModel):
    id: str
    short_description: str
    long_description: str | None = None
    is_quotient_node: bool = False
    source_schema_id: str | None = None
    metadata_status: str = "authored"
    language_demands: list[str] = Field(default_factory=list)
    math_contexts: list[MathContextLink] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


# --- Prerequisite Edges ---

class EdgeCreate(BaseModel):
    source_kc_id: str
    target_kc_id: str


class EdgeResponse(BaseModel):
    id: int
    source_kc_id: str
    target_kc_id: str
    created_at: str | None = None


# --- Math Concepts ---

class MathConceptCreate(BaseModel):
    id: str
    name: str
    description: str | None = None


class MathConceptUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class MathConceptResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class MathConceptEdgeCreate(BaseModel):
    source_id: str
    target_id: str


class MathConceptEdgeResponse(BaseModel):
    id: int
    source_id: str
    target_id: str
    created_at: str | None = None


# --- Annotations ---

class AnnotationCreate(BaseModel):
    entity_type: str
    entity_id: str
    annotation_type: str
    content: str
    author: str | None = None


class AnnotationUpdate(BaseModel):
    content: str | None = None
    resolved_at: str | None = None


class AnnotationResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    annotation_type: str
    content: str
    author: str | None = None
    created_at: str | None = None
    resolved_at: str | None = None


# --- Frames and Schemas ---

class FrameCreate(BaseModel):
    id: str
    name: str
    description: str | None = None
    frame_type: str = "internal"
    is_reference: bool = False


class FrameResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    frame_type: str
    is_reference: bool = False
    created_at: str | None = None
    updated_at: str | None = None


class SchemaCreate(BaseModel):
    id: str
    name: str
    description: str | None = None
    parent_schema_id: str | None = None


class SchemaResponse(BaseModel):
    id: str
    frame_id: str
    name: str
    description: str | None = None
    parent_schema_id: str | None = None
    kc_ids: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


# --- Bulk Import ---

class BulkImportAnnotation(BaseModel):
    entity_type: str
    entity_id: str
    annotation_type: str
    content: str
    author: str | None = None


class BulkImportSchema(BaseModel):
    id: str
    frame_id: str
    name: str
    description: str | None = None
    parent_schema_id: str | None = None
    kc_ids: list[str] = Field(default_factory=list)


class BulkImportData(BaseModel):
    math_concepts: list[MathConceptCreate] = Field(default_factory=list)
    math_concept_edges: list[MathConceptEdgeCreate] = Field(default_factory=list)
    knowledge_components: list[KCCreate] = Field(default_factory=list)
    prerequisite_edges: list[EdgeCreate] = Field(default_factory=list)
    annotations: list[BulkImportAnnotation] = Field(default_factory=list)
    frames: list[FrameCreate] = Field(default_factory=list)
    schemas: list[BulkImportSchema] = Field(default_factory=list)


class FrameUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SchemaUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class SchemaKCsAdd(BaseModel):
    kc_ids: list[str]


class QuotientRequest(BaseModel):
    schema_ids: list[str]


class QuotientSaveRequest(BaseModel):
    schema_ids: list[str]
    new_frame_name: str


class ErrorResponse(BaseModel):
    error: str


# --- Staging Area (Moderated Bulk Add) ---


class ReviewerComment(BaseModel):
    author: str
    timestamp: str
    text: str


class StagedMathContext(BaseModel):
    math_concept_id: str
    role: str = "primary"


# Staging Sessions

class StagingSessionCreate(BaseModel):
    id: str
    topic_name: str
    description: str | None = None
    source_documents: list[str] = Field(default_factory=list)


class StagingSessionUpdate(BaseModel):
    topic_name: str | None = None
    description: str | None = None
    source_documents: list[str] | None = None
    status: str | None = None


class StagingSessionResponse(BaseModel):
    id: str
    topic_name: str
    description: str | None = None
    source_documents: list[str] = Field(default_factory=list)
    status: str = "active"
    statistics: dict | None = None
    created_at: str | None = None
    updated_at: str | None = None


# Staged KCs

class StagedKCCreate(BaseModel):
    id: str
    short_description: str | None = None
    long_description: str | None = None
    source_text: str | None = None
    source_reference: str | None = None
    stage_status: str = "proposed"
    language_demands: list[str] = Field(default_factory=list)
    kc_type: str | None = None
    math_contexts: list[StagedMathContext] = Field(default_factory=list)
    ai_correctness_note: str | None = None


class StagedKCUpdate(BaseModel):
    short_description: str | None = None
    long_description: str | None = None
    source_text: str | None = None
    source_reference: str | None = None
    stage_status: str | None = None
    language_demands: list[str] | None = None
    kc_type: str | None = None
    math_contexts: list[StagedMathContext] | None = None
    ai_correctness_note: str | None = None


class StagedKCResponse(BaseModel):
    id: str
    session_id: str
    short_description: str | None = None
    long_description: str | None = None
    source_text: str | None = None
    source_reference: str | None = None
    stage_status: str = "proposed"
    language_demands: list[str] = Field(default_factory=list)
    kc_type: str | None = None
    math_contexts: list[StagedMathContext] = Field(default_factory=list)
    reviewer_comments: list[ReviewerComment] = Field(default_factory=list)
    ai_correctness_note: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class StagedKCBatchUpdate(BaseModel):
    kc_ids: list[str]
    updates: StagedKCUpdate


class StagedKCComment(BaseModel):
    author: str
    text: str


# Staged Edges

class StagedEdgeCreate(BaseModel):
    source_kc_id: str
    target_kc_id: str
    ai_reasoning: str | None = None
    status: str = "proposed"


class StagedEdgeUpdate(BaseModel):
    status: str | None = None
    ai_reasoning: str | None = None


class StagedEdgeResponse(BaseModel):
    id: int
    session_id: str
    source_kc_id: str
    target_kc_id: str
    ai_reasoning: str | None = None
    status: str = "proposed"
    reviewer_comments: list[ReviewerComment] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


# Staged Schemas

class StagedSchemaCreate(BaseModel):
    id: str
    name: str
    description: str | None = None
    parent_schema_id: str | None = None
    status: str = "proposed"


class StagedSchemaUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    parent_schema_id: str | None = None
    status: str | None = None


class StagedSchemaResponse(BaseModel):
    id: str
    session_id: str
    name: str
    description: str | None = None
    parent_schema_id: str | None = None
    status: str = "proposed"
    kc_ids: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class StagedSchemaKCsAdd(BaseModel):
    kc_ids: list[str]


# AI Proposal Requests

class AIBatchRequest(BaseModel):
    kc_ids: list[str]


# ── KC Conversations (Grain Review Chat) ──


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ConversationSendRequest(BaseModel):
    message: str


class ConversationResponse(BaseModel):
    kc_id: str
    session_id: str
    messages: list[ConversationMessage] = Field(default_factory=list)


class ConversationReply(BaseModel):
    role: str = "assistant"
    content: str
    timestamp: str
    full_history: list[ConversationMessage] = Field(default_factory=list)
