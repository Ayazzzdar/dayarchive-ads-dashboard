import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class Database:
    def __init__(self, db_path=None):
        # Use Streamlit's data directory for persistence
        if db_path is None:
            import os
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'ads_dashboard.db')
        
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Creative Tests Table - matches your actual tracker structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS creative_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign TEXT,
            ad_set_name TEXT NOT NULL UNIQUE,
            launch_date TEXT,
            creative_type TEXT,
            landing_page TEXT,
            ad_inspiration TEXT,
            variable_tested TEXT,
            format TEXT,
            desire TEXT,
            experiences TEXT,
            emotional_desire TEXT,
            angle TEXT,
            avatar TEXT,
            awareness_level TEXT,
            beliefs TEXT,
            behaviors TEXT,
            hypothesis TEXT,
            variations INTEGER,
            status TEXT DEFAULT 'Launched',
            results TEXT,
            learnings TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Meta Performance Table - matches your actual Meta export
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meta_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporting_starts TEXT NOT NULL,
            reporting_ends TEXT,
            ad_name TEXT NOT NULL,
            ad_set_name TEXT NOT NULL,
            ad_delivery TEXT,
            results INTEGER DEFAULT 0,
            cost_per_results REAL DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            ad_set_budget TEXT,
            amount_spent REAL DEFAULT 0,
            link_clicks INTEGER DEFAULT 0,
            ctr REAL DEFAULT 0,
            cpc REAL DEFAULT 0,
            adds_to_cart INTEGER DEFAULT 0,
            cost_per_atc REAL DEFAULT 0,
            checkouts_initiated INTEGER DEFAULT 0,
            cost_per_checkout REAL DEFAULT 0,
            purchases INTEGER DEFAULT 0,
            cost_per_purchase REAL DEFAULT 0,
            purchases_conversion_value REAL DEFAULT 0,
            purchase_roas REAL DEFAULT 0,
            cpm REAL DEFAULT 0,
            cvr REAL DEFAULT 0,
            frequency REAL DEFAULT 0,
            ad_id TEXT,
            ad_set_id TEXT,
            campaign_id TEXT,
            hook_rate REAL DEFAULT 0,
            hold_rate REAL DEFAULT 0,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(reporting_starts, reporting_ends, ad_name)
        )
        """)
        
        # Shopify Orders Table - UTM tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopify_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            order_number TEXT NOT NULL,
            created_at TEXT NOT NULL,
            total_price REAL NOT NULL,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            utm_term TEXT,
            matched_ad_name TEXT,
            customer_email TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Hypothesis Results Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hypothesis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creative_id INTEGER NOT NULL,
            hypothesis TEXT NOT NULL,
            actual_result TEXT,
            roas REAL,
            spend REAL,
            revenue REAL,
            conversions INTEGER,
            conclusion TEXT,
            learnings TEXT,
            next_test TEXT,
            validated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creative_id) REFERENCES creative_tests(id)
        )
        """)
        
        # Creative Analysis Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS creative_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creative_id INTEGER NOT NULL,
            analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
            visual_elements TEXT,
            recommendations TEXT,
            winning_patterns TEXT,
            FOREIGN KEY (creative_id) REFERENCES creative_tests(id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # CREATIVE TESTS - Your actual tracker structure
    # ========================================================================
    
    def add_creative_test(self, campaign: str, ad_set_name: str, launch_date: str,
                         creative_type: str = None, landing_page: str = None,
                         ad_inspiration: str = None, variable_tested: str = None,
                         format_type: str = None, desire: str = None, experiences: str = None,
                         emotional_desire: str = None, angle: str = None, avatar: str = None,
                         awareness_level: str = None, beliefs: str = None, behaviors: str = None,
                         hypothesis: str = None, variations: int = None, status: str = "Launched",
                         results: str = None, learnings: str = None):
        """Add a new creative test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO creative_tests (
            campaign, ad_set_name, launch_date, creative_type, landing_page,
            ad_inspiration, variable_tested, format, desire, experiences,
            emotional_desire, angle, avatar, awareness_level, beliefs, behaviors,
            hypothesis, variations, status, results, learnings
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (campaign, ad_set_name, launch_date, creative_type, landing_page,
              ad_inspiration, variable_tested, format_type, desire, experiences,
              emotional_desire, angle, avatar, awareness_level, beliefs, behaviors,
              hypothesis, variations, status, results, learnings))
        
        conn.commit()
        creative_id = cursor.lastrowid
        conn.close()
        
        return creative_id
    
    def get_all_creative_tests(self) -> List[Dict]:
        """Get all creative tests"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM creative_tests
        ORDER BY launch_date DESC
        """)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_creative_by_adset_name(self, ad_set_name: str) -> Optional[Dict]:
        """Get creative test by ad set name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM creative_tests
        WHERE ad_set_name = ?
        """, (ad_set_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_creative_learnings(self, creative_id: int, learnings: str):
        """Update learnings for a creative test"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE creative_tests 
            SET learnings = ?
            WHERE id = ?
        ''', (learnings, creative_id))
        conn.commit()
        conn.close()
    
    def update_creative_status(self, creative_id: int, status: str):
        """Update creative status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE creative_tests
        SET status = ?
        WHERE id = ?
        """, (status, creative_id))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # META PERFORMANCE - Your actual Meta export structure
    # ========================================================================
    
    def add_performance_data(self, reporting_starts: str, reporting_ends: str,
                            ad_name: str, ad_set_name: str, ad_delivery: str,
                            results: int, cost_per_results: float, impressions: int,
                            ad_set_budget: str, amount_spent: float, link_clicks: int,
                            ctr: float, cpc: float, adds_to_cart: int, cost_per_atc: float,
                            checkouts_initiated: int, cost_per_checkout: float,
                            purchases: int, cost_per_purchase: float, purchases_conversion_value: float,
                            purchase_roas: float, cpm: float, cvr: float, frequency: float,
                            ad_id: str = None, ad_set_id: str = None, campaign_id: str = None,
                            hook_rate: float = 0, hold_rate: float = 0):
        """Add Meta performance data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO meta_performance (
            reporting_starts, reporting_ends, ad_name, ad_set_name, ad_delivery,
            results, cost_per_results, impressions, ad_set_budget, amount_spent,
            link_clicks, ctr, cpc, adds_to_cart, cost_per_atc,
            checkouts_initiated, cost_per_checkout, purchases, cost_per_purchase,
            purchases_conversion_value, purchase_roas, cpm, cvr, frequency,
            ad_id, ad_set_id, campaign_id, hook_rate, hold_rate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (reporting_starts, reporting_ends, ad_name, ad_set_name, ad_delivery,
              results, cost_per_results, impressions, ad_set_budget, amount_spent,
              link_clicks, ctr, cpc, adds_to_cart, cost_per_atc,
              checkouts_initiated, cost_per_checkout, purchases, cost_per_purchase,
              purchases_conversion_value, purchase_roas, cpm, cvr, frequency,
              ad_id, ad_set_id, campaign_id, hook_rate, hold_rate))
        
        conn.commit()
        conn.close()
    
    def get_recent_performance(self, days: int = 7, limit: int = None) -> List[Dict]:
        """Get recent performance data - filters by reporting_ends (most recent data point)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        query = """
        SELECT * FROM meta_performance
        WHERE reporting_ends >= ?
        ORDER BY reporting_ends DESC, amount_spent DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (cutoff_date,))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_performance_summary(self, days: int = 7) -> Optional[Dict]:
        """Get aggregated performance summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute("""
        SELECT 
            SUM(amount_spent) as total_spend,
            SUM(purchases_conversion_value) as total_revenue,
            SUM(impressions) as total_impressions,
            SUM(link_clicks) as total_clicks,
            SUM(purchases) as total_conversions,
            SUM(adds_to_cart) as total_atc
        FROM meta_performance
        WHERE reporting_starts >= ?
        """, (cutoff_date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['total_spend']:
            return dict(row)
        return None
    
    def get_top_creatives(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get top performing ads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cursor.execute("""
        SELECT 
            ad_name,
            ad_set_name,
            SUM(amount_spent) as spend,
            SUM(purchases_conversion_value) as revenue,
            SUM(purchases) as conversions,
            SUM(link_clicks) as clicks,
            SUM(impressions) as impressions,
            AVG(purchase_roas) as avg_roas
        FROM meta_performance
        WHERE reporting_starts >= ?
        GROUP BY ad_name
        ORDER BY revenue DESC
        LIMIT ?
        """, (cutoff_date, limit))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_creative_performance(self, ad_set_name: str) -> Dict:
        """Get aggregated performance for a specific ad set"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            SUM(amount_spent) as total_spend,
            SUM(purchases_conversion_value) as total_revenue,
            SUM(purchases) as total_conversions,
            SUM(link_clicks) as total_clicks,
            SUM(impressions) as total_impressions
        FROM meta_performance
        WHERE ad_set_name = ?
        """, (ad_set_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['total_spend']:
            return {
                'spend': row['total_spend'],
                'revenue': row['total_revenue'],
                'conversions': row['total_conversions'],
                'clicks': row['total_clicks'],
                'impressions': row['total_impressions']
            }
        return {'spend': 0, 'revenue': 0, 'conversions': 0, 'clicks': 0, 'impressions': 0}
    
    # ========================================================================
    # SHOPIFY ORDERS
    # ========================================================================
    
    def add_shopify_order(self, order_id: str, order_number: str, created_at: str,
                         total_price: float, utm_source: str = None, utm_medium: str = None,
                         utm_campaign: str = None, utm_content: str = None, utm_term: str = None,
                         matched_ad_name: str = None, customer_email: str = None):
        """Add Shopify order with UTM tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO shopify_orders (
            order_id, order_number, created_at, total_price,
            utm_source, utm_medium, utm_campaign, utm_content, utm_term,
            matched_ad_name, customer_email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, order_number, created_at, total_price,
              utm_source, utm_medium, utm_campaign, utm_content, utm_term,
              matched_ad_name, customer_email))
        
        conn.commit()
        conn.close()
    
    def get_shopify_attribution_summary(self, days_back: int = 30) -> List[Dict]:
        """Get revenue attribution by ad from Shopify"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        cursor.execute("""
        SELECT 
            matched_ad_name as ad_name,
            COUNT(*) as order_count,
            SUM(total_price) as revenue,
            utm_campaign,
            utm_content
        FROM shopify_orders
        WHERE created_at >= ? AND matched_ad_name IS NOT NULL
        GROUP BY matched_ad_name
        ORDER BY revenue DESC
        """, (cutoff_date,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_all_shopify_orders(self, days_back: int = 30) -> List[Dict]:
        """Get all Shopify orders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        cursor.execute("""
        SELECT * FROM shopify_orders
        WHERE created_at >= ?
        ORDER BY created_at DESC
        """, (cutoff_date,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    # ========================================================================
    # HYPOTHESIS & ANALYSIS (same as before)
    # ========================================================================
    
    def save_hypothesis_result(self, creative_id: int, hypothesis: str, actual_result: str,
                               roas: float, spend: float, revenue: float, conversions: int,
                               conclusion: str, learnings: str = None, next_test: str = None):
        """Save hypothesis validation result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO hypothesis_results (
            creative_id, hypothesis, actual_result, roas, spend, revenue, conversions,
            conclusion, learnings, next_test
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (creative_id, hypothesis, actual_result, roas, spend, revenue, conversions,
              conclusion, learnings, next_test))
        
        conn.commit()
        conn.close()
    
    def get_all_hypothesis_results(self) -> List[Dict]:
        """Get all hypothesis results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            hr.*, ct.ad_set_name, ct.campaign
        FROM hypothesis_results hr
        JOIN creative_tests ct ON hr.creative_id = ct.id
        ORDER BY hr.validated_at DESC
        """)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def save_creative_analysis(self, creative_id: int, visual_elements: str,
                               recommendations: str, winning_patterns: str = None):
        """Save creative analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO creative_analysis (
            creative_id, visual_elements, recommendations, winning_patterns
        ) VALUES (?, ?, ?, ?)
        """, (creative_id, visual_elements, recommendations, winning_patterns))
        
        conn.commit()
        conn.close()
    
    def get_all_creative_analyses(self) -> List[Dict]:
        """Get all creative analyses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            ca.*, ct.ad_set_name
        FROM creative_analysis ca
        JOIN creative_tests ct ON ca.creative_id = ct.id
        ORDER BY ca.analysis_date DESC
        """)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def clear_all_data(self):
        """Clear all data from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM creative_analysis")
        cursor.execute("DELETE FROM hypothesis_results")
        cursor.execute("DELETE FROM shopify_orders")
        cursor.execute("DELETE FROM meta_performance")
        cursor.execute("DELETE FROM creative_tests")
        
        conn.commit()
        conn.close()
