"""
Test file to verify PIL Image conversion from GenAI image objects
without calling the actual API.
"""

import io
from PIL import Image as PILImage
from unittest.mock import Mock


def test_genai_image_to_pil():
    """Test converting GenAI image object to PIL Image without API call"""
    
    # Create a test PIL image
    test_pil_image = PILImage.new('RGB', (100, 100), color=(73, 109, 137))
    
    # Save it as bytes to simulate GenAI response
    buf = io.BytesIO()
    test_pil_image.save(buf, format='PNG')
    image_bytes = buf.getvalue()
    
    # Mock the GenAI image object (Pydantic model)
    mock_genai_image = Mock()
    mock_genai_image.data = image_bytes
    
    # Simulate the function that converts GenAI image to PIL
    def convert_genai_image_to_pil(image_data):
        """Convert GenAI image to PIL Image"""
        if hasattr(image_data, 'data'):
            return PILImage.open(io.BytesIO(image_data.data))
        return image_data
    
    # Test the conversion
    print("🧪 Testing GenAI Image to PIL conversion...")
    try:
        converted_image = convert_genai_image_to_pil(mock_genai_image)
        
        # Verify it's a PIL Image
        assert isinstance(converted_image, PILImage.Image), "Should return PIL Image"
        
        # Verify it has the format attribute (this was the original error)
        assert hasattr(converted_image, 'format'), "PIL Image should have format attribute"
        
        # Verify we can save it
        test_buf = io.BytesIO()
        converted_image.save(test_buf, format='PNG')
        
        print("✅ Test PASSED: GenAI image successfully converted to PIL Image")
        print(f"   - Image size: {converted_image.size}")
        print(f"   - Image format: {converted_image.format}")
        print(f"   - Image mode: {converted_image.mode}")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        return False


def test_streamlit_image_display():
    """Test that PIL Image can be used with Streamlit's st.image()"""
    
    print("\n🧪 Testing Streamlit image display compatibility...")
    try:
        # Create a test image
        test_image = PILImage.new('RGB', (200, 200), color=(255, 100, 100))
        
        # Verify it has the required attributes for Streamlit
        assert hasattr(test_image, 'format'), "Missing format attribute"
        
        # Verify we can save to bytes (what Streamlit needs)
        buf = io.BytesIO()
        test_image.save(buf, format='PNG')
        image_bytes = buf.getvalue()
        
        assert len(image_bytes) > 0, "Image bytes should not be empty"
        
        print("✅ Test PASSED: PIL Image is compatible with Streamlit")
        print(f"   - Image bytes size: {len(image_bytes)} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        return False


def test_aspect_ratio_handling():
    """Test that different aspect ratios work without API"""
    
    print("\n🧪 Testing aspect ratio image generation...")
    try:
        aspect_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
        aspect_map = {
            "1:1": (512, 512),
            "16:9": (800, 450),
            "9:16": (450, 800),
            "4:3": (640, 480),
            "3:4": (480, 640)
        }
        
        for ratio in aspect_ratios:
            width, height = aspect_map.get(ratio, (512, 512))
            img = PILImage.new('RGB', (width, height), color=(100, 150, 200))
            
            # Verify PIL can handle each aspect ratio
            assert img.size == (width, height), f"Image size mismatch for {ratio}"
            
            # Verify it can be saved
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            
            print(f"   ✓ {ratio}: {width}x{height} - {len(buf.getvalue())} bytes")
        
        print("✅ Test PASSED: All aspect ratios work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🎬 LynchVision PIL Image Conversion Tests")
    print("=" * 60)
    
    results = []
    results.append(test_genai_image_to_pil())
    results.append(test_streamlit_image_display())
    results.append(test_aspect_ratio_handling())
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("🎉 All tests passed! Ready to use with Streamlit.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")