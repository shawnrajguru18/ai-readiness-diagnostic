# AI Readiness Diagnostic - Frontend

This is a TypeScript/React application built with Vite and Tailwind CSS.

## Project Structure

```
web/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Btn.tsx          # Button component
│   │   ├── DxcLogo.tsx      # DXC logo SVG
│   │   ├── Radar.tsx        # Hexagonal radar chart
│   │   ├── TierBadge.tsx    # Tier badge component
│   │   ├── ValueDifficulty2x2.tsx  # Value vs difficulty matrix
│   │   └── Wordmark.tsx     # DXC wordmark header
│   ├── screens/             # Full-page screens
│   │   ├── Assessment.tsx   # Questionnaire screen
│   │   ├── Landing.tsx      # Home/intake screen
│   │   ├── QuickWins.tsx    # Quick wins memo screen
│   │   ├── Scorecard.tsx    # Results scorecard screen
│   │   ├── Submitted.tsx    # Submission confirmation screen
│   │   └── VoiceInterview.tsx # Voice interview screen
│   ├── App.tsx              # Main app router/shell
│   ├── constants.ts         # Constants (demo data, colors, labels)
│   ├── main.tsx             # React entry point
│   ├── types.ts             # TypeScript type definitions
│   ├── utils.ts             # Utility functions
│   └── index.css            # Global styles
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite build configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
└── .gitignore               # Git ignore rules
```

## Setup

### Install Dependencies
```bash
cd web
npm install
```

### Development Server
```bash
npm run dev
```
Opens http://localhost:5173 automatically.

### Build for Production
```bash
npm run build
```
Creates optimized build in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## Architecture

### Components
- **UI Components** (`src/components/`) - Reusable, stateless presentational components
  - Radar: Custom SVG radar chart for dimension scores
  - ValueDifficulty2x2: 2x2 matrix for opportunity mapping
  - Btn, TierBadge, Wordmark: Shared UI elements

### Screens
- **Landing**: Intake form with email/company/role/industry fields
- **Assessment**: Progressive questionnaire with conditional branching
- **Voice Interview**: ElevenLabs integration for voice-based responses
- **Submitted**: Confirmation screen with next steps
- **Scorecard**: Full report with radar, findings, quick wins, value matrix
- **QuickWins**: Detailed memo of 90-day implementation patterns

### State Management
- App.tsx manages global state: current screen, scorecard data, user responses
- Each screen receives props with callbacks (onSubmit, onBack, etc.)
- No external state library (Redux/Context) — simple prop drilling works for this flow

### Types
- `Scorecard`: Complete assessment result with dimensions, findings, quick wins
- `Question`: Individual question with type (single_select, scale_1_5, multi_select, open_short)
- `FormData`, `ConsentData`: User submission metadata
- `Answer`: User response (flexible to support different question types)

### Constants
- **DEMO_SCORECARD**: Sample scorecard for MeridianFS Holdings (shown on landing/sample view)
- **TIER_COLOR**: Color palette for tier badges
- **INDUSTRY_LABELS**: Industry selector options
- **ELEVENLABS_AGENT_ID**: Voice agent ID (configure before enabling voice)

## API Integration

The app calls these endpoints (configurable via `API` constant):
- `GET /api/questions` — Fetch question pool with branching logic
- `POST /api/assess` — Submit responses, receive scored scorecard

When `API = ''` (default), the app runs offline using the DEMO_SCORECARD.

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom colors** defined in tailwind.config.js (midnight, canvas, ink, royal, etc.)
- **Google Fonts** for Playfair Display (headers) and DM Sans (body)
- **Animations**: fadeUp (0.4s) on screen entry, spin for loading states

## Development Notes

### Adding a New Question Type
1. Add type to `Question` in `types.ts`
2. Add rendering logic in `Assessment.tsx` under `{q.type === 'your_type' && ...}`
3. Add answer validation in `answered()` function

### Customizing Demo Data
Edit `DEMO_SCORECARD` in `constants.ts`. This is shown when no API is available and as the sample on landing.

### Voice Integration
- Requires ElevenLabs agent ID in `ELEVENLABS_AGENT_ID`
- Agent must be Public and allow the current origin
- Agent calls two client tools: `record_answer()` and `finish_interview()`
- See `VoiceInterview.tsx` for implementation details

### Building for Deployment
The Vite build optimizes the bundle:
- Minifies all code
- Bundles assets
- Generates source maps
- Outputs to `dist/`

Serve `dist/` with any static host (S3, CloudFront, CDN, etc.).
