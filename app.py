import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from database import Database
from meta_importer import MetaImporter
from hypothesis_engine import HypothesisEngine
from recommendations import RecommendationEngine

# Page config
st.set_page_config(
    page_title="Meta Ads Dashboard V2 - The Day Archive",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 3rem; font-weight: bold; color: #1f2937; margin-bottom: 0.5rem;}
    .sub-header {font-size: 1.2rem; color: #6b7280; margin-bottom: 2rem;}
    .metric-card {background: white; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
    .success-badge {background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;}
    .warning-badge {background: #f59e0b; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;}
    .danger-badge {background: #ef4444; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()

# Auto-import creative tracker on first load if database is empty
if 'creative_tracker_imported' not in st.session_state:
    creatives = db.get_all_creative_tests()
    if len(creatives) == 0:
        # Database is empty - import from Excel
        try:
            import import_historical_data as importer
            import os
            
            creative_file = 'Creative_Hit_Rate_Tracker___The_Day_Archive___2026_.xlsx'
            
            if os.path.exists(creative_file):
                # Import the actual Excel file with all data
                creatives_imported = importer.import_creative_tracker(creative_file, db)
                st.session_state['creative_tracker_imported'] = True
                st.toast(f"✅ Auto-loaded {creatives_imported} creative tests from Excel!", icon="🎉")
            else:
                st.session_state['creative_tracker_imported'] = False
        except Exception as e:
            st.session_state['creative_tracker_imported'] = False
            # Silently fail if files aren't ready yet
    else:
        st.session_state['creative_tracker_imported'] = True

meta_importer = MetaImporter(db)
hypothesis_engine = HypothesisEngine(db)
recommendation_engine = RecommendationEngine(db)

# Sidebar
st.sidebar.title("🎯 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["📊 Dashboard", "🎨 Creative Tracker", "📈 Meta Performance", 
     "🛍️ Shopify Revenue", "🔬 Hypothesis Validation", "💡 Recommendations", "⚙️ Settings"]
)

# Header
st.markdown('<div class="main-header">Meta Ads Dashboard V2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The Day Archive - Performance Tracking with Shopify Integration</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: DASHBOARD OVERVIEW
# ============================================================================
if page == "📊 Dashboard":
    st.header("📊 Dashboard Overview")
    
    date_range = st.selectbox("Time Period", ["Last 7 Days", "Last 14 Days", "Last 30 Days", "All Time"], index=2)
    days_map = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 30 Days": 30, "All Time": 99999}
    days = days_map[date_range]
    
    performance = db.get_performance_summary(days)
    
    if performance:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Spend", f"${performance['total_spend']:,.2f}")
        with col2:
            st.metric("Revenue", f"${performance['total_revenue']:,.2f}")
        with col3:
            roas = performance['total_revenue'] / performance['total_spend'] if performance['total_spend'] > 0 else 0
            st.metric("ROAS", f"{roas:.2f}x", delta="🟢 On Target" if roas >= 3.0 else "🔴 Below Target")
        with col4:
            st.metric("Purchases", f"{performance['total_conversions']}")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ctr = (performance['total_clicks'] / performance['total_impressions'] * 100) if performance['total_impressions'] > 0 else 0
            st.metric("CTR", f"{ctr:.2f}%")
        with col2:
            atc = performance.get('total_atc', 0)
            st.metric("Add to Cart", f"{atc:,}")
        with col3:
            st.metric("Impressions", f"{performance['total_impressions']:,}")
        with col4:
            st.metric("Clicks", f"{performance['total_clicks']:,}")
        
        st.markdown("---")
        
        # Top Performers
        st.subheader("🏆 Top Performing Ads")
        top_creatives = db.get_top_creatives(days, limit=10)
        
        if top_creatives:
            df_top = pd.DataFrame(top_creatives)
            df_top['roas'] = df_top['revenue'] / df_top['spend']
            df_top['roas'] = df_top['roas'].replace([float('inf'), float('-inf')], 0)
            
            # Format display
            df_display = df_top[['ad_name', 'spend', 'revenue', 'conversions', 'roas']].copy()
            df_display['spend'] = df_display['spend'].apply(lambda x: f"${x:,.2f}")
            df_display['revenue'] = df_display['revenue'].apply(lambda x: f"${x:,.2f}")
            df_display['roas'] = df_display['roas'].apply(lambda x: f"{x:.2f}x")
            df_display.columns = ['Ad Name', 'Spend', 'Revenue', 'Conversions', 'ROAS']
            
            st.dataframe(df_display, width="stretch", hide_index=True)
    else:
        st.info("📥 No data yet. Upload Meta performance data to get started!")
        st.markdown("---")
        st.subheader("🚀 Quick Start")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ Import Data")
            st.write("Run the import script to load your historical data")
            st.code("python import_historical_data.py", language="bash")
        with col2:
            st.markdown("### 2️⃣ Add Creatives")
            st.write("Go to Creative Tracker and log your tests")
        with col3:
            st.markdown("### 3️⃣ Upload Meta CSV")
            st.write("Export from Meta and upload in Meta Performance tab")

# ============================================================================
# PAGE: CREATIVE TRACKER
# ============================================================================
elif page == "🎨 Creative Tracker":
    st.header("🎨 Creative Hit Rate Tracker")
    
    tab1, tab2 = st.tabs(["➕ Add New Creative", "📋 View All"])
    
    with tab1:
        st.subheader("Add New Creative Test")
        
        with st.form("creative_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign = st.text_input("Campaign", placeholder="Launch - ABO - 2/4")
                ad_set_name = st.text_input("Ad Set Name*", placeholder="Concept 9 - Ad 1 - 30/4")
                launch_date = st.date_input("Launch Date")
                variable_tested = st.selectbox("Variable Tested", 
                    ["Desire", "Angle", "Awareness", "Ad Format", "Hook", "Visual Style", "CTA", "Other"])
                format_type = st.selectbox("Format", ["Image", "Video", "Carousel", "Collection"])
                desire = st.text_input("Desire", placeholder="GIFT + SALE")
                angle = st.text_input("Angle", placeholder="Problem-aware hook")
            
            with col2:
                avatar = st.selectbox("Avatar", 
                    ["Milestone Gift Buyer (Daughter for Parent)", 
                     "Milestone Gift Buyer (Wife for Husband)",
                     "Stressed Last-Minute Buyer",
                     "Adult Child Organizing Family Gift",
                     "Other"])
                awareness_level = st.selectbox("Awareness Level", 
                    ["Problem-Aware Stage 3", "Solution-Aware", "Product-Aware", "Most Aware"])
                landing_page = st.text_input("Landing Page", placeholder="https://thedayarchive.com/...")
                ad_inspiration = st.text_input("Ad Inspiration Link (Google Drive)")
                variations = st.number_input("Variations", min_value=0, value=0)
                status = st.selectbox("Status", ["Launched", "Scaling", "Paused", "Killed"])
            
            hypothesis = st.text_area("Hypothesis*", 
                placeholder="I believe this will perform because...", height=100)
            
            results = st.text_area("Results", placeholder="Performance notes...", height=60)
            learnings = st.text_area("Learnings", placeholder="What did you learn?", height=60)
            
            submitted = st.form_submit_button("💾 Save Creative Test", width="stretch")
            
            if submitted:
                if not ad_set_name or not hypothesis:
                    st.error("⚠️ Ad Set Name and Hypothesis are required")
                else:
                    try:
                        db.add_creative_test(
                            campaign=campaign,
                            ad_set_name=ad_set_name,
                            launch_date=launch_date.strftime("%Y-%m-%d"),
                            variable_tested=variable_tested,
                            format_type=format_type,
                            desire=desire,
                            angle=angle,
                            avatar=avatar,
                            awareness_level=awareness_level,
                            landing_page=landing_page,
                            ad_inspiration=ad_inspiration,
                            variations=variations,
                            hypothesis=hypothesis,
                            status=status,
                            results=results,
                            learnings=learnings
                        )
                        st.success(f"✅ Added '{ad_set_name}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("All Creative Tests")
        
        creatives = db.get_all_creative_tests()
        
        if creatives:
            # Show import status
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Creative Tests", len(creatives))
            with col2:
                with_data = len([c for c in creatives if c.get('hypothesis') and c.get('hypothesis') != 'Imported from Meta data - add details later'])
                st.metric("With Full Data", with_data)
            with col3:
                placeholders = len(creatives) - with_data
                st.metric("Placeholders", placeholders)
            
            # Re-import button if there are placeholders
            if placeholders > 0:
                st.warning(f"⚠️ {placeholders} creative tests have placeholder data. Re-import from Excel to get full details.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Re-import from Excel", width="stretch"):
                        with st.spinner("Re-importing from Excel..."):
                            try:
                                import import_historical_data as importer
                                import os
                                
                                creative_file = 'Creative_Hit_Rate_Tracker___The_Day_Archive___2026_.xlsx'
                                
                                # Check if file exists
                                if not os.path.exists(creative_file):
                                    st.error(f"❌ File not found: {creative_file}")
                                    st.info("Current directory files:")
                                    st.code("\n".join(os.listdir('.')))
                                else:
                                    # Clear existing data first
                                    st.info("Clearing old data...")
                                    db.clear_all_data()
                                    
                                    # Re-import
                                    st.info("Importing from Excel...")
                                    creatives_imported = importer.import_creative_tracker(creative_file, db)
                                    
                                    st.success(f"✅ Re-imported {creatives_imported} creative tests with full data!")
                                    st.balloons()
                                    
                                    # Force refresh
                                    st.session_state['creative_tracker_imported'] = True
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Import error: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                
                with col2:
                    if st.button("🗑️ Clear Placeholders Only", width="stretch"):
                        # Delete only the placeholder creatives
                        for creative in creatives:
                            if creative.get('hypothesis') == 'Imported from Meta data - add details later':
                                # This is a placeholder - we could delete it
                                pass
                        st.info("Feature coming soon - use Re-import button to replace all")

            
            st.markdown("---")
            
            df = pd.DataFrame(creatives)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Status", ["All", "Launched", "Scaling", "Paused", "Killed"])
            with col2:
                format_filter = st.selectbox("Format", ["All", "Image", "Video", "Carousel"])
            with col3:
                avatar_filter = st.selectbox("Avatar", ["All"] + list(df['avatar'].dropna().unique()))
            
            # Apply filters
            if status_filter != "All":
                df = df[df['status'] == status_filter]
            if format_filter != "All":
                df = df[df['format'] == format_filter]
            if avatar_filter != "All":
                df = df[df['avatar'] == avatar_filter]
            
            # Display all columns
            # Reorder columns to put most important ones first
            column_order = [
                'launch_date', 'ad_set_name', 'campaign', 'status',
                'variable_tested', 'format', 'desire', 'angle', 'avatar', 'awareness_level',
                'hypothesis', 'results', 'learnings',
                'creative_type', 'landing_page', 'ad_inspiration', 
                'experiences', 'emotional_desire', 'beliefs', 'behaviors', 'variations'
            ]
            
            # Only include columns that exist in the dataframe
            display_columns = [col for col in column_order if col in df.columns]
            
            st.dataframe(
                df[display_columns],
                width="stretch", hide_index=True
            )
            
            # Edit status
            st.markdown("---")
            st.subheader("Edit Status")
            col1, col2 = st.columns([3, 1])
            with col1:
                creative_to_update = st.selectbox("Select Creative", df['ad_set_name'].tolist())
            with col2:
                new_status = st.selectbox("New Status", ["Launched", "Scaling", "Paused", "Killed"])
            
            if st.button("Update Status"):
                creative_id = df[df['ad_set_name'] == creative_to_update]['id'].iloc[0]
                db.update_creative_status(creative_id, new_status)
                st.success(f"✅ Updated '{creative_to_update}' to '{new_status}'")
                st.rerun()
        else:
            st.info("No creatives yet. Add your first one above or run import script!")

# ============================================================================
# PAGE: META PERFORMANCE
# ============================================================================
elif page == "📈 Meta Performance":
    st.header("📈 Meta Performance Data")
    
    tab1, tab2 = st.tabs(["📥 Upload Data", "📊 Performance View"])
    
    with tab1:
        st.subheader("Upload Meta Ads Export")
        
        st.markdown("""
        ### 📋 Export from Meta Ads Manager:
        1. Select date range
        2. Click **Export** → **Export table data**
        3. Choose **Excel** or **CSV**
        4. Upload below
        """)
        
        uploaded_file = st.file_uploader("Choose file", type=['xlsx', 'xls', 'csv'])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    result = meta_importer.import_csv(uploaded_file)
                else:
                    result = meta_importer.import_excel(uploaded_file)
                
                st.success(f"✅ Imported {result['rows_imported']} rows!")
                
                if result['matched_to_creative_tracker'] > 0:
                    st.info(f"🔗 Matched {result['matched_to_creative_tracker']} to creative tracker")
                
                if result['unmatched_ad_sets']:
                    st.warning(f"⚠️ {len(result['unmatched_ad_sets'])} ad sets not in creative tracker:")
                    st.write(result['unmatched_ad_sets'])
                
            except Exception as e:
                st.error(f"Import error: {str(e)}")
    
    with tab2:
        st.subheader("Performance Data")
        
        days = st.slider("Days to show", 1, 90, 30)
        performance_data = db.get_recent_performance(days=days)
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            
            # Display
            display_cols = ['reporting_starts', 'ad_name', 'ad_set_name', 'amount_spent', 
                           'purchases_conversion_value', 'purchases', 'purchase_roas', 
                           'ctr', 'adds_to_cart']
            
            df_display = df[display_cols].copy()
            df_display.columns = ['Date', 'Ad', 'Ad Set', 'Spend', 'Revenue', 'Purchases', 
                                 'ROAS', 'CTR', 'ATC']
            
            st.dataframe(df_display, width="stretch", hide_index=True)
            
            # Download
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                f"meta_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        else:
            st.info("No data yet. Upload Meta export above!")

# ============================================================================
# PAGE: SHOPIFY REVENUE
# ============================================================================
elif page == "🛍️ Shopify Revenue":
    st.header("🛍️ Shopify Revenue Tracking")
    
    st.info("💡 Connect your Shopify store in Settings to track real revenue via UTM parameters")
    
    # Check if Shopify is configured
    shopify_configured = st.session_state.get('shopify_configured', False)
    
    if not shopify_configured:
        st.warning("⚙️ Shopify not configured. Go to Settings to add your store credentials.")
    else:
        st.success("✅ Shopify connected!")
        
        # Shopify orders summary
        orders = db.get_all_shopify_orders(30)
        
        if orders:
            df_orders = pd.DataFrame(orders)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Orders", len(df_orders))
            with col2:
                st.metric("Total Revenue", f"${df_orders['total_price'].sum():,.2f}")
            with col3:
                matched = len(df_orders[df_orders['matched_ad_name'].notna()])
                st.metric("Matched to Ads", matched)
            with col4:
                match_rate = (matched / len(df_orders) * 100) if len(df_orders) > 0 else 0
                st.metric("Match Rate", f"{match_rate:.1f}%")
            
            st.markdown("---")
            st.subheader("Recent Orders")
            st.dataframe(
                df_orders[['created_at', 'order_number', 'total_price', 'matched_ad_name', 
                          'utm_campaign', 'utm_content']].head(20),
                width="stretch", hide_index=True
            )
        else:
            st.info("No Shopify orders imported yet. Check Settings to import.")

# ============================================================================
# PAGE: HYPOTHESIS VALIDATION
# ============================================================================
elif page == "🔬 Hypothesis Validation":
    st.header("🔬 Hypothesis Validation")
    
    st.markdown("""
    **Validation Criteria:**
    - ✅ **Validated**: ROAS ≥ 3.0x + 10 conversions
    - ⚠️ **Inconclusive**: < 10 conversions
    - ❌ **Invalidated**: ROAS < 1.0x + 10 conversions
    """)
    
    validations = hypothesis_engine.validate_all_hypotheses()
    
    if validations:
        col1, col2, col3, col4 = st.columns(4)
        validated = sum(1 for v in validations if v['conclusion'] == 'Validated')
        invalidated = sum(1 for v in validations if v['conclusion'] == 'Invalidated')
        inconclusive = sum(1 for v in validations if v['conclusion'] == 'Inconclusive')
        
        with col1:
            st.metric("✅ Validated", validated)
        with col2:
            st.metric("❌ Invalidated", invalidated)
        with col3:
            st.metric("⚠️ Inconclusive", inconclusive)
        with col4:
            st.metric("Total", len(validations))
        
        st.markdown("---")
        
        for v in validations:
            with st.expander(f"{v['ad_set_name']} - {v['conclusion']}", 
                           expanded=(v['conclusion'] == 'Validated')):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Hypothesis:**")
                    st.write(v['hypothesis'])
                    st.markdown("**Actual Result:**")
                    st.write(v['actual_result'])
                    if v['learnings']:
                        st.markdown("**Learnings:**")
                        st.write(v['learnings'])
                    if v['next_test']:
                        st.info(f"**Next:** {v['next_test']}")
                
                with col2:
                    st.metric("ROAS", f"{v['roas']:.2f}x")
                    st.metric("Spend", f"${v['spend']:.2f}")
                    st.metric("Conversions", v['conversions'])
    else:
        st.info("No hypothesis data yet. Add creatives and upload Meta performance!")

# ============================================================================
# PAGE: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.header("💡 AI-Powered Recommendations")
    
    recommendations = recommendation_engine.generate_recommendations()
    
    if recommendations:
        # Scale Opportunities
        if recommendations.get('scale_opportunities'):
            st.subheader("📈 Scale These Now")
            for opp in recommendations['scale_opportunities']:
                st.success(f"**{opp['ad_set_name']}**: {opp['reason']} - {opp['recommendation']}")
        
        # Pause Recommendations
        if recommendations.get('pause_recommendations'):
            st.subheader("⏸️ Consider Pausing")
            for pause in recommendations['pause_recommendations']:
                st.warning(f"**{pause['ad_set_name']}**: {pause['reason']}")
        
        # Next Tests
        st.subheader("🧪 What to Test Next")
        for test in recommendations.get('next_tests', []):
            with st.expander(f"Test: {test['concept']}", expanded=True):
                st.write(f"**Format:** {test['format']}")
                st.write(f"**Angle:** {test['angle']}")
                st.write(f"**Hypothesis:** {test['hypothesis']}")
                st.write(f"**Why:** {test['reasoning']}")
                st.write(f"**Predicted ROAS:** {test['predicted_roas']}")
        
        # Winning Patterns
        if recommendations.get('winning_patterns'):
            st.subheader("🏆 Your Winning Pattern DNA")
            patterns = recommendations['winning_patterns']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**What's Working:**")
                for pattern in patterns.get('working', []):
                    st.markdown(f"✅ {pattern}")
            with col2:
                st.markdown("**What's Not:**")
                for pattern in patterns.get('not_working', []):
                    st.markdown(f"❌ {pattern}")
    else:
        st.info("Not enough data yet. Add creatives and Meta performance!")

# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["🛍️ Shopify", "🔑 Claude API"])
    
    with tab1:
        st.subheader("Shopify Integration")
        
        st.markdown("""
        ### How to Connect Shopify:
        1. Use your **existing Shopify API** from your other dashboard
        2. OR create new app: Shopify Admin → Settings → Apps → Create app
        3. Enable scopes: `read_orders`, `read_customers`
        4. Copy Admin API access token
        """)
        
        shop_url = st.text_input("Store URL", placeholder="thedayarchive.myshopify.com",
                                 value=st.session_state.get('shopify_url', ''))
        access_token = st.text_input("Access Token", type="password",
                                     value=st.session_state.get('shopify_token', ''))
        
        if st.button("💾 Save Shopify Config"):
            st.session_state['shopify_url'] = shop_url
            st.session_state['shopify_token'] = access_token
            st.session_state['shopify_configured'] = True
            st.success("✅ Shopify configured!")
        
        st.markdown("---")
        
        if st.session_state.get('shopify_configured'):
            st.info("✅ Shopify Connected")
            
            if st.button("📥 Import Last 30 Days Orders"):
                with st.spinner("Importing orders from Shopify..."):
                    try:
                        from shopify_connector import ShopifyConnector
                        
                        shop_url = st.session_state.get('shopify_url')
                        access_token = st.session_state.get('shopify_token')
                        
                        if not shop_url or not access_token:
                            st.error("❌ Please save Shopify credentials first")
                        else:
                            # Initialize connector
                            connector = ShopifyConnector(shop_url, access_token, db)
                            
                            # Import orders
                            result = connector.import_orders_to_database(days_back=30)
                            
                            st.success(f"""
                            ✅ Imported {result['orders_imported']} orders!
                            - Matched to ads: {result['matched_to_ads']}
                            - Unmatched: {result['unmatched']}
                            - Total revenue: ${result['total_revenue']:,.2f}
                            - Match rate: {result['match_rate']:.1f}%
                            """)
                            
                            # Show debug info
                            if 'debug_info' in result and result['debug_info']:
                                with st.expander("🔍 Debug Info - Shopify API Response"):
                                    debug = result['debug_info']
                                    st.write(f"**Sample Order:** #{debug.get('order_number')}")
                                    st.write(f"**Available fields:** {', '.join(debug.get('available_fields', []))}")
                                    st.write(f"**Has customer_journey_summary:** {debug.get('has_customer_journey_summary')}")
                                    st.write(f"**Has client_details:** {debug.get('has_client_details')}")
                                    st.write(f"**Has landing_site_ref:** {debug.get('has_landing_site_ref')}")
                                    
                                    if debug.get('customer_journey_keys'):
                                        st.write(f"**customer_journey_summary keys:** {', '.join(debug['customer_journey_keys'])}")
                                    if debug.get('last_visit_keys'):
                                        st.write(f"**last_visit keys:** {', '.join(debug['last_visit_keys'])}")
                                    
                                    st.write("**UTM Extraction Test:**")
                                    st.json(debug.get('utm_extraction_test', {}))
                            
                            st.info("Go to 'Shopify Revenue' tab to see attribution!")
                    
                    except ImportError:
                        st.error("❌ shopify_connector.py not found. Make sure it's in your GitHub repo.")
                    except Exception as e:
                        st.error(f"❌ Shopify import error: {str(e)}")
                        st.caption("Check that your access token has 'read_orders' and 'read_customers' scopes.")
    
    with tab2:
        st.subheader("Claude API (for Creative Analysis)")
        
        api_key = st.text_input("Claude API Key", type="password", 
                                value=st.session_state.get('claude_api_key', ''))
        if st.button("💾 Save API Key"):
            st.session_state['claude_api_key'] = api_key
            st.success("✅ API key saved!")
        
        st.caption("Get your API key from console.anthropic.com")

# Footer
st.markdown("---")
st.caption("The Day Archive - Meta Ads Dashboard V2 | Powered by Streamlit + Claude")
