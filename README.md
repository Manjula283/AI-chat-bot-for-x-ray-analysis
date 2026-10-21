# ThoraxAI — Educational Chest X-ray Workspace and Chatbot

ThoraxAI is a Flask-based educational prototype for chest X-ray image exploration and radiology terminology learning. It combines image upload and preprocessing, an interactive viewer, simulated structured reports, a report-associated chatbot interface, and saved study histories.

**Current implementation:** Reports are generated using basic image statistics, handwritten rules, filename/case hints, and predefined templates. The supplied analysis pipeline does **not** use DenseNet-121, TorchXRayVision, BioBART, Clinical-T5, or a trained vision-language model.

> **Educational use only.** Do not use this application to diagnose, rule out disease, triage patients, or guide treatment. Generated text and heuristic values can be incorrect. Clinical interpretation belongs to qualified healthcare professionals. Use only synthetic or fully de-identified images.

## Live Deployment

https://thoraxai-chest-xray.onrender.com

The application is hosted on Render with Neon PostgreSQL. A free hosting instance may take time to respond after inactivity. Deployment success does not establish clinical validity or complete functional/security testing.

## Features

### Accounts and saved studies
- Registration and login, with password handling delegated to the `User` model.
- Session-based authentication.
- User-filtered analysis history.
- Ownership checks on analysis, chat, deletion, and protected image-delivery routes.
- Saved report text, metadata, conversations, and original/processed image bytes.

**Privacy caveat:** The current preprocessing code also saves image copies under `static/uploads`. These copies are not protected by the ownership checks on `/analysis/.../image` routes. Move user image storage outside the public static directory or explicitly block public access before claiming private image storage.

### Upload and preprocessing
- JPG, JPEG, and PNG uploads up to 16 MB.
- Extension, file-size, decode/integrity, and minimum-resolution checks (64 × 64 pixels).
- Image re-encoding intended to strip EXIF metadata.
- Grayscale conversion and 512 × 512 resizing for statistics.
- CLAHE contrast enhancement and aspect-ratio-preserving enhanced display images.
- Fixed-region pixel-brightness statistics.
- Built-in reference samples for demonstrating the workflow.

These checks do not establish that an uploaded image is a chest radiograph or that its orientation/projection is appropriate. Grayscale similarity is not a medical-image classifier. EXIF removal does not remove identifying information embedded in pixels or elsewhere in application records.

### Interactive workspace
- Side-by-side image and report panels.
- Original and CLAHE-enhanced image views.
- Zoom, pan, hover-to-zoom, reset, and inversion controls.
- Structured report and raw-text views.
- Plain-English explanation and terminology/glossary sections.
- Report-associated chatbot interface.
- PDF report-download interface.

Viewer behavior, export behavior, and chatbot limitations should be tested in the target browser. The chatbot implementation must be reviewed separately before claiming an LLM, strict report grounding, or enforced English-only responses.

### Simulated report generation
The reporting service selects among four predefined patterns:
1. Right lower zone consolidation teaching pattern.
2. Cardiomegaly/pleural effusion teaching pattern.
3. Left upper zone opacity teaching pattern.
4. An unremarkable/normal teaching pattern.

Selection uses fixed thresholds, filename keywords, and case hints. These are not validated medical detections. A filename or submitted hint can affect the selected report independently of image content.

## Important Implementation Limitations

The supplied code contains labels and outputs that should be corrected before public use:

- `ThoraxVLM-v2.4 (DenseNet121-CXR + BioBART Decoder)` is a text label, not evidence of a loaded model. Replace it with an accurate rule-based educational-engine label, including defaults in configuration/templates where applicable.
- Confidence scores are hard-coded and must not be presented as model confidence or diagnostic probabilities.
- Displayed cardiothoracic-ratio values are heuristic and adjusted according to the selected pattern; they are not validated anatomical measurements.
- Detailed report statements are predefined text, not independently detected findings.
- The default branch generates a normal-pattern report; it is not a safe disease-exclusion mechanism. A pending-professional-review shell is recommended for arbitrary uploads.
- The reported processing latency includes a fixed 142 ms addition and is not a pure elapsed-time measurement.
- Color conversion and preprocessing do not make an image medically suitable for interpretation.

The workspace and PDF exports should prominently display:

> **Simulated educational report — generated using handwritten rules and templates, not a validated diagnostic model. Findings and heuristic values may be incorrect. Not for diagnosis, disease exclusion, triage, or treatment.**

This README documents the limitation; changing documentation alone does not update existing interface labels, saved reports, or exports.

## Technology Stack

| Component | Technology |
| --- | --- |
| Backend | Python, Flask, Gunicorn |
| ORM | Flask-SQLAlchemy, SQLAlchemy |
| Deployed database | Neon PostgreSQL |
| Local fallback | SQLite |
| Optional database | MySQL via PyMySQL |
| PostgreSQL driver | psycopg2-binary |
| Image processing | OpenCV headless, Pillow, NumPy |
| Frontend | HTML, CSS, vanilla JavaScript |
| Tests | pytest |

## Project Structure

```text
.
├── app.py                         # Flask routes, authentication, APIs, application factory
├── config.py                      # Environment settings and database selection
├── models.py                      # User, Analysis, and ChatMessage ORM models
├── schema.sql                     # MySQL-specific schema script
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render Blueprint configuration
├── services/
│   ├── image_processor.py         # Validation, re-encoding, CLAHE, pixel statistics
│   ├── ai_report_generator.py     # Rule-based/template report service
│   ├── chatbot_engine.py          # Chat response implementation; review separately
│   ├── sample_generator.py        # Reference/sample generation utilities
│   └── seed_demo.py               # Startup seeding and sample catalogue
├── static/
│   ├── css/clinical.css
│   ├── js/workspace.js
│   ├── samples/
│   └── uploads/                   # Current local image copies; see privacy caveat
├── templates/
│   ├── base.html
│   ├── auth.html
│   ├── dashboard.html
│   └── history.html
└── tests/
    ├── test_app.py
    └── test_database_migrations.py
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Manjula283/AI-chat-bot-for-x-ray-analysis.git
cd AI-chat-bot-for-x-ray-analysis
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Use a Python version compatible with the dependencies. Pin a tested Python version and dependency versions for reproducible deployments; the current requirements use minimum versions rather than a lockfile.

### 4. Choose a database

Database selection follows this order:
1. `DATABASE_URL`, when set.
2. MySQL settings, when `MYSQL_HOST` is set.
3. SQLite at `instance/chest_xray_ai_db.sqlite` when neither is configured.

Only one database is selected for a running configuration. Supporting multiple database types does not mean they are used simultaneously.

#### Option A: SQLite for local development

Leave `DATABASE_URL` and `MYSQL_HOST` unset. The app selects the local SQLite path. Startup initialization/seeding is handled through `seed_initial_data` when not testing; review that service for its exact schema and demo-data behavior.

#### Option B: Neon PostgreSQL

Set `DATABASE_URL` privately in your shell or hosting environment. With the installed `psycopg2-binary` driver, use an explicit driver prefix:

```text
postgresql+psycopg2://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

Use your own fresh Neon connection string, preferably the pooled connection for this deployment, and change only its scheme to `postgresql+psycopg2://`. Preserve its remaining connection parameters, including `channel_binding=require` if supplied by Neon. URL-encode credential characters if constructing a URL manually.

Do not commit database credentials or paste them into screenshots, issues, chats, or logs.

#### Option C: MySQL

If using the provided MySQL script, review it before applying it to an existing database:

```bash
mysql -u root -p < schema.sql
```

Set the following variables, replacing placeholders with local values. Ensure `DATABASE_URL` is unset, because it takes priority.

macOS/Linux:

```bash
export MYSQL_HOST="127.0.0.1"
export MYSQL_PORT="3306"
export MYSQL_USER="YOUR_DB_USER"
export MYSQL_PASSWORD="YOUR_DB_PASSWORD"
export MYSQL_DB="chest_xray_ai_db"
```

Windows PowerShell:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "YOUR_DB_USER"
$env:MYSQL_PASSWORD = "YOUR_DB_PASSWORD"
$env:MYSQL_DB = "chest_xray_ai_db"
```

`schema.sql` is MySQL-specific. Do not apply it to PostgreSQL or SQLite. Cross-database migration behavior needs its own tests; identical physical schemas are not guaranteed merely by using SQLAlchemy.

### 5. Configure application settings

For local development, explicitly disable optional demo-login access if you do not need it:

macOS/Linux:

```bash
export APP_ENV="development"
export ENABLE_DEMO_ACCESS="false"
```

Windows PowerShell:

```powershell
$env:APP_ENV = "development"
$env:ENABLE_DEMO_ACCESS = "false"
```

The supplied configuration defaults to development and provides a development-only secret. Production requires a strong `FLASK_SECRET_KEY`. `ENABLE_DEMO_ACCESS=false` disables the demo-login route; it does not by itself prove startup demo accounts/data are not seeded.

Environment variables must be set in the process environment. The supplied files do not show automatic `.env` loading.

### 6. Run locally

```bash
python app.py
```

Open `http://localhost:5000`, unless `PORT` is configured differently.

## Render Deployment

The repository includes a Render Blueprint (`render.yaml`). Configure:

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1` |
| Health check | `/healthz` |
| `APP_ENV` | `production` |
| `ENABLE_DEMO_ACCESS` | `false` |
| `FLASK_SECRET_KEY` | Strong generated secret; keep private |
| `DATABASE_URL` | Private Neon URL using `postgresql+psycopg2://` |

Use the hosting environment for secrets. Never place real secrets in `render.yaml` or source control. Inspect the current Blueprint before deploying, including the selected instance plan and any costs.

Render's free local filesystem is ephemeral. Database image blobs support retrieval after local copies disappear, but the implementation should still be tested across restarts/redeploys. Do not use local SQLite as persistent production storage on an ephemeral instance.

### Health check

`GET /healthz` executes `SELECT 1` against the configured database:
- HTTP 200: database check succeeded.
- HTTP 503: database check failed.

A successful health check does not verify report correctness, chatbot behavior, security, or every application feature.

## Testing

Run the current test suite:

```bash
python -m pytest -v
```

Or run selected files:

```bash
python -m pytest -v tests/test_app.py
python -m pytest -v tests/test_database_migrations.py
```

Do not assume full PRD coverage without reviewing the assertions and running the suite against the current revision. No test-pass result for the latest deployed revision is claimed here.

Before broader use, verify:
- Registration, login, logout, and session behavior.
- Unsupported, corrupted, oversized, and non-radiograph uploads.
- Viewer controls and mobile layout.
- Clear simulated-output labels in UI and PDF exports.
- Cross-user access denial on every relevant route.
- Blocking direct public access to uploaded image copies.
- Chatbot source, grounding, language behavior, and safe response limits.
- Deletion of database records, related messages, image blobs, and local files.
- Data availability after redeployment.
- Schema/migration behavior for each supported database.

## Privacy and Security Notes

- Use synthetic or fully de-identified images only.
- Metadata stripping is not complete de-identification.
- Never commit uploads, credentials, database files, or secret keys.
- Ignoring or deleting files in the latest Git revision does not remove earlier copies from Git history. Review and remediate historical sensitive content if necessary.
- Move upload copies outside public static storage or deny public access.
- Ownership checks are present in the supplied routes, but the application has not been established as clinically or comprehensively security validated.
- Review CSRF protection, login rate limiting, upload resource limits, demo seeding, backups, and retention/deletion policies before broader deployment.
- The `/download-project-zip` route serves a named archive without authentication if that archive exists. Remove/disable it or ensure the archive contains only intentionally public source and no secrets or private data.
- Rotate any credential exposed through screenshots, source control, chat, or logs.

## Future Enhancements

- Replace arbitrary-upload report templates with a pending-professional-review shell.
- Separate clearly labeled teaching examples from user-upload processing.
- Optionally integrate a pretrained TorchXRayVision DenseNet-121 classifier with validated preprocessing and resource testing.
- Present classifier outputs as unverified scores—not confirmed diagnoses, calibrated probabilities, or complete radiology reports.
- Improve upload privacy, access-control testing, dependency pinning, and automated deployment checks.

A pretrained classifier would require additional dependencies, downloaded weights, RAM, and CPU resources. It is not currently implemented in the supplied analysis path and may require a different hosting plan.

## Scope

**In scope:** educational image viewing, terminology learning, simulated report demonstrations, and saved-study workflow exploration.

**Out of scope:** diagnosis, disease exclusion, patient triage, treatment decisions, clinical-grade measurement, validated automated radiology reporting, and claims of regulatory approval.

DICOM support and hospital/PACS integration are not implemented by the supplied JPG/PNG upload pipeline. A PACS-style visual layout does not imply PACS connectivity.
