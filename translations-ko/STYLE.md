# Korean translation style

Translate authored prose, navigation, headings, captions, image descriptions,
and prose metadata. Preserve the Chinese edition's boundaries: executable code,
code comments, generated API docstrings, plot labels, identifiers, product names,
and algorithm names remain in English. Preserve math, code spans, HTML, attribute
lists, cross-references, link destinations, and table structure exactly.

Write for Korean-speaking developers. Use natural Korean sentence order and
clear 합니다-style explanations; use 하세요 for direct instructions when useful.
Headings may be short noun phrases. Avoid literal English metaphors, repetitive
transitions, unnecessary passive constructions, and formulaic introductory text.
Sentence restructuring is welcome, but preserve every condition, qualification,
error case, and numerical claim. Do not add claims absent from the source.

Use glossary.yml for conceptual terms. Exact API identifiers take precedence:
Simulator, Estimator, Register, Operation, and their plural API page titles keep
their spelling. Distinguish quantum channels (양자 채널) from control channels
(제어 채널), and simulation (시뮬레이션) from emulation (에뮬레이션).
Use ordinary Korean punctuation and spacing. Attach Korean particles naturally
to identifiers and code spans without altering the protected text itself.

Each entry has id, en, ko, and status. Keep ko on one line. The extractor owns
id, en, ordering, and retirement. Set translated entries to machine; only a human
may mark them reviewed. Review in three passes: meaning against the English,
terminology and protected syntax, then fluent Korean in rendered page context.
