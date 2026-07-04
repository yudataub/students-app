# מדור ניקוד התנהגות — תוכנית יישום

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** להוסיף מדור בתוך `index.html` שמאפשר למורה לתת לכל תלמיד נקודות טובות/רעות (מרשימת התנהגויות ניתנת לעריכה, כל אחת עם אמוג'י), לספור אותן, לראות יומן מלא, ולמיין תלמידים לפי שם או לפי ניקוד.

**Architecture:** האפליקציה כולה קובץ HTML יחיד (`index.html`, ~5200 שורות: `<style>` אחד, HTML views אחד ליד השני, ו-`<script>` אחד עם כל הלוגיקה). התכונה החדשה מתווספת באותו דפוס בדיוק כמו "גלריה" הקיימת: state גלובלי + פונקציית `showX(cls)` שממלאת container ומפעילה `showView()`, כרטיסי תלמיד ברשת `gallery-grid`, ו-overlay-ים בסגנון `.settings-overlay` הקיים. אין קבצים חדשים.

**Tech Stack:** HTML/CSS/JS וניל, ללא build tool, ללא framework, נתונים ב-`localStorage`.

**הערה לגבי בדיקות:** בריפו הזה אין test suite אוטומטי (אין `package.json`, אין תיקיית tests) — כל הפיצ'רים הקיימים נבדקו ידנית בדפדפן. בהתאם, כל שלב "בדיקה" כאן הוא בדיקה ידנית: פתיחת `index.html` בדפדפן (למשל `python -m http.server 8080` מתיקיית הריפו ואז `http://localhost:8080/`, או פתיחה ישירה של הקובץ), ולעיתים הרצת פקודה ב-DevTools Console. זה תואם את המוסכמה הקיימת בקוד.

---

## Task 1: מודל נתונים — רשימת התנהגויות + יומן לתלמיד + פונקציות ניקוד

**Files:**
- Modify: `index.html:1342-1344` (state גלובלי בתחילת ה-script)

- [ ] **Step 1: הוסף מיגרציה ל-`behaviorLog` על כל תלמיד קיים**

מצא בקובץ:
```js
let students = JSON.parse(localStorage.getItem('students') || '[]');
students.forEach(s => { if (s.className === undefined) s.className = ''; });
let importedNamesMap = JSON.parse(localStorage.getItem('importedNamesMap') || '{}');
```

והחלף ב:
```js
let students = JSON.parse(localStorage.getItem('students') || '[]');
students.forEach(s => { if (s.className === undefined) s.className = ''; });
students.forEach(s => { if (!s.behaviorLog) s.behaviorLog = []; });
let importedNamesMap = JSON.parse(localStorage.getItem('importedNamesMap') || '{}');

const DEFAULT_BEHAVIOR_TYPES = [
    { id: 'good-hw',     emoji: '✅', label: 'הגיש שיעורי בית',   kind: 'good' },
    { id: 'good-part',   emoji: '🙋', label: 'השתתפות פעילה',     kind: 'good' },
    { id: 'good-help',   emoji: '🤝', label: 'עזר לחבר',           kind: 'good' },
    { id: 'good-gear',   emoji: '📚', label: 'הביא ציוד לשיעור',   kind: 'good' },
    { id: 'good-star',   emoji: '🌟', label: 'התנהגות למופת',      kind: 'good' },
    { id: 'bad-noise',   emoji: '🗣️', label: 'הפריע בשיעור',       kind: 'bad'  },
    { id: 'bad-phone',   emoji: '📵', label: 'טלפון בשיעור',       kind: 'bad'  },
    { id: 'bad-sleep',   emoji: '😴', label: 'לא הקשיב / ישן',     kind: 'bad'  },
    { id: 'bad-nohw',    emoji: '❌', label: 'לא הגיש שיעורי בית', kind: 'bad'  },
    { id: 'bad-respect', emoji: '🚫', label: 'חוסר כבוד',          kind: 'bad'  },
];
let behaviorTypes = JSON.parse(localStorage.getItem('behaviorTypes') || 'null') || DEFAULT_BEHAVIOR_TYPES.map(t => ({ ...t }));
function saveBehaviorTypes() { localStorage.setItem('behaviorTypes', JSON.stringify(behaviorTypes)); }
function goodCount(s) { return (s.behaviorLog || []).filter(e => e.kind === 'good').length; }
function badCount(s)  { return (s.behaviorLog || []).filter(e => e.kind === 'bad').length; }
function netScore(s)  { return goodCount(s) - badCount(s); }
```

- [ ] **Step 2: בדיקה ידנית**

פתח את `index.html` בדפדפן, פתח DevTools Console, הרץ:
```js
behaviorTypes.length
```
Expected: `10`

```js
behaviorTypes.filter(t => t.kind === 'good').length
```
Expected: `5`

```js
localStorage.getItem('behaviorTypes') !== null
```
Expected: `true` (כלומר `saveBehaviorTypes` לא רץ עדיין אוטומטית בטעינה — זה צפוי; ה-seed נשמר רק בזיכרון עד לפעולה ראשונה. אם expected שונה, זה עדיין תקין — הבדיקה החשובה היא ש-`behaviorTypes.length === 10`.)

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "הוספת מודל נתונים לניקוד התנהגות: רשימת סוגים + יומן לתלמיד"
```

---

## Task 2: HTML — מסכים חדשים (רשימה + פרופיל) ו-overlays

**Files:**
- Modify: `index.html:768` (אחרי סגירת `<!-- GALLERY -->`)
- Modify: `index.html:1187` (אחרי סגירת `missing-overlay`)

- [ ] **Step 1: הוסף שני views חדשים אחרי הגלריה**

מצא:
```html
    <!-- GALLERY -->
    <div id="view-gallery" class="view">
        <div id="gallery-content"></div>
    </div>

    <!-- STUDENT DETAIL -->
```

והחלף ב:
```html
    <!-- GALLERY -->
    <div id="view-gallery" class="view">
        <div id="gallery-content"></div>
    </div>

    <!-- BEHAVIOR LIST -->
    <div id="view-behavior" class="view">
        <div id="behavior-content"></div>
    </div>

    <!-- BEHAVIOR DETAIL -->
    <div id="view-behaviorDetail" class="view">
        <img id="bd-photo" class="student-detail-photo" alt="">
        <div class="detail-name" id="bd-name" style="margin-bottom:14px;"></div>
        <div class="stats-row">
            <div class="stat-box correct">
                <div class="stat-num" id="bd-good">0</div>
                <div class="stat-label">✅ נקודות טובות</div>
            </div>
            <div class="stat-box wrong">
                <div class="stat-num" id="bd-bad">0</div>
                <div class="stat-label">🚩 נקודות רעות</div>
            </div>
        </div>
        <button class="menu-btn btn-add" style="margin-bottom:10px;width:100%;" onclick="openAddPointPicker()">
            <span class="icon">➕</span> הוסף נקודה
        </button>
        <button class="menu-btn btn-gallery" style="margin-bottom:14px;width:100%;" onclick="toggleBehaviorLog()">
            <span class="icon">📋</span> <span id="bd-log-toggle-label">הצג פירוט</span>
        </button>
        <div id="bd-log-list" style="display:none;"></div>
    </div>

    <!-- STUDENT DETAIL -->
```

חשוב: ה-`id` של view הפרופיל הוא `view-behaviorDetail` (אות גדולה D) כדי להתאים לשם ה-view `'behaviorDetail'` שישמש בקריאות ל-`showView('behaviorDetail', ...)` (הפונקציה בונה את ה-id בתור `'view-' + name`).

- [ ] **Step 2: הוסף שני overlays חדשים אחרי `missing-overlay`**

מצא (סוף ה-overlay `missing-overlay`):
```html
            <button onclick="closeMissingOverlay()" style="margin-top:8px;width:100%;padding:10px;background:#f3f4f6;color:#374151;border:none;border-radius:10px;font-family:inherit;font-size:0.88rem;cursor:pointer;">סגור</button>
        </div>
    </div>

    <!-- LAST NAME IMPORT MODAL -->
```

והחלף ב:
```html
            <button onclick="closeMissingOverlay()" style="margin-top:8px;width:100%;padding:10px;background:#f3f4f6;color:#374151;border:none;border-radius:10px;font-family:inherit;font-size:0.88rem;cursor:pointer;">סגור</button>
        </div>
    </div>

    <!-- ADD BEHAVIOR POINT -->
    <div class="settings-overlay" id="add-point-overlay" onclick="if(event.target===this)closeAddPointPicker()">
        <div style="background:white;border-radius:20px;padding:20px;max-width:380px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3);max-height:85vh;display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <div style="font-weight:800;font-size:1rem;">➕ הוסף נקודה</div>
                <button onclick="closeAddPointPicker()" style="background:none;border:none;font-size:1.3rem;cursor:pointer;color:#9ca3af;line-height:1;">✕</button>
            </div>
            <div id="add-point-list" style="overflow-y:auto;flex:1;"></div>
        </div>
    </div>

    <!-- MANAGE BEHAVIOR TYPES -->
    <div class="settings-overlay" id="behavior-types-overlay" onclick="if(event.target===this)closeBehaviorTypesEditor()">
        <div style="background:white;border-radius:20px;padding:20px;max-width:380px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3);max-height:85vh;display:flex;flex-direction:column;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <div style="font-weight:800;font-size:1rem;">⚙️ עריכת רשימת התנהגויות</div>
                <button onclick="closeBehaviorTypesEditor()" style="background:none;border:none;font-size:1.3rem;cursor:pointer;color:#9ca3af;line-height:1;">✕</button>
            </div>
            <div id="behavior-types-list" style="overflow-y:auto;flex:1;"></div>
            <div style="border-top:1px solid #f3f4f6;margin-top:12px;padding-top:12px;">
                <div style="display:flex;gap:8px;margin-bottom:8px;">
                    <input type="text" id="bt-new-emoji" placeholder="😀" maxlength="4" style="width:56px;text-align:center;font-size:1.3rem;padding:8px;border:1.5px solid #e5e7eb;border-radius:8px;box-sizing:border-box;">
                    <input type="text" id="bt-new-label" placeholder="תיאור ההתנהגות..." style="flex:1;padding:8px 10px;border:1.5px solid #e5e7eb;border-radius:8px;font-family:inherit;font-size:0.9rem;direction:rtl;box-sizing:border-box;">
                </div>
                <div style="display:flex;gap:8px;margin-bottom:8px;">
                    <label style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:8px;border:1.5px solid #bbf7d0;border-radius:8px;cursor:pointer;background:#f0fdf4;">
                        <input type="radio" name="bt-new-kind" value="good" checked> ✅ טובה
                    </label>
                    <label style="flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:8px;border:1.5px solid #fecaca;border-radius:8px;cursor:pointer;background:#fef2f2;">
                        <input type="radio" name="bt-new-kind" value="bad"> 🚩 רעה
                    </label>
                </div>
                <button onclick="addBehaviorType()" style="width:100%;padding:10px;background:#3b82f6;color:white;border:none;border-radius:10px;font-family:inherit;font-size:0.88rem;font-weight:700;cursor:pointer;">💾 הוסף</button>
            </div>
        </div>
    </div>

    <!-- LAST NAME IMPORT MODAL -->
```

- [ ] **Step 3: בדיקה ידנית**

פתח את `index.html` בדפדפן. Expected: העמוד נטען כרגיל ללא שגיאות ב-Console (ה-views/overlays החדשים מוסתרים כברירת מחדל כי אין להם class `active`/`open`).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "הוספת מסכי HTML למדור ניקוד התנהגות (רשימה, פרופיל, ועריכת סוגים)"
```

---

## Task 3: מסך רשימה — `showBehaviorList` + מיון + כרטיס תלמיד

**Files:**
- Modify: `index.html` — הוסף פונקציות מיד אחרי `makeStudentCard` (סוף בלוק ה-GALLERY ב-JS, לפני ההערה `// ===== DETAIL =====`)

- [ ] **Step 1: הוסף את בלוק ה-JS**

מצא:
```js
function makeStudentCard(s) {
    const total = s.correct + s.wrong;
    const pct   = total > 0 ? Math.round(s.correct / total * 100) + '%' : 'טרם נבחן';
    const card  = document.createElement('div');
    card.className = 'student-card';
    const emojiBadge = s.emoji ? `<div class="card-emoji-badge" onclick="event.stopPropagation();showEmojiPopupFor('${s.id}')">${s.emoji}</div>` : '';
    card.innerHTML = `${emojiBadge}<img src="${s.photo}" alt="${s.name}"><div class="card-name">${s.name}</div><div class="card-stats">${pct}</div>`;
    card.onclick = () => showDetail(s.id);
    return card;
}

// ===== DETAIL =====
```

והחלף ב:
```js
function makeStudentCard(s) {
    const total = s.correct + s.wrong;
    const pct   = total > 0 ? Math.round(s.correct / total * 100) + '%' : 'טרם נבחן';
    const card  = document.createElement('div');
    card.className = 'student-card';
    const emojiBadge = s.emoji ? `<div class="card-emoji-badge" onclick="event.stopPropagation();showEmojiPopupFor('${s.id}')">${s.emoji}</div>` : '';
    card.innerHTML = `${emojiBadge}<img src="${s.photo}" alt="${s.name}"><div class="card-name">${s.name}</div><div class="card-stats">${pct}</div>`;
    card.onclick = () => showDetail(s.id);
    return card;
}

// ===== BEHAVIOR POINTS =====
let currentBehaviorClass;      // undefined = all, null = no class, string = specific class name
let behaviorSortMode = 'name'; // 'name' | 'score'
let currentBehaviorStudentId = null;

function sortBehaviorStudents(arr) {
    const byFirstName = (a, b) => a.name.trim().split(/\s+/)[0].localeCompare(b.name.trim().split(/\s+/)[0], 'he');
    if (behaviorSortMode === 'score') {
        return [...arr].sort((a, b) => (netScore(b) - netScore(a)) || byFirstName(a, b));
    }
    return [...arr].sort(byFirstName);
}

function makeBehaviorCard(s) {
    const card = document.createElement('div');
    card.className = 'student-card';
    card.innerHTML = `<img src="${s.photo}" alt="${s.name}"><div class="card-name">${s.name}</div><div class="card-stats">✅ ${goodCount(s)}　🚩 ${badCount(s)}</div>`;
    card.onclick = () => showBehaviorDetail(s.id);
    return card;
}

function showBehaviorList(cls) {
    currentBehaviorClass = cls;
    const isAll  = cls === undefined;
    const isNone = cls === null;
    const filtered = isAll ? students : isNone ? students.filter(s => !s.className) : students.filter(s => s.className === cls);
    const title  = isAll ? '🏆 ניקוד — כל התלמידים' : isNone ? '🏆 ניקוד — ללא כיתה' : `🏆 ניקוד — ${cls}`;

    const cont = document.getElementById('behavior-content');
    cont.innerHTML = '';

    const toolbar = document.createElement('div');
    toolbar.style.cssText = 'display:flex;gap:8px;margin-bottom:12px;';
    const editBtn = document.createElement('button');
    editBtn.style.cssText = 'background:#6b7280;color:white;padding:10px 12px;border-radius:10px;border:none;cursor:pointer;font-family:inherit;font-size:0.82rem;font-weight:700;flex:1;';
    editBtn.innerHTML = '⚙️ ערוך רשימת התנהגויות';
    editBtn.onclick = () => openBehaviorTypesEditor();
    toolbar.appendChild(editBtn);
    cont.appendChild(toolbar);

    const sortBar = document.createElement('div');
    sortBar.style.cssText = 'display:flex;align-items:center;gap:6px;margin-bottom:12px;';
    const sortLabel = document.createElement('span');
    sortLabel.style.cssText = 'font-size:0.75rem;color:#9ca3af;font-weight:700;flex-shrink:0;';
    sortLabel.textContent = 'מיון:';
    sortBar.appendChild(sortLabel);
    [['name', 'א-ב'], ['score', 'לפי ניקוד']].forEach(([mode, label]) => {
        const btn = document.createElement('button');
        const active = behaviorSortMode === mode;
        btn.style.cssText = `padding:5px 10px;border-radius:8px;border:1.5px solid ${active ? '#3b82f6' : '#e5e7eb'};background:${active ? '#eff6ff' : 'white'};color:${active ? '#1d4ed8' : '#6b7280'};font-size:0.78rem;font-weight:${active ? '700' : '500'};cursor:pointer;font-family:inherit;`;
        btn.textContent = label;
        btn.onclick = () => { behaviorSortMode = mode; showBehaviorList(cls); };
        sortBar.appendChild(btn);
    });
    cont.appendChild(sortBar);

    if (filtered.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'empty-state';
        emptyDiv.innerHTML = '<div class="empty-icon">🏆</div><div>אין תלמידים בקטגוריה זו</div>';
        cont.appendChild(emptyDiv);
    } else {
        const grid = document.createElement('div');
        grid.className = 'gallery-grid';
        sortBehaviorStudents(filtered).forEach(s => grid.appendChild(makeBehaviorCard(s)));
        cont.appendChild(grid);
    }
    showView('behavior', title);
}

// ===== DETAIL =====
```

- [ ] **Step 2: הוסף `behavior` ל-titles map כדי שיהיה כותרת ברירת מחדל תקינה**

מצא (ליד תחילת `showView`):
```js
    const titles = { home:'🎓 זוכר שמות', add:'➕ הוסף תלמיד', bulk:'📁 העלאת קבוצה', gallery:'📋 תלמידים', detail:'👤 פרופיל', quiz:'📝 מבחן', rquiz:'🔍 מצא בתמונה', mquiz:'✍️ מבחן זיכרון', summary:'📊 תוצאות', classroom:'🏫 סידור כיתה' };
```

והחלף ב:
```js
    const titles = { home:'🎓 זוכר שמות', add:'➕ הוסף תלמיד', bulk:'📁 העלאת קבוצה', gallery:'📋 תלמידים', detail:'👤 פרופיל', quiz:'📝 מבחן', rquiz:'🔍 מצא בתמונה', mquiz:'✍️ מבחן זיכרון', summary:'📊 תוצאות', classroom:'🏫 סידור כיתה', behavior:'🏆 ניקוד התנהגות', behaviorDetail:'👤 ניקוד תלמיד' };
```

- [ ] **Step 3: בדיקה ידנית**

פתח את `index.html` בדפדפן (וודא שיש לפחות תלמיד אחד ברשימה — אם לא, הוסף אחד דרך "הוסף תלמיד"). ב-DevTools Console הרץ:
```js
showBehaviorList(undefined)
```
Expected: המסך עובר למסך חדש עם כותרת "🏆 ניקוד — כל התלמידים", כפתור "⚙️ ערוך רשימת התנהגויות", שורת מיון עם "א-ב" ו"לפי ניקוד", ורשת עם כרטיס לכל תלמיד שמציג `✅ 0　🚩 0`. לחיצה על "לפי ניקוד" לא זורקת שגיאה בקונסול.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "הוספת מסך רשימה למדור ניקוד התנהגות עם מיון ורשת כרטיסים"
```

---

## Task 4: מסך פרופיל תלמיד — ניקוד + יומן + מחיקת רשומה

**Files:**
- Modify: `index.html` — הוסף פונקציות מיד אחרי הבלוק שנוסף ב-Task 3 (לפני `// ===== DETAIL =====`)

- [ ] **Step 1: הוסף את בלוק ה-JS**

מצא (סוף הבלוק שנוסף ב-Task 3):
```js
    showView('behavior', title);
}

// ===== DETAIL =====
```

והחלף ב:
```js
    showView('behavior', title);
}

function showBehaviorDetail(id) {
    const s = students.find(x => x.id === id);
    if (!s) return;
    currentBehaviorStudentId = id;
    document.getElementById('bd-photo').src = s.photo;
    document.getElementById('bd-name').textContent = s.name;
    document.getElementById('bd-good').textContent = goodCount(s);
    document.getElementById('bd-bad').textContent = badCount(s);
    document.getElementById('bd-log-list').style.display = 'none';
    document.getElementById('bd-log-toggle-label').textContent = 'הצג פירוט';
    renderBehaviorLog(s);
    showView('behaviorDetail', `👤 ${s.name}`);
}

function toggleBehaviorLog() {
    const listEl = document.getElementById('bd-log-list');
    const isOpen = listEl.style.display !== 'none';
    listEl.style.display = isOpen ? 'none' : 'block';
    document.getElementById('bd-log-toggle-label').textContent = isOpen ? 'הצג פירוט' : 'הסתר פירוט';
}

function renderBehaviorLog(s) {
    const listEl = document.getElementById('bd-log-list');
    listEl.innerHTML = '';
    const entries = [...(s.behaviorLog || [])].sort((a, b) => b.ts - a.ts);
    if (entries.length === 0) {
        listEl.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><div>אין רשומות עדיין</div></div>';
        return;
    }
    entries.forEach(e => {
        const row = document.createElement('div');
        row.className = 'missing-item';
        const dateStr = new Date(e.ts).toLocaleDateString('he-IL');
        const nameCell = document.createElement('div');
        nameCell.className = 'missing-item-name';
        nameCell.innerHTML = `${e.emoji} ${e.label} <span style="color:#9ca3af;font-weight:400;font-size:0.8rem;">— ${dateStr}</span>`;
        const delBtn = document.createElement('button');
        delBtn.className = 'missing-add-btn';
        delBtn.style.cssText = 'color:#ef4444;background:#fef2f2;border-color:#fecaca;';
        delBtn.textContent = '🗑️';
        delBtn.onclick = () => deleteBehaviorLogEntry(e.id);
        row.appendChild(nameCell);
        row.appendChild(delBtn);
        listEl.appendChild(row);
    });
}

function deleteBehaviorLogEntry(entryId) {
    const s = students.find(x => x.id === currentBehaviorStudentId);
    if (!s) return;
    if (!confirm('למחוק את הרשומה?')) return;
    s.behaviorLog = (s.behaviorLog || []).filter(e => e.id !== entryId);
    saveData();
    document.getElementById('bd-good').textContent = goodCount(s);
    document.getElementById('bd-bad').textContent = badCount(s);
    renderBehaviorLog(s);
}

// ===== DETAIL =====
```

- [ ] **Step 2: בדיקה ידנית**

ב-Console (אחרי `showBehaviorList(undefined)` מ-Task 3):
```js
showBehaviorDetail(students[0].id)
```
Expected: מעבר למסך פרופיל עם תמונת/שם התלמיד הראשון, `✅ 0` ו-`🚩 0`, כפתור "➕ הוסף נקודה" (לא עושה כלום עדיין — ייבנה ב-Task 5), וכפתור "📋 הצג פירוט". לחיצה על "הצג פירוט" מציגה "אין רשומות עדיין" והטקסט בכפתור משתנה ל"הסתר פירוט"; לחיצה נוספת מסתירה שוב.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "הוספת מסך פרופיל ניקוד: סיכום, יומן ומחיקת רשומה"
```

---

## Task 5: הוספת נקודה — בורר התנהגויות

**Files:**
- Modify: `index.html` — הוסף פונקציות מיד אחרי הבלוק שנוסף ב-Task 4 (לפני `// ===== DETAIL =====`)

- [ ] **Step 1: הוסף את בלוק ה-JS**

מצא (סוף הבלוק שנוסף ב-Task 4):
```js
    renderBehaviorLog(s);
}

// ===== DETAIL =====
```

והחלף ב:
```js
    renderBehaviorLog(s);
}

function openAddPointPicker() {
    const listEl = document.getElementById('add-point-list');
    listEl.innerHTML = '';
    ['good', 'bad'].forEach(kind => {
        const groupLabel = document.createElement('div');
        groupLabel.style.cssText = 'font-size:0.75rem;font-weight:700;color:#9ca3af;margin:10px 4px 6px;';
        groupLabel.textContent = kind === 'good' ? 'נקודות טובות' : 'נקודות רעות';
        listEl.appendChild(groupLabel);
        behaviorTypes.filter(t => t.kind === kind).forEach(t => {
            const btn = document.createElement('button');
            btn.style.cssText = 'width:100%;text-align:right;padding:10px 12px;margin-bottom:6px;border-radius:10px;border:1.5px solid #e5e7eb;background:white;cursor:pointer;font-family:inherit;font-size:0.92rem;display:flex;align-items:center;gap:10px;';
            btn.innerHTML = `<span style="font-size:1.2rem;">${t.emoji}</span><span>${t.label}</span>`;
            btn.onclick = () => addBehaviorPoint(t.id);
            listEl.appendChild(btn);
        });
    });
    document.getElementById('add-point-overlay').classList.add('open');
}
function closeAddPointPicker() {
    document.getElementById('add-point-overlay').classList.remove('open');
}
function addBehaviorPoint(typeId) {
    const s = students.find(x => x.id === currentBehaviorStudentId);
    const t = behaviorTypes.find(x => x.id === typeId);
    if (!s || !t) return;
    if (!s.behaviorLog) s.behaviorLog = [];
    s.behaviorLog.push({ id: generateId(), typeId: t.id, emoji: t.emoji, label: t.label, kind: t.kind, ts: Date.now() });
    saveData();
    closeAddPointPicker();
    showBehaviorDetail(s.id);
    showToast(`${t.emoji} נקודה נוספה`);
}

// ===== DETAIL =====
```

- [ ] **Step 2: בדיקה ידנית**

ב-Console (אחרי `showBehaviorDetail(students[0].id)` מ-Task 4):
```js
openAddPointPicker()
```
Expected: נפתחת חלונית עם שתי קבוצות ("נקודות טובות" עם 5 כפתורים, "נקודות רעות" עם 5 כפתורים). לחיצה על כפתור כלשהו (למשל "✅ הגיש שיעורי בית") סוגרת את החלונית, חוזרת למסך הפרופיל, ומעדכנת את המונה `✅` ל-`1`. פתיחת "הצג פירוט" מציגה שורה אחת עם האמוג'י, התיאור, התאריך של היום, וכפתור 🗑️.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "הוספת בורר להענקת נקודת התנהגות לתלמיד"
```

---

## Task 6: ניהול רשימת ההתנהגויות (הוספה/מחיקה)

**Files:**
- Modify: `index.html` — הוסף פונקציות מיד אחרי הבלוק שנוסף ב-Task 5 (לפני `// ===== DETAIL =====`)

- [ ] **Step 1: הוסף את בלוק ה-JS**

מצא (סוף הבלוק שנוסף ב-Task 5):
```js
    showToast(`${t.emoji} נקודה נוספה`);
}

// ===== DETAIL =====
```

והחלף ב:
```js
    showToast(`${t.emoji} נקודה נוספה`);
}

function openBehaviorTypesEditor() {
    renderBehaviorTypesList();
    document.getElementById('behavior-types-overlay').classList.add('open');
}
function closeBehaviorTypesEditor() {
    document.getElementById('behavior-types-overlay').classList.remove('open');
}
function renderBehaviorTypesList() {
    const listEl = document.getElementById('behavior-types-list');
    listEl.innerHTML = '';
    ['good', 'bad'].forEach(kind => {
        const groupLabel = document.createElement('div');
        groupLabel.style.cssText = 'font-size:0.75rem;font-weight:700;color:#9ca3af;margin:10px 4px 6px;';
        groupLabel.textContent = kind === 'good' ? 'נקודות טובות' : 'נקודות רעות';
        listEl.appendChild(groupLabel);
        behaviorTypes.filter(t => t.kind === kind).forEach(t => {
            const row = document.createElement('div');
            row.className = 'missing-item';
            const nameCell = document.createElement('div');
            nameCell.className = 'missing-item-name';
            nameCell.textContent = `${t.emoji} ${t.label}`;
            const delBtn = document.createElement('button');
            delBtn.className = 'missing-add-btn';
            delBtn.style.cssText = 'color:#ef4444;background:#fef2f2;border-color:#fecaca;';
            delBtn.textContent = '🗑️';
            delBtn.onclick = () => deleteBehaviorType(t.id);
            row.appendChild(nameCell);
            row.appendChild(delBtn);
            listEl.appendChild(row);
        });
    });
}
function deleteBehaviorType(typeId) {
    if (!confirm('למחוק את סוג ההתנהגות הזה מהרשימה?\nרשומות עבר שכבר ניתנו לא יימחקו.')) return;
    behaviorTypes = behaviorTypes.filter(t => t.id !== typeId);
    saveBehaviorTypes();
    renderBehaviorTypesList();
}
function addBehaviorType() {
    const emoji = document.getElementById('bt-new-emoji').value.trim();
    const label = document.getElementById('bt-new-label').value.trim();
    const kind = document.querySelector('input[name="bt-new-kind"]:checked').value;
    if (!emoji || !label) { showToast("⚠️ יש למלא אמוג'י ותיאור"); return; }
    behaviorTypes.push({ id: generateId(), emoji, label, kind });
    saveBehaviorTypes();
    document.getElementById('bt-new-emoji').value = '';
    document.getElementById('bt-new-label').value = '';
    renderBehaviorTypesList();
    showToast('✅ נוסף לרשימה');
}

// ===== DETAIL =====
```

- [ ] **Step 2: בדיקה ידנית**

ב-Console:
```js
openBehaviorTypesEditor()
```
Expected: חלונית עם שתי רשימות (5 טובות + 5 רעות), כל פריט עם כפתור 🗑️, וטופס הוספה בתחתית.

הוסף פריט חדש: מלא בשדה האמוג'י `🎨`, בשדה התיאור `יצירתיות`, השאר "טובה" מסומן, לחץ "💾 הוסף". Expected: הפריט מופיע ברשימת "נקודות טובות" עם toast "✅ נוסף לרשימה". רענן את הדף ופתח שוב את החלונית — הפריט עדיין קיים (נשמר ב-localStorage).

מחק את הפריט שהוספת עם 🗑️ (עם אישור ה-confirm). Expected: הפריט נעלם מהרשימה.

פתח `openAddPointPicker()` שוב על תלמיד עם רשומת יומן קיימת מ-Task 5, ומחק את סוג ההתנהגות שהתלמיד קיבל בעבר מתוך `openBehaviorTypesEditor()`. Expected: הרשומה הקיימת ביומן התלמיד (`renderBehaviorLog`) **לא** נעלמת ועדיין מוצגת עם האמוג'י/תיאור המקוריים.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "הוספת מסך ניהול רשימת סוגי ההתנהגות (הוספה ומחיקה)"
```

---

## Task 7: חיבור לניווט — כפתורים במסך הבית

**Files:**
- Modify: `index.html` — בתוך `renderHome()`, בלוק כרטיס כיתה בודדת ובלוק שורת "כל התלמידים"

- [ ] **Step 1: הוסף כפתור בכרטיס כיתה בודדת**

מצא:
```js
        const classroomBtn = document.createElement('button');
        classroomBtn.className = 'class-action-btn classroom-btn-sm';
        classroomBtn.innerHTML = '🏫 כיתה';
        classroomBtn.onclick = () => showClassroom(isNone ? null : key);

        actions.appendChild(galleryBtn);
        actions.appendChild(sep);
        actions.appendChild(quizBtn);
        actions.appendChild(sep2);
        actions.appendChild(rquizBtn);
        actions.appendChild(sep3);
        actions.appendChild(mquizBtn);
        actions.appendChild(sep4);
        actions.appendChild(classroomBtn);
```

והחלף ב:
```js
        const classroomBtn = document.createElement('button');
        classroomBtn.className = 'class-action-btn classroom-btn-sm';
        classroomBtn.innerHTML = '🏫 כיתה';
        classroomBtn.onclick = () => showClassroom(isNone ? null : key);

        const sep7 = document.createElement('div');
        sep7.className = 'class-sep';
        const behaviorBtn = document.createElement('button');
        behaviorBtn.className = 'class-action-btn';
        behaviorBtn.innerHTML = '🏆 ניקוד';
        behaviorBtn.onclick = () => showBehaviorList(isNone ? null : key);

        actions.appendChild(galleryBtn);
        actions.appendChild(sep);
        actions.appendChild(quizBtn);
        actions.appendChild(sep2);
        actions.appendChild(rquizBtn);
        actions.appendChild(sep3);
        actions.appendChild(mquizBtn);
        actions.appendChild(sep4);
        actions.appendChild(classroomBtn);
        actions.appendChild(sep7);
        actions.appendChild(behaviorBtn);
```

- [ ] **Step 2: הוסף כפתור בשורת "כל התלמידים"**

מצא:
```js
    const allClassroom = document.createElement('button');
    allClassroom.className = 'class-action-btn classroom-btn-sm';
    allClassroom.innerHTML = '🏫 כיתה';
    allClassroom.onclick = () => showClassroom(undefined);

    const allSep5 = document.createElement('div');
    allSep5.className = 'class-sep';
    const importClassBtn = document.createElement('button');
    importClassBtn.className = 'class-action-btn';
    importClassBtn.style.cssText = 'color:#7c3aed;';
    importClassBtn.innerHTML = '📥 ייבא כיתה';
    importClassBtn.onclick = () => document.getElementById('import-class-file-input').click();

    allRow.appendChild(allGallery);
    allRow.appendChild(allSep);
    allRow.appendChild(allQuiz);
    allRow.appendChild(allSep2);
    allRow.appendChild(allRquiz);
    allRow.appendChild(allSep3);
    allRow.appendChild(allMquiz);
    allRow.appendChild(allSep4);
    allRow.appendChild(allClassroom);
    allRow.appendChild(allSep5);
    allRow.appendChild(importClassBtn);
    list.appendChild(allRow);
```

והחלף ב:
```js
    const allClassroom = document.createElement('button');
    allClassroom.className = 'class-action-btn classroom-btn-sm';
    allClassroom.innerHTML = '🏫 כיתה';
    allClassroom.onclick = () => showClassroom(undefined);

    const allSep4b = document.createElement('div');
    allSep4b.className = 'class-sep';
    const allBehavior = document.createElement('button');
    allBehavior.className = 'class-action-btn';
    allBehavior.innerHTML = '🏆 ניקוד';
    allBehavior.onclick = () => showBehaviorList(undefined);

    const allSep5 = document.createElement('div');
    allSep5.className = 'class-sep';
    const importClassBtn = document.createElement('button');
    importClassBtn.className = 'class-action-btn';
    importClassBtn.style.cssText = 'color:#7c3aed;';
    importClassBtn.innerHTML = '📥 ייבא כיתה';
    importClassBtn.onclick = () => document.getElementById('import-class-file-input').click();

    allRow.appendChild(allGallery);
    allRow.appendChild(allSep);
    allRow.appendChild(allQuiz);
    allRow.appendChild(allSep2);
    allRow.appendChild(allRquiz);
    allRow.appendChild(allSep3);
    allRow.appendChild(allMquiz);
    allRow.appendChild(allSep4);
    allRow.appendChild(allClassroom);
    allRow.appendChild(allSep4b);
    allRow.appendChild(allBehavior);
    allRow.appendChild(allSep5);
    allRow.appendChild(importClassBtn);
    list.appendChild(allRow);
```

- [ ] **Step 2: בדיקה ידנית — מסלול מלא מקצה לקצה**

פתח את `index.html` בדפדפן מהתחלה (רענון מלא). ודא שיש לפחות כיתה אחת עם 2+ תלמידים (חלקם עם תמונה, חלקם בלי — ניתן להוסיף תלמיד בלי להעלות תמונה ולראות שהוא מקבל placeholder).

1. במסך הבית, בכרטיס של כיתה, לחץ על "🏆 ניקוד". Expected: נפתח מסך רשימה עם כותרת "🏆 ניקוד — <שם הכיתה>", וכרטיס לכל תלמיד בכיתה (כולל תלמיד בלי תמונה — עם ה-placeholder silhouette).
2. לחץ "לפי ניקוד" ואז "א-ב" — הרשת מתארגנת מחדש בכל פעם בלי שגיאות קונסול.
3. לחץ על כרטיס תלמיד — נפתח מסך הפרופיל שלו.
4. לחץ "➕ הוסף נקודה", בחר "🗣️ הפריע בשיעור" — חוזר לפרופיל, `🚩` עולה ל-`1`.
5. לחץ "➕ הוסף נקודה" שוב, בחר "✅ הגיש שיעורי בית" — `✅` עולה ל-`1`.
6. לחץ "📋 הצג פירוט" — רואים 2 רשומות עם תאריך היום, מהחדשה לישנה.
7. לחץ 🗑️ על אחת הרשומות, אשר את ה-confirm — הרשומה נעלמת והמונה המתאים יורד ב-1.
8. לחץ כפתור "חזרה" (או "🏠") וחזור למסך הרשימה — לחץ "לפי ניקוד" ובדוק שהתלמיד שקיבל נקודה טובה מסודר לפי ההפרש הנכון ביחס לתלמידים אחרים.
9. במסך הבית, לחץ "🏆 ניקוד" בשורת "כל (N)" התחתונה — נפתח מסך עם כל התלמידים מכל הכיתות יחד.
10. רענן את כל העמוד (F5) ופתח שוב את פרופיל הניקוד של אותו תלמיד — הנתונים (הרשומה שנשארה) עדיין קיימים (נשמרו ב-localStorage).

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "חיבור מדור ניקוד ההתנהגות לניווט ממסך הבית (כרטיסי כיתה + כל התלמידים)"
```

---

## Task 8: פוש ל-GitHub

- [ ] **Step 1: Push**

```bash
git push
```

Expected: הקומיטים מה-Task-ים 1-7 מופיעים ב-`origin/main`.
