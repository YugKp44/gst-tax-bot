# config.py - Configuration settings for the GST Tax Bot

import os
from typing import Dict, Any

class Config:
    """Configuration class for GST Tax Bot"""
    
    # Model Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    GENERATION_MODEL = "google/flan-t5-base"
    
    # Search Configuration
    DEFAULT_SEARCH_K = 5  # Number of results to retrieve
    MAX_CONTEXT_LENGTH = 4000  # Maximum context length for generation
    RELEVANCE_THRESHOLD = 1.2  # Threshold for considering results relevant
    HIGH_CONFIDENCE_THRESHOLD = 0.5  # Threshold for high confidence results
    LOW_CONFIDENCE_THRESHOLD = 0.8  # Threshold for low confidence warning
    
    # Generation Configuration
    MAX_NEW_TOKENS = 300
    TEMPERATURE = 0.1
    TOP_P = 0.9
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/tax_data")
    COLLECTION_NAME = "gst_recoords"  # Note: keeping the typo to match existing data
    
    # File Paths
    INDEX_PATH = "embeddings/faiss.index"
    META_PATH = "embeddings/faq_meta.pkl"
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    
    # Query Processing Configuration
    INTENT_CONFIDENCE_THRESHOLD = 0.7
    EXPAND_SEARCH_THRESHOLD = 0.8
    
    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Get search-related configuration"""
        return {
            'k': cls.DEFAULT_SEARCH_K,
            'relevance_threshold': cls.RELEVANCE_THRESHOLD,
            'high_confidence_threshold': cls.HIGH_CONFIDENCE_THRESHOLD,
            'low_confidence_threshold': cls.LOW_CONFIDENCE_THRESHOLD,
        }
    
    @classmethod
    def get_generation_config(cls) -> Dict[str, Any]:
        """Get generation-related configuration"""
        return {
            'max_new_tokens': cls.MAX_NEW_TOKENS,
            'temperature': cls.TEMPERATURE,
            'top_p': cls.TOP_P,
            'do_sample': True,
        }

# Performance optimization settings
PERFORMANCE_OPTIMIZATIONS = {
    'enable_query_caching': True,
    'cache_size': 1000,
    'enable_result_filtering': True,
    'enable_context_compression': True,
}

# Response formatting options
RESPONSE_FORMATTING = {
    'include_confidence_indicator': False,
    'max_sources_display': 3,
    'enable_markdown_formatting': False,
    'include_related_questions': False,
}
