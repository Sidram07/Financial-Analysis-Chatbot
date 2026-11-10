# Financial Analysis Chatbot

A Python chatbot for conversational questions about Microsoft, Tesla, and Apple annual financials for FY2023–FY2025. It remembers company, year, and metric between messages and supports year-over-year comparisons.

## Files

- `chatbot.py`: command-line chatbot and conversation state.
- `financial_data_2023_2025.csv`: nine sourced company-year records in USD millions.
- `tests/test_chatbot.py`: automated unit tests.
- `notebooks/financial_analysis.ipynb`: Google Colab walkthrough.

## Data scope

The data covers total revenue, net income, total assets, total liabilities, and cash flow from operating activities. Fiscal years are company-specific: Microsoft ends June 30, Tesla December 31, and Apple in late September. FY2025 does not mean a shared calendar-year period. All amounts are USD millions. SEC filing URLs are included in each CSV row.

The FY2023–FY2025 income and cash flow values are reported in the linked SEC 10-K filing tables; balance sheet figures are point-in-time values for each fiscal year end. Recheck against the filing before using figures in formal work. This educational chatbot does not forecast, fetch live data, or give investment advice.

## Requirements and installation

Python 3.10+ and pandas 2.x.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
python chatbot.py
```

Try `Apple`, then `assets`; the chatbot remembers the company. You can also ask `compare Microsoft net income in 2025`. If the year is omitted, FY2025 is used. Type `help`, `reset`, or `exit`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Google Colab

Upload and extract the ZIP in Colab, change the working directory to the extracted project, then run:

```python
!pip install -r requirements.txt
!python chatbot.py
```

Or open `notebooks/financial_analysis.ipynb`.

## Push to GitHub

Create an empty repository named `Financial-Analysis-Chatbot` on GitHub. In a terminal opened in this project folder:

```bash
git init
git add .
git commit -m "Initial financial analysis chatbot"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Financial-Analysis-Chatbot.git
git push -u origin main
```

Replace `YOUR-USERNAME`. The commands publish only when you run them.

## License

MIT.
