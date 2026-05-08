from typing import Dict, List
from datetime import datetime, timedelta

class RecommendationEngine:
    def __init__(self, database):
        self.db = database
        
        # Thresholds
        self.ROAS_TARGET = 3.0
        self.ROAS_KILL_THRESHOLD = 1.0
        self.MIN_CONVERSIONS = 10
        self.CTR_TARGET = 1.5
        self.FATIGUE_IMPRESSION_THRESHOLD = 50000
    
    def generate_recommendations(self) -> Dict:
        """Generate comprehensive recommendations"""
        
        recommendations = {
            'immediate_actions': [],
            'scale_opportunities': [],
            'pause_recommendations': [],
            'next_tests': [],
            'winning_patterns': {},
            'budget_optimization': {}
        }
        
        # Get recent performance
        recent_performance = self.db.get_recent_performance(days=7)
        
        if not recent_performance:
            return recommendations
        
        # Analyze each creative
        adset_stats = self.aggregate_by_adset(recent_performance)
        
        for ad_set_name, stats in adset_stats.items():
            roas = stats['revenue'] / stats['spend'] if stats['spend'] > 0 else 0
            conversions = stats['conversions']
            ctr = (stats['clicks'] / stats['impressions'] * 100) if stats['impressions'] > 0 else 0
            
            # Scale opportunities
            if roas >= self.ROAS_TARGET and conversions >= self.MIN_CONVERSIONS:
                recommendations['scale_opportunities'].append({
                    'ad_set_name': ad_set_name,
                    'roas': roas,
                    'reason': f"{roas:.2f}x ROAS with {conversions} conversions",
                    'recommendation': "Increase budget by 20-30%"
                })
            
            # Pause recommendations
            elif roas < self.ROAS_KILL_THRESHOLD and conversions >= self.MIN_CONVERSIONS:
                recommendations['pause_recommendations'].append({
                    'ad_set_name': ad_set_name,
                    'roas': roas,
                    'reason': f"Underperforming at {roas:.2f}x ROAS with {conversions} conversions",
                    'recommendation': "Pause and analyze learnings"
                })
            
            # Creative fatigue check
            elif stats['impressions'] > self.FATIGUE_IMPRESSION_THRESHOLD and ctr < 1.0:
                recommendations['immediate_actions'].append({
                    'title': f"Creative Fatigue: {ad_set_name}",
                    'description': f"{stats['impressions']:,} impressions with {ctr:.2f}% CTR",
                    'action': "Refresh creative or pause"
                })
            
            # High CTR, low conversion
            elif ctr > self.CTR_TARGET and conversions / stats['clicks'] < 0.02:
                recommendations['immediate_actions'].append({
                    'title': f"Conversion Issue: {ad_set_name}",
                    'description': f"Good CTR ({ctr:.2f}%) but low conversion rate",
                    'action': "Test landing page variations or offer changes"
                })
        
        # Winning patterns
        recommendations['winning_patterns'] = self.extract_winning_patterns(adset_stats)
        
        # Next test suggestions
        recommendations['next_tests'] = self.suggest_next_tests(adset_stats)
        
        # Budget optimization
        recommendations['budget_optimization'] = self.calculate_budget_optimization(recent_performance)
        
        return recommendations
    
    def aggregate_by_adset(self, performance_data: List[Dict]) -> Dict:
        """Aggregate performance data by ad set"""
        
        adset_stats = {}
        
        for row in performance_data:
            ad_set = row['ad_set_name']
            
            if not ad_set:
                continue
            
            if ad_set not in adset_stats:
                adset_stats[ad_set] = {
                    'spend': 0,
                    'revenue': 0,
                    'conversions': 0,
                    'clicks': 0,
                    'impressions': 0
                }
            
            adset_stats[ad_set]['spend'] += row['amount_spent']
            adset_stats[ad_set]['revenue'] += row['purchases_conversion_value']
            adset_stats[ad_set]['conversions'] += row['purchases']
            adset_stats[ad_set]['clicks'] += row['link_clicks']
            adset_stats[ad_set]['impressions'] += row['impressions']
        
        return adset_stats
    
    def extract_winning_patterns(self, adset_stats: Dict) -> Dict:
        """Extract patterns from winning vs losing creatives"""
        
        winners = []
        losers = []
        
        for ad_set_name, stats in adset_stats.items():
            roas = stats['revenue'] / stats['spend'] if stats['spend'] > 0 else 0
            
            if stats['conversions'] < self.MIN_CONVERSIONS:
                continue
            
            creative_data = self.db.get_creative_by_adset_name(ad_set_name)
            
            if not creative_data:
                continue
            
            if roas >= self.ROAS_TARGET:
                winners.append({
                    'name': creative_name,
                    'roas': roas,
                    'format': creative_data['format'],
                    'angle': creative_data['angle'],
                    'avatar': creative_data['avatar'],
                    'variable': creative_data['variable_tested'],
                    'awareness': creative_data.get('awareness_level', 'Unknown')
                })
            elif roas < self.ROAS_KILL_THRESHOLD:
                losers.append({
                    'name': creative_name,
                    'roas': roas,
                    'format': creative_data['format'],
                    'angle': creative_data['angle'],
                    'avatar': creative_data['avatar'],
                    'variable': creative_data['variable_tested']
                })
        
        # Analyze patterns
        patterns = {
            'working': [],
            'not_working': []
        }
        
        if winners:
            # Format analysis
            winner_formats = [w['format'] for w in winners]
            most_common_format = max(set(winner_formats), key=winner_formats.count)
            avg_roas_by_format = {}
            for w in winners:
                if w['format'] not in avg_roas_by_format:
                    avg_roas_by_format[w['format']] = []
                avg_roas_by_format[w['format']].append(w['roas'])
            
            for format_type, roas_list in avg_roas_by_format.items():
                avg = sum(roas_list) / len(roas_list)
                patterns['working'].append(f"{format_type} format: {avg:.2f}x avg ROAS")
            
            # Avatar analysis
            winner_avatars = [w['avatar'] for w in winners]
            most_common_avatar = max(set(winner_avatars), key=winner_avatars.count) if winner_avatars else None
            if most_common_avatar:
                patterns['working'].append(f"{most_common_avatar}: {winner_avatars.count(most_common_avatar)}/{len(winners)} winners")
            
            # Awareness stage
            winner_awareness = [w['awareness'] for w in winners]
            if winner_awareness:
                most_common_awareness = max(set(winner_awareness), key=winner_awareness.count)
                patterns['working'].append(f"{most_common_awareness} messaging resonates")
        
        if losers:
            loser_formats = [l['format'] for l in losers]
            if loser_formats:
                most_common_loser_format = max(set(loser_formats), key=loser_formats.count)
                patterns['not_working'].append(f"{most_common_loser_format} underperforming in current tests")
        
        return patterns
    
    def suggest_next_tests(self, adset_stats: Dict) -> List[Dict]:
        """Suggest next creative tests based on patterns"""
        
        suggestions = []
        
        # Get winning patterns
        winners = []
        for ad_set_name, stats in adset_stats.items():
            roas = stats['revenue'] / stats['spend'] if stats['spend'] > 0 else 0
            
            if roas >= self.ROAS_TARGET and stats['conversions'] >= self.MIN_CONVERSIONS:
                creative_data = self.db.get_creative_by_adset_name(ad_set_name)
                if creative_data:
                    winners.append(creative_data)
        
        if winners:
            # Suggest variations of winners
            top_winner = max(winners, key=lambda x: self.db.get_creative_performance(x['ad_set_name'])['revenue'] / 
                           self.db.get_creative_performance(x['ad_set_name'])['spend'])
            
            # Variation 1: Same angle, different format
            if top_winner['format'] == 'Image':
                suggestions.append({
                    'concept': f"Video version of {top_winner['ad_set_name']}",
                    'format': 'Video (15s)',
                    'angle': top_winner['angle'],
                    'hypothesis': f"Video format will outperform image while keeping winning angle: '{top_winner['angle']}'",
                    'reasoning': f"Your top performer uses {top_winner['format']} format. Video typically has higher engagement.",
                    'predicted_roas': '3.5-4.5x'
                })
            
            # Variation 2: Same format, different avatar
            suggestions.append({
                'concept': f"Test {top_winner['angle']} with different avatar",
                'format': top_winner['format'],
                'angle': top_winner['angle'],
                'hypothesis': f"Same winning angle but targeting Stressed Last-Minute Buyer avatar",
                'reasoning': f"Your {top_winner['avatar']} avatar is working. Test if the angle works for other segments.",
                'predicted_roas': '2.5-3.5x'
            })
        
        # Hybrid approach suggestion
        if len(winners) >= 2:
            suggestions.append({
                'concept': 'Hybrid: Combine winning elements',
                'format': winners[0]['format'],
                'angle': f"Combine {winners[0]['angle']} hook with {winners[1]['avatar']} targeting",
                'hypothesis': 'Combining multiple winning elements will compound effectiveness',
                'reasoning': 'You have multiple validated angles - test hybrid approach',
                'predicted_roas': '3.5-4.0x'
            })
        
        # Problem-aware urgency angle (based on your avatar doc)
        suggestions.append({
            'concept': 'Problem-Aware Urgency',
            'format': 'Video (15s)',
            'angle': "It's 2 weeks to Dad's 70th. What do you even get him?",
            'hypothesis': 'Urgency + problem-aware hook will outperform generic milestone messaging',
            'reasoning': 'Your data shows problem-aware angles perform well. Add urgency element.',
            'predicted_roas': '3.0-4.0x'
        })
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def calculate_budget_optimization(self, performance_data: List[Dict]) -> Dict:
        """Calculate budget optimization recommendations"""
        
        if not performance_data:
            return {}
        
        # Calculate daily spend
        daily_spend = {}
        for row in performance_data:
            date = row['date']
            if date not in daily_spend:
                daily_spend[date] = 0
            daily_spend[date] += row['spend']
        
        avg_daily_spend = sum(daily_spend.values()) / len(daily_spend) if daily_spend else 0
        
        # Calculate overall ROAS
        total_spend = sum(row['spend'] for row in performance_data)
        total_revenue = sum(row['revenue'] for row in performance_data)
        overall_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        # Target daily spend
        target_daily_spend = 1000  # Your goal
        
        # Recommendation
        if overall_roas >= self.ROAS_TARGET:
            recommended_daily_spend = min(avg_daily_spend * 1.3, target_daily_spend)
            reasoning = f"Strong {overall_roas:.2f}x ROAS supports scaling toward ${target_daily_spend}/day target."
        elif overall_roas >= 2.0:
            recommended_daily_spend = avg_daily_spend * 1.1
            reasoning = f"Decent {overall_roas:.2f}x ROAS. Scale cautiously by 10%."
        else:
            recommended_daily_spend = avg_daily_spend * 0.9
            reasoning = f"Below-target {overall_roas:.2f}x ROAS. Reduce spend by 10% and focus on creative optimization."
        
        return {
            'current_daily_spend': avg_daily_spend,
            'recommended_daily_spend': recommended_daily_spend,
            'target_daily_spend': target_daily_spend,
            'overall_roas': overall_roas,
            'reasoning': reasoning
        }
