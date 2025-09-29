import pandas as pd

def load_data():
    """
    Load all 4 CSV files and return as pandas dataframes.
    
    Returns:
        actuals_df, budget_df, cash_df, fx_df (tuple)
    """

    actuals_df = pd.read_csv('fixtures/actuals.csv')
    budget_df = pd.read_csv('fixtures/budget.csv')  
    cash_df = pd.read_csv('fixtures/cash.csv')
    fx_df = pd.read_csv('fixtures/fx.csv')
    
    actuals_df['amount'] = pd.to_numeric(actuals_df['amount'], errors='coerce')
    budget_df['amount'] = pd.to_numeric(budget_df['amount'], errors='coerce')
    cash_df['cash_usd'] = pd.to_numeric(cash_df['cash_usd'], errors='coerce')
    fx_df['rate_to_usd'] = pd.to_numeric(fx_df['rate_to_usd'], errors='coerce')
    
    actuals_df['month'] = pd.to_datetime(actuals_df['month'], format='%Y-%m')
    budget_df['month'] = pd.to_datetime(budget_df['month'], format='%Y-%m')
    cash_df['month'] = pd.to_datetime(cash_df['month'], format='%Y-%m')
    fx_df['month'] = pd.to_datetime(fx_df['month'], format='%Y-%m')
    
    return actuals_df, budget_df, cash_df, fx_df


def test_load_data():
    """Test the load_data function"""

    actuals, budget, cash, fx = load_data()
    
    print("Testing load_data() ... ")
    print(f"Actuals shape: {actuals.shape}")
    print(f"Budget shape: {budget.shape}")  
    print(f"Cash shape: {cash.shape}")
    print(f"FX shape: {fx.shape}")
    print("Test passed")


if __name__ == "__main__":
    test_load_data()



