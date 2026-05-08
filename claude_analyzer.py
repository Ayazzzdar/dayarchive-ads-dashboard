import anthropic
import base64
from typing import Dict, Optional
import io

class ClaudeAnalyzer:
    def __init__(self, api_key: str, database):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.db = database
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_uploaded_file(self, uploaded_file, creative_name: str, 
                              creative_data: Optional[Dict] = None) -> Dict:
        """Analyze an uploaded creative file"""
        
        # Read file and convert to base64
        file_bytes = uploaded_file.read()
        file_type = uploaded_file.type
        
        # Determine media type
        if 'image' in file_type:
            media_type = file_type
            base64_data = base64.standard_b64encode(file_bytes).decode('utf-8')
        else:
            raise Exception("Video analysis not yet supported. Please use images or provide Google Drive link.")
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt(creative_name, creative_data)
        
        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse response
        analysis_text = message.content[0].text
        
        return self.parse_analysis_response(analysis_text)
    
    def analyze_from_gdrive(self, gdrive_url: str, creative_name: str,
                           creative_data: Optional[Dict] = None) -> Dict:
        """Analyze creative from Google Drive URL"""
        
        # Note: This would require Google Drive API integration
        # For now, return a placeholder
        
        raise Exception("Google Drive integration coming soon. Please upload the file directly for now.")
    
    def create_analysis_prompt(self, creative_name: str, creative_data: Optional[Dict]) -> str:
        """Create analysis prompt based on creative context"""
        
        # Get winning patterns
        winning_patterns = self.get_winning_patterns()
        
        prompt = f"""You are analyzing a Meta ad creative for The Day Archive, an Australian e-commerce business selling personalized historical archive prints as milestone birthday gifts.

**Product Context:**
- Premium milestone birthday gifts (50th, 60th, 70th, 80th birthdays)
- Target buyer: Women 40-65 buying for aging parents or spouses
- Price point: $70 AUD
- Product: Personalized historical archive of the day someone was born

**Creative Name:** {creative_name}
"""
        
        if creative_data:
            prompt += f"""
**Creative Test Details:**
- Concept: {creative_data.get('concept_number', 'N/A')}
- Format: {creative_data.get('format', 'N/A')}
- Variable Tested: {creative_data.get('variable_tested', 'N/A')}
- Avatar: {creative_data.get('avatar', 'N/A')}
- Awareness Level: {creative_data.get('awareness_level', 'N/A')}
- Angle/Hook: {creative_data.get('angle', 'N/A')}
- Hypothesis: {creative_data.get('hypothesis', 'N/A')}
"""
        
        if winning_patterns:
            prompt += f"""
**Your Winning Pattern DNA (ROAS > 3.0x creatives):**
{winning_patterns}
"""
        
        prompt += """
**Analyze this creative and provide:**

1. **VISUAL ANALYSIS** (100-150 words):
   - First impression (thumb-stop potential)
   - Visual hierarchy and focal points
   - Product visibility and clarity
   - Color scheme and mood
   - Text readability

2. **HOOK & MESSAGING ANALYSIS** (100-150 words):
   - Hook strength (first 3 words/seconds)
   - Problem-aware vs outcome-focused approach
   - Emotional resonance with target avatar
   - Clarity of value proposition
   - CTA strength and clarity

3. **WINNING PATTERN COMPARISON** (50-100 words):
   - How does this compare to the winning patterns above?
   - What elements match winners?
   - What elements differ from winners?

4. **SPECIFIC RECOMMENDATIONS** (3-5 bullet points):
   - Concrete improvements to test
   - What to keep, what to change
   - Predicted impact on performance

Be direct and actionable. This analysis informs real ad spend decisions.
"""
        
        return prompt
    
    def get_winning_patterns(self) -> str:
        """Extract winning patterns from high-performing creatives"""
        
        # Get top performers
        top_creatives = self.db.get_top_creatives(days=30, limit=5)
        
        if not top_creatives:
            return "No winning patterns yet - need performance data."
        
        patterns = []
        
        for creative in top_creatives:
            roas = creative['revenue'] / creative['spend'] if creative['spend'] > 0 else 0
            
            if roas >= 3.0:
                creative_data = self.db.get_creative_by_name(creative['creative_name'])
                
                if creative_data:
                    patterns.append(
                        f"- {creative_data['creative_name']}: {roas:.2f}x ROAS | "
                        f"Format: {creative_data['format']} | "
                        f"Angle: {creative_data['angle']} | "
                        f"Avatar: {creative_data['avatar']}"
                    )
        
        if not patterns:
            return "No creatives with ROAS > 3.0x yet."
        
        return "\n".join(patterns)
    
    def parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's analysis response"""
        
        # Split by sections
        sections = response_text.split('**')
        
        visual_elements = ""
        recommendations = ""
        winning_patterns = ""
        
        for i, section in enumerate(sections):
            section_lower = section.lower()
            
            if 'visual analysis' in section_lower:
                visual_elements = sections[i+1] if i+1 < len(sections) else ""
            elif 'recommendations' in section_lower or 'specific recommendations' in section_lower:
                recommendations = sections[i+1] if i+1 < len(sections) else ""
            elif 'winning pattern' in section_lower:
                winning_patterns = sections[i+1] if i+1 < len(sections) else ""
        
        # If parsing failed, use full response
        if not visual_elements and not recommendations:
            visual_elements = response_text[:len(response_text)//2]
            recommendations = response_text[len(response_text)//2:]
        
        return {
            'visual_elements': visual_elements.strip(),
            'recommendations': recommendations.strip(),
            'winning_patterns': winning_patterns.strip()
        }
