"""Conversational financial Q&A over the bundled, sourced CSV dataset."""
from __future__ import annotations
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "financial_data_2023_2025.csv"
METRICS = {
    "revenue": ("Total Revenue (USD millions)", ("revenue", "sales")),
    "net income": ("Net Income (USD millions)", ("net income", "profit", "earnings")),
    "assets": ("Total Assets (USD millions)", ("assets", "asset")),
    "liabilities": ("Total Liabilities (USD millions)", ("liabilities", "liability")),
    "operating cash flow": ("Cash Flow from Operating Activities (USD millions)", ("operating cash flow", "cash flow from operations", "cash flow", "cashflow")),
}
COMPANY_ALIASES = {"microsoft": "Microsoft", "msft": "Microsoft", "tesla": "Tesla", "tsla": "Tesla", "apple": "Apple", "aapl": "Apple"}
COMPARISON_TERMS = ("change", "growth", "increased", "decreased", "increase", "decrease", "compare", "compared", "year over year", "yoy", "difference")

@dataclass
class ChatSession:
    company: str | None = None
    year: int | None = None
    metric: str | None = None
    comparison: bool = False

class FinancialChatbot:
    def __init__(self, data_path: str | Path = DATA_PATH):
        self.data_path = Path(data_path)
        if not self.data_path.is_file():
            raise FileNotFoundError(f"Financial dataset not found: {self.data_path}")
        self.data = pd.read_csv(self.data_path)
        required = {"Company", "Fiscal Year", "Fiscal Year End", *[value[0] for value in METRICS.values()], "Source URL"}
        missing = required - set(self.data.columns)
        if missing:
            raise ValueError("Dataset is missing required columns: " + ", ".join(sorted(missing)))
        self.data["Fiscal Year"] = pd.to_numeric(self.data["Fiscal Year"], errors="coerce").astype("Int64")
        self.session = ChatSession()

    def reset(self):
        self.session = ChatSession()

    @staticmethod
    def _extract_company(text):
        for alias, company in COMPANY_ALIASES.items():
            if re.search(r"\b" + re.escape(alias) + r"\b", text, re.I):
                return company
        return None

    @staticmethod
    def _extract_year(text):
        match = re.search(r"\b(?:FY\s*)?(202[3-5])\b", text, re.I)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_metric(text):
        for key in ("liabilities", "assets", "operating cash flow", "net income", "revenue"):
            aliases = METRICS[key][1]
            if any(re.search(r"\b" + re.escape(alias) + r"\b", text, re.I) for alias in aliases):
                return key
        return None

    def _help(self):
        return ("Ask about Microsoft, Tesla, or Apple for FY2023–FY2025. Supported metrics: revenue, net income, assets, liabilities, and operating cash flow. "
                "Examples: 'Apple revenue FY2025', 'Tesla' then 'assets', or 'compare Microsoft net income in 2025'. Follow-ups reuse known context; type reset to clear.")

    def reply(self, message: str) -> str:
        raw = (message or "").strip()
        q = raw.lower()
        if not q:
            return "Type a company, year, and metric, or type help for examples."
        if q in {"exit", "quit", "bye"}:
            self.reset()
            return "Goodbye. Conversation context cleared."
        if q in {"reset", "clear", "start over"}:
            self.reset()
            return "Context cleared. Which company would you like to analyze?"
        if q in {"help", "?"} or "what can you do" in q:
            return self._help()
        company = self._extract_company(raw)
        year = self._extract_year(raw)
        metric = self._extract_metric(raw)
        unsupported_year = re.search(r"\b20\d{2}\b", raw)
        if unsupported_year and year is None:
            return "This dataset covers FY2023–FY2025. Please choose one of those years."
        if company:
            self.session.company = company
        if year:
            self.session.year = year
        if metric:
            self.session.metric = metric
        if any(term in q for term in COMPARISON_TERMS):
            self.session.comparison = True
        if self.session.company is None:
            return "Which company: Microsoft, Tesla, or Apple?"
        if self.session.metric is None:
            return f"Got it — {self.session.company}. Which metric: revenue, net income, assets, liabilities, or operating cash flow?"
        if self.session.year is None:
            self.session.year = 2025
        company, year, metric = self.session.company, self.session.year, self.session.metric
        if year not in range(2023, 2026):
            return "This dataset covers FY2023–FY2025. Please choose one of those years."
        column = METRICS[metric][0]
        found = self.data[(self.data.Company == company) & (self.data["Fiscal Year"] == year)]
        if found.empty:
            return f"No data is available for {company} FY{year}."
        row = found.iloc[0]
        value = float(row[column])
        label = column.split(" (")[0]
        source = str(row["Source URL"])
        if self.session.comparison:
            prior = self.data[(self.data.Company == company) & (self.data["Fiscal Year"] == year - 1)]
            if prior.empty:
                return f"I can’t compare {company} {label} for FY{year}: FY{year-1} data is not in the dataset. Source: {source}"
            old = float(prior.iloc[0][column])
            change = value - old
            percentage = (change / abs(old) * 100) if old else None
            direction = "increased" if change > 0 else ("decreased" if change < 0 else "was unchanged")
            percent_text = f" ({abs(percentage):.2f}%)" if percentage is not None else " (percentage change unavailable because the prior value is zero)"
            answer = f"{company} {label.lower()} {direction} by ${abs(change):,.0f} million{percent_text} from FY{year-1} to FY{year}."
            self.session.comparison = False
        else:
            answer = f"{company} {label} in FY{year} was ${value:,.0f} million USD."
        return answer + f" Fiscal year end: {row['Fiscal Year End']}. Source: {source}"

    def run(self):
        print("Financial Analysis Chatbot — type help for examples, reset to clear, or exit to quit.")
        while True:
            try:
                message = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            print("Bot:", self.reply(message))
            if message.strip().lower() in {"exit", "quit", "bye"}:
                break

def main():
    parser = argparse.ArgumentParser(description="Ask questions about sourced FY2023–FY2025 company financials.")
    parser.add_argument("--data", default=str(DATA_PATH, ), help="Path to financial CSV")
    args = parser.parse_args()
    try:
        FinancialChatbot(args.data).run()
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
        raise SystemExit(f"Could not start chatbot: {exc}")

if __name__ == "__main__":
    main()
