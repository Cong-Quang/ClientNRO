"""
Pure Python Neural Network Inference Engine
Architecture: [20 -> 64 -> 64 -> 32] MLP
Zero external dependencies - optimized with list comprehensions
Performance target: <1ms inference time
"""

import json
import asyncio
from typing import List, Tuple, Dict, Any


class InferenceEngine:
    """
    Pure Python neural network inference engine.
    Loads weights from JSON and performs forward pass using only standard library.
    """
    
    def __init__(self):
        self.weights: List[Dict[str, List]] = []
        self.architecture: List[int] = []
        self.loaded = False
    
    
    def set_weights_from_dict(self, data: dict):
        """Load weights directly from dictionary (for sharing)"""
        try:
            if "layers" not in data:
                return False
                
            self.weights = data['layers']
            self.loaded = True
            return True
        except Exception:
            return False
            
    def load_weights(self, weights_path: str) -> bool:
        """
        Load neural network weights from JSON file.
        
        Format:
        {
            "architecture": [20, 64, 64, 32],
            "layers": [
                {"W": [[...], ...], "b": [...]},
                {"W": [[...], ...], "b": [...]},
                ...
            ]
        }
        """
        try:
            with open(weights_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.architecture = data.get('architecture', [])
            self.weights = data.get('layers', [])
            
            # Validate weights - check if layers are actually populated
            valid_weights = True
            for layer in self.weights:
                if not layer.get('W') or not layer.get('b'):
                    valid_weights = False
                    break
            
            if not valid_weights or not self.weights:
                print(f"[AI Brain] Warning: Weights file has empty layers")
                self._init_random_weights()
            else:
                self.loaded = True
                print(f"[AI Brain] Loaded weights: {self.architecture}")
                print(f"[AI Brain] Total layers: {len(self.weights)}")
            
        except FileNotFoundError:
            print(f"[AI Brain] Warning: Weights file not found at {weights_path}")
            print(f"[AI Brain] Using random initialization")
            self._init_random_weights()
        except json.JSONDecodeError as e:
            print(f"[AI Brain] Error parsing JSON: {e}")
            self._init_random_weights()
    
    def _init_random_weights(self) -> None:
        """Initialize random weights for testing (when no weights file exists)"""
        import random
        self.architecture = [20, 64, 64, 32]
        self.weights = []
        
        for i in range(len(self.architecture) - 1):
            in_size = self.architecture[i]
            out_size = self.architecture[i + 1]
            
            # Xavier initialization scaled down
            scale = (2.0 / (in_size + out_size)) ** 0.5
            
            W = [[random.gauss(0, scale) for _ in range(in_size)] for _ in range(out_size)]
            b = [random.gauss(0, 0.01) for _ in range(out_size)]
            
            self.weights.append({"W": W, "b": b})
        
        self.loaded = True
        print(f"[AI Brain] Initialized random weights: {self.architecture}")
    
    async def predict(self, state: List[float], action_mask: List[bool] = None) -> Tuple[int, float]:
        """
        Async inference - predict best action from state.
        
        Args:
            state: Input state vector (length 20)
            action_mask: Optional boolean mask for valid actions (length 32)
                        True = valid action, False = masked (invalid)
        
        Returns:
            (action_index, confidence) tuple
        """
        if not self.loaded:
            # Return random action if not loaded
            import random
            return (random.randint(0, 31), 0.0)
        
        # Run forward pass (can be sync since it's fast)
        # But wrapped in to_thread for consistency with async architecture
        action_idx, confidence = await asyncio.to_thread(
            self._forward_pass, state, action_mask
        )
        
        return (action_idx, confidence)
    
    def _forward_pass(self, state: List[float], action_mask: List[bool] = None) -> Tuple[int, float]:
        """
        Forward pass through network (synchronous).
        Optimized with list comprehensions for speed.
        """
        x = state  # Input layer
        
        # Hidden layers with ReLU activation
        for i, layer in enumerate(self.weights[:-1]):  # All except last layer
            x = self._linear(x, layer['W'], layer['b'])
            x = self._relu(x)
        
        # Output layer (no activation yet)
        output_layer = self.weights[-1]
        logits = self._linear(x, output_layer['W'], output_layer['b'])
        
        # Apply action masking if provided
        if action_mask is not None:
            logits = self._apply_mask(logits, action_mask)
        
        # Softmax to get probabilities
        probs = self._softmax(logits)
        
        # Return argmax and confidence
        max_idx = max(range(len(probs)), key=lambda i: probs[i])
        confidence = probs[max_idx]
        
        return (max_idx, confidence)
    
    def _linear(self, x: List[float], W: List[List[float]], b: List[float]) -> List[float]:
        """
        Linear transformation: y = Wx + b
        Optimized with list comprehension and zip.
        
        W shape: (out_features, in_features)
        x shape: (in_features,)
        b shape: (out_features,)
        Returns: (out_features,)
        """
        return [
            sum(w * x_val for w, x_val in zip(weights, x)) + bias
            for weights, bias in zip(W, b)
        ]
    
    def _relu(self, x: List[float]) -> List[float]:
        """ReLU activation: max(0, x)"""
        return [max(0.0, val) for val in x]
    
    def _softmax(self, x: List[float]) -> List[float]:
        """
        Softmax activation with numerical stability.
        exp(x - max(x)) / sum(exp(x - max(x)))
        """
        if not x:
            return []
        
        # Numerical stability: subtract max
        max_val = max(x)
        exp_vals = [pow(2.71828, val - max_val) for val in x]  # math.e ≈ 2.71828
        sum_exp = sum(exp_vals)
        
        return [val / sum_exp for val in exp_vals]
    
    def _apply_mask(self, logits: List[float], mask: List[bool]) -> List[float]:
        """
        Apply action mask to logits.
        Masked actions (False) get -inf logit → 0 probability after softmax.
        """
        MASK_VALUE = -1e9  # Effectively -inf
        return [
            logit if (i >= len(mask) or mask[i]) else MASK_VALUE
            for i, logit in enumerate(logits)
        ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model architecture and status"""
        return {
            "architecture": self.architecture,
            "total_layers": len(self.weights),
            "total_parameters": self._count_parameters(),
            "loaded": self.loaded,
            "inference_engine": "Pure Python (Standard Library Only)"
        }
    
    def _count_parameters(self) -> int:
        """Count total trainable parameters"""
        total = 0
        for layer in self.weights:
            W = layer['W']
            b = layer['b']
            total += len(W) * len(W[0]) + len(b)  # weights + biases
        return total


# Example usage and testing
if __name__ == "__main__":
    print("Testing Pure Python InferenceEngine...")
    
    # Create engine
    engine = InferenceEngine()
    
    # Load weights (will use random if file doesn't exist)
    engine.load_weights("ai_core/weights/default_weights.json")
    
    # Print model info
    info = engine.get_model_info()
    print(f"\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test inference
    import random
    test_state = [random.random() for _ in range(20)]
    
    # Test without mask
    async def test():
        action, confidence = await engine.predict(test_state)
        print(f"\nTest 1 - No mask:")
        print(f"  Predicted action: {action}, Confidence: {confidence:.4f}")
        
        # Test with action mask (only allow actions 0-7)
        mask = [True] * 8 + [False] * 24
        action_masked, conf_masked = await engine.predict(test_state, mask)
        print(f"\nTest 2 - With mask (only 0-7):")
        print(f"  Predicted action: {action_masked}, Confidence: {conf_masked:.4f}")
        print(f"  Verify: Action in [0-7]: {action_masked < 8}")
    
    asyncio.run(test())
    print("\n[SUCCESS] Pure Python InferenceEngine test complete!")
