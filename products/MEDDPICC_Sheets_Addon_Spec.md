# MEDDPICC Deal Tracker — Google Sheets Add-on

> **Product:** Google Sheets Add-on (not just a template)
> **Price Point:** $9/mo or $79/year per user
> **Target Buyer:** Sales Managers, AEs at companies without Salesforce

---

## Why an Add-on vs. Template?

| Template (Commodity) | Add-on (Defensible) |
|---------------------|---------------------|
| Static scoring | Auto-calculates deal scores |
| Manual red flag detection | Automatic alerts |
| No guidance | AI-powered next step suggestions |
| One-time purchase, easy to copy | Subscription, harder to replicate |
| No updates | Continuous improvements |

---

## Core Features

### 1. Auto-Scoring Engine
When users fill in MEDDPICC fields, the add-on automatically:
- Calculates a 0-100 deal score
- Weights categories (Champion = 25%, Pain = 20%, etc.)
- Shows score progression over time

**Scoring Logic:**
```
Each letter scored 0-3:
0 = Empty/Unknown
1 = Identified but weak
2 = Solid, validated
3 = Strong, multi-threaded

Weighted Score = (M×0.15 + E×0.15 + D×0.10 + D×0.10 + P×0.05 + I×0.20 + C×0.20 + C×0.05) × 33.33

Result: 0-100 score
```

### 2. Red Flag Detection
Automatically highlights deals with:
- **No Champion identified** after Stage 2
- **No EB access** after Stage 3
- **Decision Process unknown** with close date < 30 days
- **Competition = "None"** (suspicious)
- **Pain not quantified** (no Metrics)
- **Stale deal** (no updates in 14+ days)

Visual: Red/Yellow/Green indicators in sidebar

### 3. Next Step Suggestions
Based on gaps, suggest specific actions:

| Gap Detected | Suggested Action |
|--------------|------------------|
| No Champion | "Schedule 1:1 with your main contact to test advocacy" |
| No EB access | "Ask champion: 'Who signs the final contract?'" |
| No Metrics | "In next call, ask: 'If this problem disappeared, what's the dollar impact?'" |
| Competition unknown | "Ask: 'Who else are you evaluating?'" |
| Paper Process blank | "Map the approval process: Legal → Procurement → Finance" |

### 4. Pipeline Dashboard
Aggregated view for managers:
- Total pipeline by score tier (Strong/Medium/At Risk)
- Deals missing critical MEDDPICC elements
- Score trends over time
- Forecast confidence based on MEDDPICC completeness

### 5. Weekly Email Digest
Optional email to managers:
- Pipeline summary
- Deals that dropped in score
- Red flags requiring attention
- Top deals by score

---

## Technical Architecture

### Google Apps Script Add-on

```
/meddpicc-addon
├── Code.gs              # Main add-on logic
├── Sidebar.html         # React-like sidebar UI
├── Scoring.gs           # Scoring algorithms
├── Alerts.gs            # Red flag detection
├── Suggestions.gs       # Next step recommendations
├── Dashboard.gs         # Pipeline aggregation
├── Email.gs             # Weekly digest
├── appsscript.json      # Manifest
└── README.md
```

### Key Technical Components

**1. onEdit Trigger**
- Fires when any cell changes
- Recalculates deal score
- Updates red flag indicators
- Logs change for trend tracking

**2. Sidebar UI**
- Shows current deal score
- Lists red flags
- Displays suggested next steps
- Quick actions (mark as validated, add note)

**3. Custom Menu**
- "MEDDPICC" menu in toolbar
- Open sidebar
- Generate pipeline report
- Configure settings
- Send weekly digest now

**4. Data Structure**
```
| Deal Name | Stage | M | E | D | D | P | I | C | C | Score | Flags | Last Updated |
```

Each letter column has data validation:
- 0 = Unknown
- 1 = Weak
- 2 = Solid
- 3 = Strong

### Monetization via License Key

**Free tier:**
- Up to 10 deals
- Basic scoring
- No email digest

**Paid tier ($9/mo):**
- Unlimited deals
- Red flag alerts
- Next step suggestions
- Weekly email digest
- Pipeline dashboard

**Implementation:**
- License key stored in user properties
- Validate against simple API (Vercel serverless function)
- Grace period for expired licenses

---

## Development Estimate

| Task | Effort |
|------|--------|
| Basic scoring engine | 2-3 hours |
| Sidebar UI | 3-4 hours |
| Red flag detection | 2 hours |
| Next step suggestions | 2 hours |
| Pipeline dashboard | 3-4 hours |
| Email digest | 2-3 hours |
| License key system | 2-3 hours |
| Testing & polish | 4-6 hours |
| **Total** | **20-28 hours** |

**Timeline:** 3-5 days of focused work

---

## MVP Scope (v1.0)

Ship first with:
- [x] Auto-scoring on cell edit
- [x] Sidebar with score + red flags
- [x] 5 core red flag rules
- [x] Basic next step suggestions
- [ ] Email digest (v1.1)
- [ ] Pipeline dashboard (v1.1)
- [ ] License key system (v1.1 — start free)

**v1.0 = Free, get users**
**v1.1 = Add paid features**

---

## Sample Code: Scoring Engine

```javascript
// Code.gs

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MEDDPICC')
    .addItem('Open Scorecard', 'showSidebar')
    .addItem('Calculate All Scores', 'calculateAllScores')
    .addItem('Generate Report', 'generateReport')
    .addToUi();
}

function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('MEDDPICC Scorecard')
    .setWidth(350);
  SpreadsheetApp.getUi().showSidebar(html);
}

function calculateDealScore(row) {
  const sheet = SpreadsheetApp.getActiveSheet();

  // Column indices (adjust based on your sheet structure)
  const COLS = {
    M: 3, E: 4, D1: 5, D2: 6, P: 7, I: 8, C1: 9, C2: 10
  };

  // Weights (Champion and Pain weighted higher)
  const WEIGHTS = {
    M: 0.15,   // Metrics
    E: 0.15,   // Economic Buyer
    D1: 0.10,  // Decision Criteria
    D2: 0.10,  // Decision Process
    P: 0.05,   // Paper Process
    I: 0.20,   // Identify/Implicate Pain
    C1: 0.20,  // Champion
    C2: 0.05   // Competition
  };

  let weightedSum = 0;

  for (const [key, col] of Object.entries(COLS)) {
    const value = sheet.getRange(row, col).getValue() || 0;
    weightedSum += (value / 3) * WEIGHTS[key];
  }

  return Math.round(weightedSum * 100);
}

function getRedFlags(row) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const flags = [];

  const stage = sheet.getRange(row, 2).getValue();
  const champion = sheet.getRange(row, 9).getValue();
  const eb = sheet.getRange(row, 4).getValue();
  const pain = sheet.getRange(row, 8).getValue();
  const metrics = sheet.getRange(row, 3).getValue();
  const competition = sheet.getRange(row, 10).getValue();

  // No champion after Stage 2
  if (stage >= 2 && (!champion || champion === 0)) {
    flags.push({
      type: 'critical',
      message: 'No Champion identified',
      suggestion: 'Test your main contact for advocacy capability'
    });
  }

  // No EB after Stage 3
  if (stage >= 3 && (!eb || eb < 2)) {
    flags.push({
      type: 'critical',
      message: 'Economic Buyer not validated',
      suggestion: 'Ask: "Who signs the final contract?"'
    });
  }

  // Pain without Metrics
  if (pain >= 2 && (!metrics || metrics < 2)) {
    flags.push({
      type: 'warning',
      message: 'Pain identified but not quantified',
      suggestion: 'Ask: "What\'s the dollar impact of this problem?"'
    });
  }

  // No competition (suspicious)
  if (!competition || competition === 0) {
    flags.push({
      type: 'warning',
      message: 'Competition unknown',
      suggestion: 'Ask: "Who else are you evaluating?"'
    });
  }

  return flags;
}

function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const row = e.range.getRow();
  const col = e.range.getColumn();

  // Check if edit was in MEDDPICC columns (3-10)
  if (col >= 3 && col <= 10 && row > 1) {
    const score = calculateDealScore(row);
    sheet.getRange(row, 11).setValue(score); // Score column

    const flags = getRedFlags(row);
    const flagCount = flags.filter(f => f.type === 'critical').length;
    sheet.getRange(row, 12).setValue(flagCount > 0 ? '⚠️ ' + flagCount : '✓');

    // Update last modified
    sheet.getRange(row, 13).setValue(new Date());
  }
}
```

---

## Sidebar UI (Sidebar.html)

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      padding: 16px;
      color: #1e3a5f;
    }
    .score-circle {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 24px;
      font-size: 36px;
      font-weight: bold;
      color: white;
    }
    .score-high { background: linear-gradient(135deg, #10b981, #34d399); }
    .score-medium { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
    .score-low { background: linear-gradient(135deg, #ef4444, #f87171); }

    .section-title {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #d97706;
      margin: 24px 0 12px;
    }

    .flag {
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 8px;
    }
    .flag-critical {
      background: #fef2f2;
      border-left: 3px solid #ef4444;
    }
    .flag-warning {
      background: #fffbeb;
      border-left: 3px solid #f59e0b;
    }
    .flag-title {
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 4px;
    }
    .flag-suggestion {
      font-size: 13px;
      color: #64748b;
    }

    .next-step {
      padding: 12px;
      background: #f0fdf4;
      border-radius: 8px;
      border-left: 3px solid #10b981;
      margin-bottom: 8px;
    }

    .branding {
      text-align: center;
      font-size: 11px;
      color: #94a3b8;
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid #e2e8f0;
    }
  </style>
</head>
<body>
  <div id="app">
    <div class="score-circle score-high" id="scoreCircle">
      <span id="scoreValue">--</span>
    </div>

    <div class="section-title">Red Flags</div>
    <div id="flags"></div>

    <div class="section-title">Suggested Next Steps</div>
    <div id="suggestions"></div>

    <div class="branding">
      Powered by The CRO Report
    </div>
  </div>

  <script>
    function updateSidebar() {
      google.script.run
        .withSuccessHandler(function(data) {
          // Update score
          document.getElementById('scoreValue').textContent = data.score;
          const circle = document.getElementById('scoreCircle');
          circle.className = 'score-circle ' +
            (data.score >= 70 ? 'score-high' : data.score >= 40 ? 'score-medium' : 'score-low');

          // Update flags
          const flagsHtml = data.flags.map(f => `
            <div class="flag flag-${f.type}">
              <div class="flag-title">${f.message}</div>
              <div class="flag-suggestion">${f.suggestion}</div>
            </div>
          `).join('');
          document.getElementById('flags').innerHTML = flagsHtml || '<p style="color:#94a3b8">No red flags</p>';

          // Update suggestions
          const suggestionsHtml = data.suggestions.map(s => `
            <div class="next-step">${s}</div>
          `).join('');
          document.getElementById('suggestions').innerHTML = suggestionsHtml || '<p style="color:#94a3b8">Deal looks solid!</p>';
        })
        .getCurrentDealData();
    }

    // Update on load and every 5 seconds
    updateSidebar();
    setInterval(updateSidebar, 5000);
  </script>
</body>
</html>
```

---

## Go-to-Market

**Phase 1: Launch Free**
- Build MVP (scoring + sidebar + red flags)
- Post on LinkedIn, Product Hunt
- Get 100+ users, collect feedback

**Phase 2: Add Paid Features**
- Email digest
- Pipeline dashboard
- License key gating
- $9/mo or $79/year

**Phase 3: Enterprise**
- Team features
- Admin dashboard
- Custom scoring weights
- $29/user/mo

---

## Competitive Moat

1. **Not just a template** — active functionality
2. **Opinionated scoring** — based on CRO Report data
3. **Continuous updates** — new features, better suggestions
4. **Brand trust** — "by The CRO Report"
5. **Network effects** — if managers use it, AEs adopt it

---

*Spec created for The CRO Report — January 2026*
