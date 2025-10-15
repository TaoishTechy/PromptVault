#!/usr/bin/env python3
"""
Psychological Engine - Modular psychological scaffolding system
Zero-dependency implementation with JSON configuration
"""

import json
import re
import random
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any
import time


class ConfigLoader:
    """Load and manage configuration from JSON files."""
    
    def __init__(self, config_path: str = "config.json", techniques_path: str = "techniques.json"):
        self.config_path = config_path
        self.techniques_path = techniques_path
        self.config = self._load_json(config_path)
        self.techniques = self._load_json(techniques_path)
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load {filename}: {str(e)}")
    
    def get_emotional_lexicon(self) -> Dict[str, List[str]]:
        """Get emotional lexicon configuration."""
        return self.config.get("emotional_lexicon", {})
    
    def get_stealth_lexicon(self) -> Dict[str, List[str]]:
        """Get stealth lexicon configuration."""
        return self.config.get("stealth_lexicon", {})
    
    def get_semantic_buffer(self) -> List[str]:
        """Get semantic buffer words."""
        return self.config.get("semantic_buffer", [])
    
    def get_fractal_stories(self) -> Dict[str, str]:
        """Get fractal story templates."""
        return self.config.get("fractal_stories", {})
    
    def get_structural_templates(self) -> Dict[str, str]:
        """Get structural templates."""
        return self.config.get("structural_templates", {})
    
    def get_psych_profiles(self) -> Dict[str, Dict[str, str]]:
        """Get psychological profiles."""
        return self.config.get("psych_profiles", {})
    
    def get_emotional_themes(self) -> Dict[str, Dict[str, str]]:
        """Get emotional theme configurations."""
        return self.config.get("emotional_themes", {})
    
    def get_stealth_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Get stealth technique configurations."""
        return self.techniques.get("stealth_techniques", {})
    
    def get_technique_sequence(self) -> List[str]:
        """Get technique application sequence."""
        return self.techniques.get("technique_sequence", [])


class PsychologicalScaffolding:
    """Core psychological scaffolding engine."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.enabled_features = {
            'emotional': False,
            'cognitive': False, 
            'behavioral': False
        }
        
        self.flow_states = {'scattered': 0, 'focused': 0, 'deep_flow': 0}
        self.usage_patterns = {
            'session_start_times': [],
            'edit_frequency': [],
            'category_usage': defaultdict(int)
        }
        
        self.current_mood = "neutral"
        self.last_intervention_time = 0
        self.work_sessions = []

    def analyze_emotional_tone(self, text: str) -> str:
        """Analyze text for emotional tone using lexicon-based approach."""
        if not self.enabled_features['emotional']:
            return "neutral"
            
        lexicon = self.config.get_emotional_lexicon()
        text_lower = text.lower()
        word_counts = Counter(text_lower.split())
        tone_scores: Dict[str, int] = {}
        
        for tone, words in lexicon.items():
            score = sum(word_counts[word] for word in words if word in word_counts)
            tone_scores[tone] = score
            
        if tone_scores:
            dominant_tone = max(tone_scores.items(), key=lambda x: x[1])
            if dominant_tone[1] > 0:
                return dominant_tone[0]
                
        return "neutral"

    def detect_cognitive_load(self, text: str) -> float:
        """Estimate cognitive load from text complexity."""
        if not self.enabled_features['cognitive']:
            return 0.5
            
        words = text.split()
        if len(words) < 10:
            return 0.3
            
        long_words = sum(1 for word in words if len(word) > 8)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        complexity = (long_words / len(words)) * 0.6 + (min(avg_sentence_length / 20, 1)) * 0.4
        return min(complexity, 1.0)

    def track_work_pattern(self, action_type: str, metadata: Optional[Dict] = None) -> None:
        """Track user work patterns for behavioral insights."""
        if not any(self.enabled_features.values()):
            return
            
        current_time = time.time()
        self.usage_patterns['session_start_times'].append(current_time)
        
        if action_type == "edit":
            self.usage_patterns['edit_frequency'].append(current_time)
            
        if metadata and 'category' in metadata:
            self.usage_patterns['category_usage'][metadata['category']] += 1

    def get_emotional_theme(self, tone: str) -> Dict[str, str]:
        """Get color theme adjustments based on emotional tone."""
        themes = self.config.get_emotional_themes()
        return themes.get(tone, themes['neutral'])

    def should_intervene(self, current_activity: str) -> bool:
        """Determine if a psychological intervention is appropriate."""
        if not any(self.enabled_features.values()):
            return False
            
        current_time = time.time()
        time_since_last = current_time - self.last_intervention_time
        
        if time_since_last < 300:  # 5 minutes
            return False
            
        recent_edits = [t for t in self.usage_patterns['edit_frequency'] 
                       if current_time - t < 600]  # Last 10 minutes
        
        if len(recent_edits) > 15 and self.enabled_features['emotional']:
            self.last_intervention_time = current_time
            return True
            
        return False


class StealthScaffoldEngine:
    """Advanced psychological prompt engineering system."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader
        self.techniques_enabled = self._initialize_techniques()
        self.technique_usage_stats: Dict[str, int] = defaultdict(int)

    def _initialize_techniques(self) -> Dict[str, bool]:
        """Initialize techniques from configuration."""
        techniques_config = self.config.get_stealth_techniques()
        return {name: config['enabled'] for name, config in techniques_config.items()}

    def apply_lexical_density_cloaking(self, prompt: str, target_emotion: str) -> str:
        """Encode emotional payload by distributing keywords across semantic buffer."""
        if not self.techniques_enabled['lexical_density_cloaking']:
            return prompt
            
        target_words = self.config.get_stealth_lexicon().get(target_emotion, [])
        if not target_words:
            return prompt
            
        words = prompt.split()
        buffer_words = self.config.get_semantic_buffer()
        buffer_size = max(5, len(words) // 4)
        selected_buffer = random.sample(buffer_words, min(buffer_size, len(buffer_words)))
        
        cloaked_parts = []
        for i, word in enumerate(target_words):
            if i < len(selected_buffer):
                cloaked_parts.extend([selected_buffer[i], word])
            else:
                cloaked_parts.append(word)
                
        if len(words) > 10:
            insertion_point = len(words) // 3
            enhanced_words = words[:insertion_point] + cloaked_parts + words[insertion_point:]
        else:
            enhanced_words = words + cloaked_parts
            
        self.technique_usage_stats['lexical_density_cloaking'] += 1
        return ' '.join(enhanced_words)

    def apply_fractal_pretexting(self, prompt: str, interaction_model: str) -> str:
        """Embed miniature meta-prompt modeling desired interaction."""
        if not self.techniques_enabled['fractal_pretexting']:
            return prompt
            
        fractal_stories = self.config.get_fractal_stories()
        if interaction_model in fractal_stories:
            prefixed_prompt = fractal_stories[interaction_model] + prompt
            self.technique_usage_stats['fractal_pretexting'] += 1
            return prefixed_prompt
            
        return prompt

    def apply_syntactic_pressure_gradients(self, prompt: str, target_state: str) -> str:
        """Manipulate sentence structure to influence processing state."""
        if not self.techniques_enabled['syntactic_pressure_gradients']:
            return prompt
            
        sentences = re.split(r'[.!?]+', prompt)
        if len(sentences) < 2:
            return prompt
            
        processed_sentences = []
        
        if target_state == 'focus':
            for sentence in sentences:
                if sentence.strip():
                    words = sentence.split()
                    if len(words) > 15:
                        mid_point = len(words) // 2
                        processed_sentences.append(' '.join(words[:mid_point]))
                        processed_sentences.append(' '.join(words[mid_point:]))
                    else:
                        processed_sentences.append(sentence)
                        
        self.technique_usage_stats['syntactic_pressure_gradients'] += 1
        return '. '.join(processed_sentences) + '.'

    def apply_zero_token_scaffolding(self, prompt: str, structural_template: str) -> str:
        """Use structural elements to imply psychological demands."""
        if not self.techniques_enabled['zero_token_scaffolding']:
            return prompt
            
        templates = self.config.get_structural_templates()
        if structural_template in templates:
            template = templates[structural_template]
            enhanced_prompt = template.format(content=prompt)
            self.technique_usage_stats['zero_token_scaffolding'] += 1
            return enhanced_prompt
            
        return prompt

    def apply_stealth_optimization(self, prompt: str, psychological_profile: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
        """Apply multiple stealth techniques based on psychological profile."""
        enhanced_prompt = prompt
        applied_techniques = []
        
        target_emotion = psychological_profile.get('emotional_tone', 'clarity')
        cognitive_state = psychological_profile.get('cognitive_state', 'focus')
        interaction_mode = psychological_profile.get('interaction_mode', 'precision')
        
        technique_mapping = {
            'fractal_pretexting': lambda p: self.apply_fractal_pretexting(p, interaction_mode),
            'lexical_density_cloaking': lambda p: self.apply_lexical_density_cloaking(p, target_emotion),
            'syntactic_pressure_gradients': lambda p: self.apply_syntactic_pressure_gradients(p, cognitive_state),
            'zero_token_scaffolding': lambda p: self.apply_zero_token_scaffolding(p, 'formal')
        }
        
        sequence = self.config.get_technique_sequence()
        for tech_name in sequence:
            if self.techniques_enabled.get(tech_name, False) and tech_name in technique_mapping:
                previous_prompt = enhanced_prompt
                enhanced_prompt = technique_mapping[tech_name](enhanced_prompt)
                if enhanced_prompt != previous_prompt:
                    applied_techniques.append(tech_name)
        
        report = {
            'original_length': len(prompt),
            'enhanced_length': len(enhanced_prompt),
            'techniques_applied': applied_techniques,
            'stealth_score': self._calculate_stealth_score(applied_techniques),
            'psychological_profile': psychological_profile
        }
        
        return enhanced_prompt, report

    def _calculate_stealth_score(self, applied_techniques: List[str]) -> float:
        """Calculate how stealthy the applied techniques are."""
        techniques_config = self.config.get_stealth_techniques()
        stealth_weights = {name: config['stealth_score'] for name, config in techniques_config.items()}
        
        if not applied_techniques:
            return 0.0
            
        total_weight = sum(stealth_weights.get(tech, 0) for tech in applied_techniques)
        return min(total_weight / len(applied_techniques), 1.0)


class PsychologicalOrchestrator:
    """Orchestrates all psychological scaffolding components."""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.psych_scaffolding = PsychologicalScaffolding(self.config_loader)
        self.stealth_engine = StealthScaffoldEngine(self.config_loader)
        self.psych_profiles = self.config_loader.get_psych_profiles()

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for psychological characteristics."""
        return {
            'emotional_tone': self.psych_scaffolding.analyze_emotional_tone(content),
            'cognitive_load': self.psych_scaffolding.detect_cognitive_load(content)
        }

    def enhance_prompt(self, content: str) -> Tuple[str, Dict[str, Any]]:
        """Apply psychological enhancement to prompt content."""
        profile_type = self._detect_profile_type(content)
        profile = self.psych_profiles.get(profile_type, self.psych_profiles['analytical'])
        return self.stealth_engine.apply_stealth_optimization(content, profile)

    def _detect_profile_type(self, content: str) -> str:
        """Detect the appropriate psychological profile for content."""
        content_lower = content.lower()
        if any(word in content_lower for word in ['creative', 'idea', 'brainstorm', 'innovate']):
            return 'creative'
        elif any(word in content_lower for word in ['strategy', 'plan', 'roadmap', 'strategic']):
            return 'strategic'
        elif any(word in content_lower for word in ['urgent', 'immediate', 'action', 'tactical']):
            return 'tactical'
        return 'analytical'

    def track_activity(self, action_type: str, metadata: Optional[Dict] = None) -> None:
        """Track user activity for behavioral analysis."""
        self.psych_scaffolding.track_work_pattern(action_type, metadata)

    def should_intervene(self) -> bool:
        """Check if psychological intervention is needed."""
        return self.psych_scaffolding.should_intervene("editing")

    def get_emotional_theme(self, tone: str) -> Dict[str, str]:
        """Get emotional theme configuration."""
        return self.psych_scaffolding.get_emotional_theme(tone)
