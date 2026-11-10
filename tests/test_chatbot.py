import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chatbot import FinancialChatbot


class ChatbotTests(unittest.TestCase):
    def setUp(self):
        self.bot = FinancialChatbot()

    def test_company_then_metric_follow_up(self):
        self.assertIn("Which metric", self.bot.reply("Apple"))
        answer = self.bot.reply("assets")
        self.assertIn("Apple Total Assets in FY2025", answer)
        self.assertIn("Source: https://", answer)

    def test_metric_company_and_year_follow_ups(self):
        self.bot.reply("revenue")
        self.bot.reply("Tesla")
        answer = self.bot.reply("FY2024")
        self.assertIn("Tesla Total Revenue in FY2024", answer)

    def test_year_over_year_comparison(self):
        self.bot.reply("Microsoft")
        self.bot.reply("net income")
        answer = self.bot.reply("compare 2025")
        self.assertIn("from FY2024 to FY2025", answer)
        self.assertIn("increased", answer)

    def test_sessions_are_independent(self):
        self.bot.reply("Apple revenue 2025")
        self.assertIsNone(FinancialChatbot().session.company)

    def test_reset(self):
        self.bot.reply("Apple")
        self.assertIn("Context cleared", self.bot.reply("reset"))
        self.assertIsNone(self.bot.session.company)

    def test_out_of_range_year(self):
        self.bot.reply("Apple revenue")
        self.assertIn("FY2023–FY2025", self.bot.reply("2026"))

    def test_missing_company_prompt(self):
        self.assertIn("Which company", self.bot.reply("revenue 2025"))

    def test_help(self):
        self.assertIn("operating cash flow", self.bot.reply("help"))


if __name__ == "__main__":
    unittest.main()
