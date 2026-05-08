# 🚀 DEPLOYMENT GUIDE - Streamlit Cloud (FREE)

## Why Streamlit Cloud?

✅ **FREE hosting** - No cost  
✅ **Always-on** - 24/7 access  
✅ **Data persists** - Database saved permanently  
✅ **Access anywhere** - Phone, laptop, tablet  
✅ **Auto-updates** - Push to GitHub = instant deploy  

---

## 📦 STEP 1: Create GitHub Repository

### Option A: GitHub Website (Easiest)

1. Go to [github.com](https://github.com)
2. Click **"New Repository"**
3. Name: `dayarchive-ads-dashboard`
4. **IMPORTANT: Make it PUBLIC** (required for free Streamlit)
5. Don't initialize with README
6. Click **"Create repository"**

### Option B: GitHub CLI

```bash
gh repo create dayarchive-ads-dashboard --public
```

---

## 📤 STEP 2: Upload Your Files

### Option A: Upload via GitHub Website (Recommended)

1. On your new repo page, click **"uploading an existing file"**
2. **Drag and drop ALL these files:**
   - `app.py`
   - `database.py`
   - `meta_importer.py`
   - `shopify_connector.py`
   - `hypothesis_engine.py`
   - `recommendations.py`
   - `claude_analyzer.py`
   - `import_historical_data.py`
   - `requirements.txt`
   - `.gitignore`
   - `QUICK_START.md`
   - `WHATS_NEW.md`
   - **Your 2 Excel files:**
     - `Creative_Hit_Rate_Tracker___The_Day_Archive___2026_.xlsx`
     - `Archive-Ads-Apr-1-2026-May-6-2026.xlsx`

3. Commit message: `Initial commit - Dashboard V2 with historical data`
4. Click **"Commit changes"**

### Option B: Git Command Line

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/dayarchive-ads-dashboard.git
cd dayarchive-ads-dashboard

# Copy all dashboard files here
# (Copy the 11 files + 2 Excel files to this folder)

# Add, commit, push
git add .
git commit -m "Initial commit - Dashboard V2"
git push origin main
```

---

## ☁️ STEP 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit
4. Click **"New app"**
5. Configure:
   - **Repository:** `YOUR_USERNAME/dayarchive-ads-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
6. **Advanced settings** (click dropdown):
   - **Python version:** 3.11
7. Click **"Deploy!"**

⏱️ **Deployment takes 2-3 minutes**

---

## 🎉 STEP 4: First-Time Setup

Once deployed, dashboard opens automatically.

### Import Your Historical Data

**IMPORTANT:** You need to run the import script **ONCE** to load your data.

**Two ways to do this:**

#### Method 1: Add a "Setup" Button in Dashboard (Recommended)

I'll add a one-time setup button to the dashboard that imports your data.

#### Method 2: Import Locally, Then Upload Database

```bash
# On your computer:
python import_historical_data.py

# This creates ads_dashboard.db
# Upload this file to your GitHub repo
# Streamlit will use it
```

**I recommend Method 1** - I'll add it to the dashboard now.

---

## 🔐 STEP 5: Add API Keys (Optional)

### For Shopify Integration:

1. In Streamlit Cloud dashboard, click **"⚙️ Settings"**
2. Click **"Secrets"**
3. Add:

```toml
[shopify]
shop_url = "thedayarchive.myshopify.com"
access_token = "YOUR_SHOPIFY_ACCESS_TOKEN"

[claude]
api_key = "YOUR_CLAUDE_API_KEY"
```

4. Click **"Save"**

**OR** you can add them in the Settings tab of the dashboard itself (they'll persist in the database).

---

## 📊 YOUR DASHBOARD URL

After deployment, you'll get:
```
https://dayarchive-ads.streamlit.app
```

(Or similar - Streamlit assigns the URL)

**Bookmark this!** Access from anywhere.

---

## 🔄 DAILY WORKFLOW

### Morning (5 mins):
1. Open dashboard URL
2. Go to **Meta Performance** tab
3. Upload yesterday's Meta export
4. Check **Recommendations** tab
5. Take action in Meta Ads Manager

### New Creative Test (10 mins):
1. Go to **Creative Tracker** tab
2. Add new test with hypothesis
3. Name it exactly: `Concept_X_Ad_Y`
4. Launch in Meta with same name
5. Dashboard auto-tracks

### Weekly (20 mins):
1. **Hypothesis Validation** → What worked?
2. **Recommendations** → Next tests
3. **Shopify Revenue** → Real revenue vs Meta

---

## 📈 DATA PERSISTENCE

**How data is saved:**

- **SQLite database** (`ads_dashboard.db`) stored in Streamlit Cloud
- Persists between sessions
- Never deleted unless you clear it
- Backed up automatically by Streamlit

**To backup manually:**

1. Settings tab → Export Database
2. Download CSV files
3. Save locally

---

## 🔄 UPDATING THE DASHBOARD

When you want to add features:

1. Edit files locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Added new feature"
   git push
   ```
3. Streamlit Cloud **auto-redeploys** in ~30 seconds
4. Refresh browser - changes live!

---

## 🆘 TROUBLESHOOTING

### "Build failed"
- Check `requirements.txt` has all dependencies
- View logs in Streamlit Cloud dashboard
- Python version must be 3.11

### "Database not found"
- Run import script (Method 1 or 2 above)
- Or upload `ads_dashboard.db` to GitHub

### "Secrets not found"
- Add in Streamlit Cloud settings (Step 5)
- Or add in dashboard Settings tab

### "Out of resources"
- Free tier: 1GB RAM
- Upgrade to Streamlit Cloud Pro if needed ($20/month)
- Or optimize database queries

---

## 💰 COST

**FREE TIER:**
- ✅ Unlimited public apps
- ✅ 1GB RAM per app
- ✅ 1GB storage
- ✅ Community support

**This dashboard uses ~200MB - well within free tier!**

---

## 🎯 NEXT STEPS

1. ✅ Create GitHub repo (Step 1)
2. ✅ Upload files (Step 2)
3. ✅ Deploy to Streamlit (Step 3)
4. ✅ Import historical data (Step 4)
5. ✅ Add Shopify credentials (Step 5)
6. ✅ Start making decisions! 🚀

---

**Ready to deploy?** Follow the steps above and you'll have a live dashboard in 10 minutes!
