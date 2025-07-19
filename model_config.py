# model_config.py - Easy model switching for different performance needs

import torch

class ModelConfig:
    """Model configurations for different performance requirements"""
    
    MODELS = {
        "fastest": {
            "name": "google/flan-t5-small",
            "size": "~80MB",
            "speed": "Very Fast",
            "quality": "Good for simple queries",
            "max_tokens": 128,
            "description": "Best for very fast responses, handles simple GST questions well"
        },
        "balanced": {
            "name": "google/flan-t5-base", 
            "size": "~250MB",
            "speed": "Fast",
            "quality": "Good balance",
            "max_tokens": 256,
            "description": "Recommended: Good balance of speed and quality"
        },
        "quality": {
            "name": "google/flan-t5-large",
            "size": "~780MB", 
            "speed": "Medium",
            "quality": "High quality responses",
            "max_tokens": 512,
            "description": "Better quality but slower response times"
        },
        "premium": {
            "name": "google/flan-t5-xl",
            "size": "~3GB",
            "speed": "Slow",
            "quality": "Highest quality",
            "max_tokens": 512,
            "description": "Best quality but very slow, requires lots of memory"
        }
    }
    
    @classmethod
    def get_config(cls, model_tier: str = "balanced"):
        """Get configuration for specified model tier"""
        return cls.MODELS.get(model_tier, cls.MODELS["balanced"])
    
    @classmethod
    def get_generation_params(cls, model_tier: str = "balanced", fast_mode: bool = False):
        """Get optimized generation parameters"""
        config = cls.get_config(model_tier)
        
        base_params = {
            "max_new_tokens": config["max_tokens"],
            "do_sample": True,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "length_penalty": 1.0,
            "early_stopping": True,
            "num_beams": 1,  # Faster than beam search
        }
        
        if fast_mode:
            # Even faster settings
            base_params.update({
                "max_new_tokens": min(128, config["max_tokens"]),
                "temperature": 0.1,  # More deterministic
                "top_p": 0.8,       # More focused
                "do_sample": False, # Greedy decoding (fastest)
                "early_stopping": True,
            })
        
        return base_params
    
    @classmethod
    def get_model_load_params(cls, model_tier: str = "balanced"):
        """Get optimized model loading parameters"""
        params = {
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "low_cpu_mem_usage": True,
            "device_map": "auto" if torch.cuda.is_available() else None,
        }
        
        # For smaller models, we can load entirely in memory
        if model_tier in ["fastest", "balanced"]:
            params["device_map"] = None
            
        return params

# Current configuration - change this to switch models
CURRENT_MODEL_TIER = "balanced"  # Production: use balanced for speed
FAST_MODE = True  # Production: enable fast mode

def print_model_info():
    """Print information about available models"""
    print("\nAvailable Model Configurations:")
    print("-" * 60)
    for tier, config in ModelConfig.MODELS.items():
        print(f"{tier.upper():12} | {config['name']:20} | {config['size']:8} | {config['speed']:10} | {config['quality']}")
    print("-" * 60)
    
    current = ModelConfig.get_config(CURRENT_MODEL_TIER)
    print(f"\nCurrent Model: {current['name']}")
    print(f"Description: {current['description']}")
    print(f"Fast Mode: {'Enabled' if FAST_MODE else 'Disabled'}")
    print()

if __name__ == "__main__":
    print_model_info()
