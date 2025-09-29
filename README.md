# CFO AI Assistant

AI-powered financial analysis assistant using OpenAI GPT-4 for automated financial reporting and insights.

## Features

- Natural language queries for financial data
- Automated chart generation
- Revenue vs budget analysis
- Gross margin calculations
- Operating expense breakdowns
- Cash runway projections
- EBITDA calculations

## Project Structure

```
CFO_copilot/
├── agent/              # Financial calculation functions
├── fixtures/           # Sample financial data (CSV files)
├── tests/              # pytest test suite
├── app.py              # Streamlit application
├── openai_cfo_agent.py # OpenAI integration with function calling
└── requirements.txt    # Python dependencies
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## Usage

Ask natural language questions about your financial data:

- "What was our revenue vs budget for Q2 2025?"
- "Show me gross margin trend for the last 6 months"
- "Break down our operating expenses"
- "What's our cash runway based on last 3 months?"
- "Calculate EBITDA for Q1 2025"

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only function tests (no API calls)
pytest tests/test_cfo_functions.py -v

# Run integration tests (requires API key)
pytest tests/test_openai_agent.py -v
```

## Data Format

Place your financial data CSV files in the `fixtures/` directory:
- `actuals.csv` - Actual financial transactions
- `budget.csv` - Budgeted amounts
- `cash.csv` - Cash balance data
- `fx.csv` - Foreign exchange rates

## Technologies

- **OpenAI GPT-4** - Natural language processing and function calling
- **Streamlit** - Web application framework
- **Plotly** - Interactive chart generation
- **Pandas** - Data manipulation
- **pytest** - Testing framework

## License

MIT