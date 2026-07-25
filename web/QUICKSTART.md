# Quick Start Guide

Get the UI running in 2 minutes.

## 1. Install & Start

```bash
cd web
npm install
npm run dev
```

Opens http://localhost:5173 automatically.

## 2. Try the App

- **Landing**: Fill in prospect details, click "Begin assessment"
- **Assessment**: Answer 20+ questions (branching logic), click "Submit"
- **Submitted**: Confirmation screen
- **Scorecard**: Full report with radar, findings, quick wins
- **QuickWins**: 90-day action patterns

## 3. Edit & Reload

Edit any file in `src/` and save. Browser reloads automatically with your changes:

- **Screens**: `src/screens/*.tsx`
- **Components**: `src/components/*.tsx`
- **Data**: `src/constants.ts`
- **Styles**: `src/index.css` or Tailwind classes in JSX

## 4. Build for Production

```bash
npm run build
```

Output goes to `dist/`. Deploy this folder to any static host or FastAPI.

## Common Edits

### Change Demo Company
`src/constants.ts` → Find `DEMO_SCORECARD` → Edit `company_name`

### Change Colors
`tailwind.config.js` → Edit the `colors` object

### Add API Connection
`src/constants.ts` → Change `API = ''` to your backend URL

### Enable Voice
`src/constants.ts` → Replace `ELEVENLABS_AGENT_ID` with your agent ID

## See Also

- **USAGE.md** — Full guide with all tasks and troubleshooting
- **README.md** — Project structure and architecture
- **REFACTORING.md** — What changed from the original

## Support

Node.js 16+ required. If issues, delete `node_modules` and `npm install` again.
