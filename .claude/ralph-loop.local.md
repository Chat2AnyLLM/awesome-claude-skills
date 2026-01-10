---
active: true
iteration: 52
max_iterations: 0
completion_promise: null
started_at: "2026-01-10T04:18:54Z"
---


check the logic, the code should look through the specified repos directory, then it should look for SKILL in the following folder structure to identify a skill
pdf-processing/
├── SKILL.md              # Overview and quick start
├── FORMS.md              # Form field mappings and filling instructions
├── REFERENCE.md          # API details for pypdf and pdfplumber
└── scripts/
    ├── fill_form.py      # Utility to populate form fields
    └── validate.py       # Checks PDFs for required fields

if a path specifiec in the config, okly look at that folder
if a execlude specified, skip that folder matching it
