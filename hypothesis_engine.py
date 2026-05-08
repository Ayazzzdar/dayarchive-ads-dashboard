from typing import List, Dict
from datetime import datetime, timedelta

class HypothesisEngine:
    def __init__(self, database):
        self.db = database
        
        # Validation thresholds
        self.ROAS_THRESHOLD_VALIDATED = 3.0
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
        
        # Determine conclusion based on 7 days minimum
        if days_running < self.MIN_DAYS_RUNNING:
            conclusion = "Inconclusive"
            actual_result = f"Only running for {days_running} days. Need {self.MIN_DAYS_RUNNING} days minimum for validation."
            learnings = "Continue running to gather more data."
            next_test = "Wait until 7 days have passed before making decisions."
        
        elif roas >= self.ROAS_THRESHOLD_VALIDATED:
            conclusion = "Validated"
            actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions confirms hypothesis."
            learnings = self.extract_learnings_from_winner(creative, performance)
            next_test = self.suggest_next_test_from_winner(creative, performance)
        
        elif roas < self.ROAS_THRESHOLD_INVALIDATED:
            conclusion = "Invalidated"
            actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions. Hypothesis did not hold."
            learnings = self.extract_learnings_from_loser(creative, performance)
            next_test = self.suggest_next_test_from_loser(creative, performance)
        
        else:
            # Between 1.0x and 3.0x
            conclusion = "Partially Validated"
            actual_result = f"After {days_running} days: ROAS of {roas:.2f}x with {conversions} conversions. Profitable but below target."
            learnings = "Creative is working but has room for improvement."
            next_test = "Test variations of this creative to optimize performance."
        
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
        learnings.append(f"✅ {creative['awareness_stage']} messaging works for this audience.")
        
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
