import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class ShopifyConnector:
    """
    Shopify API integration for The Day Archive
    Fetches orders with UTM parameters to track ad attribution
    """
    
    def __init__(self, shop_url: str, access_token: str, database):
        """
        Initialize Shopify connector
        
        Args:
            shop_url: Your Shopify store URL (e.g., "thedayarchive.myshopify.com")
            access_token: Shopify Admin API access token
            database: Database instance for storing order data
        """
        self.shop_url = shop_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.db = database
        self.base_url = f"https://{self.shop_url}/admin/api/2024-01"
        
    def get_headers(self) -> Dict:
        """Get API request headers"""
        return {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def fetch_orders(self, days_back: int = 30, status: str = 'any') -> List[Dict]:
        """
        Fetch orders from Shopify
        
        Args:
            days_back: Number of days to look back
            status: Order status filter ('any', 'open', 'closed', 'cancelled')
        
        Returns:
            List of order dictionaries
        """
        created_at_min = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        url = f"{self.base_url}/orders.json"
        params = {
            'status': status,
            'created_at_min': created_at_min,
            'limit': 250,  # Max per page
            # Request customer_journey_summary explicitly
            'fields': 'id,order_number,created_at,total_price,customer,customer_journey_summary,client_details,landing_site,landing_site_ref,referring_site'
        }
        
        all_orders = []
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            orders = data.get('orders', [])
            all_orders.extend(orders)
            
            # Handle pagination if needed
            while 'link' in response.headers:
                # Shopify uses Link header for pagination
                links = response.headers['link'].split(',')
                next_link = None
                
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link.split(';')[0].strip('<> ')
                        break
                
                if not next_link:
                    break
                
                response = requests.get(next_link, headers=self.get_headers(), timeout=30)
                response.raise_for_status()
                data = response.json()
                orders = data.get('orders', [])
                all_orders.extend(orders)
            
            return all_orders
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Shopify API error: {str(e)}")
    
    def extract_utm_params(self, order: Dict) -> Dict:
        """
        Extract UTM parameters from order
        
        Shopify 2024-01+ API stores UTM params in multiple places:
        1. customer_journey_summary.last_visit.utm_parameters (most reliable)
        2. client_details fields
        3. landing_site_ref (fallback)
        """
        utm_params = {
            'utm_source': None,
            'utm_medium': None,
            'utm_campaign': None,
            'utm_content': None,
            'utm_term': None
        }
        
        # Try customer_journey_summary first (Shopify 2024-01+ API)
        customer_journey = order.get('customer_journey_summary')
        if customer_journey and customer_journey.get('last_visit'):
            last_visit = customer_journey['last_visit']
            
            # Extract from utm_parameters object
            if 'utm_parameters' in last_visit:
                utm_data = last_visit['utm_parameters']
                utm_params['utm_source'] = utm_data.get('utm_source')
                utm_params['utm_medium'] = utm_data.get('utm_medium')
                utm_params['utm_campaign'] = utm_data.get('utm_campaign')
                utm_params['utm_content'] = utm_data.get('utm_content')
                utm_params['utm_term'] = utm_data.get('utm_term')
                
                if any(v is not None for v in utm_params.values()):
                    return utm_params
            
            # Fallback: parse from landing_site in last_visit
            landing_site = last_visit.get('landing_site')
            if landing_site and '?' in landing_site:
                return self._parse_utm_from_url(landing_site)
        
        # Try client_details (alternative location)
        client_details = order.get('client_details')
        if client_details:
            for key in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']:
                if key in client_details:
                    utm_params[key] = client_details[key]
            
            if any(v is not None for v in utm_params.values()):
                return utm_params
        
        # Fallback: landing_site_ref (older API)
        landing_site_ref = order.get('landing_site_ref', '')
        if landing_site_ref:
            return self._parse_utm_from_url(landing_site_ref)
        
        return utm_params
    
    def _parse_utm_from_url(self, url: str) -> Dict:
        """Parse UTM parameters from URL query string"""
        utm_params = {
            'utm_source': None,
            'utm_medium': None,
            'utm_campaign': None,
            'utm_content': None,
            'utm_term': None
        }
        
        if '?' in url:
            query_string = url.split('?')[1]
            params = query_string.split('&')
            
            for param in params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    if key in utm_params:
                        # URL decode the value
                        import urllib.parse
                        utm_params[key] = urllib.parse.unquote(value)
        
        return utm_params
    
    def match_order_to_ad(self, utm_params: Dict, ad_name: str = None) -> Optional[str]:
        """
        Match Shopify order to Meta ad using UTM parameters
        
        UTM content typically contains ad identifier
        Example: utm_content=C9_Ad_1_30/4
        
        Args:
            utm_params: Extracted UTM parameters
            ad_name: Optional ad name override
        
        Returns:
            Matched ad name or None
        """
        # If utm_content exists, try to match to ad name
        utm_content = utm_params.get('utm_content')
        utm_campaign = utm_params.get('utm_campaign')
        
        if utm_content:
            # Try exact match first
            ad_name_from_utm = utm_content.replace('_', ' ').replace('-', ' ')
            
            # Check if this matches any Meta ad
            # This will be done during import by checking against meta_performance table
            return utm_content
        
        if utm_campaign:
            # Try to extract ad info from campaign name
            return utm_campaign
        
        return None
    
    def import_orders_to_database(self, days_back: int = 30) -> Dict:
        """
        Import Shopify orders into database with UTM tracking
        
        Returns:
            Import summary statistics
        """
        orders = self.fetch_orders(days_back=days_back)
        
        imported = 0
        matched_to_ads = 0
        total_revenue = 0
        
        # Store debug info to return
        debug_info = {}
        
        if orders:
            # Capture first order structure for debugging
            first_order = orders[0]
            debug_info['order_number'] = first_order.get('order_number')
            debug_info['available_fields'] = list(first_order.keys())
            debug_info['has_customer_journey_summary'] = 'customer_journey_summary' in first_order
            debug_info['has_client_details'] = 'client_details' in first_order
            debug_info['has_landing_site_ref'] = 'landing_site_ref' in first_order
            
            if 'customer_journey_summary' in first_order:
                cj = first_order['customer_journey_summary']
                debug_info['customer_journey_keys'] = list(cj.keys()) if cj else None
                if cj and cj.get('last_visit'):
                    debug_info['last_visit_keys'] = list(cj['last_visit'].keys())
            
            # Try to extract UTMs from first order
            utm_test = self.extract_utm_params(first_order)
            debug_info['utm_extraction_test'] = utm_test
        
        for order in orders:
            # Extract order details
            order_id = order.get('id')
            order_number = order.get('order_number')
            created_at = order.get('created_at', '')[:10]  # YYYY-MM-DD
            total_price = float(order.get('total_price', 0))
            financial_status = order.get('financial_status')
            
            # Only count paid orders
            if financial_status not in ['paid', 'partially_paid']:
                continue
            
            # Extract UTM params
            utm_params = self.extract_utm_params(order)
            
            # Try to match to ad
            matched_ad = self.match_order_to_ad(utm_params)
            
            # Customer info
            customer = order.get('customer', {})
            customer_email = customer.get('email', '') if customer else ''
            
            # Save to database
            self.db.add_shopify_order(
                order_id=str(order_id),
                order_number=str(order_number),
                created_at=created_at,
                total_price=total_price,
                utm_source=utm_params.get('utm_source'),
                utm_medium=utm_params.get('utm_medium'),
                utm_campaign=utm_params.get('utm_campaign'),
                utm_content=utm_params.get('utm_content'),
                utm_term=utm_params.get('utm_term'),
                matched_ad_name=matched_ad,
                customer_email=customer_email
            )
            
            imported += 1
            total_revenue += total_price
            
            if matched_ad:
                matched_to_ads += 1
        
        return {
            'orders_imported': imported,
            'matched_to_ads': matched_to_ads,
            'unmatched': imported - matched_to_ads,
            'total_revenue': total_revenue,
            'match_rate': (matched_to_ads / imported * 100) if imported > 0 else 0,
            'debug_info': debug_info  # Add debug info to return
        }
    
    def get_attribution_summary(self, days_back: int = 30) -> List[Dict]:
        """
        Get revenue attribution by ad from Shopify orders
        
        Returns:
            List of {ad_name, order_count, revenue} for each matched ad
        """
        return self.db.get_shopify_attribution_summary(days_back)
    
    def reconcile_with_meta(self) -> Dict:
        """
        Compare Shopify-tracked revenue vs Meta-tracked revenue
        Shows tracking gap
        
        Returns:
            Reconciliation report
        """
        # Get Shopify revenue by ad
        shopify_data = self.db.get_shopify_attribution_summary(30)
        
        # Get Meta revenue by ad
        meta_data = self.db.get_recent_performance(30)
        
        # Compare
        comparison = []
        
        for meta_row in meta_data:
            ad_name = meta_row['creative_name'] or meta_row['ad_name']
            meta_revenue = meta_row['revenue']
            meta_purchases = meta_row['conversions']
            
            # Find matching Shopify data
            shopify_match = next((s for s in shopify_data if s['ad_name'] == ad_name), None)
            
            shopify_revenue = shopify_match['revenue'] if shopify_match else 0
            shopify_purchases = shopify_match['order_count'] if shopify_match else 0
            
            tracking_gap = meta_revenue - shopify_revenue if meta_revenue > 0 else 0
            tracking_rate = (shopify_revenue / meta_revenue * 100) if meta_revenue > 0 else 0
            
            comparison.append({
                'ad_name': ad_name,
                'meta_revenue': meta_revenue,
                'meta_purchases': meta_purchases,
                'shopify_revenue': shopify_revenue,
                'shopify_purchases': shopify_purchases,
                'tracking_gap': tracking_gap,
                'tracking_rate': tracking_rate
            })
        
        return comparison
