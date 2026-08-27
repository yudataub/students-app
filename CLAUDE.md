# students-app — "זוכר שמות תלמידים"

אפליקציה למורה לזכירת שמות תלמידים: תמונות, מבחני זיכרון, סידורי ישיבה, ניקוד התנהגות, רמזים אישיים. **שתי גרסאות חיות** (ר' סעיף ייעודי למטה) — קרא את זה לפני כל עריכה.

## עובדות בסיס

- **קובץ יחיד**: כל האפליקציה ב-`index.html` (~6,600 שורות) — HTML + CSS + JS inline. אין build, אין תלויות, אין node_modules.
- **שפה**: UI בעברית, RTL. מזהים (משתנים/פונקציות) באנגלית. **תקשורת עם המשתמש: בעברית בלבד**, כולל עדכוני סטטוס קצרים. הודעות commit בעברית.
- **אחסון**: רשומות התלמידים ב-localStorage, **התמונות ב-IndexedDB** (ר' הסעיף הייעודי — זה השתנה!). סנכרון ענן אופציונלי (Firebase Firestore, פרויקט `name-2b45a`). בגרסה המקומית (`desktop/`) הכל בקובץ אחד על הדיסק, בלי ענן.
- **פריסה**: GitHub Pages מ-branch `main`, שורש הריפו. ריפו: `yudataub/students-app`. אתר חי: https://yudataub.github.io/students-app/ — **חשוב**: push ל-GitHub ≠ "עובד בכל מקום". רק ה-`index.html` הראשי רץ בפועל דרך GitHub Pages. הגרסה המקומית (`desktop/`) היא רק **קוד מגובה** ב-git — היא לא "רצה" באף מקום עד שמישהו מריץ אותה פיזית על מחשב ספציפי (`הפעל.bat`), בנפרד בכל מחשב.
- **אין טסטים אוטומטיים** (מוסכם עם המשתמש) — בדיקות ידניות בדפדפן בלבד (Claude Browser: `preview_start` + `javascript_tool` לסימולציית תרחישים).
- **סופי שורות: CRLF**. אל תמיר ל-LF (סקריפט python שכותב את הקובץ חייב לשמר CRLF, אחרת ה-diff יהיה כל הקובץ).

## ⚠️⚠️ אזהרה ראשונה במעלה: אל תבדוק על הנתונים החיים של המשתמש

**קרה בפועל (אוגוסט 2026):** בדיקה שהורצה על הגרסה המקומית שרצה אצל המשתמש (`localhost:8733`) הציבה `students = [...]` וקראה ל-`saveData()` — וזה **דרס את רשימת התלמידים האמיתית שלו בדיסק**. הנתונים שוחזרו רק כי היה עותק באתר החי.

**כללים שנגזרו מזה:**
1. **בדיקות רק על `localhost:8732`** (שרת הבדיקה מ-`.claude/launch.json` שמצביע על תיקיית הריפו) — **לעולם לא על 8733** (הגרסה המקומית של המשתמש עם הנתונים האמיתיים).
2. אם חייבים לגעת ב-8733 — **קריאה בלבד**, ובגיבוי מראש: `cp desktop/data/data.json desktop/data/data.json.backup-$(date +%Y%m%d-%H%M%S)`.
3. תמיד לנקות בסוף בדיקה: `localStorage.clear()` + ניקוי ה-object store של IndexedDB.
4. **אל תשתמש ב-`indexedDB.deleteDatabase()` באמצע סשן בדיקה** — אם יש חיבור פתוח היא נחסמת ומתבצעת מאוחר יותר בזמן ה-reload, ומוחקת בשקט את מה שכתבת אחריה (בלבל אותי בבדיקה אמיתית). במקום זה: `store.clear()` בתוך טרנזקציה.

## ⚠️ שתי גרסאות = שני קבצים כמעט-זהים

יש **`desktop/index.html`** — עותק כמעט-מדויק של `index.html` הראשי, שרץ מקומית על מחשב המשתמש (ר' `desktop/CLAUDE.md` להסבר המלא).

**כלל ברזל: כל שינוי בפיצ'ר ב-`index.html` חייב להיכנס גם ל-`desktop/index.html`**, אלא אם הוא ספציפי ל-Firebase/ענן/שיתוף או לשכבת האחסון (שם הגרסאות שונות בכוונה).

**הדרך הבטוחה להעתיק שינוי גדול** (הוכחה את עצמה): סקריפט Python שעושה החלפות מחרוזת מדויקות ו**נופל אם החלפה לא תאמה בדיוק פעם אחת** — ואז לוודא בעזרת diff שאין הבדל אף שורה בקוד החדש בין הקבצים. `patch`/`git apply` **לא עובדים** כאן בגלל ה-CRLF ("different line endings").

**הבדלים לגיטימיים בין הקבצים** (לא לתקן!): `let USE_IDB_PHOTOS` (true בראשי / false בדסקטופ), שכבת ה-shim של האחסון, ניטרול Firebase, קוד ה-`extraPhotos` בסנכרון הענן, `exportFullBackup` (ראשי) מול `desktopImportBackup` (דסקטופ), וה-CSS שמסתיר את מדור הענן.

## מבנה נתונים

| מפתח | תוכן |
|---|---|
| `students` (localStorage) | `{id, name, className, photo, extraPhotos, association, hint, correct, wrong, behaviorLog, srsLevel, srsDue}` — **בלי photo/extraPhotos** באתר (הם ב-IndexedDB); **עם** בדסקטופ |
| `photos` (IndexedDB, DB בשם `students-app-photos`) | מסמך לכל תלמיד: `{photo, extraPhotos}` — **רק באתר** |
| `behaviorTypes` | סוגי התנהגות לניקוד: `{id, emoji, label, kind:'good'|'bad'}` |
| `importedNamesMap` | רשימות שמות מיובאות לפי כיתה (למנגנון "שמות חסרים") |
| `deletedTombstones` | **רשת ביטחון**: מזהי תלמידים שנמחקו במפורש + timestamp (180 יום) |
| `seating_<class>`, `progressive_<class>` | סידורי ישיבה, התקדמות למידה הדרגתית |
| `firebaseConfig`, `cloudLastSync` | הגדרות ענן (לא רלוונטי בדסקטופ) |

- `s.photo` **תמיד קיים** — `PLACEHOLDER_PHOTO` (SVG inline) כשאין תמונה אמיתית. ר' האזהרה בסעיף הבא.
- `s.extraPhotos` — תמונות נוספות של **אותו** תלמיד. במבחנים נבחרת אקראית אחת מ-`[photo, ...extraPhotos]` (`_quizPhotoFor`) — עדיין תשובה נכונה אחת.
- `s.hint` — רמז אישי לזכירת השם, **נפרד** מ-`association`.

## אחסון תמונות (IndexedDB) — הסעיף הכי עדין בקוד

localStorage מוגבל ל-~5MB וזה נגמר בכיתה מלאה. התמונות עברו ל-IndexedDB; הרשומות הקטנות נשארו ב-localStorage. אותה הפרדה בדיוק שסנכרון הענן כבר עושה מול Firestore.

**הפונקציות:** `_idbOpen`/`_idbPutPhoto`/`_idbGetAllPhotos`/`_idbDeletePhoto`, `_persistPhotos`, `_persistStudents`, `_initPhotoStorage` (~1540-1700).

**כללים שאסור לשבור:**
1. **`_isRealPhoto(p)` לפני כל החלטה על תמונה.** `PLACEHOLDER_PHOTO` הוא ערך אמיתי במחרוזת, ולכן `if (s.photo)` הוא **תמיד true**. בגרסה ראשונה של השינוי זה גרם לכך שבטעינה השנייה נכתבה הצללית האפורה **על גבי התמונות השמורות** ומחקה אותן. נתפס רק בבדיקת רענון-חוזר. **תמיד תבדוק רענון שני, לא רק ראשון.**
2. **סדר ההעברה:** קודם כותבים תמונות ל-IndexedDB, **ורק אחר כך** כותבים ל-localStorage בלי התמונות. עד ש-`_photosHydrated === true`, שמירות ממשיכות בפורמט הישן (inline) — כדי שלא יהיה רגע שבו התמונות לא נמצאות באף מקום.
3. **`_persistPhotos` לעולם לא מוחק ולא כותב placeholder.** המחיקה היחידה היא ב-`recordDeletion` (מחיקה מפורשת של תלמיד).
4. **כתיבה רק כשהתמונה השתנתה** — `_writtenPhotos` / `_photoUnchanged` / `_markPhotoWritten`. `saveData()` רץ על כל תשובה במבחן; בלי זה כל לחיצה כותבת מחדש מגה-בייטים. הסימון נעשה **רק אחרי** שהכתיבה הצליחה, כדי שכשל ינוסה שוב.
5. **`USE_IDB_PHOTOS = false` בדסקטופ**, והשינוי נעשה **בשורת ההצהרה עצמה** — לא בהשמה מאוחרת, כי `_initPhotoStorage()` נקרא לפני ה-overrides שבתחתית הקובץ.

מדידות אמיתיות (30 תלמידים, ~3MB): מסך מגיב תוך 26ms, תמונות מיידיות, 10 תשובות במבחן = **0 כתיבות**, החלפת תמונה אחת = כתיבה אחת. עומס 60 תלמידים / ~11MB עבר בלי שגיאת מכסה.

## חוקי ברזל — סנכרון ענן (אל תשבור אותם!)

הוטמעה רשת ביטחון אחרי אובדן נתונים אמיתי (כיתה שלמה נמחקה מסנכרון דורס):

1. **עדכון מהענן לעולם לא מוחק תלמיד.** `_applyCloudData` ממזגת — תלמידים מקומיים שחסרים בענן נשמרים ומועלים חזרה (ריפוי). לעולם אל תחזיר החלפה גורפת (`students = cloudData`).
2. **מחיקה רק במפורש.** כל מסלול מחיקה חדש חייב לקרוא `recordDeletion(ids)` — יוצר tombstone שמסתנכרן ומונע "תחייה" של תלמיד שנמחק בכוונה. הפונקציה גם מוחקת את התמונה מ-IndexedDB.
3. tombstones נכללים ב-`_getCloudSnapshot()` וממוזגים ב-`_applyCloudData`.
4. **`photo`/`extraPhotos` תמיד מוצאים מהמסמך הראשי ב-Firestore** ונשמרים ב-subcollection `photos` (מסמך לכל תלמיד) — מגבלת 1MB למסמך. שדה תמונה חדש בעתיד → לעדכן גם `cloudSaveNow` וגם `_readCloudData`.
5. **כתיבת תלמידים תמיד דרך `_persistStudents()`** — לא `localStorage.setItem('students', ...)` גולמי. היו שני באגים כאלה: ב-`_applyCloudData` (כשל זרק החוצה, `cloudLastSync` לא נכתב → משיכה אינסופית מהענן) וב-`_listenSharedClass` (השאיר `_applyingRemoteUpdate` תקוע על true לצמיתות; עכשיו ב-`try/finally`).

## אזורים מרכזיים בקוד (`index.html`, שורות משוערות)

- אחסון תמונות + `saveData`/`_persistStudents`/`_persistPhotos`/`_initPhotoStorage` (~1540-1700)
- tombstones + `recordDeletion` (~1495)
- `showView`/`goBack`/`navStack` — ניווט (~1700+)
- `exportFullBackup()` — ייצוא `backup.json` לגרסה המקומית
- `renderHome()` — מסך הבית, כרטיסי כיתות
- **"שמות חסרים"**: `_normName`, `_namesMatch`, `getMissingNames` — **`_normName` תפוס!** לנרמול חדש תן שם ייחודי (למשל `_bulkNorm`, `_stripBulkDupSuffix`)
- העלאת קבוצה: `setBulkMode`, `_findBestMatch`, `_mergeDuplicateBulkItems`, `_findExistingStudentForBulkName`, `saveBulk`/`saveBulkMatches`
- `findAndMergeDuplicateStudents()` — כלי בהגדרות לאיחוד כפילויות ישנות. **מאחד רק בתוך אותה כיתה** (בכוונה — שני ילדים שונים עשויים לחלוק שם), ומבקש אישור לכל קבוצה
- מבחנים: `startQuiz`/`renderQuestion`+`buildOptions`, `startRQuiz`, `startMQuiz`/`renderMQuestion`/`submitMAnswer`; בחירת תמונה דרך `_quizPhotoFor(s)`
- רמזים במבחן זיכרון: `toggleMQuizAskHint`/`toggleMQuizAutoHint`, `revealMQuizHint`, `saveMQuizHint`, `startEditHint`/`saveEditHint`
- ניקוד התנהגות: `showBehaviorList`, `showBehaviorDetail`, `openAddPointPicker`, `openBehaviorTypesEditor`
- סנכרון ענן: `_applyCloudData`, `cloudSaveNow`, `_readCloudData`, `_checkAndPullCloud`
- כיתות משותפות: `_listenSharedClass`, `joinSharedClass`

## תהליך עבודה מומלץ

1. `git fetch origin && git log --oneline main..origin/main` — **בדוק שאין שינויים משיחה מקבילה** (קרה בפועל כמה פעמים)
2. branch חדש: `git checkout -b feature/<name>`
3. עריכות ב-`index.html` → **ואז אותו diff ב-`desktop/index.html`**
4. בדיקת תחביר על **שני** הקבצים:
   ```bash
   node -e "const fs=require('fs');['index.html','desktop/index.html'].forEach(p=>{const h=fs.readFileSync(p,'utf8');[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(m=>new Function(m[1]));console.log(p,'OK');});"
   ```
   + בדיקת כפילויות שמות פונקציות/const (שני `const` באותו שם = SyntaxError ששובר את כל האפליקציה — קרה בפועל)
5. בדיקה בדפדפן על **פורט 8732 בלבד** (ר' האזהרה למעלה), כולל **רענון שני** לתרחישי אחסון
6. commit (עברית, מפורט על מה נבדק) → merge ל-main → push
7. **אימות פריסה**: `curl` עם cache-buster עד שהשינוי מופיע (~2 דק', `run_in_background`). ידוע: לפעמים ה-deploy נתקע ("Deployment failed, try again later" / Queued לנצח) — מה שעבד: **push של commit ריק** שמייצר ריצה חדשה. Re-run של הריצה התקועה **לא** עזר.
8. **הגרסה המקומית לא מתעדכנת לבד** — צריך `git pull` בפועל על אותו מחשב.

## באגים ידועים שלא טופלו

- **ניווט**: `goBack()` עושה pop כפול + מסכים שנטענים מחדש דוחפים כפילויות ל-`navStack` → "חזור" לפעמים מגיע למסך לא צפוי. קיים מזמן, לא קריטי.
- שורת הפעולות בכרטיס כיתה צפופה (7-8 כפתורים) — מועמדת לתפריט "⋯".
- **`desktopImportBackup` מחליף את כל הקובץ** — ייבוא גיבוי בגרסה המקומית מוחק מפתחות שלא נמצאים ב-`backup.json` (למשל `progressive_*`). הוצע למשתמש להפוך את זה למיזוג; **לא בוצע, ממתין להחלטה שלו**.
- כפילויות בין **כיתות שונות** (אותו תלמיד רשום בשתי כיתות) לא נתפסות ע"י כלי האיחוד — בכוונה. צריך תיקון ידני של הכיתה קודם.
- הערה: במסך הבית כפתורי "חזור"/"בית" מוסתרים **בכוונה** — זה לא באג.
- תוסף אפשרי (לא בנוי): ניהול `extraPhotos` ידני מהפרופיל.

## היסטוריה

**יולי 2026:** מדור ניקוד התנהגות מלא · רשת ביטחון לסנכרון ענן (מיזוג + tombstones) · מצב "🔗 התאם תמונות לקיימים" בהעלאת קבוצה.

**אוגוסט 2026:**
- **`desktop/`** — גרסה מקומית (Python stdlib, פורט 8733, `localhost` בלבד). ר' `desktop/CLAUDE.md` ו-`docs/superpowers/specs/2026-08-12-desktop-local-app-design.md`.
- כפתור "📦 ייצוא גיבוי מלא למחשב" בהגדרות.
- **`extraPhotos`** — קבצים עם אותו שם וסיומת מבדילה ("דוד כהן א"/"ב", "1"/"2") מזוהים כאותו תלמיד. מכוסה בשני מסלולים: מיזוג בתוך אותה העלאה (`_mergeDuplicateBulkItems`) **וגם** צירוף לתלמיד שכבר קיים מהעלאה קודמת (`_findExistingStudentForBulkName`) — הראשון לבדו לא הספיק.
- **כלי איחוד כפילויות ישנות** בהגדרות (`findAndMergeDuplicateStudents`).
- **תיקון: `buildOptions` שאב אפשרויות תשובה מכל התלמידים** במקום רק מהכיתה שנבחרה — מבחן על "ו בנים" הציג שמות מ"ו בנות". עכשיו מ-`quizStudents`.
- **מבחן זיכרון**: Enter/רווח מעביר לשאלה הבאה אחרי טעות · **רמזים אישיים** (`hint`) עם שתי אפשרויות בהגדרות (כתיבה אחרי טעות / הצגה אוטומטית), כבויות כברירת מחדל.
  - ⚠️ המאזין הגלובלי של Enter/רווח **חייב להתעלם מ-INPUT/TEXTAREA** — אחרת רווח בתוך תיבת הרמז קופץ לשאלה הבאה ומאבד את הטקסט.
- **התמונות עברו ל-IndexedDB** — ר' הסעיף הייעודי. תיקן גם את "שגיאת ענן: exceeded the quota" ושני באגי `setItem` גולמי.
- ⚠️ עבודה משתי שיחות במקביל גרמה כבר להתנגשויות (שתי פונקציות `_normName`) — עדיף לא לעבוד משתי שיחות במקביל, ותמיד `git fetch` לפני שמתחילים.

## מסמכים נוספים בריפו

- `docs/superpowers/specs/` — מסמכי אפיון (ניקוד התנהגות, גרסה מקומית)
- `docs/superpowers/plans/` — תוכניות מימוש; טובות גם כ-checklist לרגרסיה ידנית
- `desktop/CLAUDE.md` — הוראות לגרסה המקומית (שכבת האחסון, פורמט `data.json`, מה שונה)
