# Deployment Checklist

Pre-deployment verification checklist for AWS.

## Pre-Build Checks

- [ ] All TypeScript files compile without errors
- [ ] No ESLint warnings (if configured)
- [ ] No console.log or debug code left
- [ ] API constants correctly configured
- [ ] Environment variables (.env) are in .gitignore
- [ ] No hardcoded credentials or secrets

## Build Verification

- [ ] Build completes successfully: `npm run build`
- [ ] No build warnings or errors
- [ ] `dist/` folder created with all files
- [ ] `dist/index.html` exists and contains script tags
- [ ] JS bundle files exist in `dist/`
- [ ] CSS files compiled correctly
- [ ] Assets (fonts, images) included

## Local Testing (Before AWS)

### Dev Server
- [ ] Dev server starts: `npm run dev`
- [ ] App loads at http://localhost:5173
- [ ] No TypeScript errors in console
- [ ] Hot reload works (edit a file, changes appear)

### Production Preview
- [ ] Build succeeds: `npm run build`
- [ ] Preview build works: `npm run preview`
- [ ] App loads at served URL
- [ ] No 404 errors for assets
- [ ] Network tab shows all assets loaded

### User Flows
- [ ] Landing page loads and displays correctly
- [ ] Form validation works
- [ ] Can navigate to Assessment screen
- [ ] Questions render correctly
- [ ] Can select answers and submit
- [ ] Submitted screen appears
- [ ] Can view Scorecard
- [ ] Scorecard displays radar, findings, quick wins
- [ ] Can view QuickWins memo
- [ ] "New assessment" returns to landing
- [ ] Voice interview screen loads (if ElevenLabs configured)

### Responsive Design
- [ ] Desktop view (1920x1080): All elements aligned
- [ ] Tablet view (768px): Responsive layout works
- [ ] Mobile view (375px): Text readable, buttons clickable
- [ ] No horizontal scroll on any viewport

### API Integration
- [ ] API URL configured in constants
- [ ] Questions load from API (or demo if offline)
- [ ] Submission sends to API (or shows demo scorecard)
- [ ] No CORS errors in console
- [ ] API errors handled gracefully

### Performance
- [ ] Page loads in < 3 seconds
- [ ] No console errors or warnings
- [ ] Network waterfall shows no blocked resources
- [ ] Bundle size reasonable (check DevTools)

## AWS Deployment

### S3 Bucket Setup
- [ ] S3 bucket created
- [ ] Block public access disabled (if public website)
- [ ] Bucket policy allows GET from origin
- [ ] Static website hosting enabled
- [ ] Error page set to index.html (for SPA routing)

### CloudFront Setup (Optional but recommended)
- [ ] CloudFront distribution created
- [ ] S3 bucket set as origin
- [ ] Cache policy configured (short TTL for index.html, long for assets)
- [ ] Distribution deployed and active

### FastAPI Integration
- [ ] FastAPI serves static files from dist/
- [ ] API endpoints (/api/questions, /api/assess) return correct data
- [ ] CORS headers configured correctly
- [ ] Routes configured for SPA (non-existent routes → index.html)

## Post-Deployment Testing (AWS)

### Access & Loading
- [ ] App accessible at AWS URL
- [ ] Page loads in < 5 seconds
- [ ] No 404 errors in console for assets
- [ ] No mixed content warnings (HTTPS)

### Core Functionality
- [ ] Landing page displays correctly
- [ ] Can submit form and navigate
- [ ] All screens render without layout shifts
- [ ] Buttons are clickable and responsive
- [ ] Forms accept input

### API Calls
- [ ] Network tab shows API calls to correct endpoint
- [ ] Requests include proper headers
- [ ] Responses are valid JSON
- [ ] No CORS errors
- [ ] Fallback to demo data works if API unavailable

### Error Handling
- [ ] Network errors don't crash app
- [ ] Invalid API responses handled gracefully
- [ ] Browser console has no JavaScript errors
- [ ] 404 pages redirect to app (if using CloudFront)

### Performance
- [ ] First contentful paint < 3s
- [ ] Largest contentful paint < 5s
- [ ] Cumulative layout shift minimal
- [ ] Network requests optimized

### Security
- [ ] HTTPS enabled (no HTTP)
- [ ] No sensitive data in console or Network tab
- [ ] No API keys exposed
- [ ] CSP headers present (if configured)
- [ ] X-Frame-Options set (prevents clickjacking)

## Monitoring (After Deployment)

- [ ] CloudWatch logs configured (if using CloudFront)
- [ ] Error tracking enabled (e.g., Sentry, DataDog)
- [ ] Performance monitoring in place
- [ ] Daily health check scheduled
- [ ] Alerts configured for errors

## Rollback Plan

- [ ] Previous version backed up
- [ ] Rollback procedure documented
- [ ] Estimated rollback time: < 5 minutes
- [ ] Team knows who to contact if issues arise

## Sign-Off

- [ ] QA testing passed
- [ ] Product owner approved
- [ ] Deployment checklist completed
- [ ] All team members notified
- [ ] Documentation updated

---

## Testing Commands

```bash
# Type check
npx tsc --noEmit

# Build
npm run build

# Preview production build
npm run preview

# Bundle analysis (if configured)
npm run build -- --report

# Check for unused code
npx depcheck
```

## Monitoring the Deployment

After deploying to AWS, monitor these metrics:

- **Page Load Time:** Should be < 3s
- **Error Rate:** Should be < 0.1%
- **API Response Time:** Should be < 500ms
- **User Session Duration:** Monitor for unexpected drops
- **Browser Errors:** Track in console or error tracking service

---

## Rollback Procedure

If issues occur post-deployment:

1. **Immediate:** Revert CloudFront cache invalidation
2. **S3:** Upload previous dist/ folder
3. **FastAPI:** Restart with previous build
4. **Testing:** Verify previous version works
5. **Communication:** Notify team
6. **Post-Mortem:** Review what went wrong

Estimated time: 5-10 minutes
