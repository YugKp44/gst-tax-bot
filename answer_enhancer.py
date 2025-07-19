# answer_enhancer.py - Enhance short or incomplete answers

import re
from typing import List, Dict, Optional

class AnswerEnhancer:
    """Enhance answers that are too short or incomplete"""
    
    def __init__(self):
        # Common GST terms and their explanations
        self.gst_explanations = {
            'gstin': {
                'full_form': 'Goods and Services Tax Identification Number',
                'description': 'A unique 15-digit number assigned to every GST registered business in India',
                'format': 'Format: 2 digits (State Code) + 10 digits (PAN) + 1 digit (Registration Type) + 1 digit (Check Sum) + 1 letter (Z) + 1 digit/letter (Check Sum)',
                'importance': 'Required for all GST registered businesses to identify them uniquely across India'
            },
            'gst': {
                'full_form': 'Goods and Services Tax',
                'description': 'A comprehensive indirect tax levied on the supply of goods and services in India',
                'implementation': 'Implemented on July 1, 2017, replacing multiple indirect taxes',
                'structure': 'It has four components: CGST, SGST, IGST, and UTGST',
                'rates': 'GST rates are 0%, 5%, 12%, 18%, and 28% based on the type of goods/services'
            }
        }
        
        # Templates for expanding short answers
        self.expansion_templates = {
            'definition': """
{term_name}:

{description}

Key Details:
{details}

Importance:
{importance}
""",
            'explanation': """
{description}

Additional Information:
{additional_info}
"""
        }

    def enhance_answer(self, answer: str, query: str, contexts: List[Dict]) -> str:
        """Enhance a short or incomplete answer"""
        
        # Check if answer is too short
        if len(answer.strip()) < 50:
            return self._expand_short_answer(answer, query, contexts)
        
        # Check if answer lacks detail for common questions
        if self._is_definition_question(query) and len(answer.strip()) < 100:
            return self._add_comprehensive_definition(answer, query, contexts)
        
        return answer

    def _expand_short_answer(self, answer: str, query: str, contexts: List[Dict]) -> str:
        """Expand very short answers using additional context"""
        
        enhanced_parts = [answer.strip()] if answer.strip() else []
        
        # Check for common GST terms in query
        query_lower = query.lower()
        
        if 'gstin' in query_lower or 'gst number' in query_lower:
            gstin_info = self.gst_explanations['gstin']
            enhanced_parts.extend([
                f"\n{gstin_info['full_form']} (GSTIN) is {gstin_info['description']}.",
                f"\nFormat: {gstin_info['format']}",
                f"\n{gstin_info['importance']}"
            ])
        
        elif any(term in query_lower for term in ['what is gst', 'gst', 'goods and services tax']):
            gst_info = self.gst_explanations['gst']
            enhanced_parts.extend([
                f"\n{gst_info['full_form']} (GST) is {gst_info['description']}.",
                f"\n{gst_info['implementation']}.",
                f"\nStructure: {gst_info['structure']}.",
                f"\nTax Rates: {gst_info['rates']}."
            ])
        
        # Add context information if available
        if contexts:
            context_info = self._extract_additional_info_from_contexts(contexts, query)
            if context_info:
                enhanced_parts.append(f"\nAdditional Information:\n{context_info}")
        
        return ''.join(enhanced_parts)

    def _is_definition_question(self, query: str) -> bool:
        """Check if the query is asking for a definition"""
        definition_indicators = [
            'what is', 'what are', 'define', 'meaning of', 'explain', 
            'definition of', 'tell me about', 'describe'
        ]
        return any(indicator in query.lower() for indicator in definition_indicators)

    def _add_comprehensive_definition(self, answer: str, query: str, contexts: List[Dict]) -> str:
        """Add more comprehensive information for definition questions"""
        
        # Extract key terms from the query
        query_lower = query.lower()
        
        enhanced_answer = answer
        
        # Add structure and examples based on context
        if contexts:
            additional_info = []
            for context in contexts[:2]:  # Use top 2 contexts
                context_answer = context.get('answer', '')
                if len(context_answer) > len(answer):
                    # Extract additional sentences that weren't in the original answer
                    additional_sentences = self._extract_new_sentences(answer, context_answer)
                    additional_info.extend(additional_sentences)
            
            if additional_info:
                enhanced_answer += "\n\nAdditional Details:\n" + "\n".join(f"- {info}" for info in additional_info[:3])
        
        return enhanced_answer

    def _extract_additional_info_from_contexts(self, contexts: List[Dict], query: str) -> str:
        """Extract additional relevant information from contexts"""
        additional_info = []
        
        for context in contexts:
            answer = context.get('answer', '')
            question = context.get('question', '')
            
            # Look for sentences that contain key information
            sentences = re.split(r'[.!?]+', answer)
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 20 and 
                    any(term in sentence.lower() for term in ['gst', 'tax', 'rate', 'register', 'compliance']) and
                    sentence not in additional_info):
                    additional_info.append(sentence)
                    
                if len(additional_info) >= 3:  # Limit to 3 additional points
                    break
        
        return '\n- '.join(additional_info) if additional_info else ""

    def _extract_new_sentences(self, original_answer: str, context_answer: str) -> List[str]:
        """Extract sentences from context that aren't in the original answer"""
        original_words = set(original_answer.lower().split())
        
        sentences = re.split(r'[.!?]+', context_answer)
        new_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:
                sentence_words = set(sentence.lower().split())
                # If sentence has new information (less than 70% overlap)
                overlap = len(original_words.intersection(sentence_words)) / len(sentence_words) if sentence_words else 0
                if overlap < 0.7:
                    new_sentences.append(sentence)
        
        return new_sentences[:3]  # Return up to 3 new sentences

# Global answer enhancer
answer_enhancer = AnswerEnhancer()
