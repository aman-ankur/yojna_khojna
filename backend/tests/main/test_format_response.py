import unittest
from backend.src.main import format_response

class TestFormatResponse(unittest.TestCase):
    
    def test_format_response_monetary_values_hindi(self):
        """Test that monetary values are properly highlighted in Hindi responses."""
        # Test with various monetary formats
        test_responses = [
            "The scheme provides ₹2.5 lakh for housing in rural areas.",
            "Eligible farmers receive Rs. 6,000 per year under PM-KISAN.",
            "A subsidy of Rs 1,20,000 is available for housing construction.",
            "Women entrepreneurs can get loans up to ₹10 lakhs under PMEGP."
        ]
        
        for response in test_responses:
            formatted = format_response(response, language="hi")
            self.assertNotEqual(formatted, response, "Response should be formatted")
            self.assertIn("<strong>", formatted, "Formatting should include HTML tags")
            
    def test_format_response_monetary_values_english(self):
        """Test that monetary values are properly highlighted in English responses."""
        test_response = "Eligible farmers receive Rs. 6,000 per year under PM-KISAN."
        formatted = format_response(test_response, language="en")
            
        self.assertNotEqual(formatted, test_response, "Response should be formatted")
        self.assertIn("<strong>", formatted, "Formatting should include HTML tags")
        self.assertIn("<strong>Rs. 6,000</strong>", formatted)
            
    def test_format_response_no_monetary_values(self):
        """Test that responses without monetary values remain unchanged."""
        test_response = "You need to submit your Aadhaar card and ration card to apply for this scheme."
        formatted = format_response(test_response)
        self.assertEqual(formatted, test_response, "Response without monetary values should remain unchanged")
    
    def test_format_response_prepend_amount_hindi(self):
        """Test formatting when amount is in later part of response in Hindi mode."""
        test_response = "To apply for this scheme, visit your local Gram Panchayat office. You will receive ₹2.5 lakh for housing construction."
        
        formatted = format_response(test_response, language="hi")
        self.assertNotEqual(formatted, test_response, "Response should be formatted")
        
        # Verify amount is prepended in Hindi
        self.assertTrue(formatted.startswith("आपको <strong>₹2.5 lakh</strong> की राशि मिल सकती है।"), 
                         "Hindi response should prepend amount")
        
    def test_format_response_prepend_amount_english(self):
        """Test formatting when amount is in later part of response in English mode."""
        test_response = "To apply for this scheme, visit your local Gram Panchayat office. You will receive ₹2.5 lakh for housing construction."
        
        formatted = format_response(test_response, language="en")
        self.assertNotEqual(formatted, test_response, "Response should be formatted")
        
        # Verify amount is prepended in English
        self.assertTrue(formatted.startswith("You may be eligible for <strong>₹2.5 lakh</strong>."), 
                         "English response should prepend amount")
        
    def test_format_response_mixed_content(self):
        """Test formatting with mixed content including scheme names and monetary values."""
        test_response = "Under Pradhan Mantri Awas Yojana (PMAY), you can receive ₹2.5 lakh for housing construction. Additionally, SC/ST beneficiaries may get Rs 70,000 extra support."
        
        formatted = format_response(test_response)
        self.assertNotEqual(formatted, test_response, "Response should be formatted")
        
        # Verify monetary values are highlighted
        self.assertIn("<strong>₹2.5 lakh</strong>", formatted)
        self.assertIn("<strong>Rs 70,000</strong>", formatted) 