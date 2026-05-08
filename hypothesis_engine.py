from typing import List, Dict
from datetime import datetime, timedelta

class HypothesisEngine:
    def __init__(self, database):
        self.db = database
        
        # Validation thresholds
        self.ROAS_THRESHOLD_VALIDATED = 2.0  # Changed from 3.0 to 2.0
        self.ROAS_THRESHOLD_INVALIDATED = 1.0
        self.MIN_DAYS_RUNNING = 7  # Changed from 10 conversions to 7 days
    
    def validate_all_hypotheses(self) -> List[Dict]:
        """Validate all creative hypotheses against actual performance"""
        
        creatives = self.db.get_all_creative_tests()
        validations = []
        
        for creative in creatives:
            validation = self.validate_creative(creative)
            if validation:
                validations.append(validation)
        
        return validations
    
    def validate_creative(self, creative: Dict) -> Dict:
        """Validate a single creative's hypothesis"""
        
        # Get performance data by ad set name
        performance = self.db.get_creative_performance(creative['ad_set_name'])
        
        if not performance or performance['spend'] == 0:
            return None  # No performance data yet
        
        # Calculate ROAS
        roas = performance['revenue'] / performance['spend'] if performance['spend'] > 0 else 0
        conversions = performance['conversions']
        spend = performance['spend']
        
        # Check how long it's been running
        launch_date = creative.get('launch_date')
        if launch_date:
            try:
                launch_dt = datetime.strptime(launch_date, '%Y-%m-%d')
                days_running = (datetime.now() - launch_dt).days
            except:
                days_running = 0
        else:
            days_running = 0
        
        # EARLY PERFORMANCE INDICATORS (before 7 days)
        if days_running < self.MIN_DAYS_RUNNING:
            # Show early signals based on ROAS
            if roas >= 2.0:
                conclusion = "Early Winner 🔥"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions and ${spend:.2f} spend. STRONG EARLY SIGNAL - This is working!"
                learnings = f"✅ EARLY WIN: Above 2x ROAS after {days_running} days. This angle/format is resonating. Monitor closely and prepare to scale at day 7."
                next_test = f"Continue running. If ROAS holds above 2x through day 7, scale immediately. Consider creating variations of this winning angle."
            
            elif roas >= 1.5:
                conclusion = "Promising Signal 📊"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions and ${spend:.2f} spend. Profitable with room to improve."
                learnings = f"📈 LEARNING OPPORTUNITY: Between 1.5-2x ROAS. Something is working. Review hypothesis - which element is performing? Consider iterating on: headline, image, angle, or offer."
                next_test = f"Continue to day 7. Analyze what's working: Is it the {creative.get('angle', 'angle')}? The {creative.get('format', 'format')}? Create 2-3 variations testing individual elements."
            
            else:
                conclusion = "Inconclusive (Early)"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions. Need {self.MIN_DAYS_RUNNING} days minimum for validation."
                learnings = f"⏳ TOO EARLY: Only {days_running} days running. Continue to day 7 before making decisions."
                next_test = "Wait until 7 days have passed before making decisions."
        
        # FULL VALIDATION (7+ days)
        else:
            if roas >= self.ROAS_THRESHOLD_VALIDATED:
                conclusion = "Validated ✅"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions confirms hypothesis."
                learnings = self.extract_learnings_from_winner(creative, performance)
                next_test = self.suggest_next_test_from_winner(creative, performance)
            
            elif roas < self.ROAS_THRESHOLD_INVALIDATED:
                conclusion = "Invalidated ❌"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions. Hypothesis did not hold."
                learnings = self.extract_learnings_from_loser(creative, performance)
                next_test = self.suggest_next_test_from_loser(creative, performance)
            
            else:
                # Between 1.0x and 2.0x
                conclusion = "Partially Validated ⚠️"
                actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions. Profitable but below 2.0x target."
                learnings = "Creative is profitable (above 1.0x) but not hitting the 2.0x validation threshold. Some elements are working, others need optimization."
                next_test = "Test variations to push this above 2.0x. Focus on: improving hook rate, strengthening CTA, or testing different angle/format combinations."
        
        # Save to database
        self.db.save_hypothesis_result(
            creative_id=creative['id'],
            hypothesis=creative['hypothesis'],
            actual_result=actual_result,
            roas=roas,
            spend=performance['spend'],
            revenue=performance['revenue'],
            conversions=conversions,
            conclusion=conclusion,
            learnings=learnings,
            next_test=next_test
        )
        
        return {
            'ad_set_name': creative['ad_set_name'],
            'hypothesis': creative['hypothesis'],
            'actual_result': actual_result,
            'roas': roas,
            'spend': performance['spend'],
            'revenue': performance['revenue'],
            'conversions': conversions,
            'conclusion': conclusion,
            'learnings': learnings,
            'next_test': next_test
        }
    
    def extract_learnings_from_winner(self, creative: Dict, performance: Dict) -> str:
        """Extract learnings from successful creative"""
        learnings = []
        
        # Avatar learnings
        learnings.append(f"✅ {creative['avatar']} avatar responds well to this messaging.")
        
        # Angle learnings
        learnings.append(f"✅ '{creative['angle']}' angle is effective.")
        
        # Format learnings
        ctr = (performance['clicks'] / performance['impressions'] * 100) if performance['impressions'] > 0 else 0
        if ctr > 1.5:
            learnings.append(f"✅ {creative['format']} format generates strong {ctr:.2f}% CTR.")
        
        # Awareness stage learnings
        learnings.append(f"✅ {creative.get('awareness_level', 'Unknown')} messaging works for this audience.")
        
        return " ".join(learnings)
    
    def extract_learnings_from_loser(self, creative: Dict, performance: Dict) -> str:
        """Extract learnings from unsuccessful creative"""
        learnings = []
        
        # Determine what went wrong
        ctr = (performance['clicks'] / performance['impressions'] * 100) if performance['impressions'] > 0 else 0
        
        if ctr < 1.0:
            learnings.append(f"❌ Low CTR ({ctr:.2f}%) suggests hook/visual isn't stopping the scroll.")
            learnings.append(f"Consider testing stronger hooks or different {creative['format']} style.")
        else:
            learnings.append(f"❌ Good CTR ({ctr:.2f}%) but low conversion suggests:")
            learnings.append("Landing page mismatch OR offer not compelling enough.")
        
        learnings.append(f"❌ {creative['angle']} angle may not resonate with {creative['avatar']}.")
        
        return " ".join(learnings)
    
    def suggest_next_test_from_winner(self, creative: Dict, performance: Dict) -> str:
        """Suggest next test based on winning creative"""
        
        suggestions = []
        
        # Suggest scaling
        suggestions.append("SCALE: Increase budget by 20-30%.")
        
        # Suggest variations
        if creative['variable_tested'] == 'Angle':
            suggestions.append(f"TEST: Keep same visual, test different angle variations.")
        elif creative['variable_tested'] == 'Visual Style':
            suggestions.append(f"TEST: Keep same angle, test different visual treatments.")
        elif creative['variable_tested'] == 'Hook':
            suggestions.append(f"TEST: Test this hook with different avatars.")
        
        # Suggest format expansion
        if creative['format'] == 'Image':
            suggestions.append("TEST: Adapt this creative to video format (same angle).")
        
        return " ".join(suggestions)
    
    def suggest_next_test_from_loser(self, creative: Dict, performance: Dict) -> str:
        """Suggest next test based on losing creative"""
        
        suggestions = []
        
        ctr = (performance['clicks'] / performance['impressions'] * 100) if performance['impressions'] > 0 else 0
        
        if ctr < 1.0:
            # Hook/visual problem
            suggestions.append("TEST: Completely different hook/visual approach.")
            suggestions.append(f"Try opposite of {creative['angle']} - maybe outcome-focused instead of problem-aware.")
        else:
            # Conversion problem
            suggestions.append("TEST: Same creative with different offer/CTA.")
            suggestions.append("Consider landing page optimization or bundle offer.")
        
        # Avatar pivot
        suggestions.append(f"CONSIDER: Testing different avatar - maybe {creative['avatar']} isn't ideal for this angle.")
        
        return " ".join(suggestions)
    
    def get_validation_summary(self) -> Dict:
        """Get summary of all validations"""
        
        results = self.db.get_all_hypothesis_results()
        
        if not results:
            return None
        
        validated = [r for r in results if r['conclusion'] == 'Validated']
        invalidated = [r for r in results if r['conclusion'] == 'Invalidated']
        inconclusive = [r for r in results if r['conclusion'] in ['Inconclusive', 'Partially Validated']]
        
        return {
            'total_tests': len(results),
            'validated_count': len(validated),
            'invalidated_count': len(invalidated),
            'inconclusive_count': len(inconclusive),
            'validation_rate': (len(validated) / len(results) * 100) if results else 0,
            'validated_creatives': validated,
            'invalidated_creatives': invalidated
        }
