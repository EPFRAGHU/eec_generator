# EPFO EEC-2026 Generator — Design System

**Product:** EPFO EEC-2026 Return File Generator  
**Audience:** Payroll officers, HR teams, compliance professionals  
**Tone:** Professional, trustworthy, efficient, government-compliant  
**Brand:** Clean, institutional, precise — not playful

---

## Color Palette

### Primary (EPFO Institutional Blue)
| Role | Hex | Usage |
|------|-----|-------|
| Primary 600 | `#1E4A8C` | Primary buttons, headers, key actions |
| Primary 700 | `#163A6E` | Hover states, emphasis |
| Primary 500 | `#2A5DB0` | Focus rings, links |
| Primary 100 | `#E8F0FA` | Subtle backgrounds, selected states |

### Secondary (Compliance Green)
| Role | Hex | Usage |
|------|-----|-------|
| Secondary 600 | `#0D7A3F` | Success states, download buttons |
| Secondary 100 | `#E8F7ED` | Success messages, completed steps |

### Neutral (Slate)
| Role | Hex | Usage |
|------|-----|-------|
| Neutral 950 | `#0F172A` | Primary text, headers |
| Neutral 700 | `#334155` | Body text, labels |
| Neutral 500 | `#64748B` | Placeholders, secondary text |
| Neutral 300 | `#CBD5E1` | Borders, dividers |
| Neutral 100 | `#F1F5F9` | Card backgrounds, input backgrounds |
| Neutral 50 | `#F8FAFC` | Page background |
| White | `#FFFFFF` | Card surfaces, modals |

### Semantic
| Role | Hex | Usage |
|------|-----|-------|
| Error 600 | `#DC2626` | Errors, destructive actions |
| Error 100 | `#FEF2F2` | Error backgrounds |
| Warning 600 | `#D97706` | Warnings, pending states |
| Warning 100 | `#FFFBEB` | Warning backgrounds |
| Info 600 | `#2563EB` | Info messages, links |

---

## Typography

### Font Stack
```
Primary: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
Mono: "JetBrains Mono", "Fira Code", Consolas, monospace
```

### Scale
| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| Display | 32px | 700 | 1.2 | Page title |
| H1 | 24px | 700 | 1.3 | Section headers |
| H2 | 20px | 600 | 1.4 | Subsection headers |
| H3 | 16px | 600 | 1.5 | Card titles, table headers |
| Body | 14px | 400 | 1.6 | Default text |
| Body-sm | 13px | 400 | 1.5 | Captions, hints |
| Caption | 12px | 400 | 1.5 | Metadata, timestamps |
| Mono | 13px | 400 | 1.6 | Code, UANs, numbers |

---

## Spacing System (4px base)

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight gaps |
| space-2 | 8px | Standard gaps |
| space-3 | 12px | Form fields |
| space-4 | 16px | Card padding, section gaps |
| space-5 | 20px | Larger gaps |
| space-6 | 24px | Section padding |
| space-8 | 32px | Page margins |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| radius-sm | 4px | Inputs, badges |
| radius-md | 8px | Cards, buttons |
| radius-lg | 12px | Modals, panels |
| radius-full | 9999px | Pills, avatars |

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| shadow-sm | `0 1px 2px rgba(15,23,42,0.05)` | Cards, inputs |
| shadow-md | `0 4px 6px -1px rgba(15,23,42,0.1)` | Elevated cards, dropdowns |
| shadow-lg | `0 10px 15px -3px rgba(15,23,42,0.1)` | Modals, popovers |

---

## Components

### Button
```css
.btn-primary {
  background: #1E4A8C;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.15s ease;
}
.btn-primary:hover { background: #163A6E; }
.btn-primary:focus { box-shadow: 0 0 0 3px rgba(30,74,140,0.3); }

.btn-secondary {
  background: #0D7A3F;
  color: white;
  ...
}

.btn-ghost {
  background: transparent;
  color: #1E4A8C;
  border: 1px solid #1E4A8C;
}
```

### Card
```css
.card {
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(15,23,42,0.05);
}
```

### Input
```css
.input {
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  transition: border 0.15s, box-shadow 0.15s;
}
.input:focus {
  border-color: #2A5DB0;
  box-shadow: 0 0 0 3px rgba(30,74,140,0.15);
}
```

### KPI Card
```css
.kpi-card {
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 20px;
}
.kpi-value { font-size: 28px; font-weight: 700; color: #0F172A; }
.kpi-label { font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
```

### Table / Data Grid
```css
.data-table {
  border-collapse: collapse;
  width: 100%;
}
.data-table th {
  background: #F8FAFC;
  border-bottom: 2px solid #E2E8F0;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748B;
}
.data-table td {
  border-bottom: 1px solid #F1F5F9;
  padding: 12px 16px;
  font-size: 13px;
}
.data-table tr:hover td { background: #F8FAFC; }
```

### Badge / Status Pill
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.badge-success { background: #E8F7ED; color: #0D7A3F; }
.badge-warning { background: #FFFBEB; color: #D97706; }
.badge-info { background: #E8F0FA; color: #1E4A8C; }
.badge-error { background: #FEF2F2; color: #DC2626; }
```

---

## Layout

### Page Structure
```
┌─────────────────────────────────────────────────────┐
│ Header (64px) — Logo, Title, User, Actions         │
├──────────────┬──────────────────────────────────────┤
│ Sidebar      │ Main Content (max-width 1200px)      │
│ (280px)      │                                      │
│ Navigation   │  Section → Card → Card               │
│ Filters      │  KPI Row → Data Grid → Actions       │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

### Responsive Breakpoints
| Breakpoint | Width | Behavior |
|------------|-------|----------|
| Mobile | < 640px | Sidebar → drawer, stacked KPIs, horizontal scroll table |
| Tablet | 640–1024px | Sidebar collapsible, 2-col KPI grid |
| Desktop | > 1024px | Full layout |

---

## Motion

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| fast | 150ms | ease-out | Hover, focus, simple transitions |
| normal | 250ms | ease-out | Panel expand, modal enter |
| slow | 350ms | ease-out | Page transitions, complex animations |

---

## Accessibility

- **Contrast:** All text meets WCAG AA (4.5:1), UI elements 3:1
- **Focus:** Visible focus rings on all interactive elements
- **Keyboard:** Full keyboard navigation, logical tab order
- **Screen readers:** Semantic HTML, ARIA labels on icon-only buttons
- **Reduced motion:** Respects `prefers-reduced-motion`

---

## Streamlit Implementation Notes

Since Streamlit limits CSS customization, we inject styles via `st.markdown(unsafe_allow_html=True)` and use:
- Custom CSS for colors, spacing, typography
- `st.columns`, `st.container`, `st.expander` for layout
- `st.data_editor` with `column_config` for tables
- Custom components via `streamlit-components` if needed

Key classes to target:
- `.stApp` — page root
- `.stSidebar` — sidebar
- `.stButton > button` — buttons
- `.stTextInput > div > input` — inputs
- `.stSelectbox > div` — selects
- `[data-testid="stMetric"]` — metric cards
- `[data-testid="stDataFrame"]` — dataframes
- `.stTabs [data-baseweb="tab"]` — tabs

---

## Design Tokens (CSS Variables for Injection)

```css
:root {
  --color-primary: #1E4A8C;
  --color-primary-hover: #163A6E;
  --color-primary-light: #E8F0FA;
  --color-secondary: #0D7A3F;
  --color-secondary-light: #E8F7ED;
  --color-error: #DC2626;
  --color-error-light: #FEF2F2;
  --color-warning: #D97706;
  --color-warning-light: #FFFBEB;
  --color-text: #0F172A;
  --color-text-secondary: #64748B;
  --color-border: #E2E8F0;
  --color-bg: #F8FAFC;
  --color-surface: #FFFFFF;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-sm: 0 1px 2px rgba(15,23,42,0.05);
  --shadow-md: 0 4px 6px -1px rgba(15,23,42,0.1);
  --shadow-lg: 0 10px 15px -3px rgba(15,23,42,0.1);
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
}
```