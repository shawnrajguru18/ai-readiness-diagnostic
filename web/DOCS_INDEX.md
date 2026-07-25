# Documentation Index

Complete guide to the AI Readiness Diagnostic UI refactoring.

## Overview

The UI has been refactored from a single monolithic HTML file with embedded JSX into a professional TypeScript/React project with Vite, Tailwind CSS, and a clean modular architecture.

## Documentation Files

### 📖 **QUICKSTART.md** — Start here
**2-minute guide to get the app running locally.**
- Install & start dev server
- Try the app flow
- Edit & auto-reload
- Build for production
- Quick edits (colors, demo data, API connection)

**When to read:** You just cloned the project and want to run it immediately.

---

### 📚 **USAGE.md** — Complete developer guide
**Comprehensive guide covering all development tasks.**
- Installation and prerequisites
- Development workflow (dev server, hot reload, debugging)
- Project structure (directories, components, screens)
- Common tasks:
  - Add new question types
  - Customize demo scorecard
  - Change colors
  - Enable voice interview
  - Connect to API
  - Add new screens
  - Modify form fields
- Building & deployment (production build, FastAPI integration, cloud deployment)
- Configuration (environment variables, Vite options, Tailwind settings)
- Troubleshooting (port conflicts, hot reload issues, TypeScript errors, build failures, API issues)

**When to read:** You need to understand how to develop, modify, or deploy the app.

---

### 🏗️ **README.md** — Architecture overview
**High-level project structure and setup.**
- Project structure (directories and files)
- Setup instructions
- Component breakdown
- Screens overview
- State management approach
- Type definitions
- API integration (offline mode with demo data)
- Styling (Tailwind CSS, custom colors, animations)
- Development notes (adding question types, customizing demo, voice integration, deployment)

**When to read:** You want to understand the code organization and how components fit together.

---

### 🔄 **REFACTORING.md** — Migration notes
**What changed from the original single-file HTML.**
- Before/after comparison
- Directory structure
- Component breakdown
- Migration steps
- Benefits of refactoring
- Backward compatibility
- Next steps

**When to read:** You want to understand what was changed and why, or need to migrate related code.

---

### 🔌 **API_CONTRACT.md** — Backend integration guide
**Expected API endpoints and request/response formats.**
- Overview (two endpoints needed)
- GET /api/questions (fetch question pool)
  - Request format
  - Response format (question types, conditional logic)
- POST /api/assess (submit responses, get scorecard)
  - Request format
  - Response format (scorecard structure, fields)
- Question types (single_select, scale_1_5, multi_select, open_short)
- Conditional logic (skip_if, branch_if)
- Offline mode (falls back to demo data)
- Testing (curl examples)
- Error handling (404, 500, timeouts)
- CORS considerations
- Integration checklist

**When to read:** You need to implement the backend API or connect an existing API.

---

## Quick Navigation

### I want to...

**...run the app locally**
→ Read [QUICKSTART.md](QUICKSTART.md)

**...modify the UI (colors, text, demo data)**
→ Read [USAGE.md](USAGE.md) → "Common Tasks" section

**...add a new question type**
→ Read [USAGE.md](USAGE.md) → "Add a New Question Type"

**...build for production**
→ Read [QUICKSTART.md](QUICKSTART.md) or [USAGE.md](USAGE.md) → "Building & Deployment"

**...deploy to AWS/Netlify/FastAPI**
→ Read [USAGE.md](USAGE.md) → "Building & Deployment"

**...understand the code organization**
→ Read [README.md](README.md) → "Project Structure"

**...understand the refactoring**
→ Read [REFACTORING.md](REFACTORING.md)

**...implement the backend API**
→ Read [API_CONTRACT.md](API_CONTRACT.md)

**...fix issues with the app**
→ Read [USAGE.md](USAGE.md) → "Troubleshooting"

**...enable voice interview**
→ Read [USAGE.md](USAGE.md) → "Enable Voice Interview"

---

## File Organization

```
web/
├── QUICKSTART.md        ← Start here (2 min)
├── USAGE.md             ← Full developer guide
├── README.md            ← Architecture & setup
├── REFACTORING.md       ← What changed
├── API_CONTRACT.md      ← Backend integration
├── DOCS_INDEX.md        ← This file
├── src/
│   ├── components/      ← Reusable UI components
│   ├── screens/         ← Full-page screens
│   ├── App.tsx          ← Main router
│   ├── main.tsx         ← Entry point
│   ├── types.ts         ← TypeScript interfaces
│   ├── constants.ts     ← Static data & config
│   ├── utils.ts         ← Helper functions
│   └── index.css        ← Global styles
├── index.html           ← HTML template
├── package.json         ← Dependencies
├── vite.config.ts       ← Build config
├── tsconfig.json        ← TypeScript config
├── tailwind.config.js   ← Tailwind theme
└── postcss.config.js    ← CSS processing
```

---

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 5
- **Styling:** Tailwind CSS 3
- **Fonts:** Google Fonts (Playfair Display, DM Sans)
- **Voice Integration:** ElevenLabs ConvAI (optional)

## Key Features

✅ Modular component architecture
✅ Full TypeScript type safety
✅ Fast dev server with hot reload
✅ Optimized production builds
✅ Offline mode with demo data
✅ Responsive design
✅ Voice interview support
✅ Conditional questionnaire branching
✅ Custom radar chart visualization
✅ Value/difficulty opportunity matrix

## Getting Help

1. **Quick question?** Check [QUICKSTART.md](QUICKSTART.md)
2. **Need details?** Check [USAGE.md](USAGE.md) or relevant section above
3. **Building features?** Check [README.md](README.md) for architecture
4. **Integrating backend?** Check [API_CONTRACT.md](API_CONTRACT.md)
5. **Stuck?** Check [USAGE.md](USAGE.md) → "Troubleshooting"

---

## Summary

| Document | Audience | Time | Focus |
|----------|----------|------|-------|
| QUICKSTART.md | All | 2 min | Get running immediately |
| README.md | Developers | 10 min | Understand structure |
| USAGE.md | Developers | 30 min | Learn all tasks & troubleshooting |
| REFACTORING.md | Architects | 5 min | Understand what changed |
| API_CONTRACT.md | Backend devs | 15 min | Implement API integration |

---

**Last updated:** July 24, 2026
**Tech:** TypeScript/React with Vite + Tailwind CSS
