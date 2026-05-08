# ⚡ QUICK START - V2 Dashboard

## 🎯 What's Different from V1?

1. **Uses YOUR actual data** - Creative tracker + Meta export format
2. **Shopify integration** - Real revenue tracking via UTM
3. **Full funnel** - ATC, Checkouts, Purchases
4. **Better matching** - By Ad Set Name (not ad name)

---

## 📦 Files Status

### ✅ Complete & Ready:
- `database.py` - Updated schema with Shopify + your tracker structure
- `shopify_connector.py` - Shopify API integration  
- `meta_importer.py` - Imports your actual Excel format
- `import_historical_data.py` - Loads your 2 uploaded files
- `WHATS_NEW.md` - Full changelog

### 🚧 In Progress (you'll get these next):
- `app.py` - Main dashboard (being rebuilt with Shopify tab)
- `hypothesis_engine.py` - Updated for new structure
- `recommendations.py` - Updated for new structure
- `claude_analyzer.py` - Same as V1

---

## 🚀 Deploy in 3 Steps

### 1. Copy Your Files
Put these in the dashboard folder:
- `Creative_Hit_Rate_Tracker___The_Day_Archive___2026_.xlsx`
- `Archive-Ads-Apr-1-2026-May-6-2026.xlsx`

### 2. Import Historical Data
```bash
python import_historical_data.py
```

This loads:
- 18 creative tests
- 59 Meta performance records
- April 1 - May 6, 2026 data

### 3. Run Dashboard
```bash
streamlit run app.py
```

---

## 📊 Your Current Data

**Overall Performance (Apr 1 - May 6):**
- Spend: $6,084 AUD
- Revenue: $11,808 AUD
- Purchases: 157
- ROAS: **1.94x**

**Top Performer:**
- **C12 - Ad 3**: 9.46x ROAS ($7 spend → $70 revenue)
- **ACTION:** Scale Concept 12 immediately

**Volume Winner:**
- **C2 - Ad 2**: 2.39x ROAS ($1,194 spend → $2,850 revenue, 85 purchases)
- **ACTION:** This is your workhorse - keep running

---

## 🔑 Shopify Setup (Optional but Recommended)

### Get Shopify API Credentials:

1. Go to Shopify Admin
2. Settings → Apps and sales channels
3. Develop apps → Create an app
4. Configure Admin API scopes:
   - `read_orders`
   - `read_customers`
5. Install app
6. Copy **Admin API access token**

### Add to Dashboard:

1. Settings tab
2. "Shopify Configuration"
3. Store URL: `thedayarchive.myshopify.com`
4. Access Token: [paste token]
5. Click "Test Connection"
6. Click "Import Orders"

---

## 📈 Missing Metrics (Recommended Adds)

For better decisions, add these to your next Meta export:

**Video Performance:**
- ThruPlay
- 3-second video plays
- Video avg watch time

**Engagement:**
- Post reactions/comments/shares
- Post saves

**Audience:**
- Age breakdown
- Gender breakdown
- Placement breakdown

---

## 🎯 UTM Parameter Setup

Add to Meta campaign settings:

**URL Parameters:**
```
?utm_source=facebook&utm_medium=cpc&utm_campaign={{campaign.name}}&utm_content={{ad.name}}
```

This lets Shopify track which specific ad drove each order.

---

## 📝 Daily Workflow

**Morning (5 mins):**
1. Export yesterday's Meta data
2. Upload to dashboard
3. Check Shopify reconciliation
4. Review recommendations

**Weekly (20 mins):**
1. Hypothesis validation review
2. Upload top performer for Claude analysis
3. Plan next creative tests

---

## 🆘 Troubleshooting

**"Creative not matching Meta data"**
- Check Ad Set Name in tracker matches exactly
- Look at "Meta Performance" tab, unmatched section

**"Shopify API error"**
- Verify API token has `read_orders` scope
- Check store URL format (no https://)

**"Import failed"**
- Ensure Excel files are in same folder as script
- Check file names match exactly

---

**Next:** I'm rebuilding the main app.py with Shopify tab. You'll get the complete V2 package shortly!
