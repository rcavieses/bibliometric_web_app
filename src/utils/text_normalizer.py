import re
from typing import Dict, Any

def normalize_model_name(model_name: str) -> str:
    """Normalize AI model names to a standard format."""
    if not model_name or not isinstance(model_name, str):
        return "Not mentioned"
        
    # Convert to lowercase
    normalized = model_name.lower()
    
    # Remove numbers at start
    normalized = re.sub(r'^\d+\s*', '', normalized)
    
    # Common model name mappings
    model_mappings = {
        r'(lstm|long short[ -]term memory)': 'lstm',
        r'(gru|gated recurrent unit)': 'gru',
        r'(cnn|convolutional neural network)': 'cnn',
        r'(ann|artificial neural network)': 'ann',
        r'(rnn|recurrent neural network)': 'rnn',
        r'(svm|support vector machine)': 'svm',
        r'random[ -]?forest': 'random forest',
        r'(bert|bidirectional encoder)': 'bert',
        r'gradient[ -]?boost': 'gradient boost',
        r'naive[ -]?bayes': 'naive bayes',
        r'decision[ -]?tree': 'decision tree',
        r'xgboost': 'xgboost',
        r'light[ -]?gbm': 'lightgbm',
    }
    
    # Apply mappings
    for pattern, replacement in model_mappings.items():
        if re.search(pattern, normalized):
            return replacement
            
    return normalized

def consolidate_model_counts(counts: Dict[str, Any]) -> Dict[str, Any]:
    """Consolidate model counts by normalizing model names."""
    normalized_counts = {}
    
    for model, count in counts.items():
        normalized_model = normalize_model_name(model)
        normalized_counts[normalized_model] = normalized_counts.get(normalized_model, 0) + count
        
    return normalized_counts
