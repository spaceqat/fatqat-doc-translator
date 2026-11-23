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
Follow the Korean README's established wording for shared terms: 노이즈,
커플링, 트랜스몬, 네이티브 연산, and 벨 상태. Write 큐디트(qudit, 다준위 양자 시스템) at the
first mention on a page when readers may not know the term.
Use ordinary Korean punctuation and spacing. Attach Korean particles naturally
to identifiers and code spans without altering the protected text itself.

Each entry has id, en, ko, and status. Keep ko on one line. The extractor owns
id, en, ordering, and retirement. Set translated entries to machine; only a human
may mark them reviewed. Review in three passes: meaning against the English,
terminology and protected syntax, then fluent Korean in rendered page context.

## User guide voice

Lead with the reader's task, then explain what to do, what the result means,
and why. Keep the tone approachable and pedagogical. Use short, connected
sentences and concrete verbs; split paragraphs that answer different questions.
Keep explanations needed to understand the example, including prerequisites,
units, uncertainty, supported behavior, and limitations. Avoid repeated setup
instructions, architecture summaries, and chapter previews that do not help
with the current task. Keep links that help the reader complete or understand it.

Adapt sentence structure to the target language rather than translating English
word order. Preserve exact API names and use consistent conceptual terminology.
When content or structure needs to change, update the English source first and
synchronize both locales through extraction. Do not hide removed prose in HTML
comments or let the localized guides drift apart.

## API reference headings

For API sections that list symbols, translate `Reference`, `Detailed reference`,
and `API` as “API 레퍼런스”, matching the API index. For headings that
list other API pages, use “API 레퍼런스 페이지”. This rule does not apply
to citations or programming references such as `RegisterRef`.
