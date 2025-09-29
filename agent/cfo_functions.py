import pandas as pd
from agent.data_loader import load_data

def convert_to_usd(amount, currency, month, fx_df):
    """
    Convert any currency amount to USD using FX rates.
    """
    if currency == 'USD':
        return float(amount)
    
    fx_rate = fx_df[(fx_df['month'] == month) & (fx_df['currency'] == currency)]['rate_to_usd'].item()
    
    usd_amount = amount * fx_rate
    return float(usd_amount)


def convert_df_to_usd(df, amount_col, currency_col, month_col, fx_df):
    """
    Convert entire DataFrame columns to USD and add as new column.
    """
    df_copy = df.copy()
    converted_amounts = []
    
    for _, row in df_copy.iterrows():
        usd_amount = convert_to_usd(row[amount_col], row[currency_col], row[month_col], fx_df)
        converted_amounts.append(usd_amount)
    
    df_copy['amount_usd'] = converted_amounts
    return df_copy


def get_revenue_vs_budget(start_month, start_year, end_month, end_year):
    """
    Compare actual revenue vs budget in USD for a date range.
    
    Args:
        start_month: Starting month (1-12)
        start_year: Starting year (e.g., 2025)
        end_month: Ending month (1-12)
        end_year: Ending year (e.g., 2025)
        
    Returns:
        dict: {'actual_usd': float, 'budget_usd': float, 'difference': float, 'percent_diff': float}
    """

    actuals, budget, cash, fx = load_data()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')
    
    actual_revenue = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date) & (actuals['account_category'] == 'Revenue')]
    budget_revenue = budget[(budget['month'] >= start_date) & (budget['month'] <= end_date) & (budget['account_category'] == 'Revenue')]
    
    actual_revenue_usd = convert_df_to_usd(actual_revenue, 'amount', 'currency', 'month', fx)
    budget_revenue_usd = convert_df_to_usd(budget_revenue, 'amount', 'currency', 'month', fx)

    total_actual_usd = actual_revenue_usd['amount_usd'].sum()
    total_budget_usd = budget_revenue_usd['amount_usd'].sum()

    difference = total_actual_usd - total_budget_usd
    percent_diff = (difference / total_budget_usd) * 100
    
    return {
        'actual_usd': total_actual_usd,
        'budget_usd': total_budget_usd,
        'difference': difference,
        'percent_diff': percent_diff
    }

def calculate_gross_margin(start_month, start_year, end_month, end_year):
    """
    Calculate gross margin percentage for each month in a date range.
    
    Args:
        start_month: Starting month (1-12)
        start_year: Starting year (e.g., 2025)
        end_month: Ending month (1-12) 
        end_year: Ending year (e.g., 2025)
        
    Returns:
        dict: {'YYYY-MM': margin_percent, ...}
    """
    actuals, budget, cash, fx = load_data()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')
    
    months_in_range = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date)]['month'].unique()
    
    margin_trend = {}
    for m in sorted(months_in_range):
        month_data = actuals[actuals['month'] == m]
        
        revenue_data = month_data[month_data['account_category'] == 'Revenue']
        cogs_data = month_data[month_data['account_category'] == 'COGS']
        
        revenue_usd = convert_df_to_usd(revenue_data, 'amount', 'currency', 'month', fx)
        cogs_usd = convert_df_to_usd(cogs_data, 'amount', 'currency', 'month', fx)
        
        total_revenue = revenue_usd['amount_usd'].sum()
        total_cogs = cogs_usd['amount_usd'].sum()
        
        gross_profit = total_revenue - total_cogs
        margin_percent = (gross_profit / total_revenue) * 100
        
        margin_trend[m.strftime('%Y-%m')] = round(margin_percent, 2)
    
    return margin_trend


def opex_by_category(start_month, start_year, end_month, end_year):
    """
    Break down operating expenses in USD by category for a date range.
    
    Args:
        start_month: Starting month (1-12)
        start_year: Starting year (e.g., 2025)
        end_month: Ending month (1-12)
        end_year: Ending year (e.g., 2025)
        
    Returns:
        dict: {'Marketing': amount_usd, 'Sales': amount_usd, ...}
    """
    actuals, budget, cash, fx = load_data()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')
    
    opex_data = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date) & (actuals['account_category'].str.startswith('Opex:'))]
    opex_usd = convert_df_to_usd(opex_data, 'amount', 'currency', 'month', fx)
    
    opex_category = {}
    for _, row in opex_usd.iterrows():
        category = row['account_category'].replace('Opex:', '')
        if category in opex_category:
            opex_category[category] += row['amount_usd']
        else:
            opex_category[category] = row['amount_usd']
    
    return opex_category


def calculate_cash_runway(start_month, start_year, end_month, end_year):
    """
    Calculate cash runway based on a rate from a date range.
    
    Args:
        start_month: Starting month (1-12)
        start_year: Starting year (e.g., 2025)
        end_month: Ending month (1-12)
        end_year: Ending year (e.g., 2025)
        
    Returns:
        dict: {'current_cash': float, 'monthly_cash_flow': float, 'runway_months': float}
    """

    actuals, budget, cash, fx = load_data()
    
    latest_cash_date = cash['month'].max()
    current_cash = cash[cash['month'] == latest_cash_date]['cash_usd'].item()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')
    
    months_in_range = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date)]['month'].unique()
    
    monthly_flows = []
    for m in months_in_range:
        month_data = actuals[actuals['month'] == m]
        month_usd = convert_df_to_usd(month_data, 'amount', 'currency', 'month', fx)
        
        revenue = month_usd[month_usd['account_category'] == 'Revenue']['amount_usd'].sum()
        cogs = month_usd[month_usd['account_category'] == 'COGS']['amount_usd'].sum()
        opex = month_usd[month_usd['account_category'].str.startswith('Opex:')]['amount_usd'].sum()
        
        monthly_flow = revenue - cogs - opex
        monthly_flows.append(monthly_flow)
    
    avg_monthly_cash_flow = sum(monthly_flows) / len(monthly_flows)
    if avg_monthly_cash_flow < 0:
        runway_months = current_cash / abs(avg_monthly_cash_flow)
    else:
        runway_months = float('inf')
    
    return {
        'current_cash': current_cash,
        'monthly_cash_flow': avg_monthly_cash_flow, 
        'runway_months': runway_months
    }

def calculate_gross_margin_aggregate(start_month, start_year, end_month, end_year):
    """
    Calculate one aggregated gross margin percent for entire date range.
    """
    actuals, budget, cash, fx = load_data()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')
    
    revenue_data = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date) & (actuals['account_category'] == 'Revenue')]
    cogs_data = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date) & (actuals['account_category'] == 'COGS')]
    
    revenue_usd = convert_df_to_usd(revenue_data, 'amount', 'currency', 'month', fx)
    cogs_usd = convert_df_to_usd(cogs_data, 'amount', 'currency', 'month', fx)
    
    total_revenue = revenue_usd['amount_usd'].sum()
    total_cogs = cogs_usd['amount_usd'].sum()
    
    gross_profit = total_revenue - total_cogs
    margin_percent = (gross_profit / total_revenue) * 100
    
    return {
        'margin_percent': round(margin_percent, 1),
        'total_revenue': total_revenue,
        'total_cogs': total_cogs
    }

def calculate_ebitda(start_month, start_year, end_month, end_year):
    """
    Calculate EBITDA in USD for a date range.
    EBITDA = Revenue - COGS - Total Opex
    
    Args:
        start_month: Starting month (1-12)
        start_year: Starting year (e.g., 2025)
        end_month: Ending month (1-12)
        end_year: Ending year (e.g., 2025)
        
    Returns:
        dict: {'ebitda_usd': float, 'total_revenue': float, 'total_cogs': float, 'total_opex': float}
    """
    actuals, budget, cash, fx = load_data()
    
    start_date = pd.to_datetime(f'{start_year}-{start_month:02d}', format='%Y-%m')
    end_date = pd.to_datetime(f'{end_year}-{end_month:02d}', format='%Y-%m')

    date_filtered = actuals[(actuals['month'] >= start_date) & (actuals['month'] <= end_date)]
    
    revenue_data = date_filtered[date_filtered['account_category'] == 'Revenue']
    cogs_data = date_filtered[date_filtered['account_category'] == 'COGS']
    opex_data = date_filtered[date_filtered['account_category'].str.startswith('Opex:')]
    
    revenue_usd = convert_df_to_usd(revenue_data, 'amount', 'currency', 'month', fx)
    cogs_usd = convert_df_to_usd(cogs_data, 'amount', 'currency', 'month', fx)
    opex_usd = convert_df_to_usd(opex_data, 'amount', 'currency', 'month', fx)
    
    total_revenue = revenue_usd['amount_usd'].sum()
    total_cogs = cogs_usd['amount_usd'].sum()
    total_opex = opex_usd['amount_usd'].sum()

    ebitda = total_revenue - total_cogs - total_opex
    
    return {
        'ebitda_usd': ebitda,
        'total_revenue': total_revenue,
        'total_cogs': total_cogs,
        'total_opex': total_opex
    }