# query_processor.py - Advanced query processing for better accuracy

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryIntent:
    intent_type: str  # 'gstin_lookup', 'gst_rate', 'compliance', 'filing', 'general'
    confidence: float
    extracted_entities: Dict[str, str]
    processed_query: str

class QueryProcessor:
    def __init__(self):
        # GST-specific keywords and patterns
        self.intent_patterns = {
            'gstin_lookup': [
                r'(?:gstin|gst\s*number|registration\s*number)\s*[:=]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
                r'(?:information|details|lookup|search|find).*(?:gstin|gst\s*number)',
                r'(?:verify|check|validate).*gstin'
            ],
            'gst_rate': [
                r'(?:gst\s*rate|tax\s*rate|rate\s*of\s*gst)(?:\s+(?:for|on|of))?\s*([a-zA-Z\s,]+)',
                r'(?:what|how\s*much).*(?:gst|tax).*(?:rate|percentage|%)',
                r'(?:hsn|sac)\s*code?\s*([0-9]+)',
                r'(?:18%|28%|12%|5%|0%).*gst'
            ],
            'compliance': [
                r'(?:compliance|penalty|fine|notice|audit)',
                r'(?:late\s*filing|return\s*filing)',
                r'(?:gst\s*(?:notice|penalty|audit))',
                r'(?:input\s*tax\s*credit|itc)'
            ],
            'filing': [
                r'(?:gstr[-\s]?[1-9]|return\s*filing)',
                r'(?:due\s*date|deadline).*(?:gst|return)',
                r'(?:monthly|quarterly|annual).*(?:return|filing)',
                r'(?:how\s*to\s*file|filing\s*process)'
            ],
            'invoice': [
                r'(?:invoice|bill|receipt).*(?:format|requirement)',
                r'(?:b2b|b2c).*invoice',
                r'(?:tax\s*invoice|commercial\s*invoice)',
                r'(?:invoice\s*number|serial\s*number)'
            ]
        }
        
        # Common GST terms for entity extraction
        self.gst_entities = {
            'states': ['maharashtra', 'karnataka', 'tamil nadu', 'gujarat', 'rajasthan', 'uttar pradesh', 
                      'west bengal', 'madhya pradesh', 'bihar', 'andhra pradesh', 'telangana', 'kerala',
                      'odisha', 'punjab', 'haryana', 'assam', 'jharkhand', 'chhattisgarh'],
            'business_types': ['proprietorship', 'partnership', 'llp', 'private limited', 'public limited',
                             'trust', 'society', 'huf', 'individual'],
            'gst_terms': ['cgst', 'sgst', 'igst', 'utgst', 'cess', 'itc', 'input tax credit', 
                         'reverse charge', 'rcm', 'composition scheme', 'regular scheme']
        }

    def detect_intent(self, query: str) -> QueryIntent:
        """Detect the intent of the user query"""
        query_lower = query.lower()
        intent_scores = {}
        extracted_entities = {}
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query_lower)
                if matches:
                    score += 1
                    # Extract entities if found
                    if intent == 'gstin_lookup' and matches:
                        # Extract GSTIN from the match
                        gstin_match = re.search(r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})', query.upper())
                        if gstin_match:
                            extracted_entities['gstin'] = gstin_match.group(1)
                    elif intent == 'gst_rate' and matches:
                        # Extract product/service name
                        extracted_entities['item'] = matches[0] if isinstance(matches[0], str) else matches[0][0]
            
            if score > 0:
                intent_scores[intent] = score / len(patterns)  # Normalize by pattern count
        
        # Determine best intent
        if not intent_scores:
            best_intent = 'general'
            confidence = 0.5
        else:
            best_intent = max(intent_scores.keys(), key=intent_scores.get)
            confidence = intent_scores[best_intent]
        
        # Extract additional entities
        self._extract_entities(query_lower, extracted_entities)
        
        # Process query for better search
        processed_query = self._process_query(query, best_intent)
        
        return QueryIntent(
            intent_type=best_intent,
            confidence=confidence,
            extracted_entities=extracted_entities,
            processed_query=processed_query
        )

    def _extract_entities(self, query: str, entities: Dict[str, str]):
        """Extract relevant entities from query"""
        # Extract state names
        for state in self.gst_entities['states']:
            if state in query:
                entities['state'] = state
                break
        
        # Extract business type
        for btype in self.gst_entities['business_types']:
            if btype in query:
                entities['business_type'] = btype
                break
        
        # Extract amounts/percentages
        amount_match = re.search(r'(?:rs\.?|₹)\s*([0-9,]+(?:\.[0-9]{2})?)', query)
        if amount_match:
            entities['amount'] = amount_match.group(1)
        
        percentage_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%', query)
        if percentage_match:
            entities['percentage'] = percentage_match.group(1)

    def _process_query(self, query: str, intent: str) -> str:
        """Process query for better retrieval based on intent"""
        processed = query.lower()
        
        # Remove common stop words that don't add value
        stop_words = ['can', 'you', 'please', 'tell', 'me', 'about', 'what', 'is', 'the', 'a', 'an']
        words = processed.split()
        words = [w for w in words if w not in stop_words or len(w) > 3]
        
        # Add context-specific terms based on intent
        if intent == 'gst_rate':
            words.extend(['rate', 'tax', 'percentage'])
        elif intent == 'compliance':
            words.extend(['compliance', 'penalty', 'rules'])
        elif intent == 'filing':
            words.extend(['filing', 'return', 'due date'])
        elif intent == 'invoice':
            words.extend(['invoice', 'format', 'requirements'])
        
        return ' '.join(words)

    def should_expand_search(self, intent: QueryIntent, initial_results: List[dict]) -> bool:
        """Determine if we should expand search with related terms"""
        if not initial_results:
            return True
        
        # If confidence is low or best result has high distance score
        if intent.confidence < 0.7 or (initial_results and initial_results[0].get('score', 0) > 0.8):
            return True
        
        return False

    def generate_related_queries(self, intent: QueryIntent) -> List[str]:
        """Generate related queries for expanded search"""
        base_query = intent.processed_query
        related_queries = []
        
        if intent.intent_type == 'gst_rate':
            related_queries = [
                f"{base_query} hsn code",
                f"{base_query} tax slab",
                f"{base_query} gst classification"
            ]
        elif intent.intent_type == 'compliance':
            related_queries = [
                f"{base_query} penalty",
                f"{base_query} rules",
                f"{base_query} requirements"
            ]
        elif intent.intent_type == 'filing':
            related_queries = [
                f"{base_query} process",
                f"{base_query} deadline",
                f"{base_query} procedure"
            ]
        
        return related_queries[:3]  # Limit to 3 related queries
