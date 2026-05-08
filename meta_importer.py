import pandas as pd
import io
from typing import Dict
from datetime import datetime

class MetaImporter:
    def __init__(self, database):
        self.db = database
    
    def import_excel(self, uploaded_file) -> Dict:
        """
        Import Meta Ads Manager Excel export
        Matches The Day Archive's actual export format
        """
        
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            raise Exception(f"Failed to read Excel file: {str(e)}")
        
        # Verify expected columns exist
        required_cols = ['Reporting starts', 'Ad name', 'Ad set name', 'Amount spent (AUD)', 'Purchases']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            raise Exception(f"Missing required columns: {', '.join(missing)}")
        
        # Clean data
        # Replace NaN with 0 for numeric columns
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
        
        # Match to creative tracker by ad set name
        matched_count = 0
        rows_imported = 0
        
        for idx, row in df.iterrows():
            # Try to match ad set name to creative tracker
            ad_set_name = str(row['Ad set name'])
            creative_match = self.db.get_creative_by_adset_name(ad_set_name)
            
            if creative_match:
                matched_count += 1
            
            # Import to database
            self.db.add_performance_data(
                reporting_starts=row['Reporting starts'],
                reporting_ends=row.get('Reporting ends', row['Reporting starts']),
                ad_name=str(row['Ad name']),
                ad_set_name=ad_set_name,
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
                ad_id=str(row.get('Ad ID', '')),
                ad_set_id=str(row.get('Ad set ID', '')),
                campaign_id=str(row.get('Campaign ID', '')),
                hook_rate=float(row.get('Hook Rate', 0)),
                hold_rate=float(row.get('Hold Rate New', 0))
            )
            
            rows_imported += 1
        
        # Get unmatched ad sets
        all_ad_sets = df['Ad set name'].unique().tolist()
        creative_ad_sets = [c['ad_set_name'] for c in self.db.get_all_creative_tests()]
        unmatched = [ad_set for ad_set in all_ad_sets if ad_set not in creative_ad_sets]
        
        return {
            'rows_imported': rows_imported,
            'matched_to_creative_tracker': matched_count,
            'unmatched_ad_sets': unmatched[:10]  # First 10
        }
    
    def import_csv(self, uploaded_file) -> Dict:
        """Import CSV format (same logic as Excel)"""
        try:
            content = uploaded_file.read()
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise Exception(f"Failed to read CSV: {str(e)}")
        
        # Use same logic as Excel import
        # Convert to in-memory Excel format
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            tmp.seek(0)
            return self.import_excel(tmp.name)
