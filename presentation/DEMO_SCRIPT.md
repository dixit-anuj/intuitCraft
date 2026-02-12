# Interview Demo Script

## 15-Minute Presentation Flow

---

### **[0-2 minutes] Introduction & Problem Statement**

**Script:**

"Thank you for the opportunity to present today. I've built a sales forecasting system for QuickBooks Commerce that addresses a critical business need.

**The Problem**: Merchants struggle with inventory management - they either overstock, tying up capital, or understock, missing sales opportunities. They need accurate predictions of what will sell and when.

**The Solution**: An AI-powered forecasting system that predicts top-selling products by category across different time periods - week, month, or year.

Let me show you what I've built."

**[Share screen - Show README]**

---

### **[2-4 minutes] System Architecture Overview**

**Script:**

"Before diving into the demo, let me quickly explain the architecture.

**[Open: docs/ARCHITECTURE_DIAGRAM.md]**

The system consists of five main layers:

1. **Frontend**: React dashboard with TypeScript, styled with Intuit brand colors and built for accessibility (WCAG AA)

2. **API Layer**: FastAPI backend - I chose this because it's asynchronous by default, has automatic API documentation, and is one of the fastest Python frameworks

3. **ML Layer**: This is the heart of the system - an ensemble model combining:
   - **XGBoost** for capturing complex feature interactions across 25 engineered features
   - **Holt-Winters Exponential Smoothing** for per-category weekly seasonality
   - By combining both with a 60/40 weighted average, we achieve R² 0.96 on a 30-day holdout

4. **Data Layer**: 
   - Synthetic training data with category-specific baselines and realistic patterns (5% noise)
   - Model trained on 2 years of daily data (5,848 records, 730 days across 8 categories)

5. **Production Design**:
   - PostgreSQL for transactional data
   - Redis for caching
   - AWS deployment architecture with auto-scaling

**Key Design Decision**: Ensemble approach - XGBoost alone misses seasonality, Holt-Winters alone can't use engineered features. Together, they complement each other."

---

### **[4-9 minutes] Live Demo**

**Script:**

"Let me show you the system in action."

**[Start backend if not running]**
```bash
cd backend
source venv/bin/activate
python -m app.main
```

**[Start frontend if not running]**
```bash
cd frontend
npm start
```

**[Open browser to http://localhost:3000]**

#### Part 1: Dashboard Overview (1 min)

"Here's the main dashboard. Notice the Intuit-themed design. You can see:
- **8 product categories** with predictions from the trained model
- **Time period selector** - switch between week, month, or year
- Each card shows predicted sales, revenue, and growth trend
- All elements are keyboard-navigable with clear focus indicators

Let me drill into a category."

**[Click or press Enter on a category card]**

#### Part 2: Detailed Analysis (2 min)

"Now we see:
1. **Historical trend** (blue line) - actual sales data
2. **Forecast** (dashed line) - model predictions going forward
3. **Confidence interval** (shaded area) - 95% uncertainty range

The model captures:
- Weekly patterns (weekends vs. weekdays)
- Category-specific baselines
- Overall trends

On the right, we have **top products** ranked by predicted sales with growth percentages. These are actionable insights for inventory decisions."

#### Part 3: Different Time Periods (1 min)

**[Click "Year" button]**

"Switch to yearly forecast - notice how:
- Predictions extend further
- Confidence intervals widen with more uncertainty
- But trends remain consistent

**[Click "Week" button]**

And weekly forecasts give tighter confidence intervals, more precise."

#### Part 4: Accessibility Features (30 sec)

"I also want to highlight the accessibility features:
- Tab through all interactive elements
- Screen reader support with ARIA labels
- Focus indicators for keyboard users
- Skip-to-content link
- All following WCAG AA guidelines"

#### Part 5: API Documentation (30 sec)

**[Open http://localhost:8000/docs in new tab]**

"The backend provides a full REST API with:
- **Interactive documentation** (Swagger/OpenAPI)
- Try out endpoints directly
- Model version and accuracy score in responses"

---

### **[9-12 minutes] Technical Deep Dive**

**Script:**

"Let me explain the technical details.

#### ML Model Architecture

**Feature Engineering** (25 features):
1. **Time features**: day_of_week, month, quarter, is_weekend (6 features)
   - Captures cyclical shopping patterns

2. **Lag features**: sales from 7, 14, 30 days ago (3 features)
   - Recent sales predict future sales

3. **Rolling statistics**: 7-day and 30-day moving averages and standard deviations (4 features)
   - Captures trends and volatility

4. **Cyclical encoding**: sin/cos for day_of_week, month, day_of_year
5. **Trend**: days_since_start
6. **Momentum**: 7/30 ratio, 7/14 ratio
7. **Interaction**: weekend × category, volatility ratio
8. **Category encoding** (1 feature)

**Why This Matters**:
- Simple models use just date and sales
- We use 25 features for richer predictions

#### Ensemble Strategy

```
XGBoost (60% weight)        Holt-Winters (40% weight)
        ↓                           ↓
    Captures complex          Handles weekly
    feature interactions      seasonality per category
        ↓                           ↓
            Ensemble = Best of both
            
Result: R² 0.96 on 30-day holdout
```

#### Why Holt-Winters Over Prophet?

'Prophet is a great library, but it has heavy C/Stan dependencies that cause installation issues across environments. Holt-Winters from statsmodels is lightweight, well-understood, and captures weekly seasonality just as well for our use case. It's the pragmatic, production-reliable choice.'

#### Training Pipeline

1. Generate synthetic data (seed=42, reproducible, 5% noise)
2. Engineer 25 features (cyclical, trend, momentum, interaction, volatility)
3. Train XGBoost on all categories (R² 0.999 train, 0.978 val)
4. Train Holt-Winters per category (weekly period=7)
5. Evaluate on 30-day holdout (R² 0.96, MAE 4.1%, MAPE 4.3%)
6. Save model artifact (ensemble_model.pkl)"

---

### **[12-14 minutes] Scalability & Production Readiness**

**Script:**

"This isn't just a prototype - the architecture is production-ready.

#### Scalability (Design)

**Horizontal Scaling**:
- API instances: Auto-scale 2-20 based on CPU
- Each instance loads the model into memory at startup
- Redis cache for frequent queries

**Handle Growth**:
- Add read replicas for database
- CDN for static React build
- Model artifact on S3 for consistent deployment

#### Frontend Quality

- **Intuit Brand Theme**: Official QuickBooks colors (Super Blue, QB Green)
- **Accessibility**: WCAG AA, keyboard navigation, ARIA attributes
- **Responsive**: Works on desktop and tablet

#### Code Quality

- **Pydantic v2**: Strict request/response validation
- **Loguru**: Structured logging throughout
- **Error handling**: Graceful degradation
- **API Docs**: Auto-generated Swagger"

---

### **[14-15 minutes] Business Impact & Conclusion**

**Script:**

"Let's talk business impact.

#### What Makes This Special

**Technical Excellence**:
- Trained ensemble model with real evaluation metrics
- 25 engineered features, not just raw data
- R² 0.96 on holdout — reliable predictions
- Accessible, branded UI

**Business Value**:
- Actionable product-level predictions per category
- Confidence intervals help merchants assess risk
- Time period flexibility (week/month/year)
- Easy-to-understand dashboard

**Production Ready**:
- RESTful API with documentation
- Scalable architecture design
- Comprehensive documentation
- WCAG accessible frontend

#### What I Would Do Next

**Short-term** (Next 3 months):
1. Integrate real sales data (QuickBooks API)
2. Add external indicators (FRED API for GDP, inflation)
3. Improve model accuracy with more features
4. User testing with merchants

**Long-term** (6-12 months):
1. Deep learning models (LSTM, Transformers)
2. Real-time predictions with streaming data
3. Personalized models per merchant
4. Automated inventory recommendations

#### Why I'm Excited About Intuit

This project aligns with Intuit's mission to power prosperity. By giving merchants AI-powered insights, we're helping them make data-driven decisions and grow their business.

Thank you! I'm happy to answer any questions."

---

## Q&A Preparation

### Common Technical Questions

**Q: How do you handle new products with no history?**

A: "We use category-level predictions as baseline. The model forecasts at the category level, and new products inherit the category trend. As data accumulates, we can add product-specific features."

---

**Q: Why Holt-Winters instead of Prophet?**

A: "Prophet has heavy C/Stan dependencies that cause installation issues. Holt-Winters from statsmodels is lightweight, well-tested, and captures weekly seasonality effectively. For production reliability, it's the better choice."

---

**Q: How do you prevent overfitting?**

A: "Multiple strategies:
1. XGBoost regularization (subsample=0.8, colsample=0.8)
2. Moderate tree depth (max_depth=7)
3. Low learning rate (0.05) with more trees (500)
4. 30-day holdout evaluation — R² 0.96 vs training R² 0.999 shows excellent generalization
5. Reproducible data with seed(42)"

---

**Q: What's the gap between train and holdout R²?**

A: "Training R² is 0.999 and holdout is 0.96. The small gap indicates minimal overfitting. We achieved this with:
1. 2 years of training data (5,848 records)
2. 25 engineered features including cyclical encoding
3. XGBoost tuning: n_estimators=500, max_depth=7, min_child_weight=5
4. Reduced noise to 5% for cleaner signal"

---

**Q: How would you scale to millions of merchants?**

A: "Multi-tenancy architecture:
1. Shard database by merchant_id
2. Tenant-specific cache namespaces
3. Per-tenant models (or tiered approach)
4. Resource quotas and rate limiting
5. Kubernetes for orchestration"

---

## Time Management

- **Introduction**: 2 minutes
- **Architecture**: 2 minutes  
- **Demo**: 5 minutes (Most important)
- **Technical Deep Dive**: 3 minutes
- **Scalability**: 2 minutes
- **Conclusion**: 1 minute
- **Q&A**: Remaining time

**Total**: ~15 minutes + Q&A

---

## Tips for Delivery

1. **Practice the demo flow** - know exactly what to click
2. **Train the model before the demo** - run `python -m scripts.train_model`
3. **Speak clearly and confidently** - you built something real
4. **Connect features to business value** - always explain "why it matters"
5. **Be honest about metrics** - R² 0.96 demonstrates strong model performance
6. **Show enthusiasm** - genuine passion is contagious
7. **Listen carefully to questions** - it's okay to think before answering
8. **Time yourself** - practice to stay within 15 minutes
