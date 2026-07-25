# UI Refactoring: Single-File HTML → TypeScript/React with Vite

## Summary

The UI has been refactored from a single-file HTML application (with inline React JSX) to a proper TypeScript/React project with a modern build pipeline.

## What Changed

### Before
- **single index.html** with 590 lines of inline JSX
- No build step — Babel transpiled JSX in the browser
- No type safety
- Monolithic file structure
- Vendored libraries (React, ReactDOM, Babel, Tailwind) loaded via script tags

### After
- **Modular TypeScript/React** with separate components and screens
- **Vite** build tool with fast development and optimized production builds
- **Full type safety** with TypeScript
- **Clean separation of concerns**: components, screens, types, constants, utils
- **npm package management** instead of vendored libraries
- **Source maps** for easier debugging
- **Modern tooling**: PostCSS, Tailwind CSS JIT compilation

## Directory Structure

```
web/
├── src/
│   ├── components/     # Reusable UI components
│   ├── screens/        # Full-page screens
│   ├── App.tsx         # Main router/shell
│   ├── main.tsx        # Entry point
│   ├── types.ts        # Type definitions
│   ├── constants.ts    # Constants & demo data
│   ├── utils.ts        # Helper functions
│   └── index.css       # Global styles
├── index.html          # HTML template (Vite will inject built JS)
├── package.json        # Dependencies
├── vite.config.ts      # Build configuration
├── tsconfig.json       # TypeScript configuration
└── tailwind.config.js  # Tailwind CSS customization
```

## Component Breakdown

### Components (src/components/)
- **Btn.tsx** — Reusable button with variants (primary, ghost, light)
- **DxcLogo.tsx** — SVG logo component
- **Wordmark.tsx** — DXC + AdvisoryX header
- **Radar.tsx** — Hexagonal radar chart (custom SVG)
- **TierBadge.tsx** — Colored badge for maturity tiers
- **ValueDifficulty2x2.tsx** — 2x2 matrix visualization

### Screens (src/screens/)
- **Landing.tsx** — Intake form (prospect name, role, email, company, industry)
- **Assessment.tsx** — Progressive questionnaire with conditional skip/branch logic
- **VoiceInterview.tsx** — ElevenLabs voice agent integration
- **Submitted.tsx** — Confirmation + next steps
- **Scorecard.tsx** — Full results report with radar, findings, quick wins, opportunity map
- **QuickWins.tsx** — 90-day implementation patterns

### Core Files
- **App.tsx** — Screen router, state management, API calls
- **types.ts** — TypeScript interfaces for all data structures
- **constants.ts** — DEMO_SCORECARD, colors, labels, agent ID
- **utils.ts** — personaFromRole() and framing preference mapping
- **main.tsx** — React entry point
- **index.css** — Global Tailwind + animations

## Migration Steps (If Needed)

### 1. Install Dependencies
```bash
cd web
npm install
```

### 2. Development
```bash
npm run dev
```
This starts Vite on http://localhost:5173 with hot module reloading.

### 3. Build for Deployment
```bash
npm run build
```
Output goes to `web/dist/`. This is what FastAPI should serve statically.

### 4. Update FastAPI Static Files
In your FastAPI app, point static files to the new build location:
```python
app.mount("/", StaticFiles(directory="web/dist"), name="static")
```

## Benefits

1. **Type Safety** — Catch errors at compile-time, not runtime
2. **Modularity** — Components are isolated, testable, reusable
3. **Maintainability** — Clear file organization, easier to navigate
4. **Performance** — Vite optimizes the bundle, faster load times
5. **Developer Experience** — Hot module reloading, source maps, better IDE support
6. **Scalability** — Easy to add new screens, components, or features
7. **Build Pipeline** — Production build with minification, tree-shaking, etc.

## Backward Compatibility

The app behaves identically to the original:
- Same screens and flows
- Same demo data (DEMO_SCORECARD in constants.ts)
- Same API endpoints (/api/questions, /api/assess)
- Same styling and animations
- Same ElevenLabs voice integration

## Next Steps

1. **Test locally**: `npm run dev` and verify all flows work
2. **Build**: `npm run build` to create `dist/` folder
3. **Deploy**: Serve `dist/` from FastAPI (or any static host)
4. **Optional**: Add tests (Jest/Vitest), linting (ESLint), or CI/CD

## Original HTML File

The original index.html (single-file version) has been replaced with a new, minimal template that Vite will inject the built JS into. If you need to reference the original JSX, all the code has been extracted and organized into the `src/` directory structure.
