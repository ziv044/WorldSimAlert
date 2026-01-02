# World Sim - UX Specification

## Game Description (For UI/UX Development)

**World Sim** is a real-time country management simulation. Players control a real nation (Israel) making strategic decisions across economy, military, and diplomacy. The game combines:
- **SimCity**: Economic management, budget allocation, infrastructure building
- **Red Alert**: Military unit purchasing, queuing, real-time operations on a map
- **Google Maps**: Real-world geography as the interactive battlefield/territory

---

## Screen Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TOP BAR - Key KPIs + Game Clock + Speed Controls                           │
├────────────────┬────────────────────────────────────────┬───────────────────┤
│                │                                        │                   │
│  LEFT PANEL    │         CENTER - WORLD MAP             │   RIGHT PANEL     │
│                │         (Google Maps Style)            │                   │
│  - Budget      │                                        │   - Military      │
│  - Economy     │    Real geography of your country      │     Inventory     │
│  - Sectors     │    and surrounding regions             │   - Build Queue   │
│  - Demographics│                                        │   - Operations    │
│                │    Click to select regions,            │   - Unit Stats    │
│                │    deploy units, view info             │                   │
│                │                                        │                   │
├────────────────┴────────────────────────────────────────┴───────────────────┤
│  BOTTOM BAR - Notifications / Events / Action Log                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## TOP BAR - Key Performance Indicators (KPIs)

Always visible. Shows critical metrics at a glance.

| KPI | Description | Format | Warning Threshold |
|-----|-------------|--------|-------------------|
| **GDP** | Total economic output | $XXX.X B | < 0% growth |
| **Treasury** | Available funds | $XX.X B | < $5B |
| **Debt** | National debt % of GDP | XX% | > 80% |
| **Population** | Total citizens | X.XX M | Declining |
| **Unemployment** | Jobless rate | X.X% | > 8% |
| **Approval** | Public satisfaction | XX% | < 40% |
| **Military Readiness** | Combat preparedness | Low/Normal/High/Max | Low |
| **Active Threats** | Ongoing conflicts/events | Count | > 0 |

**Game Clock Display:**
```
┌──────────────────────────────────┐
│  📅 March 15, 2024   ⏱️ 14:32   │
│  [⏸️] [▶️] [1x] [2x] [5x] [10x]  │
└──────────────────────────────────┘
```

---

## LEFT PANEL - Economy & Development

### Budget Tab
Manage national spending. Drag sliders or click +/- to adjust.

```
┌─ BUDGET ALLOCATION ─────────────┐
│ Total Revenue: $180.5B/year     │
│ Tax Rate: [====|====] 32%  [±]  │
├─────────────────────────────────┤
│ Defense        [████████░░] 18% │
│ Healthcare     [███████░░░] 15% │
│ Education      [██████░░░░] 12% │
│ Infrastructure [█████░░░░░] 10% │
│ Social Welfare [████░░░░░░]  9% │
│ R&D            [████░░░░░░]  8% │
│ ...                             │
├─────────────────────────────────┤
│ Surplus/Deficit: -$2.3B         │
│ [Apply Changes]                 │
└─────────────────────────────────┘
```

### Economy Tab
View economic health indicators.

```
┌─ ECONOMY ───────────────────────┐
│ GDP Growth      ▲ +2.3%         │
│ Inflation       ● 3.1%          │
│ Trade Balance   ▼ -$4.2B        │
│ Foreign Reserves  $185B         │
│ Credit Rating     A+            │
├─────────────────────────────────┤
│ GDP Breakdown by Sector:        │
│ ┌─────────────────────────┐     │
│ │ Tech 22% | Finance 18%  │     │
│ │ Defense 15% | Mfg 12%   │     │
│ └─────────────────────────┘     │
└─────────────────────────────────┘
```

### Sectors Tab
Invest in economic sectors (like SimCity zones).

```
┌─ SECTORS ───────────────────────┐
│ Click sector to invest          │
├─────────────────────────────────┤
│ 🖥️ Technology    Lv.72  [+$1B] │
│ 🏭 Manufacturing Lv.58  [+$1B] │
│ ⚡ Energy        Lv.65  [+$1B] │
│ 🏗️ Construction  Lv.51  [+$1B] │
│ 🎓 Education     Lv.68  [+$1B] │
│ 🏥 Healthcare    Lv.64  [+$1B] │
│ 🛡️ Defense Ind.  Lv.75  [+$1B] │
├─────────────────────────────────┤
│ Investment Cost: $1B = +2 Lv    │
│ Higher levels = more GDP output │
└─────────────────────────────────┘
```

### Infrastructure Tab
Build national infrastructure projects.

```
┌─ INFRASTRUCTURE ────────────────┐
│ 🔌 Power Plants     12/15       │
│ 🛣️ Highways         78%         │
│ 🚢 Ports            4/6         │
│ ✈️ Airports         3/4         │
│ 🎓 Universities     8/10        │
│ 🏥 Hospitals        85%         │
│ 🏭 Military Factories 5/8       │
├─────────────────────────────────┤
│ [Build New Project...]          │
│                                 │
│ In Progress:                    │
│ • Port Haifa Expansion (67%)    │
│ • Solar Farm North (23%)        │
└─────────────────────────────────┘
```

---

## CENTER - WORLD MAP

**Style**: Real-world geography like Google Maps, but with game overlays.

### Map Features
- **Terrain**: Satellite/terrain view of actual geography
- **Borders**: Country borders highlighted, your territory in distinct color
- **Cities**: Major cities marked with population indicators
- **Military Bases**: Icons showing base locations
- **Unit Positions**: Military units displayed on map
- **Threat Zones**: Red highlighting for hostile areas/conflicts

### Map Interactions
| Click | Action |
|-------|--------|
| **City** | View city stats, local economy, garrison |
| **Military Base** | View stationed units, readiness |
| **Enemy Territory** | View threat assessment, relations |
| **Empty Area** | Deploy units, start operation |
| **Your Unit** | Select unit, view stats, give orders |

### Map Overlays (Toggle)
- **Economic**: Heat map of GDP by region
- **Military**: Unit positions, ranges, threat levels
- **Infrastructure**: Roads, power grid, ports
- **Diplomatic**: Colored by relation status (ally/neutral/hostile)

```
┌─────────────────────────────────────────┐
│  [Satellite] [Terrain] [Political]      │
│  ☑️ Military  ☑️ Cities  ☐ Economic      │
├─────────────────────────────────────────┤
│                                         │
│         🏛️ Haifa                        │
│              ●                          │
│    ✈️ Base                 LEBANON      │
│     ▲▲▲              ─────────────      │
│            🏛️ Tel Aviv    ⚠️ SYRIA      │
│                 ●●●                     │
│    🏛️ Jerusalem                         │
│         ●●                              │
│              ⚓ Naval                    │
│                 Base        JORDAN      │
│                        ─────────────    │
│         EGYPT                           │
│                                         │
└─────────────────────────────────────────┘
```

---

## RIGHT PANEL - Military (Red Alert Style)

### Build Queue (Like Red Alert Sidebar)
Click to purchase units. Units queue and deliver over time.

```
┌─ BUILD MILITARY ────────────────┐
│ Defense Budget: $32.4B/year     │
│ Available: $8.2B                │
├─────────────────────────────────┤
│ ✈️ AIR FORCE                    │
│ ┌─────┬─────┬─────┬─────┐      │
│ │ F-35│F-15 │Drone│ SAM │      │
│ │$110M│ $65M│ $20M│ $85M│      │
│ │ +1  │ +1  │ +5  │ +1  │      │
│ └─────┴─────┴─────┴─────┘      │
│                                 │
│ 🚗 GROUND FORCES                │
│ ┌─────┬─────┬─────┬─────┐      │
│ │Tank │ APC │Arty │Iron │      │
│ │Merk.│Namer│ M109│Dome │      │
│ │ $6M │ $3M │ $5M │$50M │      │
│ │ +10 │ +20 │ +10 │ +1  │      │
│ └─────┴─────┴─────┴─────┘      │
│                                 │
│ ⚓ NAVY                         │
│ ┌─────┬─────┬─────┬─────┐      │
│ │Corv.│Sub  │Missle│Patrol│    │
│ │$320M│$500M│ Boat │ $45M│     │
│ │ +1  │ +1  │ +2   │ +4  │     │
│ └─────┴─────┴─────┴─────┘      │
└─────────────────────────────────┘
```

### Production Queue
Shows what's being built/delivered.

```
┌─ PRODUCTION QUEUE ──────────────┐
│ 🔨 Building:                    │
│ ├─ F-35 (1) ████████░░ 2.3 yrs │
│ ├─ Merkava (10) ██████░░ 0.8 yr│
│ └─ Iron Dome (2) ███░░░░ 1.5 yr│
│                                 │
│ 📦 Arriving Soon:               │
│ • 5x Hermes Drones - March 2024 │
│ • 20x Namer APC - June 2024     │
├─────────────────────────────────┤
│ Total on Order: $2.4B           │
│ [Cancel Order]                  │
└─────────────────────────────────┘
```

### Current Inventory
What you have available.

```
┌─ MILITARY INVENTORY ────────────┐
│ ✈️ Air Force                    │
│   F-35I Adir         50 ✓       │
│   F-15I Ra'am        84 ✓       │
│   F-16 variants     175 ✓       │
│   Hermes 900 Drones  45 ✓       │
│   Iron Dome Batteries 10 ✓      │
│                                 │
│ 🚗 Ground Forces                │
│   Merkava Mk4       360 ✓       │
│   Namer APC         200 ✓       │
│   M109 Artillery    600 ✓       │
│   Active Personnel  170K        │
│   Reserves         465K         │
│                                 │
│ ⚓ Navy                         │
│   Sa'ar Corvettes     4 ✓       │
│   Dolphin Subs        5 ✓       │
│   Missile Boats      11 ✓       │
└─────────────────────────────────┘
```

### Military Operations
Launch operations (like Red Alert attack orders).

```
┌─ OPERATIONS ────────────────────┐
│ Readiness: [NORMAL ▼]           │
│                                 │
│ Available Operations:           │
│ ┌─────────────────────────────┐ │
│ │ ✈️ Air Strike               │ │
│ │ Cost: 4 fighters + missiles │ │
│ │ Success: 75% | Losses: 5%   │ │
│ │ [Launch →]                  │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 🎯 Recon Mission            │ │
│ │ Cost: 2 drones              │ │
│ │ Success: 90% | Losses: 2%   │ │
│ │ [Launch →]                  │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ ⚓ Naval Patrol              │ │
│ │ Cost: 2 corvettes           │ │
│ │ Duration: 30 days           │ │
│ │ [Deploy →]                  │ │
│ └─────────────────────────────┘ │
│                                 │
│ 🔴 Active Operations: 2         │
│ • Air Patrol North (Day 12/30) │
│ • Naval Blockade (Day 5/60)    │
└─────────────────────────────────┘
```

---

## BOTTOM BAR - Events & Notifications

Shows real-time events, requires player response.

```
┌─ EVENTS & NOTIFICATIONS ────────────────────────────────────────────────────┐
│ 🔴 CRISIS: Border tensions with Lebanon escalating! [Respond]               │
│ 🟡 Economic: Q2 GDP report released: +2.1% growth                           │
│ 🟢 Military: F-35 delivery complete. 5 aircraft added to inventory.         │
│ 🔵 Diplomatic: USA requests joint military exercise. [Accept] [Decline]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Response Modal
When clicking [Respond]:

```
┌─ CRISIS RESPONSE ─────────────────────────────┐
│ ⚠️ BORDER TENSIONS - LEBANON                  │
│                                               │
│ Intelligence reports increased Hezbollah      │
│ activity near the northern border.            │
│                                               │
│ Current Relations: -45 (Hostile)              │
│ Threat Level: HIGH                            │
│                                               │
│ Your Options:                                 │
│ ┌───────────────────────────────────────────┐ │
│ │ 🛡️ Increase Border Patrols                │ │
│ │ Cost: $50M | Readiness +10%               │ │
│ │ Risk: Low | Relations: No change          │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ ✈️ Preemptive Air Strike                  │ │
│ │ Cost: $200M | Threat -40%                 │ │
│ │ Risk: Medium | Relations: -20 globally    │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ 🤝 Diplomatic Channel                     │ │
│ │ Cost: Political Capital                   │ │
│ │ Risk: High | May reduce tension           │ │
│ └───────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────┐ │
│ │ ⏳ Wait and Monitor                       │ │
│ │ Cost: None                                │ │
│ │ Risk: Tension may escalate                │ │
│ └───────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

---

## KPI Definitions (Complete Reference)

### Economic KPIs
| KPI | What It Measures | Affected By |
|-----|------------------|-------------|
| **GDP** | Total economic output ($B) | Sector levels, unemployment, infrastructure |
| **GDP Growth** | Annual % change | Investments, policies, global events |
| **Revenue** | Government income ($B/yr) | Tax rate × GDP |
| **Expenditure** | Government spending ($B/yr) | Budget allocations |
| **Deficit/Surplus** | Revenue - Expenditure | Budget balance |
| **Debt** | Accumulated borrowing (% GDP) | Deficits over time |
| **Inflation** | Price increase rate (%) | Money supply, spending |
| **Trade Balance** | Exports - Imports | Sector productivity, relations |
| **Reserves** | Foreign currency held ($B) | Trade, borrowing |
| **Credit Rating** | Borrowing trustworthiness | Debt level, stability |

### Demographic KPIs
| KPI | What It Measures | Affected By |
|-----|------------------|-------------|
| **Population** | Total citizens (M) | Birth/death rates, migration |
| **Working Age** | Employable population | Demographics |
| **Unemployment** | Jobless rate (%) | Economy, sector levels |
| **Workforce Pools** | Specialized labor available | Education, sector development |
| **Happiness** | Public satisfaction (%) | Services, economy, events |

### Military KPIs
| KPI | What It Measures | Affected By |
|-----|------------------|-------------|
| **Readiness** | Combat preparedness level | Training, supplies, morale |
| **Personnel** | Active + Reserve soldiers | Budget, recruitment |
| **Equipment Count** | Units by type | Procurement, losses |
| **Operational Status** | % forces deployable | Maintenance, readiness |
| **Munitions** | Ammo/missile stockpiles | Production, usage |

### Diplomatic KPIs
| KPI | What It Measures | Affected By |
|-----|------------------|-------------|
| **Relations Score** | Bilateral relationship (-100 to +100) | Actions, treaties, history |
| **Trade Agreements** | Active trade deals | Diplomacy |
| **Military Alliances** | Defense pacts | Relations, treaties |
| **Global Standing** | International reputation | Actions, diplomacy |

---

## Interaction Patterns

### Red Alert Style Building
1. **Click unit icon** in sidebar → Highlights, shows tooltip with stats
2. **Click again** → Adds to production queue (if funds available)
3. **Right-click** → Cancel/remove from queue
4. **Drag** → Reorder queue priority
5. **Progress bar** fills as unit is produced/delivered

### Map Interactions
1. **Left-click** → Select (city, unit, base)
2. **Right-click** → Context menu (move, attack, patrol)
3. **Drag box** → Multi-select units
4. **Scroll wheel** → Zoom in/out
5. **Middle-drag** → Pan map
6. **Double-click unit** → Center and follow

### Time Controls
- **Spacebar** → Pause/Resume
- **1-4 keys** → Speed settings
- **Events auto-pause** → Critical events pause game for response

---

## Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark navy | #0a1929 |
| Panel BG | Dark blue-gray | #132f4c |
| Primary text | White | #ffffff |
| Secondary text | Light gray | #b2bac2 |
| Accent/Highlight | Blue | #1976d2 |
| Success/Positive | Green | #2e7d32 |
| Warning | Orange | #ed6c02 |
| Danger/Negative | Red | #d32f2f |
| Your territory | Blue tint | #1565c0 |
| Enemy territory | Red tint | #c62828 |
| Neutral | Gray | #757575 |

---

## Summary for UI Developer

Build a **real-time strategy game UI** with:

1. **Top bar**: Critical KPIs always visible + game clock with pause/speed
2. **Left panel**: Economic management (budget sliders, sector investments, infrastructure)
3. **Center**: Interactive world map (Google Maps style) showing real geography, units, cities
4. **Right panel**: Red Alert-style military sidebar (click to build, queue system, inventory)
5. **Bottom bar**: Event notifications with response buttons

**Key interactions**:
- Click-to-build military units
- Drag sliders for budget allocation
- Click map to deploy/command units
- Respond to events via modal dialogs
- Real-time updates as game clock advances
