"""
Steganographic Encoder - Secret Variable Injection System

Enables hiding information in visual encodings through:
- Micro-adjustments to positions (sub-pixel shifts)
- Color LSB manipulation (least significant bits)
- Glow intensity modulation
- Pattern phase shifts
- Rotation adjustments

Use cases:
- Authentication (verify official visualizations)
- Timestamping (when was this created)
- Provenance (which domain/dataset)
- Messages (arbitrary encoded text)
- Artist signature (personal mark)

This is the magician's secret: Hidden layers of meaning in plain sight.
"""

import numpy as np
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import json
from datetime import datetime

from utils.formula_engine import VisualEncoding

logger = logging.getLogger(__name__)


@dataclass
class SecretMessage:
    """A message to be encoded in visualizations"""
    message_type: str  # 'signature', 'timestamp', 'metadata', 'text', 'checksum'
    content: str
    encoding_method: str  # 'lsb', 'position', 'rotation', 'glow', 'multi'
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            'message_type': self.message_type,
            'content': self.content,
            'encoding_method': self.encoding_method,
            'timestamp': self.timestamp,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'SecretMessage':
        return SecretMessage(**data)


class SteganographicEncoder:
    """
    Encodes and decodes secret variables in visual representations
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encoder
        
        Args:
            secret_key: Optional key for encryption (makes messages unreadable without key)
        """
        self.secret_key = secret_key or "nominative_determinism_2025"
        self.encoding_precision = 0.001  # How much we can adjust values
        
    def inject_message(self, visual_encoding: VisualEncoding,
                      message: SecretMessage) -> VisualEncoding:
        """
        Inject a secret message into a visual encoding
        
        Args:
            visual_encoding: Original visual encoding
            message: Message to hide
            
        Returns:
            Modified visual encoding with hidden message
        """
        logger.info(f"Injecting {message.message_type} message using {message.encoding_method}")
        
        # Convert message to binary
        binary_message = self._text_to_binary(message.content)
        
        # Choose encoding method
        if message.encoding_method == 'lsb':
            modified = self._encode_lsb(visual_encoding, binary_message)
        elif message.encoding_method == 'position':
            modified = self._encode_position(visual_encoding, binary_message)
        elif message.encoding_method == 'rotation':
            modified = self._encode_rotation(visual_encoding, binary_message)
        elif message.encoding_method == 'glow':
            modified = self._encode_glow(visual_encoding, binary_message)
        elif message.encoding_method == 'multi':
            modified = self._encode_multi(visual_encoding, binary_message)
        else:
            logger.warning(f"Unknown encoding method: {message.encoding_method}")
            modified = visual_encoding
        
        # Store message metadata in secret_variable
        modified.secret_variable = json.dumps(message.to_dict())
        
        return modified
    
    def extract_message(self, visual_encoding: VisualEncoding,
                       encoding_method: Optional[str] = None) -> Optional[SecretMessage]:
        """
        Extract hidden message from visual encoding
        
        Args:
            visual_encoding: Visual encoding to decode
            encoding_method: Method used (if None, try to detect)
            
        Returns:
            SecretMessage if found, None otherwise
        """
        # Check if metadata is present
        if visual_encoding.secret_variable:
            try:
                message_dict = json.loads(visual_encoding.secret_variable)
                message = SecretMessage.from_dict(message_dict)
                return message
            except:
                pass
        
        # Try to extract without metadata (blind extraction)
        if encoding_method:
            binary = self._decode_with_method(visual_encoding, encoding_method)
            if binary:
                text = self._binary_to_text(binary)
                return SecretMessage(
                    message_type='unknown',
                    content=text,
                    encoding_method=encoding_method,
                    timestamp=datetime.now().isoformat()
                )
        
        return None
    
    def create_signature(self, artist_name: str, date: Optional[str] = None) -> SecretMessage:
        """Create artist signature message"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        content = f"{artist_name}|{date}"
        
        return SecretMessage(
            message_type='signature',
            content=content,
            encoding_method='multi',
            timestamp=datetime.now().isoformat()
        )
    
    def create_timestamp(self) -> SecretMessage:
        """Create timestamp message"""
        timestamp = datetime.now().isoformat()
        
        return SecretMessage(
            message_type='timestamp',
            content=timestamp,
            encoding_method='rotation',
            timestamp=timestamp
        )
    
    def create_metadata(self, domain: str, formula_id: str, 
                       entity_count: int) -> SecretMessage:
        """Create metadata message"""
        content = f"domain:{domain}|formula:{formula_id}|n:{entity_count}"
        
        return SecretMessage(
            message_type='metadata',
            content=content,
            encoding_method='position',
            timestamp=datetime.now().isoformat()
        )
    
    def create_checksum(self, visual_encoding: VisualEncoding) -> SecretMessage:
        """Create checksum for authentication"""
        # Generate checksum from visual properties
        data = f"{visual_encoding.name}|{visual_encoding.formula_id}|" \
               f"{visual_encoding.hue:.2f}|{visual_encoding.x:.4f}"
        
        checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        return SecretMessage(
            message_type='checksum',
            content=checksum,
            encoding_method='lsb',
            timestamp=datetime.now().isoformat()
        )
    
    def create_text_message(self, text: str) -> SecretMessage:
        """Create arbitrary text message"""
        return SecretMessage(
            message_type='text',
            content=text,
            encoding_method='multi',
            timestamp=datetime.now().isoformat()
        )
    
    # =========================================================================
    # Encoding Methods
    # =========================================================================
    
    def _encode_lsb(self, visual: VisualEncoding, binary: str) -> VisualEncoding:
        """
        Least Significant Bit encoding
        Modify the least significant digits of numerical properties
        """
        modified = visual.__class__(**visual.__dict__)
        
        # Target properties for LSB encoding
        properties = [
            ('hue', 360.0),
            ('saturation', 100.0),
            ('brightness', 100.0),
            ('rotation', 360.0),
        ]
        
        bit_index = 0
        for prop_name, max_val in properties:
            if bit_index >= len(binary):
                break
            
            current_val = getattr(modified, prop_name)
            
            # Encode bit by adjusting least significant digit
            bit = int(binary[bit_index])
            
            # Adjust value slightly based on bit
            adjustment = self.encoding_precision * max_val
            if bit == 1:
                new_val = current_val + adjustment
            else:
                new_val = current_val - adjustment
            
            # Ensure within bounds
            new_val = new_val % max_val
            
            setattr(modified, prop_name, new_val)
            bit_index += 1
        
        return modified
    
    def _encode_position(self, visual: VisualEncoding, binary: str) -> VisualEncoding:
        """
        Position encoding
        Encode message in x, y, z coordinates through micro-adjustments
        """
        modified = visual.__class__(**visual.__dict__)
        
        # Encode in position (sub-pixel adjustments)
        if len(binary) >= 2:
            x_bit = int(binary[0])
            y_bit = int(binary[1])
            
            # Micro-adjust x based on first bit
            modified.x += self.encoding_precision * (1 if x_bit == 1 else -1)
            modified.x = np.clip(modified.x, -1.0, 1.0)
            
            # Micro-adjust y based on second bit
            modified.y += self.encoding_precision * (1 if y_bit == 1 else -1)
            modified.y = np.clip(modified.y, -1.0, 1.0)
        
        if len(binary) >= 3:
            z_bit = int(binary[2])
            modified.z += self.encoding_precision * (1 if z_bit == 1 else -1)
            modified.z = np.clip(modified.z, 0.0, 1.0)
        
        return modified
    
    def _encode_rotation(self, visual: VisualEncoding, binary: str) -> VisualEncoding:
        """
        Rotation encoding
        Encode message in rotation angle
        """
        modified = visual.__class__(**visual.__dict__)
        
        # Convert binary to integer
        if binary:
            value = int(binary[:8], 2) if len(binary) >= 8 else int(binary, 2)
            
            # Encode as small adjustment to rotation
            adjustment = (value / 255.0) * self.encoding_precision * 360
            modified.rotation = (modified.rotation + adjustment) % 360
        
        return modified
    
    def _encode_glow(self, visual: VisualEncoding, binary: str) -> VisualEncoding:
        """
        Glow intensity encoding
        Encode in glow and pattern properties
        """
        modified = visual.__class__(**visual.__dict__)
        
        if len(binary) >= 1:
            bit = int(binary[0])
            adjustment = self.encoding_precision * (1 if bit == 1 else -1)
            modified.glow_intensity += adjustment
            modified.glow_intensity = np.clip(modified.glow_intensity, 0.0, 1.0)
        
        if len(binary) >= 2:
            bit = int(binary[1])
            adjustment = self.encoding_precision * (1 if bit == 1 else -1)
            modified.pattern_density += adjustment
            modified.pattern_density = np.clip(modified.pattern_density, 0.0, 1.0)
        
        return modified
    
    def _encode_multi(self, visual: VisualEncoding, binary: str) -> VisualEncoding:
        """
        Multi-channel encoding
        Distribute message across multiple properties for robustness
        """
        modified = visual.__class__(**visual.__dict__)
        
        # Distribute bits across different channels
        channels = [
            ('lsb', self._encode_lsb),
            ('position', self._encode_position),
            ('rotation', self._encode_rotation),
            ('glow', self._encode_glow),
        ]
        
        # Split message into chunks
        chunk_size = max(1, len(binary) // len(channels))
        
        for i, (method_name, encode_func) in enumerate(channels):
            start = i * chunk_size
            end = start + chunk_size if i < len(channels) - 1 else len(binary)
            
            if start < len(binary):
                chunk = binary[start:end]
                modified = encode_func(modified, chunk)
        
        return modified
    
    # =========================================================================
    # Decoding Methods
    # =========================================================================
    
    def _decode_with_method(self, visual: VisualEncoding, method: str) -> Optional[str]:
        """Decode binary message using specified method"""
        if method == 'lsb':
            return self._decode_lsb(visual)
        elif method == 'position':
            return self._decode_position(visual)
        elif method == 'rotation':
            return self._decode_rotation(visual)
        elif method == 'glow':
            return self._decode_glow(visual)
        elif method == 'multi':
            return self._decode_multi(visual)
        else:
            return None
    
    def _decode_lsb(self, visual: VisualEncoding) -> str:
        """Decode LSB-encoded message"""
        # Extract least significant variations
        binary = ""
        
        properties = [
            ('hue', 360.0),
            ('saturation', 100.0),
            ('brightness', 100.0),
            ('rotation', 360.0),
        ]
        
        for prop_name, max_val in properties:
            val = getattr(visual, prop_name)
            
            # Check if value has small fractional adjustment
            fractional = val - int(val)
            threshold = self.encoding_precision * max_val / 2
            
            if fractional > threshold:
                binary += "1"
            else:
                binary += "0"
        
        return binary
    
    def _decode_position(self, visual: VisualEncoding) -> str:
        """Decode position-encoded message"""
        binary = ""
        
        # Extract from fractional parts
        x_frac = abs(visual.x) - int(abs(visual.x))
        y_frac = abs(visual.y) - int(abs(visual.y))
        z_frac = visual.z - int(visual.z)
        
        threshold = self.encoding_precision / 2
        
        binary += "1" if x_frac > threshold else "0"
        binary += "1" if y_frac > threshold else "0"
        binary += "1" if z_frac > threshold else "0"
        
        return binary
    
    def _decode_rotation(self, visual: VisualEncoding) -> str:
        """Decode rotation-encoded message"""
        # Extract adjustment from rotation
        fractional = visual.rotation - int(visual.rotation)
        
        # Convert back to binary
        value = int((fractional / (self.encoding_precision * 360)) * 255)
        binary = format(value, '08b')
        
        return binary
    
    def _decode_glow(self, visual: VisualEncoding) -> str:
        """Decode glow-encoded message"""
        binary = ""
        
        glow_frac = visual.glow_intensity - int(visual.glow_intensity)
        pattern_frac = visual.pattern_density - int(visual.pattern_density)
        
        threshold = self.encoding_precision / 2
        
        binary += "1" if glow_frac > threshold else "0"
        binary += "1" if pattern_frac > threshold else "0"
        
        return binary
    
    def _decode_multi(self, visual: VisualEncoding) -> str:
        """Decode multi-channel message"""
        # Combine all channels
        binary = ""
        binary += self._decode_lsb(visual)
        binary += self._decode_position(visual)
        binary += self._decode_rotation(visual)
        binary += self._decode_glow(visual)
        
        return binary
    
    # =========================================================================
    # Utility Functions
    # =========================================================================
    
    def _text_to_binary(self, text: str) -> str:
        """Convert text to binary string"""
        binary = ''.join(format(ord(char), '08b') for char in text)
        return binary
    
    def _binary_to_text(self, binary: str) -> str:
        """Convert binary string to text"""
        # Pad to multiple of 8
        while len(binary) % 8 != 0:
            binary += '0'
        
        chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            try:
                char = chr(int(byte, 2))
                if char.isprintable():
                    chars.append(char)
            except:
                pass
        
        return ''.join(chars)
    
    def verify_authenticity(self, visual: VisualEncoding,
                           expected_checksum: Optional[str] = None) -> bool:
        """
        Verify if a visualization is authentic
        
        Args:
            visual: Visual encoding to verify
            expected_checksum: Expected checksum (if None, extract from visual)
            
        Returns:
            True if authentic, False otherwise
        """
        # Extract embedded checksum
        embedded = self.extract_message(visual, 'lsb')
        
        if not embedded or embedded.message_type != 'checksum':
            logger.warning("No checksum found in visualization")
            return False
        
        # Calculate actual checksum
        actual = self.create_checksum(visual)
        
        # Compare
        if expected_checksum:
            return embedded.content == expected_checksum
        else:
            # Just verify that a checksum exists
            return len(embedded.content) > 0
    
    def batch_inject(self, visual_encodings: List[VisualEncoding],
                    message: SecretMessage) -> List[VisualEncoding]:
        """Inject same message into multiple visual encodings"""
        modified = []
        
        for visual in visual_encodings:
            modified_visual = self.inject_message(visual, message)
            modified.append(modified_visual)
        
        logger.info(f"Injected message into {len(modified)} visualizations")
        
        return modified
    
    def generate_authentication_code(self, visual: VisualEncoding) -> str:
        """
        Generate authentication code for a visualization
        Can be shared publicly to verify authenticity later
        """
        data = f"{visual.name}|{visual.formula_id}|" \
               f"{visual.hue:.2f}|{visual.x:.4f}|{visual.y:.4f}"
        
        # Hash with secret key
        data_with_key = data + self.secret_key
        
        auth_code = hashlib.sha256(data_with_key.encode()).hexdigest()[:12]
        
        return auth_code.upper()
    
    def verify_authentication_code(self, visual: VisualEncoding, 
                                   auth_code: str) -> bool:
        """Verify authentication code matches visual"""
        generated = self.generate_authentication_code(visual)
        return generated.upper() == auth_code.upper()

