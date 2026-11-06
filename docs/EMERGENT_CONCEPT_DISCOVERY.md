# Emergent Concept Discovery and Knowledge-Gap Detection

## Purpose

The system must discover concepts and teaching requirements that are not explicitly named or separately explained in the source vaults. It must not assume that the final taxonomy is already present in filenames, headings, tags, or an initial topic list.

While extracting and comparing many notes, the agent should infer when scattered pieces of evidence collectively reveal a concept that deserves dedicated treatment. It should also detect when existing notes repeatedly rely on an unexplained prerequisite, mathematical tool, derivation, mechanism, distinction, or procedure.

This is a required corpus-level reasoning capability, not merely keyword counting, duplicate detection, or extraction of the headings that already exist.

## Core behavior

As source files and knowledge units are processed, the system must continuously:

1. **Collect candidate concepts and dependencies.** Identify explicit concepts, implicit concepts, prerequisite ideas, recurring terms, mathematical operations, mechanisms, assumptions, methods, distinctions, and unexplained references in the evidence. Do not restrict candidates to a predefined taxonomy.
2. **Connect evidence across notes.** Link units that describe the same idea in different language, use the same underlying mechanism, depend on the same prerequisite, or expose different parts of a broader concept.
3. **Detect recurring explanatory debt.** Notice when multiple notes use a concept, equation, derivation, technique, or distinction without explaining it sufficiently for the intended reader. The fact that each source note is locally understandable does not prove the corpus explains the dependency anywhere.
4. **Infer candidate concepts.** Propose a new concept when evidence suggests that a coherent topic is missing, fragmented across notes, buried inside larger topics, or important enough to merit a dedicated explanation.
5. **Evaluate whether it deserves a dedicated note or section.** Consider conceptual coherence, prerequisite importance, recurrence across independent contexts, explanatory depth, reader value, and whether the material can be treated clearly inside an existing canonical note. Repetition alone is not sufficient; a rare but essential concept may also warrant its own treatment.
6. **Create a reviewable concept proposal.** Record the proposed name and scope, the source evidence, related knowledge-unit IDs, where the concept is used, what is currently explained or missing, why a standalone note/section is justified, suggested prerequisites and dependents, and confidence/uncertainty.
7. **Update the concept map and dossiers.** Accepted discoveries become first-class concepts in the knowledge registry, concept graph, and dossier workflow. They must not remain informal observations in an agent's context or handoff prose.
8. **Revisit discoveries as coverage grows.** Later notes can reveal that two candidates are one concept, one candidate should be split into distinct concepts, an apparent gap is already adequately covered elsewhere, or a new prerequisite is needed. Keep proposals and decisions revisable with an audit trail.

## Example: a concept discovered from repeated use

Suppose three notes independently use the chain rule:

- A backpropagation note applies it to gradients through composed functions but does not teach the rule from first principles.
- A convolutional-network note uses partial derivatives in a gradient calculation and assumes the reader already understands the derivative chain.
- An optimization note discusses gradients and Jacobians but does not connect them into a step-by-step derivation.

A heading-based extractor might record three existing topics and stop. A keyword counter might report that “chain rule” occurs several times. Neither action is the required behavior.

The system should recognize that the notes share a mathematical dependency, assemble their evidence, check whether another source passage already provides an adequate treatment, and propose a dedicated concept such as **The Chain Rule: From Composite Functions to Neural-Network Backpropagation**. Its dossier should specify the required prerequisites, formal statement, assumptions and notation, step-by-step derivation, worked examples, computational interpretation, and links to the notes that depend on it—where supported by the source evidence and the intended learning path.

The new note must not be fabricated from recurrence alone. It must be grounded in the source material, with any newly added explanation or correction identified in internal provenance records and independently verified where possible.

## Example: recurring derivations and hidden prerequisites

If several topics use a derivation without explaining its intermediate steps, the system should propose a dedicated derivation or prerequisite concept when that would materially improve the knowledge base. It must preserve the original derivation steps as knowledge units and map them to the resulting note or notes. It must not collapse the derivation into a final formula simply because the formula appears repeatedly.

The same principle applies beyond mathematics: tensor-shape reasoning, probability identities, numerical stability, API lifecycle assumptions, evaluation metrics, algorithmic complexity, chemical mechanisms, and any other concept actually found in the corpus.

## Evidence required for each candidate

A candidate-concept record should include, at minimum:

- Stable candidate/concept ID and proposed title.
- Status: proposed, accepted, merged, split, rejected, or deferred.
- Supporting knowledge-unit IDs and exact source locators.
- Independent source notes and contexts where the concept appears or is assumed.
- Relationship types: explicitly explained, partially explained, merely used, assumed prerequisite, contradicted, or unclear.
- Existing canonical concept(s) that might already cover the material.
- The specific teaching gap or fragmentation being addressed.
- Proposed scope and boundaries, including what should remain in neighboring notes.
- Proposed prerequisites, dependent concepts, and canonical destinations.
- Decision rationale, confidence, reviewer, and unresolved questions.
- When accepted, the dossier requirements and verification criteria for the new concept.

Store counts with denominators and scope. A repeated mention in one copied passage is not equivalent to independent evidence across several contexts. Deduplicate near-identical source passages before treating recurrence as evidence.

## Discovery signals and safeguards

Use multiple signals together rather than one hard-coded threshold:

- Recurrence across independent notes or domains.
- Frequent use without a sufficient explanation in the local note.
- References to an assumed prerequisite, unexplained symbol, named theorem, formula, mechanism, or method.
- A derivation or reasoning chain that is repeatedly abbreviated.
- Several partial explanations that become coherent when combined.
- A concept that bridges otherwise separate topics.
- A critical concept that appears only once but is necessary to understand a larger body of material.
- A mismatch between the concept's importance in dependent notes and the depth of its existing explanation.

Automated counts and graph analysis may rank candidates, but semantic review must decide whether the candidate is a real concept, whether a dedicated note is useful, and what its boundaries should be. Avoid both under-discovery and note explosion: not every repeated term merits a new note, and not every missing detail needs a standalone page. Some candidates belong as a section in an existing note; others should be merged into an existing concept, deferred, or rejected with a rationale.

Do not assume a concept is missing simply because the system has not yet processed the note that explains it. Candidate status must distinguish **not yet searched**, **evidence of a real gap**, and **confirmed gap after corpus-wide checking**.

## Required integration with the pipeline

- **Extraction:** Capture implicit uses, assumptions, unexplained references, derivation fragments, and prerequisite relationships—not only explicit definitions and headings.
- **Overlap discovery:** Compare candidate concepts semantically across source notes and distinguish genuine conceptual overlap from shared vocabulary.
- **Registry:** Support concepts discovered after initial schema/taxonomy setup; extend schemas additively and record migration/decision evidence.
- **Dossiers:** Include all evidence for the concept, existing explanations, missing instructional steps, dependencies, and proposed acceptance checks.
- **Synthesis planning:** Add accepted concepts to the canonical-note/section plan before the relevant dependent notes are finalized. Update dependent notes to link to and correctly use the new treatment.
- **Verification:** Test that the discovered concept is actually addressed, the supporting source units are accounted for, dependent notes reference it appropriately, and the new explanation does not duplicate or contradict existing canonical content.
- **Session handoff:** Persist discovered candidates, decisions, evidence, open questions, and the next discovery action so later sessions continue the process.

## Acceptance tests

Before relying on this capability corpus-wide, create synthetic fixtures with known expected discoveries, including:

1. A concept used in several notes but never adequately defined.
2. A derivation split across several notes whose intermediate steps need a coherent dedicated treatment.
3. Multiple differently worded explanations of the same underlying concept.
4. A repeated term that means different things in different contexts, which must not be incorrectly merged.
5. A concept already explained well in another note, which must not be falsely reported as missing.
6. A rare but essential prerequisite that appears only once and must still be considered.
7. Two candidate concepts that should be merged, and one broad candidate that should be split.
8. A candidate that should become a section in an existing note rather than a new file.
9. An apparently missing concept that is unresolved only because its source note has not yet been processed.
10. A newly accepted concept whose source units and dependent canonical notes must all be traceable.

The test manifest must define expected candidate findings and decisions before execution. Record true positives, false positives, false negatives, and localization accuracy. Do not claim that semantic discovery is solved solely because a keyword search or graph-building script runs successfully.

## Definition of done for a discovered concept

A candidate is not complete merely because its name was added to a list. For each accepted discovery, the project must establish a defensible scope, source evidence, dossier, canonical destination, relationships to dependent concepts, source-unit dispositions, and verification criteria. The resulting note or section must receive the same completeness, technical, provenance, and editorial review as any other output.

This feature complements knowledge-unit accounting and overlap classification; it does not replace either. Knowledge accounting protects the details already present in the source material. Emergent concept discovery identifies new organizing concepts and teaching structures needed to explain that material coherently.
