# System Architecture

## 1. Purpose

AI Skill Framework is designed to build reusable, modular, testable, and maintainable AI skills.

The framework avoids one giant prompt. Instead, it separates responsibilities into independent layers.

---

## 2. High-Level Architecture

User
  ->
Master Skill
  ->
Workflow Engine
  ->
Skill Library
  ->
Knowledge Base
  ->
Evaluation Engine
  ->
Reflection Engine
  ->
Final Output

---

## 3. Core Components

### 3.1 Master Skill

The Master Skill is the orchestrator.

It does not directly perform specialized work.

Responsibilities:

- Understand the user request
- Detect the goal
- Select the correct workflow
- Select required skills
- Coordinate execution
- Merge outputs
- Send the result through evaluation and reflection

---

### 3.2 Workflow Engine

The Workflow Engine defines the order of work.

Example:

Research -> Plan -> Write -> Review -> Improve -> Deliver

A workflow should not contain deep domain knowledge.

Workflow manifests, step ordering, mappings, and failure behavior follow the
[Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md).
Lifecycle and execution semantics follow the
[Workflow Architecture](WORKFLOW_ARCHITECTURE.md).

---

### 3.3 Skill Library

A Skill is a reusable module that performs one specific task.

Examples:

- Research Skill
- Planning Skill
- Writing Skill
- Coding Skill
- Review Skill
- Fact Check Skill
- SEO Skill

Rule:

One Skill = One Responsibility.

Every Skill package follows the
[AI Skill Specification](../specifications/AI_SKILL_SPECIFICATION.md).
Its lifecycle, folder structure, template, and validation process follow the
[Skill Architecture](SKILL_ARCHITECTURE.md).

---

### 3.4 Knowledge Base

The Knowledge Base stores reusable knowledge.

Examples:

- Writing principles
- Storytelling patterns
- Coding guidelines
- PostgreSQL notes
- Prompt engineering rules
- Good examples
- Bad examples

Knowledge should not be hard-coded into one giant prompt.

Knowledge is organized by category, domain, topic, and focused knowledge
document. The Knowledge Index provides discovery while the repository remains
the authoritative source. See
[Knowledge Architecture](KNOWLEDGE_ARCHITECTURE.md) for hierarchy, governance,
lifecycle, and consumption rules.

---

### 3.5 Evaluation Engine

The Evaluation Engine checks output quality.

Common criteria:

- Accuracy
- Completeness
- Logic
- Clarity
- Structure
- Usefulness
- Risk
- Actionability

Pipeline, scoring, thresholds, and failure routing follow the
[Evaluation Engine Architecture](EVALUATION_ARCHITECTURE.md).

---

### 3.6 Reflection Engine

The Reflection Engine improves output before final delivery.

It asks:

- What is missing?
- What is weak?
- What is unclear?
- What may be inaccurate?
- What can be improved?

Triggers, improvement rules, retry policy, and termination follow the
[Reflection Engine Architecture](REFLECTION_ARCHITECTURE.md).

---

## 4. Design Rule

The Master Skill should stay thin.

Business logic belongs to Skills.

Reusable knowledge belongs to the Knowledge Base.

Quality control belongs to Evaluation and Reflection.

The contracts for artifact metadata, versions, Knowledge dependencies,
evaluation, and reflection are indexed in the
[Specification Registry](../specifications/README.md).

Machine-readable structure and layered validation follow the
[Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md).

---

## 5. Initial Architecture Version

Version: 0.1

Status: Draft
