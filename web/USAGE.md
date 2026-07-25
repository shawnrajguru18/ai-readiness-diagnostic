# AI Readiness Diagnostic UI — Usage Guide

Complete guide to developing, building, and deploying the refactored React/TypeScript UI.

## Table of Contents

1. [Installation](#installation)
2. [Development](#development)
3. [Project Structure](#project-structure)
4. [Common Tasks](#common-tasks)
5. [Building & Deployment](#building--deployment)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- **Node.js** 16+ (download from [nodejs.org](https://nodejs.org))
- **npm** 7+ (comes with Node.js)

### Setup Steps

```bash
# Navigate to the web directory
cd C:\Users\srajguru\Desktop\AIDiagnosticMVP\web

# Install all dependencies
npm install

# Verify installation (should show version numbers)
npm -v
node -v
```

Dependencies installed:
- **react** & **react-dom** — UI framework
- **vite** — Build tool & dev server
- **typescript** — Type checking
- **tailwindcss** — Utility-first CSS
- **@vitejs/plugin-react** — Vite + React integration

---

## Development

### Start the Dev Server

```bash
npm run dev
```

This will:
- Start a local server at `http://localhost:5173`
- Automatically open the app in your browser
- Enable **hot module reloading** (changes appear instantly without refresh)
- Show errors in the browser console

### Edit & Save Workflow

1. Open a file in your editor (VS Code, WebStorm, etc.)
2. Make changes to `.tsx`, `.ts`, or `.css` files
3. Save the file
4. The app reloads automatically in the browser
5. No build step needed during development

### Example: Change the Landing Page Title

File: `src/screens/Landing.tsx` (line 48)

```tsx
// Before
<h1 className="display text-5xl md:text-6xl leading-tight font-extrabold">
  Know where you stand on AI. In 30 minutes.
</h1>

// After (edit to your message)
<h1 className="display text-5xl md:text-6xl leading-tight font-extrabold">
  Assess your AI readiness in 30 minutes.
</h1>
```

Save → Browser refreshes automatically with your change.

---

## Project Structure

### `src/` Directory

#### **screens/** — Full-page components
Each screen is a complete page in the user flow:

- **Landing.tsx** — Home page with intake form
  - Collects: name, email, role, company, industry, company size
  - Routes to: Assessment or Voice Interview
  
- **Assessment.tsx** — Questionnaire screen
  - Supports 4 question types: single_select, scale_1_5, multi_select, open_short
  - Conditional branching (skip_if, branch_if)
  - Progress bar and time remaining
  
- **VoiceInterview.tsx** — Voice-based Q&A via ElevenLabs
  - Integrates ElevenLabs ConvAI widget
  - Records answers via client tools
  - Fallback to chat if voice not available
  
- **Submitted.tsx** — Confirmation after submission
  - Shows what happens next
  - Links to preview scorecard
  
- **Scorecard.tsx** — Full results report
  - Radar chart of 6 dimensions
  - Findings and recommendations
  - Download links for PDF exports
  - Quick wins summary
  - Opportunity map (value vs difficulty)
  
- **QuickWins.tsx** — 90-day action plans
  - Shows 3 implementation patterns
  - Prerequisites, timeline, effort, expected outcome

#### **components/** — Reusable UI elements

- **Btn.tsx** — Button with 3 variants: primary, ghost, light
- **DxcLogo.tsx** — DXC brand mark (SVG)
- **Wordmark.tsx** — "DXC AdvisoryX" header
- **Radar.tsx** — Custom hexagonal radar chart
- **TierBadge.tsx** — Colored maturity tier badge
- **ValueDifficulty2x2.tsx** — 2x2 matrix for opportunities

#### **Core Files**

- **App.tsx** — Main router & state container
  - Manages which screen is visible
  - Handles screen transitions
  - Makes API calls (/api/questions, /api/assess)
  - Holds shared state: scorecard data, user responses, form data

- **types.ts** — TypeScript interfaces
  - `Scorecard` — Complete assessment result
  - `Question` — Quiz question with options/anchors
  - `FormData` — User submission info
  - `Answer` — User response to a question
  - ~13 total types

- **constants.ts** — Static data
  - `DEMO_SCORECARD` — Sample scorecard (MeridianFS Holdings)
  - `TIER_COLOR` — Color palette for badges
  - `INDUSTRY_LABELS` — Dropdown options
  - `ELEVENLABS_AGENT_ID` — Voice agent ID
  - `DXC_PATH` — SVG path for logo

- **utils.ts** — Helper functions
  - `personaFromRole()` — Infers persona (P1/P2/P3) from job title
  - `FRAMING_FOR` — Maps persona to narrative framing

- **main.tsx** — React entry point
  - Renders `<App />` into `#root` div

- **index.css** — Global styles
  - Tailwind imports
  - Custom animations (fadeUp, spin)
  - Base typography

#### **index.html** — HTML template
- Vite injects compiled JS here
- Single `<div id="root"></div>` for React

#### Config Files

- **package.json** — Dependencies & scripts
  - `npm run dev` — Start dev server
  - `npm run build` — Build for production
  - `npm run preview` — Preview production build

- **vite.config.ts** — Vite settings
  - React plugin enabled
  - Path alias `@/*` → `src/*`
  - Dev server on port 5173

- **tsconfig.json** — TypeScript configuration
  - Strict mode enabled
  - Target ES2020
  - Module ESNext

- **tailwind.config.js** — Tailwind customization
  - Custom color palette (midnight, canvas, ink, royal, etc.)
  - Custom fonts (Playfair Display, DM Sans)

- **postcss.config.js** — PostCSS with Tailwind & Autoprefixer

---

## Common Tasks

### Add a New Question Type

**Step 1:** Add type to `src/types.ts`

```typescript
export interface Question {
  // ... existing fields
  type: 'single_select' | 'scale_1_5' | 'multi_select' | 'open_short' | 'new_type' // ← Add here
}
```

**Step 2:** Add rendering logic in `src/screens/Assessment.tsx`

```tsx
{q.type === 'new_type' && (
  <div className="space-y-3">
    {/* Your input component */}
    <input 
      value={ans.custom_field || ""}
      onChange={(e) => setAns({ custom_field: e.target.value })}
    />
  </div>
)}
```

**Step 3:** Update `answered()` function to validate

```typescript
const answered = (): boolean => {
  if (q.type === 'new_type') return !!ans.custom_field
  // ... rest
}
```

### Change the Demo Scorecard

File: `src/constants.ts`

The `DEMO_SCORECARD` object is shown when:
- No API is available (offline mode)
- User clicks "See a sample scorecard" on landing

```typescript
export const DEMO_SCORECARD: Scorecard = {
  company_name: 'Your Company Name', // ← Edit here
  industry_label: 'Your Industry',
  overall_score: 75, // Change the score
  dimensions: [
    // Edit dimension scores and tiers
  ],
  quick_wins: [
    // Edit quick win patterns
  ],
  // ... etc
}
```

Save and the demo updates immediately.

### Customize Colors

File: `tailwind.config.js`

```javascript
colors: {
  midnight: "#0E1020",     // Dark blue (text)
  canvas: "#F6F3F0",       // Light beige (background)
  ink: "#3D3F50",          // Gray (secondary text)
  peach: "#FFC982",        // Light orange (Emerging tier)
  gold: "#FFAE41",         // Orange (Developing tier)
  sky: "#A1E6FF",          // Light blue (Established tier)
  trueblue: "#4995FF",     // Blue (links)
  royal: "#004AAC",        // Dark blue (primary buttons)
  risk: "#D14600",         // Red (errors/warnings)
}
```

After editing, save and the dev server recompiles Tailwind automatically.

### Enable Voice Interview

File: `src/constants.ts`

```typescript
// Before (disabled)
export const ELEVENLABS_AGENT_ID = 'agent_2801ksn2g1w4f8q950snp6pc62mf'

// After (replace with your agent ID from ElevenLabs dashboard)
export const ELEVENLABS_AGENT_ID = 'agent_YOUR_ID_HERE'
```

The agent must:
1. Be **Public** (not private)
2. Allow this site's origin (CORS)
3. Have these client tools registered:
   - `record_answer({question_id, option_id})` or `({question_id, scale_value})`
   - `finish_interview()`

See `src/screens/VoiceInterview.tsx` for implementation.

### Connect to Your API

File: `src/constants.ts`

```typescript
// Before (offline mode)
export const API = ''

// After (point to your server)
export const API = 'http://localhost:8000'  // Local development
// or
export const API = 'https://api.example.com' // Production
```

The app calls:
- `GET {API}/api/questions` — Fetch question pool
- `POST {API}/api/assess` — Submit responses, get scorecard

### Add a New Screen

**Step 1:** Create `src/screens/MyNewScreen.tsx`

```tsx
interface MyNewScreenProps {
  onNext: () => void
  onBack: () => void
}

export function MyNewScreen({ onNext, onBack }: MyNewScreenProps) {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="max-w-3xl mx-auto px-6 py-6">
        <Wordmark />
      </div>
      <div className="max-w-3xl mx-auto px-6">
        {/* Your content */}
      </div>
    </div>
  )
}
```

**Step 2:** Import and add to `src/App.tsx`

```typescript
import { MyNewScreen } from './screens/MyNewScreen'

// Add screen state type
const [screen, setScreen] = useState<'landing' | 'assessment' | ... | 'mynew'>('landing')

// Add routing logic
if (screen === 'mynew') return <MyNewScreen onNext={() => setScreen('next')} onBack={() => setScreen('prev')} />
```

### Modify Landing Form Fields

File: `src/screens/Landing.tsx`

Add new field to form state:

```typescript
const [form, setForm] = useState({
  prospect_name: '',
  prospect_role: '',
  prospect_email: '',
  company_name_raw: '',
  industry_tag: 'FS',
  size_band: 'large',
  phone_number: '', // ← Add new field
})
```

Add input to JSX:

```tsx
<input
  value={form.phone_number}
  onChange={updateForm('phone_number')}
  placeholder="Phone number"
  className="w-full px-4 py-3 rounded-lg border border-black/15 ..."
/>
```

Update type in `src/types.ts`:

```typescript
export interface FormData {
  // ... existing fields
  phone_number: string // ← Add here
}
```

---

## Building & Deployment

### Build for Production

```bash
npm run build
```

This:
- Runs TypeScript type checking
- Bundles and minifies all code
- Optimizes images & assets
- Outputs to `dist/` folder
- Generates source maps for debugging

The `dist/` folder contains everything needed to serve the app.

### Serve with FastAPI

Update your FastAPI app to serve the compiled assets:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve API endpoints first
@app.post("/api/assess")
async def assess(request: dict):
    # ... your logic
    return scorecard_result

# Serve static files last (catches all other routes)
app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
```

**Important:** The `StaticFiles(html=True)` ensures that routes like `/assessment` serve `index.html` (so React Router can handle them).

### Deploy to AWS S3 + CloudFront

```bash
# 1. Build
npm run build

# 2. Upload dist/ to S3
aws s3 sync dist/ s3://your-bucket-name/

# 3. Invalidate CloudFront cache (if using CloudFront)
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Deploy to Netlify or Vercel

Both automatically detect Vite projects:

```bash
# With Netlify CLI
netlify deploy --prod --dir=dist

# With Vercel CLI
vercel --prod
```

### Check Build Size

```bash
npm run build
# Look at output in terminal for bundle size
# dist/ should be ~150-200kb gzipped
```

---

## Configuration

### Environment Variables

Create `.env` file in `web/` directory:

```
VITE_API_URL=http://localhost:8000
VITE_ELEVENLABS_AGENT_ID=agent_xxxxx
```

Access in code:

```typescript
export const API = import.meta.env.VITE_API_URL || ''
export const ELEVENLABS_AGENT_ID = import.meta.env.VITE_ELEVENLABS_AGENT_ID || 'agent_2801...'
```

### Vite Build Options

File: `vite.config.ts`

```typescript
export default defineConfig({
  build: {
    outDir: 'dist',           // Output directory
    minify: 'terser',         // Minifier (terser or esbuild)
    sourcemap: true,          // Generate source maps
    chunkSizeWarningLimit: 500, // Warning threshold (KB)
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendors into separate chunk
          vendor: ['react', 'react-dom']
        }
      }
    }
  }
})
```

### Tailwind Content Scanning

File: `tailwind.config.js`

Tells Tailwind which files to scan for class names:

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.css",  // ← Add if using CSS modules
  ],
}
```

---

## Troubleshooting

### Dev Server Won't Start

**Error:** `Port 5173 already in use`

```bash
# Kill the process using port 5173
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5173
kill -9 <PID>

# Or specify different port
npm run dev -- --port 3000
```

### Hot Module Reloading Not Working

1. Check that Vite server is running (terminal should show `VITE v5.0.0...`)
2. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
3. Check browser console for errors
4. Restart dev server: `npm run dev`

### TypeScript Errors

```bash
# Check for type errors without building
npx tsc --noEmit

# Fix linting issues automatically
npx eslint src --fix  # (if ESLint is set up)
```

### Build Fails

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

### App Shows Demo Data Instead of Real Data

1. Check `API` constant in `src/constants.ts` — it should point to your backend
2. Ensure backend `/api/questions` endpoint returns valid data
3. Check browser Network tab to see if API calls are being made
4. Check browser Console for fetch errors

### Tailwind Classes Not Applying

1. Ensure class is in the content scanning list (`tailwind.config.js`)
2. Avoid dynamic class names:
   ```tsx
   // ❌ Won't work (Tailwind can't scan dynamic strings)
   const colorClass = `bg-${color}`
   
   // ✅ Use static class names instead
   const colorClass = color === 'blue' ? 'bg-blue-500' : 'bg-red-500'
   ```
3. Restart dev server after changing `tailwind.config.js`

### Voice Interview Not Showing Widget

1. Verify `ELEVENLABS_AGENT_ID` is set and not a placeholder
2. Check that agent is **Public** in ElevenLabs dashboard
3. Add site origin to agent's allowed origins in ElevenLabs
4. Open browser console for errors
5. The widget loads from `https://unpkg.com/@elevenlabs/convai-widget-embed` — check internet connectivity

### Build Size Too Large

```bash
# Analyze bundle
npm run build --report  # (if setup)

# Or use this:
npm install -g rollup-plugin-visualizer
# Add to vite.config.ts:
import { visualizer } from 'rollup-plugin-visualizer'
plugins: [visualizer()]
```

Then open `stats.html` after build to see what's taking space.

---

## Next Steps

1. **Run locally**: `npm run dev` and test all flows
2. **Connect to backend**: Update `API` constant in `src/constants.ts`
3. **Build**: `npm run build` to create production files
4. **Deploy**: Serve `dist/` folder from FastAPI or static host
5. **Monitor**: Check browser console and Network tab for errors

For questions, refer to the [Vite docs](https://vitejs.dev), [React docs](https://react.dev), or [Tailwind docs](https://tailwindcss.com).
