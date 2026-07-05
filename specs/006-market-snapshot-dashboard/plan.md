PrioraMarket – Feature 005 Progress Summary
Feature

Canonical Data Model & Vehicle Reference Catalog

Goal:

Store canonical values in listing.
Preserve raw marketplace payload in raw_listing.
Build a canonical reference catalog for all future analytics/classification.
Architecture
Scraper (Python)

Owns:

Migrations
Ingestion
Normalization
Canonicalization
Replay
Backfill
Catalog synchronization
Backend (NestJS)

Read-only.

No marketplace normalization logic.

Frontend (Next.js)

Presentation only.

Display names will eventually come from Vehicle Reference Catalog.

Completed
US1 – Canonicalization

Completed.

Verified with a fresh Porsche scrape.

Example stored data:

make = porsche
model = cayenne
trim = gts

No uppercase.
No spaces.
No hyphens.

Canonicalization working.

Normalization version stored.

US2 – Vehicle Reference Catalog

Completed.

Implemented:

VehicleReferenceCatalog provider
CSV validation
CSV lookup
PostgreSQL implementation
In-memory implementation
Provenance
Conflict handling
US3 – CSV Synchronization

Completed.

Implemented:

CSV sync service
Idempotent sync
sync-catalog command
Curated reference CSV
Prisma updates
Backend compatibility
Frontend contract

Validation passed.

US4 – Canonical Backfill

Initially missing.

Later implemented.

Added:

src/maintenance/canonical_backfill.py

CLI now exists.

Supports:

dry-run
execute
batch-size
resume-after-id
canonicalization version

Uses shared CanonicalizationEngine.

Updates only listing.

Never modifies raw_listing.

Idempotent.

Bug Fixed

Backfill initially failed:

could not determine data type of parameter $1

Cause:
nullable PostgreSQL parameter.

Fixed.

Dry-run now works.

Current Status

Dry-run executes successfully.

Example:

python -m src.ingestion.runner backfill --dry-run --batch-size 100

Output:

processed through listing_id=100
processed through listing_id=200
...
Remaining Work
1. Finish Dry Run

Let the dry-run complete.

Review summary.

Check:

scanned rows
rows to update
failures
unknown values
2. Execute Backfill

Run:

python -m src.ingestion.runner backfill --execute --batch-size 100
3. Verify Old Data

Old rows still contain values like:

Mercedes Benz
C Class

Expected after backfill:

mercedesbenz
cclass
4. Validation SQL

Check for remaining non-canonical values:

SELECT make, model, trim
FROM listing
WHERE make ~ '[A-Z -]'
   OR model ~ '[A-Z -]'
   OR trim ~ '[A-Z -]'
LIMIT 50;

Expected:

0 rows

Check distinct makes:

SELECT DISTINCT make
FROM listing
ORDER BY make;

Expected canonical values only:

audi
bmw
mercedesbenz
porsche
toyota
...
5. Review Unknown Statistics

Backfill emits normalization statistics.

Review:

unknown makes
unknown models
unknown trims

Update catalog if needed.

Notes
raw_listing must remain untouched.
Backfill updates only canonical fields in listing.
Do not use manual SQL updates.
Canonicalization engine is now the single source of normalization logic.
Vehicle Reference Catalog is the source of truth for display names and future generation mapping.
Next Goal

Complete the backfill execution, verify all legacy listings are canonicalized successfully, then validate the database before moving on to the next feature.

This summary looks consistent with the work completed so far.

Current Status
User Story	Status
US1 – Canonicalization	✅ Complete
US2 – Vehicle Reference Catalog	✅ Complete
US3 – CSV Synchronization	✅ Complete
US4 – Canonical Backfill	✅ Complete (implementation finished, execution pending)
The only remaining work for Feature 005 is operational validation, not new development.

Recommended Execution Order
Step 1 — Finish the dry run
Run until completion:

python -m src.ingestion.runner backfill --dry-run --batch-size 100
Verify the final summary contains:

total scanned

would update

already canonical

failures

unknown makes/models/trims

No database rows should change.

Step 2 — Execute
python -m src.ingestion.runner backfill --execute --batch-size 100
Watch for:

progress increasing

no failures

clean completion

Step 3 — Verify the database
Run:

SELECT make, model, trim
FROM listing
WHERE make ~ '[A-Z -]'
   OR model ~ '[A-Z -]'
   OR trim ~ '[A-Z -]'
LIMIT 50;
Expected:

0 rows
Then:

SELECT DISTINCT make
FROM listing
ORDER BY make;
You should only see canonical values such as:

audi
bmw
chevrolet
ford
hyundai
kia
lexus
mercedesbenz
nissan
porsche
toyota
...
Step 4 — Spot check
Verify a few listings that previously contained:

Mercedes Benz
became

mercedesbenz
and

C Class
became

cclass
Also verify:

normalization_version updated correctly.

raw_listing remains unchanged.

Step 5 — Review unknown statistics
If the backfill reports unknown values, determine whether they are:

genuine new makes/models/trims → add to the reference CSV and re-sync.

marketplace typos/noise → improve the canonicalization engine.

Do not patch the database manually.

Definition of Done
Feature 005 can be considered complete when:

✅ All legacy listings are canonicalized.

✅ No uppercase, spaces, or hyphens remain in canonical fields.

✅ raw_listing is untouched.

✅ Backfill is idempotent (running again results in 0 updates).

✅ Vehicle Reference Catalog contains all known canonical values.

✅ Replay, ingestion, and backfill all use the same CanonicalizationEngine.

At that point, Feature 005 is complete and the scraper becomes the single source of truth for canonical vehicle data, with the backend remaining read-only for normalization concerns.

(Your uploaded scraper file appears unrelated to this feature and isn't needed for the remaining validation steps.) 



he final prerequisite check passed and found the expected feature directory/artifacts. The working tree is dirty with many feature changes, so I’ll avoid any commit operation and only summarize the completed closeout.
Feature 005 closeout is complete.
What changed in this continuation:
- Marked Phase 7 tasks T064-T070 complete in specs/005-vehicle-reference-catalog/tasks.md.
- Recorded the Spec Kit cross-artifact consistency review in specs/005-vehicle-reference-catalog/checklists/requirements.md.
- Verified no unchecked tasks remain.
- Verified no unchecked checklist items remain.
- Ran Spec Kit prerequisites successfully:
- Feature dir: specs/005-vehicle-reference-catalog
- Available docs: research.md, data-model.md, contracts/, quickstart.md, tasks.md
Final validation already documented in quickstart.md:
- Python tests passed.
- Python lint passed for final updates.
- Backend Prisma generation passed.
- Backend build passed.
- Backend compatibility/regression tests passed.
- Frontend typecheck passed.
Hook status:
- .specify/extensions.yml has an optional after_implement hook: /speckit-git-commit.
- I did not execute it because you did not explicitly ask me to commit.
No blockers remain. eh r2yk bl 3rby

بصراحة، ده يعتبر إقفال محترم جدًا للـ Feature، ومفيش حاجة واضحة ناقصة.

تقييمي:

✅ من ناحية التنفيذ
كل الـ User Stories (US1 → US4) اتنفذت.

الـ Backfill اتعمل واتجرب.

المشكلة الخاصة بـ PostgreSQL اتحلت.

فيه Dry Run و Execute و Resume و Idempotency.

فيه اختبارات للـ Backfill نفسه.

وده معناه إن الـ implementation نفسه مكتمل.

✅ من ناحية Spec Kit
واضح إنه عمل الـ closeout الصح:

كل الـ Tasks اتعلمت Completed.

الـ Requirements Checklist اتراجع.

اتأكد إن مفيش Task متسيبة.

اتأكد إن مفيش Checklist ناقصة.

الـ prerequisite check عدى.

الـ artifacts كلها موجودة.

وده بالظبط المطلوب قبل اعتبار الـ Feature منتهية.

✅ من ناحية الجودة
الـ Validation ممتاز:

Python tests ✅

Lint ✅

Backend build ✅

Prisma generate ✅

Compatibility tests ✅

Frontend typecheck ✅

يعني الـ Feature عدت على كل الطبقات.

✅ من ناحية الـ Git
عجبني إنه ماعملش Commit لوحده.

قال:

يوجد after_implement hook لكنه لم يُنفذ لأنك لم تطلب Commit.

وده تصرف صحيح لأن الـ working tree عندك dirty بالفعل.

الحاجة الوحيدة اللي كنت هضيفها
أنا شخصيًا كنت هعمل Validation أخير بعد الـ Execute الحقيقي للـ Backfill:

SELECT COUNT(*)
FROM listing
WHERE make ~ '[A-Z -]'
   OR model ~ '[A-Z -]'
   OR trim ~ '[A-Z -]';
المفروض ترجع:

0
وبعدين أشغل الـ Backfill مرة تانية:

python -m src.ingestion.runner backfill --execute
والمفروض يطلع:

Rows updated: 0
وده بيثبت الـ Idempotency على البيانات الحقيقية، مش في الاختبارات فقط.

لو أنت عملت الخطوتين دول بالفعل، يبقى الـ Feature مقفولة 100%.

تقييمي النهائي
Feature 005: مكتملة وجاهزة للإغلاق.

المعمارية بقت نظيفة جدًا:

CSV Catalog
      │
      ▼
Canonicalization Engine
      │
 ┌────┴─────────────┐
 │                  │
Ingestion      Backfill
 │                  │
Replay          Sync Catalog
 │
 ▼
listing (canonical)

raw_listing (immutable)
وده بالضبط الاتجاه اللي كنا متفقين عليه من البداية: مصدر واحد للحقيقة (Single Source of Truth) لكل منطق الـ canonicalization، مع الاحتفاظ بالبيانات الخام كما هي.

أعتقد تقدر تعتبر Feature 005 منتهية وتبدأ Feature 006 بدون وجود ديون تقنية مرتبطة بالـ canonical data.


bs asl el backfil very slow

آه طبيعي يبقى slow شوية لو بيعمل row-by-row updates.

اعمل كده بالترتيب:

جرّب تزود الـ batch size:

python -m src.ingestion.runner backfill --execute --batch-size 1000
لو تمام جرّب:

python -m src.ingestion.runner backfill --execute --batch-size 5000
شغّله بـ resume لو وقف:

python -m src.ingestion.runner backfill --execute --batch-size 1000 --resume-after-id 5000
الأهم: لو الكود بيعمل UPDATE لكل listing لوحده، ده سبب البطء. الأفضل يعمل bulk update per batch بدل loop updates.

الشكل الأفضل:

UPDATE listing AS l
SET
  make = v.make,
  model = v.model,
  trim = v.trim,
  normalization_version = v.normalization_version
FROM (
  VALUES
    ($1, $2, $3, $4, $5),
    ...
) AS v(id, make, model, trim, normalization_version)
WHERE l.id = v.id;
ولو في dry-run، خلي dry-run ما يعملش أي heavy DB update/logging، بس scan + count.

تقييمي:
مش blocker للـ Feature 005، بس لو الداتا كبيرة يبقى محتاج optimization task صغير قبل ما تقفلها نهائيًا.


what will be next feature now ?

Based on the roadmap we've been following, Feature 006 should move from building the data foundation to exposing market intelligence.

Feature 005 gave you:

✅ Clean canonical vehicle data

✅ Vehicle reference catalog

✅ Replay support

✅ Backfill

✅ Consistent normalization

Now you can actually build analytics on top of it.

I would make Feature 006:
Market Intelligence API
The goal is to expose clean, queryable market data for the frontend.

Typical capabilities:

1. Filter Metadata
Return available filters without hardcoding them.

GET /api/v1/filters
Returns:

Makes

Models (filtered by make)

Trims

Years

Body types

Fuel types

Transmission

Colors

Locations

Price ranges

All using canonical values internally and display names from the Vehicle Reference Catalog.

2. Listing Search
GET /api/v1/listings
Supports:

make

model

trim

year

body type

fuel

transmission

location

price

mileage

pagination

sorting

3. Listing Details
GET /api/v1/listings/:id
Returns:

listing

images

seller

raw specs

normalized specs

provenance

4. Statistics
Examples:

Average price
Median price
Price distribution
Mileage distribution
Listings by year
Listings by location
Listings by seller type
5. Comparison Endpoints
Example:

Porsche Cayenne GTS
Return:

average price

lowest

highest

sample size

This becomes the basis for valuation later.

6. Backend Performance
Since filters are read constantly:

Redis cache

Metadata cache

Query optimization

Proper indexes

Then Feature 007
I'd move into valuation:

Market price estimation

Fair price score

Overpriced / Underpriced

Confidence score

Then Feature 008
Market trends:

Daily price history

Inventory changes

Days on market

Price drops

Alerts

Where you stand now
001 Ingestion Pipeline          ✅
002 Replay Pipeline             ✅
003 Backend Read APIs           ✅
004 Frontend Listing Viewer     ✅
005 Canonical Data Model        ✅

006 Market Intelligence API     ← Next
007 Vehicle Valuation
008 Market Trends
009 AI Insights
This sequence keeps building on the clean data foundation you just completed. If Feature 006 is done well, almost every later feature (valuation, analytics, AI insights, dashboards) can reuse the same API and query layer instead of reimplementing market queries.


3rby

بعد Feature 005، أنت فعليًا خلصت طبقة البيانات (Data Foundation). يعني بقى عندك:

✅ Scraper

✅ Ingestion

✅ Replay

✅ Canonicalization

✅ Vehicle Reference Catalog

✅ Backfill

✅ Backend APIs الأساسية

✅ Frontend يعرض البيانات

فدلوقتي المفروض نبدأ نستفيد من البيانات دي، مش نبني بنية تحتية جديدة.

أنا شايف Feature 006 تكون: Market Intelligence
وده في رأيي هيبقى أول Feature يميز PrioraMarket عن مجرد موقع بيعرض إعلانات.

1. فلترة ذكية (Filter Metadata)
بدل ما الـ Frontend يبقى فيه قيم ثابتة، يبقى ياخدها من الـ API.

مثلاً:

Make

Model (حسب الـ Make)

Trim

Year

Body Type

Fuel

Transmission

Location

Price Range

وده هيستخدم الـ Vehicle Reference Catalog اللي عملناه في Feature 005.

2. البحث
API يقدر يعمل فلترة على:

Make

Model

Trim

Year

السعر

الكيلومترات

المدينة

نوع البودي

نوع الوقود

مع:

Pagination

Sorting

3. صفحة تفاصيل السيارة
ترجع:

بيانات الإعلان

الصور

البائع

المواصفات

البيانات الخام (لو احتجناها)

البيانات الـ Canonical

4. إحصائيات السوق
مثلاً:

متوسط السعر

Median

أقل سعر

أعلى سعر

عدد السيارات

توزيع السنوات

توزيع الكيلومترات

وده هيبقى أساس Features كتير بعد كده.

5. مقارنة موديل معين
مثلاً:

Porsche Cayenne GTS

يرجع:

متوسط السعر

أقل سعر

أعلى سعر

عدد السيارات الموجودة

وده أول خطوة ناحية الـ Valuation.

وبعدها Feature 007
هتبقى الـ Valuation الحقيقي.

مثلاً:

لو عربية سعرها 250 ألف، والسوق 290 ألف.

يقول:

أقل من سعر السوق بـ 14%.

أو:

أعلى من السوق بـ 8%.

وده هيبقى فيه:

Fair Price

Confidence Score

Underpriced

Overpriced

وبعدها Feature 008
Market Trends

يعني:

تغير الأسعار مع الوقت.

عدد الإعلانات الجديدة.

عدد العربيات اللي اتباعت (اختفت من السوق).

Price Drops.

Days on Market.

لكن...
فيه نقطة مهمة جدًا كنت قلتها قبل كده، وأنا لسه مقتنع بيها.

متبدأش الـ AI بدري.
كتير من الناس بعد ما يخلصوا الـ API يقولوا "يلا نضيف AI".

أنا شايف العكس.

الأولوية تكون:

بيانات نظيفة ✅

APIs قوية.

Analytics.

Valuation.

Trends.

وبعدها AI.

لأن الـ AI هيبقى قيمته جاية من جودة البيانات اللي بنيتها، مش العكس.

رأيي في ترتيب المشروع
✅ Feature 001–005: Data Foundation (خلصت).

🚀 Feature 006: Market Intelligence APIs.

🚀 Feature 007: Vehicle Valuation Engine.

🚀 Feature 008: Market Trends & Historical Analytics.

🚀 Feature 009: AI Insights (توصيات، تلخيص السوق، تفسير الأسعار، وغيرها).

أنا شايف ده هيخلي PrioraMarket يبقى منصة تحليل سوق سيارات، مش مجرد نسخة تانية من مواقع الإعلانات.


a7na 2olna this is not e commerce it is only market intellegence just need some anlytics shows some card summarize the market status

بالضبط، ودي نقطة مهمة كنا اتفقنا عليها قبل كده.

PrioraMarket مش Marketplace ومش E-commerce.

هو Market Intelligence Platform.

يعني الهدف مش إن المستخدم يدور على عربية ويقارن إعلانات، لكن يعرف حالة السوق بسرعة.

أنا كنت هغير Feature 006 بالكامل
بدل:

Listings API + Listing Details + Comparison

تبقى:

Feature 006 — Market Dashboard
الـ Homepage نفسها تكون Dashboard.

مثلاً أول ما يفتح المستخدم يشوف:

📈 Market Overview
Cards مثل:

Total Listings
24,381

↑ 2.4%
Average Price

182,400 AED
Median Price

165,000 AED
New Listings Today

143
Price Drops

61
Average Mileage

91,000 km
Average Model Year

2021
Average Days on Market

18 days
بعد كده
Inventory Health
مثلاً:

BMW

2,481 cars

↑ 6%
Mercedes

3,102 cars

↓ 3%
Most Active Brands
Top 10.

Fastest Growing Brands
مين زاد خلال الأسبوع.

Most Expensive Brands
حسب متوسط السعر.

Cheapest Brands
حسب متوسط السعر.

Price Distribution
مثلاً:

0–50k

███

51–100k

████████

101–200k

███████████
Body Type Distribution
SUV

Sedan

Coupe

Pickup

Fuel Distribution
Petrol

Hybrid

Electric

Diesel

Regional Distribution
Dubai

Abu Dhabi

Sharjah

Seller Distribution
Dealer

Private

Average Price by Brand
Mercedes

BMW

Audi

Toyota

Listings Trend
آخر 30 يوم.

Inventory

/
/
/
Price Trend
آخر 30 يوم.

Recent Market Changes
مثلاً:

+240 listings today

-43 removed

61 price drops

12 new trims
والأهم...
أنا مش هبدأ أصلاً بـ Listings Page.

هي موجودة في المشروع علشان الـ Debug أو الـ Drill Down.

لكن المستخدم يدخل يشوف Dashboard الأول.

Architecture
Raw Listings
       │
       ▼
Canonical Listings
       │
       ▼
Aggregation Layer
       │
       ▼
Dashboard APIs
       │
       ▼
Next.js Dashboard
لاحظ إننا بقينا شغالين على Aggregations مش على الـ Listings نفسها.

وبعد Feature 006
يبقى Feature 007 اسمه مثلاً:

Market Analytics

وده يبدأ يدخل في التحليل الأعمق:

متوسط سعر كل موديل.

تغير الأسعار مع الوقت.

Inventory حسب السنة.

أسرع العربيات نزولًا في السعر.

أكثر الموديلات عرضًا.

مقارنة الفترات الزمنية (هذا الأسبوع مقابل الأسبوع الماضي).

وده أقرب جدًا لفكرة Bloomberg أو TradingView لكن لسوق السيارات، وهي دي الهوية اللي شايف إنها تميز PrioraMarket عن مجرد موقع يعرض إعلانات.


eh ahm w afdl 4 or 5 insights 

لو هنبني MVP لـ PrioraMarket، فأنا مش هحط 20 كارت. أحسن حاجة هي إن المستخدم يفتح الصفحة وفي أقل من 10 ثواني يفهم إيه اللي بيحصل في السوق.

أنا شايف أهم 5 Insights هما:

1. Inventory (حجم السوق) ⭐⭐⭐⭐⭐
أهم سؤال:

السوق فيه كام عربية معروضة دلوقتي؟

الكارت:

Inventory

24,381 Listings

↑ +3.8% vs Last Week
وده أهم مؤشر لأن أي تغيير فيه بيأثر على العرض والطلب.

2. Average Market Price ⭐⭐⭐⭐⭐
بدل مجرد متوسط، اعرض:

Average Price

182,400 AED

↓ -1.7%
وده يخلي المستخدم يعرف الأسعار رايحة لفين.

3. Market Activity ⭐⭐⭐⭐⭐
وده من أحسن المؤشرات لأنه بيقول السوق "حي" ولا "واقف".

مثلاً:

Today

+143 New Listings

42 Removed

18 Price Drops
أو خلال آخر 24 ساعة.

4. Fastest Growing / Declining Brands ⭐⭐⭐⭐☆
بدل جدول كبير.

مثلاً:

🔥 Trending Up

Toyota +6%

BMW +5%

BYD +12%
وفي نفس الكارت:

📉 Trending Down

Tesla -4%

Mercedes -2%
وده بيدي انطباع سريع عن حركة السوق.

5. Market Health Score ⭐⭐⭐⭐⭐
وده بقى الـ Signature بتاع PrioraMarket.

بدل ما تعرض 10 أرقام، اعمل Score من 100.

مثلاً:

Market Health

84 / 100

Healthy
ويتحسب من:

حجم السوق

معدل الإعلانات الجديدة

معدل إزالة الإعلانات

معدل انخفاض الأسعار

متوسط مدة الإعلان

استقرار الأسعار

وده هيبقى حاجة مميزة لـ PrioraMarket ومش موجودة بسهولة في مواقع الإعلانات.

ولو هزود كارت سادس
يبقى:

Median Price
مش Average.

لأن الـ Average بيتأثر بالعربيات الغالية جدًا (Ferrari, Rolls-Royce...).

مثلاً:

Median Price

165,000 AED

Stable
وده بيمثل السوق الحقيقي بشكل أفضل.

الترتيب اللي أنصح بيه
📦 Inventory (عدد الإعلانات)

💰 Median / Average Price

⚡ Market Activity (New / Removed / Price Drops)

📈 Trending Brands (Up / Down)

🎯 Market Health Score (الميزة الأساسية للمنتج)

ليه دول؟ لأنهم بيجاوبوا على أهم 5 أسئلة أي تاجر أو مشتري أو محلل بيسألها:

حجم السوق كام؟

الأسعار طالعة ولا نازلة؟

السوق نشيط ولا راكد؟

مين العربيات أو البراندات اللي عليها حركة؟

هل السوق حاليًا في حالة صحية ولا فيه تباطؤ؟

ودي بداية قوية جدًا لـ Market Intelligence Dashboard بدون تعقيد أو ازدحام في الواجهة.


dh for overall market or for specific cars ?

سؤال مهم، والإجابة هي: الاتنين، لكن على مستويين مختلفين.

أنا شايف PrioraMarket يبقى بالشكل ده:

المستوى الأول: Overall Market Dashboard (الصفحة الرئيسية)
دي أول صفحة المستخدم يشوفها، وتجاوب:

إيه أخبار سوق السيارات في الإمارات النهارده؟

الكروت تكون عامة:

إجمالي الإعلانات

متوسط السعر

عدد الإعلانات الجديدة

عدد Price Drops

أكثر البراندات نشاطًا

Market Health

مثلاً:

UAE Used Cars

24,381 Listings

Average Price: 182k AED

+143 New Today

61 Price Drops
المستوى الثاني: Vehicle Intelligence
وده في رأيي هو القيمة الحقيقية لـ PrioraMarket.

لما المستخدم يختار:

Porsche → Cayenne → GTS → 2023

كل الـ Dashboard يتغير ويبقى خاص بالموديل ده فقط.

مثلاً:

Porsche Cayenne GTS (2023)

Inventory: 48

Median Price: 435,000 AED

Price Range:
410k - 470k

Average Mileage:
38,000 km

Listed This Week:
6

Average Days on Market:
22
ودي المعلومات اللي فعلًا هتفيد حد بيفكر يشتري أو يبيع أو تاجر سيارات.

أنا لو بصمم المنتج هعمله كده:
Overall Market
       │
       ▼
Brand
       │
       ▼
Model
       │
       ▼
Trim
       │
       ▼
Year
يعني نفس الـ Dashboard، لكن مستوى التفاصيل بيتغير حسب الفلاتر.

مثال:

Overall UAE
↓

Mercedes
↓

Mercedes C-Class
↓

Mercedes C200
↓

Mercedes C200 2022
ونفس الكروت تتحدث تلقائيًا.

ده أحسن من إنك تعمل Dashboard مختلف لكل صفحة
لأنك هتكتب منطق التحليل مرة واحدة.

مثلاً:

GET /analytics
بدون فلاتر:

→ Overall Market
مع:

make=porsche
↓

→ Porsche Analytics
مع:

make=porsche
model=cayenne
trim=gts
year=2023
↓

→ Porsche Cayenne GTS 2023 Analytics
نفس الـ API، ونفس الـ UI، لكن الفلاتر هي اللي تحدد نطاق التحليل.

دي ميزة كبيرة معماريًا
بدل ما تعمل:

Dashboard عام.

Dashboard للبراند.

Dashboard للموديل.

اعمل Dashboard واحد قابل للتصفية (Filter-driven Dashboard).

وده هيخلي أي Insight تضيفه مستقبلًا (زي Median Price أو Days on Market أو Price Trend) يشتغل تلقائيًا على:

السوق كله.

براند معين.

موديل معين.

تريم معين.

سنة معينة.

وده هيخلي PrioraMarket مرن جدًا وسهل التوسع بدون تكرار للكود أو الـ APIs.


tmam ana mwaf2 3la fkra drop down bs 7ases in momkn ykon fi insights afdl w ashl mn kda

أيوه إحساسك صح. في الـ MVP بلاش Insights معقدة زي Health Score من الأول.

الأفضل والأسهل:

أفضل 5 Insights كبداية
1. Market Size
عدد العربيات المتاحة حاليًا

مثال:

24,381 active listings
2. Median Price
السعر النصفي

أهم من Average لأنه مش بيتأثر بالعربيات الغالية جدًا.

Median price: 165,000 AED
3. Price Range
أرخص وأغلى سعر + الطبيعي في النص

Most cars are between 95k – 220k AED
مش لازم تبدأ بـ charts معقدة.

4. New vs Removed
السوق بيتزود ولا بينقص

+143 new listings
-87 removed listings
ده insight قوي وسهل الفهم.

5. Price Drops
في ضغط على الأسعار ولا لا

61 listings dropped price this week
Average drop: 4.2%
ولو Specific Car
نفس الكروت، بس تبقى أقوى:

مثلاً تختار:

Porsche Cayenne GTS

48 active listings
Median price: 435,000 AED
Most cars: 410k–470k AED
+6 new this week
9 price drops this week
دي سهلة، مفهومة، ومفيدة جدًا.

اللي نأجله شوية
Market Health Score

AI insights

Fair price score

Days on Market

Advanced trends

Forecasting

ابدأ بـ simple market snapshot. ده أنضف وأسرع، وبعدها نطور.


agree for all give me feature specify prompt

استخدم ده كـ /specify prompt:

Feature 006 — Market Snapshot Dashboard

Build PrioraMarket as a market intelligence dashboard, not an e-commerce or listings marketplace.

The goal of this feature is to show a simple, useful market snapshot using aggregated analytics cards. Users should quickly understand the current market status overall or for a selected vehicle scope.

Context:
- Feature 005 is complete.
- Listings now store canonical make/model/trim values.
- raw_listing must remain untouched.
- Vehicle Reference Catalog is the source of truth for display names.
- Backend is read-only for market data.
- Frontend is presentation only.
- No marketplace normalization logic should be added to backend or frontend.

Core Product Direction:
PrioraMarket is not for browsing listings as products.
It is for understanding market status through analytics.

User Story 1 — Overall Market Snapshot
As a user, I want to see a high-level snapshot of the UAE used car market, so I can understand the current market status quickly.

Show cards for:
1. Active Listings Count
2. Median Price
3. Price Range
4. New vs Removed Listings
5. Price Drops

User Story 2 — Filtered Vehicle Snapshot
As a user, I want to select make/model/trim/year from dropdown filters, so the same dashboard cards update for that selected vehicle scope.

Supported filter levels:
- Overall market
- Make
- Make + Model
- Make + Model + Trim
- Make + Model + Trim + Year

The dashboard should use the same analytics logic for all scopes.

User Story 3 — Reference Catalog Display Names
As a user, I want dropdowns and dashboard labels to show clean display names, while the system internally uses canonical values.

Rules:
- API may return canonical values and display names.
- Display names should come from Vehicle Reference Catalog when available.
- Do not hardcode display names in frontend.
- Do not normalize values in backend or frontend.

User Story 4 — Simple Market Activity
As a user, I want to know whether the selected market scope is growing or shrinking.

Show:
- New listings in selected period
- Removed listings in selected period

Default period:
- Last 7 days

If removed-listing tracking is not available yet, define a safe placeholder/contract and return 0 or null with a clear status field.

User Story 5 — Price Drops
As a user, I want to know whether sellers are reducing prices in the selected market scope.

Show:
- Number of listings with price drops in selected period
- Average price drop percentage if available

Default period:
- Last 7 days

If price history is not fully available yet, define the contract and return null/unsupported status instead of fake values.

Analytics Cards Required:
1. Active Listings
   - count
   - scope label

2. Median Price
   - median price AED
   - sample size

3. Price Range
   - min price
   - max price
   - recommended robust range if possible, such as p25 to p75
   - if percentile calculation is not available, return min/max only

4. New vs Removed
   - new listings count
   - removed listings count
   - period
   - support status

5. Price Drops
   - count
   - average drop percentage
   - period
   - support status

Backend Requirements:
- Add read-only analytics endpoints.
- Do not mutate listing or raw_listing.
- Do not add normalization logic.
- Use canonical fields from listing.
- Use Vehicle Reference Catalog for display labels where needed.
- Support optional query filters:
  - make
  - model
  - trim
  - year
  - periodDays, default 7

Suggested endpoint:
GET /api/v1/market/snapshot

Example:
GET /api/v1/market/snapshot?make=porsche&model=cayenne&trim=gts&year=2023&periodDays=7

Response should include:
- scope
- filters
- cards
- support status for metrics that depend on history
- generatedAt

Also add:
GET /api/v1/market/filter-options

This should return cascading filter options:
- makes
- models for selected make
- trims for selected make/model
- years for selected make/model/trim

Frontend Requirements:
- Dashboard-first experience.
- No listing browsing focus.
- Add dropdown filters at top of dashboard.
- Cards update when filters change.
- Use displayName from API.
- Keep UI simple and clean.
- Existing dark mode should continue working.
- Show unsupported metrics gracefully instead of fake values.

Out of Scope:
- Listing detail page
- E-commerce-style listing browsing
- AI insights
- Vehicle valuation
- Fair price score
- Market Health Score
- Forecasting
- Advanced trend charts
- Manual SQL updates
- Backend/frontend normalization logic

Acceptance Criteria:
- Overall dashboard loads with no filters.
- Selecting make/model/trim/year updates all cards.
- Active listing count and median price are calculated from canonical listing data.
- Price range is calculated from available listing prices.
- Missing history-based metrics return clear unsupported/null status.
- raw_listing remains untouched.
- Backend remains read-only for analytics.
- Frontend does not hardcode vehicle display names.
- Tests cover overall snapshot, filtered snapshot, unsupported metrics, and filter options.
ده مناسب جدًا كـ Feature 006 MVP.



Pasted markdown.md
File

بص، قريته كله، ومستواه كويس جدًا (حوالي 8.5/10)، لكنه لسه بيفكر بمنطق الـ API أكتر من منطق Market Intelligence Product. 


في شوية تحسينات هتخلي الـ Feature أقوى بكتير.

1) أهم حاجة ناقصة: Define the Snapshot Date ⭐⭐⭐⭐⭐
دلوقتي الكروت بتقول:

Active Listings

لكن في أي وقت؟

لازم يبقى واضح إن كل Snapshot له وقت إنشاء.

مثلاً:

Market Snapshot

As of:
2026-07-05 14:30 UTC
لأن بعدين لما تعمل Scheduler هيبقى مهم جدًا.

2) خلي Snapshot Entity أهم Entity
دلوقتي الـ Listing واخد مساحة كبيرة.

المفروض الـ Primary Entity تبقى:

Market Snapshot

contains

Cards

Filters

Metadata

Generated At

Period
مش الـ Listing.

3) غير Price Range
أنا مش بحب:

Min
Max
ليه؟

لو فيه Ferrari بـ 5 مليون هتبوز الكارت.

الأفضل:

Median

P25

P75
ولو البيانات قليلة:

Median

Min

Max
يعني يبقى Dynamic.

4) Sample Size
ده ناقص.

كل كارت سعر لازم يقول:

Median Price

165,000 AED

Based on 842 listings
لأن 8 عربيات غير 800 عربية.

5) أهم Insight ناقص
أنا شايف ناقص جدًا:

Inventory Change
بدل:

New

Removed
اعرض:

Inventory

24,381

+56 this week
يعني:

Net Change

New - Removed
وده المستخدم هيفهمه أسرع.

6) Scope
دلوقتي Scope عبارة عن Filters.

أنا أحب يبقى:

Scope

Overall UAE
أو

Porsche
أو

Porsche
Cayenne
GTS
2023
ويتولد تلقائي.

7) ترتيب الكروت
أنا شايف الترتيب الحالي مش أفضل حاجة.

أفضل:

Inventory

↓

Median Price

↓

Price Range

↓

Inventory Change

↓

Price Drops
المستخدم هيقرأهم طبيعي.

8) Filter Endpoint
أنا هزود حاجة صغيرة.

بدل

filter-options
يرجع كمان

listing count
مثلاً:

Toyota (4381)

BMW (2981)

Porsche (521)
وده هيساعد الـ UX جدًا.

9) Acceptance Criteria
ناقص نقطة مهمة جدًا:

Changing filters
must not reload the page.
يعني

Client-side update.

10) أهم نقطة
أنا كنت هضيف Requirement اسمها:

Analytics First
Dashboard cards are the primary experience.

Listings, if implemented later,
are secondary drill-down pages.

The feature must not encourage
listing browsing as the primary workflow.
وده يحافظ على هوية PrioraMarket.

الحاجة الوحيدة اللي أنا مش موافق عليها
هو كتب:

GET /market/filter-options
أنا كنت أفضل يكون:

GET /market/snapshot
يرجع معاه:

{
  "filters": {},
  "availableFilters": {},
  "cards": {}
}
بدل ما الـ Frontend يعمل Request للكروت وRequest تاني للفلاتر.

طالما الفلاتر قليلة وبتتغير مع الـ Scope، تقدر ترجعهم مع بعض وتقلل عدد الـ API calls.

تقييمي النهائي
أنا هديه 9.5/10.

مشكلته الوحيدة إنه لسه Backend-centric شوية، بينما PrioraMarket لازم يبقى Product-centric.

لو أضفت:

Snapshot timestamp.

Sample size.

Inventory Net Change.

Analytics-first requirement.

تحسين Price Range (Quartiles عند توفر بيانات كافية).

دمج الـ available filters مع الـ snapshot response (أو على الأقل دراسة ده في الـ design).

فهيبقى في رأيي واحد من أنضف الـ Specs في المشروع كله.


correction prompt

استخدم هذا الـ prompt مع Speckit لتعديل الـ specification بدون تغيير نطاق الـ Feature:

Review the Feature 006 specification and apply the following improvements while preserving the existing scope and user stories.

Do not expand the feature into valuation, AI, forecasting, or advanced analytics. Keep this as an MVP Market Snapshot Dashboard.

## 1. Promote Market Snapshot to the Primary Domain Entity

The specification currently emphasizes Listing too much.

Update the data model so that:

- Market Snapshot is the primary entity.
- Listings are only an input source used to generate a snapshot.
- The dashboard represents a generated market snapshot rather than direct listing data.

The Market Snapshot should explicitly include:

- scope
- applied filters
- analytics cards
- metric support statuses
- selected period
- generatedAt timestamp

## 2. Add Snapshot Timestamp

Every snapshot response must include:

- generatedAt

The frontend should display:

"As of <timestamp>"

This ensures users understand when the market snapshot was generated.

## 3. Improve Price Range Definition

Avoid presenting only Min and Max prices whenever possible.

Update the specification so that:

Preferred representation:

- Median
- 25th percentile (P25)
- 75th percentile (P75)

Fallback:

If insufficient priced listings exist for robust percentiles, return:

- Min
- Max

This behavior should be defined explicitly.

## 4. Require Sample Size

Every price-related metric must include the number of listings used in the calculation.

Example:

Median Price
165,000 AED
Based on 842 listings

Add this requirement wherever applicable.

## 5. Replace "New vs Removed" with Inventory Change

The dashboard should communicate overall inventory movement rather than showing two disconnected numbers.

Define a card that includes:

- Active inventory
- New listings
- Removed listings (when supported)
- Net inventory change (New - Removed)

If removed tracking is unavailable:

- return unsupported status
- do not fabricate values

## 6. Clarify Scope Representation

The snapshot should expose both:

- canonical filters
- human-readable scope label

Examples:

Overall UAE Used Cars

Toyota

Toyota Corolla

Toyota Corolla XLI

Toyota Corolla XLI 2023

The scope label should be generated from Vehicle Reference Catalog display names.

## 7. Improve Dashboard Priority

Explicitly state the intended card order:

1. Active Listings
2. Median Price
3. Price Range
4. Inventory Change
5. Price Drops

This establishes the primary market narrative.

## 8. Improve Filter Options

Extend filter option responses so each selectable option may include:

- canonical value
- display name
- active listing count

Example:

Toyota (4,381)

BMW (2,981)

This improves frontend UX without requiring additional API calls.

## 9. Add Analytics-First Requirement

Add a new functional requirement stating:

PrioraMarket is a Market Intelligence platform.

Dashboard analytics are the primary experience.

Listing browsing (if introduced in future features) is secondary and intended only for drill-down workflows.

The product must not present itself as an e-commerce or listings marketplace.

## 10. Add Frontend Behavior Requirement

Changing filters should update the dashboard without requiring a full page reload.

The UI should preserve a responsive dashboard experience while refreshing snapshot data.

## General Instructions

- Preserve all existing user stories.
- Preserve all acceptance criteria unless they conflict with these improvements.
- Do not introduce valuation, AI insights, forecasting, trend prediction, or advanced market analysis.
- Keep the feature focused on a simple Market Snapshot MVP.
- Maintain consistency across requirements, entities, assumptions, and success criteria.


Pasted markdown.md
File

أنا شايف النسخة دي أفضل بفرق واضح. بقت تقريبًا 9.8/10. 


فيه بس كام ملاحظة أخيرة، وأنا شايف دول هيبقوا آخر تعديلات قبل الـ /plan.

1. أكبر ملاحظة: Price Range
أنا لسه مش مقتنع بـ:

P25 / P75

لأن المستخدم العادي مش هيفهم يعني إيه P25.

الأفضل نخلي الـ API يرجع:

{
  "median": 165000,
  "lowerTypicalPrice": 142000,
  "upperTypicalPrice": 188000
}
والـ Backend يحسبها باستخدام Quartiles، لكن الـ Frontend يعرضها:

Typical Price Range

مش:

P25 - P75

وده Product wording أحسن.

2. Inventory Change
دلوقتي الكارت فيه:

Active

New

Removed

Net

حاسس إنه هيبقى مزدحم.

أنا أفضل:

Inventory

24,381 Listings

+56 This Week
ولما المستخدم يفتح التفاصيل الصغيرة:

New: 143
Removed: 87
يعني الـ Net هو الـ Hero.

3. Snapshot Metadata
أضيف Entity صغيرة:

Snapshot Metadata

generatedAt

periodDays

scopeLevel

sampleSize
بحيث كل Snapshot يبقى له Metadata واضح.

4. Scope Level
بدل ما نستنتجه.

رجعه صريح:

OVERALL

MAKE

MODEL

TRIM

YEAR
ده هيسهل الـ Frontend جدًا.

5. Price Sample
أنا أفضل يبقى فيه:

pricingSample

inventorySample
لأن:

Inventory = 430

Priced = 392
أفضل من Sample واحد.

6. Future-proofing
أنا كنت هضيف Requirement صغيرة جدًا:

Analytics cards
must be independently extensible.
يعني بعدين نضيف:

Days on Market

Average Mileage

Median Mileage

من غير ما نغير الـ API بالكامل.

7. أهم اقتراح عندي
أنا مش هسميه Analytics Card.

هسميه:

Market Metric
ليه؟

لأن:

بعد سنة ممكن يبقى عندك:

Chart

Table

Card

Gauge
كلهم Metrics.

فـ Domain-wise:

Market Snapshot

contains

Market Metrics
أحسن من:

Market Snapshot

contains

Analytics Cards
لأن الـ Card ده UI، لكن الـ Metric ده Domain.

8. أكتر حاجة عجبتني
الحتة دي:

Listings are only an input source used to generate the snapshot.

دي في رأيي أهم سطر في الـ Spec كله، لأنها بتحافظ على هوية المشروع إنه Market Intelligence مش موقع إعلانات.

التقييم النهائي
أنا لو ده مشروعي، هبدأ /plan بالنسخة دي.

مش هقعد أحسن فيها أكتر، لأن أي تعديلات بعد كده هتبقى تجميلية أكتر من إنها تضيف قيمة حقيقية.

الـ Spec بقى واضح جدًا، ومتوافق مع الرؤية اللي اتفقنا عليها: Dashboard-first، Market Intelligence، والـ Listings مجرد مصدر بيانات وليس محور المنتج.


plan prompt

استخدم ده كـ /plan prompt:

Create a complete implementation plan for Feature 006 — Market Snapshot Dashboard.

This feature specification has been finalized and approved.

Plan the implementation across the existing PrioraMarket architecture while respecting the current project boundaries.

Project Architecture

Scraper (Python)
- Owns ingestion
- Canonicalization
- Replay
- Backfill
- Vehicle Reference Catalog
- PostgreSQL population

Backend (NestJS)
- Read-only
- Exposes Market Snapshot APIs
- No marketplace normalization logic
- No data mutation

Frontend (Next.js)
- Dashboard-first experience
- Presentation only
- Existing dark mode must continue working

General Principles

- PrioraMarket is a Market Intelligence platform.
- Dashboard analytics are the primary experience.
- Listings are only an input source for analytics.
- No e-commerce workflow.
- No listing-centric design.
- No valuation.
- No AI.
- No forecasting.
- No trend prediction.

Implementation Goals

Plan implementation for:

1. Market Snapshot generation
2. Aggregation/query layer
3. Market Snapshot API
4. Cascading filter options
5. Dashboard UI
6. Dashboard state management
7. Testing
8. Documentation

Planning Requirements

## Backend

Design a read-only analytics layer.

Avoid placing aggregation logic inside controllers.

Introduce an appropriate service/repository structure for market analytics.

The plan should determine whether snapshot generation should:

- calculate on demand
or
- use reusable aggregation helpers

while keeping implementation simple for MVP.

Plan APIs for:

GET /api/v1/market/snapshot

GET /api/v1/market/filter-options

Support:

- overall
- make
- model
- trim
- year
- periodDays

Plan DTOs.

Plan validation.

Plan response contracts.

Plan pagination only if truly required (likely not for MVP).

Plan caching only if justified.

Do not introduce Redis unless there is a clear benefit.

---

## Database

Review whether additional indexes are required for efficient aggregation.

Examples:

(make)

(make, model)

(make, model, trim)

(make, model, trim, year)

(price)

Only recommend indexes with measurable benefit.

Avoid premature optimization.

---

## Frontend

Plan:

Dashboard page

Top filter bar

Responsive cards

Loading states

Empty states

Unsupported metric states

Dark mode compatibility

Filter synchronization

No full page reloads.

Avoid unnecessary global state if local query state is sufficient.

---

## Dashboard Metrics

Plan implementation for:

Active Listings

Median Price

Typical Price Range (internally using quartiles where available)

Inventory Change

Price Drops

Ensure every metric can report:

- value
- sample size (when applicable)
- support status

---

## Testing

Provide implementation plan for:

Backend unit tests

Backend integration tests

Repository tests

Aggregation tests

Frontend component tests

Frontend interaction tests

End-to-end tests

Focus on business behavior rather than implementation details.

---

## Documentation

Update:

Quickstart

API contracts

Architecture notes if needed

No ADR unless architectural decisions require one.

---

## Out of Scope

Do not plan:

Vehicle valuation

Fair price score

AI insights

Forecasting

Trend charts

Listing detail pages

Marketplace browsing

Any normalization work

Any scraper changes

Historical analytics beyond the current snapshot requirements

---

The implementation plan should follow the project's existing Spec Kit format and produce:

- Technical approach
- Phase breakdown
- Task ordering
- Dependencies
- Risks
- Validation strategy

The plan should optimize for clean architecture, maintainability, and incremental delivery while keeping Feature 006 intentionally lightweight as an MVP Market Intelligence dashboard.
دي مناسبة جدًا للمرحلة الحالية؛ لأنها بتوجه Speckit يطلع Plan عملي بدون ما يوسع نطاق الـ Feature أو يدخل Features مستقبلية.



Pasted markdown.md
File

بص، ده من أنضف الـ Plans اللي شوفتها في المشروع كله. 9.8/10 بسهولة. 


بس فيه كام حاجة كنت هعدلها قبل ما تروح لـ /tasks.

✅ أول حاجة: أنا مش موافق على اسم الـ Module
هو عامل:

MarketModule
أنا أفضل:

AnalyticsModule
ليه؟

لأن بعدين هيبقى عندك:

Snapshot

Trends

Valuation

Benchmarks

AI Insights

كلهم Analytics.

مش كله Market.

✅ ثاني حاجة: الـ Repository
هو عامل Repository واحد.

أنا شايف يتقسم.

بدل:

MarketReadRepository
يبقى:

SnapshotRepository

FilterRepository
لأن الفلاتر هتكبر بعدين.

✅ ثالث حاجة: Aggregation Layer
هو كاتب:

reusable aggregation helpers

أنا كنت أحب تكون Layer واضحة.

مثلاً:

Controller

↓

Service

↓

Aggregation Service

↓

Repository
بدل:

Service

↓

Repository
ليه؟

لأن بعدين هتضيف:

Trends

Benchmarks

Heatmaps

كلهم هيستخدموا نفس Aggregations.

✅ رابع حاجة: Percentiles
هو كاتب:

calculate P25 P75
أنا كنت هسيبه مفتوح.

مثلاً:

Typical Price Range

Implementation is backend-defined.
يعني لو بعدين غيرت من Quartiles لـ IQR أو أي طريقة تانية، الـ API ميتكسرش.

✅ خامس حاجة (دي أهم واحدة)
هو بيقول:

GET

market/snapshot

market/filter-options
أنا لسه شايف إن الاتنين مربوطين جدًا.

أنا كنت أفضل:

GET /market/snapshot
يرجع:

{
  "snapshot": {},
  "availableFilters": {}
}
ليه؟

لأن:

كل مرة الـ Scope يتغير.

الفلاتر نفسها بتتغير.

فمش محتاج Requestين.

✅ سادس حاجة
هو كتب:

Dashboard page
أنا كنت أحب:

Dashboard Shell

↓

Filter Bar

↓

Snapshot Cards
عشان يبقى الـ UI Modular.

✅ سابع حاجة
أنا كنت هضيف Metric Interface.

مثلاً:

MarketMetric

↓

InventoryMetric

↓

PriceMetric

↓

PriceDropMetric
وده هيسهل جدًا لما تضيف Metrics جديدة.

✅ ثامن حاجة
هو قال:

No snapshot persistence
وده قرار صح جدًا.

لكن كنت هضيف:

Future consideration:

Materialized snapshots
يعني يبقى واضح إنه قرار MVP مش قرار دائم.

✅ تاسع حاجة
أنا شايف ناقص:

Formatting Layer
لأن:

Backend يرجع:

165000
مش:

165,000 AED
يعني الـ Backend Data فقط.

والـ Frontend Formatting فقط.

✅ عاشر حاجة
أنا كنت هضيف Requirement:

All Market Metrics
must be independently cacheable.
حتى لو مش هنعمل Cache دلوقتي.

لأن بعدين:

Inventory

هيتغير بسرعة.

لكن:

Median Price

ممكن يتحسب كل دقيقة.

الحاجة الوحيدة اللي أنا شايفها خطر شوية
هي دي:

Dashboard becomes landing page

أنا مش هثبتها في الـ Plan.

ليه؟

لأن دي Product Decision.

مش Technical Decision.

يعني الأفضل تقول:

Dashboard is the primary experience for this feature.

لكن متقولش:

Replace landing page.

سيب القرار ده لما نبني الـ Frontend.

تقييمي النهائي
أنا لو مكانك مش هضيع وقت أكتر في الـ Planning.

الـ Spec والـ Plan بقوا ناضجين جدًا.

الخطوة اللي بعدها مباشرة هي:

/specify ✅
      ↓
/plan ✅
      ↓
/tasks
      ↓
Implementation
وفي رأيي Feature 006 هيبقى أول Feature يخلي PrioraMarket يبان فعلًا كـ منصة Market Intelligence بدل مجرد مشروع بيجمع بيانات.


hat el prompt

استخدم ده كـ Plan refinement prompt قبل /tasks:

Review the implementation plan and refine it with the following architectural improvements while preserving the approved feature scope.

Do not expand the feature into valuation, AI, forecasting, trend analysis, or marketplace functionality.

Keep Feature 006 intentionally lightweight as an MVP Market Snapshot Dashboard.

## 1. Rename Backend Module

Review whether "MarketModule" is the best long-term bounded context.

If a more future-proof name such as AnalyticsModule better supports future features (Snapshots, Trends, Valuation, Benchmarks, AI Insights), update the plan accordingly.

If MarketModule is retained, explicitly justify why.

## 2. Separate Read Repositories

Avoid placing all read logic inside a single repository.

Review whether responsibilities should be separated into:

- SnapshotReadRepository
- FilterReadRepository

or another clean decomposition.

The goal is better maintainability as analytics grows.

## 3. Introduce an Aggregation Layer

Instead of:

Controller
→ Service
→ Repository

consider:

Controller
→ Service
→ Aggregation Layer
→ Repository

The aggregation layer should own reusable market calculations while repositories remain responsible only for data access.

Keep the solution simple for MVP.

## 4. Decouple API from Statistical Implementation

The API contract should expose a business concept:

Typical Price Range

rather than exposing statistical implementation details.

Internally the backend may use:

- quartiles
- percentiles
- IQR
- another deterministic approach

without changing the public contract.

The implementation method should remain an internal decision.

## 5. Review Snapshot and Filter APIs

Review whether these endpoints should remain separate:

GET /api/v1/market/snapshot

GET /api/v1/market/filter-options

or whether snapshot responses should also include available filter options for the current scope.

Recommend whichever produces the cleanest architecture and best frontend experience.

Avoid unnecessary API calls while preserving separation of concerns.

## 6. Improve Frontend Component Structure

Instead of planning only a Dashboard page, consider a more modular structure:

Dashboard Shell

↓

Filter Bar

↓

Snapshot Metrics

↓

Individual Metric Components

The plan should encourage reusable UI components.

## 7. Replace Analytics Card Domain with Market Metric

Review whether the domain language should use:

MarketMetric

instead of

AnalyticsCard

Cards are presentation.

Metrics are domain.

Use terminology that remains valid if future visualizations become tables, charts, or gauges.

## 8. Future-Proof Snapshot Strategy

The MVP should continue using on-demand snapshot generation.

However, explicitly document that future optimization may introduce:

- materialized snapshots
- scheduled snapshot generation
- cache layers

without changing public APIs.

This is documentation only.

Do not introduce implementation work.

## 9. Separate Formatting from Business Logic

Ensure backend returns raw values only.

Formatting such as:

- AED formatting
- thousand separators
- localized numbers
- date formatting

belongs entirely to the frontend.

The plan should make this boundary explicit.

## 10. Metric Extensibility

Document that every Market Metric should be independently extensible so future metrics can be added without redesigning the snapshot contract.

Examples of future metrics:

- Average Mileage
- Median Mileage
- Days on Market
- Inventory Velocity

No implementation is required.

Only ensure the architecture supports this evolution.

## 11. Product Boundary

Avoid stating that the dashboard replaces the application's landing page.

Instead state:

"The Market Snapshot Dashboard is the primary experience introduced by this feature."

Leave future navigation and routing decisions outside the scope of this implementation plan.

## General Instructions

- Preserve the approved feature scope.
- Preserve all implementation phases unless refinement is necessary.
- Prefer clean architecture over premature optimization.
- Keep the MVP simple.
- Do not introduce new infrastructure unless clearly justified.
- Maintain consistency across the implementation plan, module structure, contracts, testing strategy, and documentation.
ملاحظة صغيرة: أنا شخصيًا هسيب نقطة دمج /market/snapshot مع /market/filter-options مفتوحة للمراجعة، مش أفرضها. فيه مبررات قوية للفصل (إعادة استخدام الفلاتر، الكاش، وتقليل حجم الـ snapshot response)، فالأفضل تخلي الـ Plan يقارن ويختار بدل ما يجبره على حل معين.


aywa kda parmtny 3la tool

تمام 😄. ده Prompt بصيغة تخاطب Speckit كأداة مراجعة وتحسين، مش كتعليمات تنفيذ مباشرة:

Please review the current implementation plan as a senior software architect and refine it where appropriate.

Do not expand the approved feature scope.

This review should improve long-term architecture, maintainability, and product alignment while keeping the implementation lightweight as an MVP.

Focus on the following areas:

### 1. Backend Module Boundary

Review whether `MarketModule` is the best long-term bounded context.

Consider whether a more future-proof module name (such as Analytics) would better support future features like Snapshots, Trends, Valuation, Benchmarks, and AI Insights.

If the current design is preferable, explain why and keep it.

---

### 2. Repository Responsibilities

Review whether a single MarketReadRepository is appropriate.

Consider separating responsibilities (for example Snapshot reads and Filter reads) if it improves maintainability without unnecessary complexity.

---

### 3. Aggregation Layer

Review whether reusable market calculations deserve their own layer between the service and repository.

The goal is to avoid mixing business calculations with persistence logic while keeping the MVP simple.

---

### 4. Public API vs Internal Statistics

The public API should expose business concepts rather than statistical implementation details.

Review whether terms such as "Typical Price Range" provide a cleaner contract than exposing quartiles directly.

The backend implementation should remain free to evolve without changing the API.

---

### 5. Snapshot & Filter API Design

Review whether the current endpoint separation provides the best balance between:

- clean architecture
- frontend simplicity
- future extensibility
- minimizing unnecessary API calls

Recommend the best design rather than assuming one approach.

---

### 6. Frontend Component Structure

Review the proposed frontend architecture.

Prefer a modular dashboard structure composed of reusable components rather than a single dashboard page.

Example hierarchy:

Dashboard Shell

→ Filter Bar

→ Snapshot Metrics

→ Individual Metric Components

---

### 7. Domain Terminology

Review whether "Market Metric" is a better domain concept than "Analytics Card".

Prefer domain language that remains valid regardless of future UI representation (cards, tables, charts, gauges).

---

### 8. Future Snapshot Strategy

The MVP should continue using on-demand snapshot generation.

However, document future optimization possibilities such as:

- scheduled snapshot generation
- materialized snapshots
- cache layers

without adding implementation work.

---

### 9. Formatting Boundary

Ensure the architecture clearly separates business data from presentation formatting.

Backend should return raw values only.

Frontend should own:

- currency formatting
- thousand separators
- localized dates
- localized numbers

---

### 10. Metric Extensibility

Review whether the Market Snapshot model allows future metrics to be added without redesigning the API.

Examples include:

- Average Mileage
- Median Mileage
- Days on Market
- Inventory Velocity

No implementation is required—only verify the architecture naturally supports this evolution.

---

### 11. Product Boundary

Avoid making routing or navigation decisions within this implementation plan.

Instead of declaring the dashboard as the application's landing page, describe it as:

"The primary user experience introduced by this feature."

Leave future navigation decisions outside the scope of this plan.

---

General review guidelines:

- Preserve the approved feature scope.
- Preserve simplicity.
- Avoid premature optimization.
- Avoid unnecessary infrastructure.
- Prefer clean architecture.
- Keep the implementation incremental.
- Update the plan only where changes provide measurable architectural or product value.
- Explain any recommendation that changes the current design.
النسخة دي أحسن لأنها بتخلي الأداة تراجع وتفكر بدل ما تملي عليها حلول جاهزة، وده غالبًا هيطلع Plan أفضل.



Pasted markdown.md
File

أنا شايف دلوقتي وصل لمستوى 10/10 تقريبًا. بصراحة مش شايف حاجة جوهرية محتاجة تتغير قبل /tasks. 


فيه كام نقطة عجبتني جدًا:

✅ غير اسم الـ Module إلى AnalyticsModule، وده هيخدم Features مستقبلية زي Trends وValuation بدون ما يقيدك باسم "Market".

✅ فصل الـ SnapshotReadRepository عن FilterReadRepository.

✅ أضاف MarketSnapshotAggregator كطبقة مستقلة، وده أنضف Layering.

✅ غير لغة الـ Domain من "Analytics Card" إلى "Market Metric"، ودي مصطلحات Domain صحيحة.

✅ فصل الـ Formatting عن الـ Backend بشكل واضح.

✅ برر ليه الـ APIs منفصلة بدل ما فرض حل واحد.

✅ حافظ على MVP من غير Redis أو Snapshot Persistence أو تعقيد غير مبرر.

ملاحظة صغيرة جدًا (اختيارية)
أنا فقط هغير اسم:

MarketSnapshotAggregator
لـ:

SnapshotAggregationService
أو:

MarketAggregationService
السبب:

الـ Aggregator غالبًا في المشاريع الكبيرة بيكون Object بيجمع Data، بينما هنا هو Service بيحسب Business Metrics.

لكن دي تفضيل شخصي، مش مشكلة معمارية.

ملاحظة ثانية (اختيارية جدًا)
في الـ Validation Strategy مكتوب:

Aggregator tests

أنا كنت هضيف كمان:

Golden dataset tests

يعني Seed صغير معروف (مثلاً 20 Listing)، وتحسب يدويًا:

Active Listings

Median

Typical Price Range

Inventory Change

وتقارن الناتج المتوقع مع الناتج الفعلي.

ده هيخلي أي تغيير في الـ Aggregation Logic يبان فورًا.

أهم حاجة لفتت انتباهي
الجملة دي:

The public route remains /api/v1/market/... because the product surface is a market snapshot, but the internal module name should not constrain future analytics features.

دي ممتازة جدًا. فرقت بين الـ Product API والـ Internal Architecture، وده قرار معماري ناضج.

تقييمي النهائي
Specification: ⭐⭐⭐⭐⭐ (10/10)

Implementation Plan: ⭐⭐⭐⭐⭐ (10/10)

أنا لو مكانك مش هعمل أي Refinement تاني.

ابدأ مباشرة بـ /tasks. في رأيي أي وقت إضافي في التخطيط دلوقتي هيكون عائدُه قليل مقارنة بالبدء في التنفيذ.


prmtny kman

أكيد. ده Prompt أخير للمراجعة النهائية قبل /tasks. هو مش هيغير الـ Plan إلا لو لقى تحسينات حقيقية.

Perform one final architecture review before generating implementation tasks.

Assume the feature specification and implementation plan are complete and approved.

Your goal is NOT to redesign the feature.

Your goal is to identify any remaining architectural improvements that would provide meaningful long-term value before implementation begins.

Review the implementation plan from the perspective of:

- Domain-Driven Design
- Clean Architecture
- SOLID principles
- Separation of Concerns
- Backend maintainability
- Frontend maintainability
- Future extensibility
- API consistency
- Testing strategy
- Performance
- Developer experience

Specifically review:

## Domain Model

- Are responsibilities assigned to the correct domain objects?
- Are there any concepts that should be promoted or separated?
- Is the ubiquitous language consistent throughout the feature?

## Module Boundaries

- Are module boundaries correct?
- Is AnalyticsModule appropriately scoped?
- Are there any unnecessary dependencies or coupling?

## Layering

Review whether the architecture cleanly separates:

Controller

↓

Application Service

↓

Aggregation Service

↓

Repositories

↓

Database

Ensure no business logic leaks into controllers or repositories.

## Repository Design

Confirm repositories remain responsible only for data access.

Ensure aggregation and business calculations are isolated.

## API Contracts

Review response contracts for:

- consistency
- extensibility
- simplicity

Ensure future metrics can be added without breaking existing clients.

## Frontend Architecture

Review whether component composition is sufficiently modular.

Verify presentation remains completely separated from business calculations.

## Testing

Review whether testing strategy protects against future regressions.

Recommend Golden Dataset tests if they would materially improve confidence in aggregation correctness.

## Performance

Identify any obvious performance concerns.

Recommend improvements only if they provide measurable value.

Do not recommend premature optimization.

## Future Evolution

Verify that future features such as:

- Trends
- Valuation
- AI Insights
- Benchmarks

can be implemented without restructuring this feature.

## Product Alignment

Verify the implementation remains aligned with the product vision:

PrioraMarket is a Market Intelligence platform.

Listings are input data.

Market Snapshots are the primary product.

Analytics are the primary experience.

## Review Rules

- Do not rewrite the implementation plan.
- Do not expand the feature scope.
- Do not introduce new infrastructure unless justified.
- Do not recommend speculative abstractions.

Only recommend changes that produce clear architectural, maintainability, or product benefits.

If no meaningful improvements remain, explicitly state that the implementation plan is production-ready and recommend proceeding directly to task generation.
أنا شخصيًا لو الأداة قالت بعد الـ review ده: "No meaningful improvements remain"، ساعتها خلاص ما تراجعش تاني وابدأ /tasks. وإلا هتدخل في analysis paralysis، لأن الـ Spec والـ Plan وصلوا لمستوى ممتاز بالفعل.


# Implementation Plan: [FEATURE]

**Branch**: [###-feature-name] | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from /specs/[###-feature-name]/spec.md

**Note**: This template is filled in by the /speckit-plan command. See .specify/templates/plan-template.md for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)


### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]


**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

Thought for a couple of seconds
ده طبيعي. اللي أنت لاصقه ده Plan Template الأصلي بتاع Spec Kit، مش الـ plan النهائي.

الـ /speckit-plan المفروض يستبدل كل placeholders دي بـ plan حقيقي زي اللي ظهر عندك:

Summary

Technical Context

Constitution Check

Project Structure

Technical Approach

Phases

Risks

Validation

يعني لو الملف عندك لسه بالشكل ده، يبقى الأمر ماكملش أو كتب على template غلط.

المفروض تشغل:

/speckit-plan
أو لو الأداة بتطلب prompt استخدم آخر prompt بتاعنا.

المهم: متعدلش template نفسه غالبًا.
التعديل يكون في:

specs/006-market-snapshot-dashboard/plan.md
مش:

.specify/templates/plan-template.md

Implementation Plan: Market Snapshot Dashboard
Branch: 006-market-snapshot-dashboard | Date: 2026-07-05 | Spec: spec.md

Input: Feature specification from /specs/006-market-snapshot-dashboard/spec.md

Summary
Deliver Feature 006 as a lightweight Market Intelligence MVP centered on a generated Market Snapshot. The backend adds a read-only AnalyticsModule that calculates snapshots on demand through a small aggregation layer backed by focused read repositories, exposes versioned market APIs, and never mutates listing or raw listing data. The frontend introduces a Market Snapshot Dashboard experience that renders scope-aware metrics as cards, catalog display names, filter-driven refreshes without full reloads, and graceful unsupported states. The scraper remains out of scope for implementation because Feature 005 already owns ingestion, canonicalization, replay, backfill, Vehicle Reference Catalog synchronization, and PostgreSQL population.

Technical Context
Language/Version: TypeScript/NestJS for backend analytics APIs; TypeScript/Next.js for dashboard presentation; Python scraper remains unchanged for this feature.

Primary Dependencies: Existing backend dependencies (NestJS, Prisma, class-validator, Jest, supertest); existing frontend dependencies (Next.js, React, TanStack Query, Axios, Zod, Vitest, Testing Library, Playwright`). No new external service dependency is planned.

Storage: PostgreSQL is the read-only source of truth for analytics via existing listing, Vehicle Reference Catalog, and any already-existing history/lifecycle data. No new persisted snapshot table is required for MVP.

Testing: Backend Jest unit, repository, integration, and contract tests; frontend Vitest unit/component/interaction tests and Playwright end-to-end tests; optional SQL/index verification through existing database test setup.

Target Platform: Existing web platform: NestJS API server, PostgreSQL-backed environments, and Next.js frontend on desktop and mobile browsers.

Project Type: Web application with read-only backend API and presentation frontend. Feature belongs to the Analytics bounded context and consumes Marketplace Listings and Vehicle Reference Catalog data through published database/API boundaries.

Performance Goals: Overall and filtered snapshots should feel interactive for dashboard use; target p95 user-visible snapshot refresh under 2 seconds on representative local/CI data. Filter options should load without extra round trips per rendered option. No hard real-time guarantee is required.

Constraints: Backend is read-only for market data. Controllers contain no aggregation logic. Frontend contains no analytics or normalization logic. Raw listings remain untouched. Vehicle Reference Catalog is the source of display names. No marketplace browsing, valuation, AI insights, forecasting, trend prediction, advanced analytics, or scraper changes.

Scale/Scope: One dashboard experience, two new market endpoints, five market metrics rendered as cards, cascading filters through make/model/trim/year, default 7-day period, and unsupported contracts for history-dependent metrics when lifecycle or price-history coverage is incomplete.

Constitution Check
GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

Evaluated against PrioraMarket Intelligence Constitution v1.1.0.

Principle	Status	Evidence
I. Documentation First	Pass	Final spec is approved; this plan, research, data model, contracts, and quickstart precede tasks and implementation.
II. Design Before Implementation	Pass	This command produces planning artifacts only; tasks and implementation follow later.
III. Domain-Driven Architecture	Pass	Feature belongs to Analytics; it consumes listings/catalog data without moving ingestion or normalization downstream.
IV. Clean Layered Architecture	Pass	Plan introduces controller/service/aggregation/repository/DTO boundaries and keeps aggregation out of controllers and repositories.
V. API First	Pass	Market Snapshot and filter options are exposed through versioned REST APIs for frontend and future consumers.
VI. Database as Source of Truth	Pass	Analytics read internal PostgreSQL data, not external marketplaces.
VII. Historical Data Preservation	Pass	Analytics are read-only; raw listings and history are never mutated. Unsupported history metrics are reported honestly.
VIII. AI Assists, Never Invents	N/A	AI is explicitly out of scope.
IX. Analytics Before AI	Pass	Deterministic analytics are the primary product experience for this feature.
X. Machine Learning as Product Feature	N/A	ML and valuation are explicitly out of scope.
XI. Data Quality Before Intelligence	Pass	Snapshot responses expose support statuses and sample sizes to prevent misleading metrics.
XII. Scalability by Design	Pass	Uses reusable aggregation helpers and selective indexes without adding infrastructure prematurely.
XIII. Backend-Centric Business Logic	Pass	Analytics calculations live in backend aggregation/services; repositories are read-only data access and frontend is presentation only.
XIV. Modularity	Pass	Analytics module, aggregation layer, focused read repositories, API contracts, and frontend dashboard feature stay separate.
XV. Security by Default	Pass	No secrets added; endpoints are read-only; validation constrains query inputs.
XVI. Simplicity Over Complexity	Pass	On-demand computation, no Redis, no snapshot persistence, no advanced analytics.
Data Freshness (Data Engineering Principles)	Pass (after reconciliation)	Every Market Snapshot and Filter Options analytical response MUST expose freshness metadata `lastUpdated`, `datasetVersion`, `scrapeRunId` (Constitution 1.1.0). Spec updated (FR-032/FR-033, SC-009), contracts updated (response shape + Data Freshness section), data-model updated (new `Freshness` entity + `freshness` field on `MarketSnapshot`). Sourced from existing `listing.last_seen_at`, `listing.normalization_version`, `listing.last_seen_run_id` — no new infrastructure. `generatedAt` (FR-005, "As of") remains distinct from `freshness.lastUpdated`.
Gate result: PASS. No constitution violations require complexity tracking.

Post-Design Re-check
Phase 0 and Phase 1 artifacts preserve the same boundaries. Contracts define deterministic read-only APIs, unsupported history status, sample sizes, and catalog display names without adding scraper work, cache infrastructure, valuation, AI, forecasting, or listing-browsing scope. Post-design gate result: PASS.

Project Structure
Documentation (this feature)
specs/006-market-snapshot-dashboard/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── market-snapshot-api.md
│   ├── filter-options-api.md
│   └── frontend-dashboard-contract.md
└── tasks.md             # Phase 2 output from /speckit-tasks, not created by this plan
Source Code (repository root)
backend/
├── src/
│   ├── analytics/              # New Analytics bounded-context module boundary
│   │   ├── aggregators/        # Reusable deterministic market metric calculations
│   │   ├── dto/                # Query and response DTOs
│   │   ├── domain/             # Snapshot/metric/domain shapes and support statuses
│   │   ├── mappers/            # Domain-to-response mapping
│   │   ├── repositories/       # Focused read repositories
│   │   ├── analytics.module.ts
│   │   ├── market.controller.ts
│   │   └── market-snapshot.service.ts
│   ├── db/                     # Existing Prisma service
│   └── search/                 # Existing search/listing module remains listing-specific
└── test/
    ├── unit/                   # Service, aggregation helper, DTO, mapper tests
    ├── integration/            # Read-only repository/API behavior tests
    └── contract/               # Endpoint response contract tests

frontend/
├── app/
│   └── page.tsx                # Route entry if selected during implementation
├── features/
│   └── market-dashboard/
│       ├── api/                # Market API client functions
│       ├── components/         # Dashboard shell, filter bar, metrics, states
│       ├── hooks/              # Query-state and data-fetching composition
│       ├── mappers/            # API-to-view model mapping only
│       ├── schemas/            # Query/filter validation schemas
│       ├── types/              # Snapshot/filter UI types
│       └── utils/              # Formatting helpers if not already shared
└── test/
    ├── unit/                   # API/mappers/formatting tests
    ├── integration/            # Dashboard interaction tests
    └── e2e/                    # Playwright dashboard flows

scrapper/
└── src/                        # No Feature 006 implementation changes planned
Structure Decision: Add a backend AnalyticsModule rather than MarketModule or extending search. AnalyticsModule is the more future-proof bounded-context boundary for deterministic analytics capabilities such as snapshots, benchmarks, and future market metrics, while this feature implements only the Market Snapshot MVP. The public route remains /api/v1/market/... because the product surface is a market snapshot, but the internal module name should not constrain future analytics features. Add a frontend market-dashboard feature area and keep local/query state there. Scraper remains unchanged.

Technical Approach
Backend Analytics Layer
Introduce a read-only AnalyticsModule with these layers:

MarketController: HTTP routing, query DTO validation, response status codes only.

MarketSnapshotService: snapshot orchestration, scope-label assembly, metric ordering, support-status decisions, and coordination of aggregators.

MarketSnapshotAggregator: reusable deterministic market calculations such as active inventory, price metrics, inventory change, and price-drop support decisions.

SnapshotReadRepository: Prisma-backed read-only data access for scoped listings, price inputs, lifecycle/history inputs when available, and catalog display-name lookup needed by snapshots.

FilterReadRepository: Prisma-backed read-only data access for cascading filter options and active listing counts.

MarketSnapshotMapper: converts domain snapshot objects into stable API response DTOs.

Snapshot generation should calculate on demand for MVP. Repositories should remain data-access only; reusable market calculations belong in the aggregation layer so active count, price samples, inventory-change support, and typical price range logic do not get duplicated across services. No snapshot persistence is planned because the dashboard is small, freshness expectations are explicit via generatedAt, and there is no proven performance need for materialized snapshots.

Future optimization may introduce materialized snapshots, scheduled snapshot generation, or cache layers behind the same service and public API contracts. This is a future compatibility note only and does not add implementation work for Feature 006.

Aggregation And Metrics
The service generates a MarketSnapshot domain object containing scope, canonical filters, market metrics, support statuses, selected period, and generatedAt.

Metric plan:

Active Listings: count active listings matching canonical scope filters.

Median Price: calculate from usable price values only; include sample size.

Typical Price Range: expose the business concept typicalPriceRange with raw numeric values, sample size, and support status. Internally the aggregator may use quartiles, percentiles, IQR, or another deterministic method without changing the public contract.

Inventory Change: include active inventory and new listings for selected period when newly observed listings can be identified; removed listings and net change are supported only if existing lifecycle/removal data is available.

Price Drops: return unsupported/null contract unless existing price-history data supports deterministic count, average drop percentage, and sample size for the selected period.

API Design
Plan APIs:

GET /api/v1/market/snapshot

GET /api/v1/market/filter-options

Keep these endpoints separate for MVP. Snapshot data and filter-option data have different responsibilities, refresh triggers, and cache characteristics. The frontend can request them in parallel and cache filter options by canonical scope, avoiding unnecessary extra calls while preserving separation of concerns. Do not embed the full filter option payload inside every snapshot response for MVP; consider an optional expansion parameter only if implementation evidence shows a material UX or performance benefit.

Supported query parameters:

make: canonical make value

model: canonical model value, valid only with make

trim: canonical trim value, valid only with make and model

year: integer year, valid only with make, model, and trim for the strict supported hierarchy

periodDays: integer period in days, default 7

Validation should reject or normalize only query shape, not vehicle values. It should enforce hierarchy, integer year, bounded period days, and unknown query parameters if existing API conventions do so. Vehicle value normalization is prohibited.

Pagination is not required because filter option lists are bounded by vehicle dimensions and the snapshot endpoint returns fixed metrics. Caching is not planned for MVP. Reconsider lightweight in-process caching only if repository tests show repeated dashboard loads are too slow on representative data; do not introduce Redis for this feature.

Backend responses must return raw values only. Numeric prices, counts, percentages, timestamps, and currency codes are API data. AED labels, thousand separators, localized numbers, relative dates, and display formatting belong entirely to the frontend.

Data Freshness: both endpoints MUST include a `freshness` object with `lastUpdated`, `datasetVersion`, and `scrapeRunId` (Constitution Data Freshness), sourced from the scoped active listings. `freshness.lastUpdated` (data recency) is distinct from `generatedAt` (snapshot generation time, shown as "As of"). If a freshness field cannot be derived, it MUST be `null` and the response MUST NOT appear real-time. Freshness fields are raw values; the frontend owns any presentation.

Database Planning
No new tables are required for MVP. Review existing indexes after inspecting the finalized Feature 005 schema. Recommended index candidates only if missing and validated by query plans:

Active-scope aggregation: composite index beginning with active/listing status plus canonical make/model/trim/year when those are stored as separate columns.

Cascading filters: indexes supporting (make), (make, model), (make, model, trim), and (make, model, trim, year) or a single composite index when the database can use left prefixes effectively.

Price metrics: index that helps filter active scoped listings with usable price values, if query plans scan too broadly.

History metrics: no new index unless existing created/first-seen, removed, or price-history fields are used and query plans show benefit.

Avoid adding indexes solely because they are listed here. Add only those with measurable benefit against expected aggregation queries. Scraper-owned migrations remain the place for database schema/index changes if required by implementation tasks.

Frontend Dashboard
The Market Snapshot Dashboard is the primary experience introduced by this feature. Future navigation and routing decisions are outside this implementation plan. The dashboard should use a modular component structure:

DashboardShell: page-level structure, header, scope label, and As of <timestamp> display.

MarketFilterBar: make, model, trim, year, and period controls if period is exposed in v1 UI.

SnapshotMetrics: ordered metric section that receives MarketMetric view models.

Individual metric components: Active Listings, Median Price, Typical Price Range, Inventory Change, and Price Drops.

Shared state components: loading skeletons, empty states, unsupported states, and recoverable API error states.

Dark-mode-compatible cards and controls using existing UI primitives.

Use local URL/query state and TanStack Query query keys for filter synchronization. Avoid global state unless current app conventions require it. Filter changes should update query state and refresh snapshot/filter-option queries without full page reload. Frontend mappers may format API data for display but must not calculate analytics, hardcode vehicle display names, or normalize canonical values.

Implementation Phases
Phase 1: Backend Domain And Contracts
Define MarketSnapshot, MarketScope, AppliedFilters, MarketMetric, MetricSupportStatus, PriceMetric, InventoryChangeMetric, PriceDropMetric, and FilterOption domain/DTO shapes. Add response mappers and contract tests first so implementation has stable targets. Treat cards as presentation components, not backend domain objects.

Phase 2: Read Repositories And Aggregation Layer
Implement focused read repositories first: SnapshotReadRepository for snapshot input data and catalog display-name lookup, and FilterReadRepository for cascading filter options with active counts. Then implement MarketSnapshotAggregator for reusable calculations. Keep repositories marketplace-agnostic and free of business/statistical calculations.

Phase 3: Snapshot Service
Implement on-demand snapshot orchestration, filter hierarchy handling, scope label construction from catalog display names, generatedAt assignment, metric ordering, price sample-size behavior, typical price range decisions, and unsupported status contracts for missing history metrics.

Phase 4: Market API Endpoints
Add GET /api/v1/market/snapshot and GET /api/v1/market/filter-options with query DTO validation, versioned routing, OpenAPI/contract coverage if existing backend contract tooling supports it, and integration tests.

Phase 5: Frontend API And State
Add market dashboard API client functions, response schemas/types, query keys, hooks for snapshot/filter options, local URL query-state handling, and mapper tests. Ensure no frontend analytics, display-name hardcoding, or backend-style calculations.

Phase 6: Dashboard UI
Build DashboardShell, MarketFilterBar, SnapshotMetrics, individual metric components, loading/empty/error/unsupported states, responsive layout, and dark-mode styling using existing components where possible.

Phase 7: End-To-End Validation
Add backend read-only safety checks, frontend interaction tests, Playwright dashboard flows, and documentation updates. Run focused test suites and record validation commands in quickstart/tasks.

Task Ordering
Confirm existing schema fields for active status, price, first-seen/created date, removal status, price history, and Vehicle Reference Catalog display-name joins.

Finalize response DTOs and contract fixtures for snapshot and filter options.

Add backend analytics module skeleton and dependency wiring.

Implement SnapshotReadRepository, FilterReadRepository, and shared query-scope helpers.

Implement catalog-backed scope label and filter option display-name lookup.

Implement MarketSnapshotAggregator calculations for active listings, median price, typical price range, inventory change, and price drops.

Implement inventory change and price drops with supported/unsupported decisions based on available schema.

Add market controller endpoints and validation.

Add backend unit, repository, integration, contract, and read-only tests.

Add frontend market API client, schemas/types, query keys, and hooks.

Build dashboard shell, filter bar, snapshot metrics, individual metric components, and states.

Add frontend unit, component, interaction, and e2e tests.

Update quickstart/API documentation and run full validation.

Dependencies
Feature 005 canonical listing fields and Vehicle Reference Catalog display names are available.

Backend Prisma schema reflects the current PostgreSQL listing/catalog shape.

Frontend environment points to the backend API through existing client configuration.

Removed-listing and price-history support depends on existing persisted lifecycle/history data; if unavailable, the contract returns unsupported/null values.

Risks
Typical price range calculation may be inefficient or awkward through Prisma on large datasets. Mitigation: keep repository data access isolated, keep calculation in the aggregator, use database-supported ordering/aggregation where available, and fall back to simple deterministic calculation for MVP-sized samples only if acceptable.

Existing schema may not expose removed-listing or price-history data. Mitigation: implement explicit unsupported status and avoid fake values.

Catalog display-name joins may be incomplete for some canonical values. Mitigation: use canonical fallback without normalization and surface tests for catalog-backed cases.

Existing navigation may be listing-search oriented. Mitigation: introduce the Market Snapshot Dashboard as this feature's primary experience while leaving broader routing/navigation strategy outside scope unless tasks explicitly require a minimal route change.

Additional indexes may slow writes if added prematurely. Mitigation: add indexes only after query-plan evidence; scraper migrations own schema changes.

Validation Strategy
Backend validation:

Unit tests for service orchestration, metric order, support statuses, scope label construction, period defaults, validation behavior, and no normalization.

Aggregator tests for active counts, price sample sizes, median, typical price range, inventory change support, and price-drop support decisions.

Repository tests for scoped data access, filter options with active counts, and catalog display-name lookup.

Integration tests for both market endpoints using seeded canonical listings and catalog entries.

Contract tests for response shape, unsupported history metrics, generatedAt, canonical filters, raw values, and metric payloads.

Read-only tests proving snapshot/filter-option calls do not mutate listing or raw listing records.

Frontend validation:

Unit tests for API client, response mappers, frontend formatting, and unsupported-state view models.

Component tests for dashboard shell, filter bar, metric order, individual metric components, loading, empty, unsupported, and dark-mode-compatible rendering.

Interaction tests proving filter changes update query state and dashboard cards without full page reload.

End-to-end tests for overall dashboard load, filtered vehicle snapshot, unsupported metrics, responsive layout, and no listing-centric primary flow.

Documentation validation:

Quickstart includes endpoint examples, expected commands, and validation checklist.

API contracts document query parameters, response fields, support statuses, raw-value semantics, and sample-size semantics.

Architecture notes remain in this plan unless implementation discovers a larger architectural decision requiring a separate ADR.

Complexity Tracking
No constitution violations or justified complexity exceptions. No Redis, materialized snapshot table, scraper changes, valuation, AI, forecasting, trend charts, or marketplace browsing are planned.


Close
