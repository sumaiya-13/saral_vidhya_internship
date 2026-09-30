# FastAPI PDF Learning App

A mini FastAPI application that lets authenticated users upload educational PDFs, extract text with PDF parsing + Tesseract OCR, and generate an AI summary and quiz.

## Features

- `POST /users` - create a user
- `POST /auth/login` - OAuth2 password flow + JWT
- `POST /materials/upload` - authenticated PDF upload + OCR
- `POST /materials/{id}/summary` - authenticated AI summary
- `POST /materials/{id}/quiz` - authenticated AI quiz generation
- SQLite database with SQLAlchemy models
- Swagger/OpenAPI at `/docs`
- Secrets loaded from environment variables
- Google Colab notebook demonstrating PDF -> OCR -> summary -> quiz

## Project structure

```text
fastapi-pdf-learning-app/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── dependencies.py
│   ├── routes/
│   │   ├── users.py
│   │   ├── auth.py
│   │   └── materials.py
│   └── services/
│       ├── ocr.py
│       └── llm.py
├── colab/
│   └── pdf_ocr_summary_quiz.ipynb
├── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Prerequisites

- Python 3.10+
- Tesseract OCR
- A Groq API key (or replace `app/services/llm.py` with another LLM provider)

### Install Tesseract

Ubuntu/Colab:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

Windows:

Install Tesseract OCR, then either add its installation directory to PATH or configure `pytesseract.pytesseract.tesseract_cmd` in `app/services/ocr.py`.

## 2. Setup

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd fastapi-pdf-learning-app

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
copy .env.example .env
```

or on Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env` and set a strong `JWT_SECRET_KEY` and your `GROQ_API_KEY`.

## 3. Run

```bash
uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Route list

| Method | Route | Auth | Purpose |
|---|---|---|---|
| POST | `/users` | No | Create user |
| POST | `/auth/login` | No | Login and receive JWT |
| POST | `/materials/upload` | Bearer JWT | Upload PDF + OCR |
| POST | `/materials/{id}/summary` | Bearer JWT | Generate summary |
| POST | `/materials/{id}/quiz` | Bearer JWT | Generate quiz |

## Swagger flow

1. `POST /users`
2. `POST /auth/login`
   - Swagger uses the OAuth2 password form.
   - Enter the registered email in the `username` field.
3. Click **Authorize** and provide the login credentials.
4. Call `POST /materials/upload` with a PDF.
5. Copy the returned material ID.
6. Call `POST /materials/{id}/summary`.
7. Call `POST /materials/{id}/quiz`.

A screenshot of `/docs` should be added to the repository as `docs/swagger.png` before final submission.

## API security

- Passwords are hashed with bcrypt.
- JWTs are signed using a secret from `.env`.
- Material endpoints require a valid bearer token.
- Users can access only materials they own.
- API secrets are not hardcoded.
- `.env` is ignored by Git.

## Colab

Open `colab/pdf_ocr_summary_quiz.ipynb` in Google Colab. The notebook:

1. Installs Tesseract and Python packages.
2. Uploads a PDF.
3. Extracts text.
4. Runs OCR for scanned pages.
5. Sends extracted text to the configured LLM.
6. Generates a summary.
7. Generates quiz questions.
8. Prints the output and includes coding answers for the pipeline.

For Colab, add `GROQ_API_KEY` through Colab Secrets or an environment variable. Do not put a real API key in the notebook.

## Example curl

Create user:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"student@example.com\",\"password\":\"password123\"}"
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@example.com&password=password123"
```

Upload:

```bash
curl -X POST http://127.0.0.1:8000/materials/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample.pdf"
```

Then:

```bash
curl -X POST http://127.0.0.1:8000/materials/1/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

curl -X POST http://127.0.0.1:8000/materials/1/quiz \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Notes

For production, use PostgreSQL, object storage for PDFs, file-size limits, MIME/content validation, background jobs for OCR/LLM work, refresh-token rotation, rate limiting, and stricter prompt/data handling.
