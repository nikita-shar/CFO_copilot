import openai
import json
from datetime import datetime
import agent.cfo_functions as cfo

class OpenAICFOAgent:
    def __init__(self, api_key):
        """
        Initialize the OpenAI-powered CFO agent.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.conversation_history = []
        
        # Define tools/functions that the LLM can call
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_revenue_vs_budget",
                    "description": "Compare actual revenue vs budgeted revenue for a specific time period. Use this when users ask about revenue performance, how we did against budget, or revenue targets.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {
                                "type": "integer",
                                "description": "Starting month (1-12)"
                            },
                            "start_year": {
                                "type": "integer",
                                "description": "Starting year (e.g., 2025)"
                            },
                            "end_month": {
                                "type": "integer",
                                "description": "Ending month (1-12)"
                            },
                            "end_year": {
                                "type": "integer",
                                "description": "Ending year (e.g., 2025)"
                            }
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_gross_margin",
                    "description": "Calculate gross margin percentage for each month in a date range. Returns a trend/breakdown by month. Use this when users ask about margin trends, monthly margins, or how margins changed over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {"type": "integer", "description": "Starting month (1-12)"},
                            "start_year": {"type": "integer", "description": "Starting year"},
                            "end_month": {"type": "integer", "description": "Ending month (1-12)"},
                            "end_year": {"type": "integer", "description": "Ending year"}
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_gross_margin_aggregate",
                    "description": "Calculate a single aggregated gross margin percentage for an entire time period. Use this when users ask for overall margin, total margin, or aggregate margin for a period.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {"type": "integer", "description": "Starting month (1-12)"},
                            "start_year": {"type": "integer", "description": "Starting year"},
                            "end_month": {"type": "integer", "description": "Ending month (1-12)"},
                            "end_year": {"type": "integer", "description": "Ending year"}
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "opex_by_category",
                    "description": "Break down operating expenses by category (Marketing, Sales, R&D, etc.) for a time period. Use when users ask about spending, opex breakdown, or where money is going.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {"type": "integer", "description": "Starting month (1-12)"},
                            "start_year": {"type": "integer", "description": "Starting year"},
                            "end_month": {"type": "integer", "description": "Ending month (1-12)"},
                            "end_year": {"type": "integer", "description": "Ending year"}
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_cash_runway",
                    "description": "Calculate how many months of cash runway remain based on current cash and burn rate from a specific period. Use when users ask about runway, how long cash will last, or burn rate.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {"type": "integer", "description": "Starting month for burn rate calculation (1-12)"},
                            "start_year": {"type": "integer", "description": "Starting year for burn rate calculation"},
                            "end_month": {"type": "integer", "description": "Ending month for burn rate calculation (1-12)"},
                            "end_year": {"type": "integer", "description": "Ending year for burn rate calculation"}
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_ebitda",
                    "description": "Calculate EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) for a time period. Use when users ask about profitability, EBITDA, or operating profit.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_month": {"type": "integer", "description": "Starting month (1-12)"},
                            "start_year": {"type": "integer", "description": "Starting year"},
                            "end_month": {"type": "integer", "description": "Ending month (1-12)"},
                            "end_year": {"type": "integer", "description": "Ending year"}
                        },
                        "required": ["start_month", "start_year", "end_month", "end_year"]
                    }
                }
            }
        ]
    
    def process_tool_call(self, function_name, function_args):
        """
        Execute the actual function call based on function name.
        """
        function_map = {
            "get_revenue_vs_budget": cfo.get_revenue_vs_budget,
            "calculate_gross_margin": cfo.calculate_gross_margin,
            "calculate_gross_margin_aggregate": cfo.calculate_gross_margin_aggregate,
            "opex_by_category": cfo.opex_by_category,
            "calculate_cash_runway": cfo.calculate_cash_runway,
            "calculate_ebitda": cfo.calculate_ebitda
        }
        
        func = function_map.get(function_name)
        if func:
            result = func(**function_args)
            return result
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    def ask(self, user_question):
        """
        Main method to process user questions.
        
        Returns:
            dict: {
                'answer': str,  # Natural language response
                'data': dict,   # Raw data from function calls
                'chart_config': dict  # Suggested chart configuration
            }
        """
        # System message with context
        system_message = f"""You are a financial analyst assistant. Today's date is {datetime.now().strftime('%B %d, %Y')} (month {self.current_month}, year {self.current_year}).

When users ask questions without specifying dates:
- "last 3 months" means the last 3 complete months
- "this quarter" or "Q1/Q2/Q3/Q4" refers to the appropriate quarter
- "this year" means January through December of current year
- If they just say a month name without a year, assume current year

CRITICAL FORMATTING RULES:
- Use proper spacing between all words and numbers
- Never use asterisks (*) or underscores (_) in your responses
- Format all numbers with commas: $3,990,000 not $3990000
- Always put spaces around "and", "is", "of", etc.
- Write in plain text only, no markdown formatting

After getting data from function calls, you should:
1. Provide a clear, conversational answer
2. Include a chart_config recommendation in JSON format with this structure:
{{
  "chart_type": "line" | "bar" | "pie" | "area",
  "title": "Chart title",
  "x_label": "X axis label",
  "y_label": "Y axis label",
  "data": {{
    "labels": [...],
    "values": [...]
  }}
}}

Choose chart types based on:
- Trends over time: "line" or "area"
- Comparisons: "bar"
- Proportions/breakdown: "pie"
- Single values: "bar" with one bar"""

        # Build messages
        messages = [{"role": "system", "content": system_message}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_question})
        
        # Initial API call
        response = self.client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-turbo" or "gpt-3.5-turbo"
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        # Handle tool calls
        collected_data = {}
        response_message = response.choices[0].message
        
        # Process function calls iteratively
        while response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                result = self.process_tool_call(function_name, function_args)
                collected_data[function_name] = result
                
                # Add function response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            # Get next response
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
        
        # Extract final answer
        final_answer = response_message.content or ""

        # Update conversation history (keep last 10 messages to control context)
        self.conversation_history.append({"role": "user", "content": user_question})
        self.conversation_history.append({"role": "assistant", "content": final_answer})
        if len(self.conversation_history) > 20:  # Keep last 10 exchanges
            self.conversation_history = self.conversation_history[-20:]
        
        # Parse chart configuration from the response
        chart_config = self.extract_chart_config(final_answer, collected_data)
        
        return {
            "answer": final_answer,
            "data": collected_data,
            "chart_config": chart_config
        }
    
    def extract_chart_config(self, answer, data):
        """
        Extract or generate chart configuration from the LLM's response and data.
        """
        # Try to find JSON chart_config in the answer
        try:
            if "chart_config" in answer.lower() or "{" in answer:
                start = answer.find("{")
                end = answer.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = answer[start:end]
                    config = json.loads(json_str)
                    if "chart_type" in config:
                        return config
        except:
            pass
        
        # Generate default chart config based on the data
        if not data:
            return None
        
        # Auto-generate based on function called
        first_func = list(data.keys())[0]
        first_data = list(data.values())[0]
        
        if first_func == "get_revenue_vs_budget":
            return {
                "chart_type": "bar",
                "title": "Revenue: Actual vs Budget",
                "x_label": "Category",
                "y_label": "Amount (USD)",
                "data": {
                    "labels": ["Actual", "Budget"],
                    "values": [first_data["actual_usd"], first_data["budget_usd"]]
                }
            }
        
        elif first_func == "calculate_gross_margin":
            return {
                "chart_type": "line",
                "title": "Gross Margin Trend",
                "x_label": "Month",
                "y_label": "Margin %",
                "data": {
                    "labels": list(first_data.keys()),
                    "values": list(first_data.values())
                }
            }
        
        elif first_func == "opex_by_category":
            return {
                "chart_type": "pie",
                "title": "Operating Expenses by Category",
                "data": {
                    "labels": list(first_data.keys()),
                    "values": list(first_data.values())
                }
            }
        
        elif first_func == "calculate_ebitda":
            return {
                "chart_type": "bar",
                "title": "EBITDA Breakdown",
                "x_label": "Component",
                "y_label": "Amount (USD)",
                "data": {
                    "labels": ["Revenue", "COGS", "OpEx", "EBITDA"],
                    "values": [
                        first_data["total_revenue"],
                        -first_data["total_cogs"],
                        -first_data["total_opex"],
                        first_data["ebitda_usd"]
                    ]
                }
            }
        
        return None
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []