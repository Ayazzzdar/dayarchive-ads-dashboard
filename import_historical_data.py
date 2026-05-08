"""
Data Import Script - Load Historical Data
Imports your actual Creative Hit Rate Tracker and Meta performance data
"""

import pandas as pd
from database import Database
from datetime import datetime

def import_creative_tracker(excel_file_path, db):
    """Import creative tests from your Excel tracker"""
    
    print("📥 Importing Creative Hit Rate Tracker...")
    
    # Check if file exists
    import os
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"File not found: {excel_file_path}")
    
    df = pd.read_excel(excel_file_path, sheet_name='2026')
    
    # Clean up column names
    df.columns = df.columns.str.strip()
    
    imported = 0
    
    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['Ad Set Name']):
            continue
        
        # Extract date
        launch_date = row.get('Launch Date (double click)')
        if pd.notna(launch_date):
            if isinstance(launch_date, datetime):
                launch_date = launch_date.strftime('%Y-%m-%d')
            else:
                launch_date = str(launch_date)[:10]
        else:
            launch_date = None
        
        try:
            db.add_creative_test(
                campaign=str(row.get('Campaign', '')) if pd.notna(row.get('Campaign')) else None,
                ad_set_name=str(row['Ad Set Name']),
                launch_date=launch_date,
                creative_type=str(row.get('Creative Type', '')) if pd.notna(row.get('Creative Type')) else None,
                landing_page=str(row.get('Landing Page ', '')) if pd.notna(row.get('Landing Page ')) else None,
                ad_inspiration=str(row.get('Ad Inspiration ', '')) if pd.notna(row.get('Ad Inspiration ')) else None,
                variable_tested=str(row.get("Variable We're Testing (Desire, Angle, Awareness, Ad Format)", '')) if pd.notna(row.get("Variable We're Testing (Desire, Angle, Awareness, Ad Format)")) else None,
                format_type=str(row.get('Format', '')) if pd.notna(row.get('Format')) else None,
                desire=str(row.get('Desire', '')) if pd.notna(row.get('Desire')) else None,
                experiences=str(row.get('Experience(s)', '')) if pd.notna(row.get('Experience(s)')) else None,
                emotional_desire=str(row.get('Emotional Desire', '')) if pd.notna(row.get('Emotional Desire')) else None,
                angle=str(row.get('Angle', '')) if pd.notna(row.get('Angle')) else None,
                avatar=str(row.get('Avatar', '')) if pd.notna(row.get('Avatar')) else None,
                awareness_level=str(row.get('Awareness Level ', '')) if pd.notna(row.get('Awareness Level ')) else None,
                beliefs=str(row.get('Beliefs', '')) if pd.notna(row.get('Beliefs')) else None,
                behaviors=str(row.get('Behaviors', '')) if pd.notna(row.get('Behaviors')) else None,
                hypothesis=str(row.get("What's your hypothesis? What are you creating / testing?\n(creative plans) What gives you confidence that this will improve overall performance?", '')) if pd.notna(row.get("What's your hypothesis? What are you creating / testing?\n(creative plans) What gives you confidence that this will improve overall performance?")) else None,
                variations=int(row.get('Variations? ', 0)) if pd.notna(row.get('Variations? ')) else None,
                status=str(row.get('Status', 'Launched')) if pd.notna(row.get('Status')) else 'Launched',
                results=str(row.get('Results', '')) if pd.notna(row.get('Results')) else None,
                learnings=str(row.get('Learnings (Fill Out AFTER Minimum 7 Days)', '')) if pd.notna(row.get('Learnings (Fill Out AFTER Minimum 7 Days)')) else None
            )
            imported += 1
            print(f"  ✅ Imported: {row['Ad Set Name']}")
        
        except Exception as e:
            print(f"  ⚠️ Skipped {row.get('Ad Set Name', 'Unknown')}: {str(e)}")
    
    print(f"\n✅ Imported {imported} creative tests\n")
    return imported

def import_meta_performance(excel_file_path, db):
    """Import Meta performance data from Excel export"""
    
    print("📥 Importing Meta Performance Data...")
    
    # Check if file exists
    import os
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"File not found: {excel_file_path}")
    
    df = pd.read_excel(excel_file_path)
    
    # Clean numeric columns
    numeric_cols = [
        'Results', 'Cost per results', 'Impressions', 'Amount spent (AUD)',
        'Link clicks', 'CTR (link click-through rate)', 'CPC (cost per link click) (AUD)',
        'Adds to cart', 'Cost per add to cart (AUD)', 'Checkouts initiated',
        'Cost per checkout initiated (AUD)', 'Purchases', 'Cost per purchase (AUD)',
        'Purchases conversion value', 'Purchase ROAS (return on ad spend)',
        'CPM (cost per 1,000 impressions) (AUD)', 'CVR', 'Frequency',
        'Hook Rate', 'Hold Rate New'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convert dates
    df['Reporting starts'] = pd.to_datetime(df['Reporting starts']).dt.strftime('%Y-%m-%d')
    if 'Reporting ends' in df.columns:
        df['Reporting ends'] = pd.to_datetime(df['Reporting ends']).dt.strftime('%Y-%m-%d')
    else:
        df['Reporting ends'] = df['Reporting starts']
    
    imported = 0
    
    for idx, row in df.iterrows():
        try:
            db.add_performance_data(
                reporting_starts=row['Reporting starts'],
                reporting_ends=row.get('Reporting ends', row['Reporting starts']),
                ad_name=str(row['Ad name']),
                ad_set_name=str(row['Ad set name']),
                ad_delivery=str(row.get('Ad delivery', '')),
                results=int(row.get('Results', 0)),
                cost_per_results=float(row.get('Cost per results', 0)),
                impressions=int(row.get('Impressions', 0)),
                ad_set_budget=str(row.get('Ad set budget', '')),
                amount_spent=float(row['Amount spent (AUD)']),
                link_clicks=int(row.get('Link clicks', 0)),
                ctr=float(row.get('CTR (link click-through rate)', 0)),
                cpc=float(row.get('CPC (cost per link click) (AUD)', 0)),
                adds_to_cart=int(row.get('Adds to cart', 0)),
                cost_per_atc=float(row.get('Cost per add to cart (AUD)', 0)),
                checkouts_initiated=int(row.get('Checkouts initiated', 0)),
                cost_per_checkout=float(row.get('Cost per checkout initiated (AUD)', 0)),
                purchases=int(row.get('Purchases', 0)),
                cost_per_purchase=float(row.get('Cost per purchase (AUD)', 0)),
                purchases_conversion_value=float(row.get('Purchases conversion value', 0)),
                purchase_roas=float(row.get('Purchase ROAS (return on ad spend)', 0)),
                cpm=float(row.get('CPM (cost per 1,000 impressions) (AUD)', 0)),
                cvr=float(row.get('CVR', 0)),
                frequency=float(row.get('Frequency', 0)),
                ad_id=str(row.get('Ad ID', '')) if pd.notna(row.get('Ad ID')) else None,
                ad_set_id=str(row.get('Ad set ID', '')) if pd.notna(row.get('Ad set ID')) else None,
                campaign_id=str(row.get('Campaign ID', '')) if pd.notna(row.get('Campaign ID')) else None,
                hook_rate=float(row.get('Hook Rate', 0)),
                hold_rate=float(row.get('Hold Rate New', 0))
            )
            imported += 1
            if imported % 10 == 0:
                print(f"  Imported {imported} rows...")
        
        except Exception as e:
            print(f"  ⚠️ Error on row {idx}: {str(e)}")
    
    print(f"\n✅ Imported {imported} performance records\n")
    return imported

def main():
    """Main import function"""
    
    print("=" * 60)
    print("  THE DAY ARCHIVE - HISTORICAL DATA IMPORT")
    print("=" * 60)
    print()
    
    # Initialize database
    db = Database('ads_dashboard.db')
    print("✅ Database initialized\n")
    
    # Import creative tracker
    creative_tracker_file = 'Creative_Hit_Rate_Tracker___The_Day_Archive___2026_.xlsx'
    creatives_imported = import_creative_tracker(creative_tracker_file, db)
    
    # Import Meta performance
    meta_file = 'Archive-Ads-Apr-1-2026-May-6-2026.xlsx'
    meta_imported = import_meta_performance(meta_file, db)
    
    # Summary
    print("=" * 60)
    print("  IMPORT COMPLETE")
    print("=" * 60)
    print(f"  Creative Tests: {creatives_imported}")
    print(f"  Meta Records:   {meta_imported}")
    print()
    print("🚀 Your dashboard is now populated with historical data!")
    print()
    print("Next steps:")
    print("1. Run: streamlit run app.py")
    print("2. Go to Dashboard Overview to see your metrics")
    print("3. Go to Settings to add Shopify API credentials")
    print()

if __name__ == "__main__":
    main()
