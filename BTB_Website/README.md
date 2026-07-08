# Beyond the Blueprint — Website

Vue 3 + Vite front end for the BTB project: a homepage introducing the series,
a detail page per interview (video + full profile), and an AI Q&A assistant on
every page, powered by the FastAPI RAG backend in `../BTB_AI`.

## Run it

```bash
# 1. Start the AI backend (in ../BTB_AI)
uvicorn app.main:app --port 8000

# 2. Start the site (in this folder)
npm install
npm run dev        # http://localhost:5173
```

The chat works without the backend too — it just shows a friendly "start the
backend" message instead of answers.

## Point the chat at a different backend

Copy `.env.example` to `.env` and set `VITE_API_BASE_URL`. Default is
`http://127.0.0.1:8000`.

## Add or edit interviews

Everything lives in [`src/data/interviews.js`](src/data/interviews.js) — one
object per episode (name, role, bio paragraphs, highlights, quote, suggested
questions).

- **Videos:** set the `video` field to a YouTube link (any format) or a file in
  `public/` (e.g. `/videos/XavierEldridge.mp4`). Leave `''` for a
  "video on its way" placeholder.
- **`ragId`** must match the interview id used by the backend (the folder names
  in `BTB_Prepare`) so chat sources display correctly.

## Build for production

```bash
npm run build      # outputs to dist/
npm run preview    # serve the build locally
```

## Chat history

The conversation is shared between the homepage chat and every interview
sidebar, persists across reloads (localStorage key `btb-chat-v1`), and the
backend session id is kept alongside it so follow-up questions stay in context.
"Clear" wipes both the local history and the backend session.
