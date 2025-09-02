import unittest
import pandas as pd
from app.analyzer import calculate_moving_average

class TestAnalyzer(unittest.TestCase):

    def test_calculate_moving_average(self):
        """Test the moving average calculation."""
        # Create a sample DataFrame (newest to oldest, like the API)
        data = {
            '4. close': [18, 16, 14, 12, 10]
        }
        df = pd.DataFrame(data)

        # Calculate moving average with a window of 3
        ma = calculate_moving_average(df, window=3)

        # Check the results (still newest to oldest)
        self.assertEqual(ma.iloc[0], 16.0) # (18 + 16 + 14) / 3
        self.assertEqual(ma.iloc[1], 14.0) # (16 + 14 + 12) / 3
        self.assertEqual(ma.iloc[2], 12.0) # (14 + 12 + 10) / 3
        self.assertTrue(pd.isna(ma.iloc[3]))
        self.assertTrue(pd.isna(ma.iloc[4]))

if __name__ == '__main__':
    unittest.main()
