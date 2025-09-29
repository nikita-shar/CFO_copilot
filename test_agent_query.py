#!/usr/bin/env python3
"""
Test the agent with real API calls to OpenAI.
Uses simple queries that you can manually verify.
"""

import os
from openai_cfo_agent import OpenAICFOAgent

def test_agent():
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY='sk-proj-...'")
        return
    
    print("=" * 70)
    print("Testing CFO Agent with Simple, Verifiable Queries")
    print("=" * 70)
    print("\nThis will make real API calls to OpenAI (~$0.05 total)")
    print("Initializing agent...")
    
    # Initialize agent
    try:
        agent = OpenAICFOAgent(api_key)
        print("✅ Agent initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Test questions - easy to manually verify
    test_questions = [
        {
            "question": "What was our revenue in January 2025?",
            "verify": "Check your fixtures/actuals.csv - sum all Revenue rows for 2025-01"
        },
        {
            "question": "What was our total COGS in January 2025?",
            "verify": "Check your fixtures/actuals.csv - sum all COGS rows for 2025-01"
        },
        {
            "question": "What was budgeted revenue for January 2025?",
            "verify": "Check your fixtures/budget.csv - sum all Revenue rows for 2025-01"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_questions, 1):
        print("\n" + "=" * 70)
        print(f"TEST {i}/{len(test_questions)}")
        print("=" * 70)
        print(f"\n📝 Question: {test['question']}")
        print(f"✍️  How to verify: {test['verify']}")
        print("\n⏳ Waiting for GPT-4 response (3-5 seconds)...\n")
        
        try:
            response = agent.ask(test['question'])
            
            print("🤖 ANSWER:")
            print("-" * 70)
            print(response['answer'])
            print("-" * 70)
            
            print("\n📊 RAW DATA (for manual verification):")
            if response['data']:
                for func_name, data in response['data'].items():
                    print(f"\n  Function called: {func_name}")
                    for key, value in data.items():
                        if isinstance(value, (int, float)):
                            print(f"    • {key}: ${value:,.2f}")
                        elif isinstance(value, dict):
                            print(f"    • {key}:")
                            for k, v in value.items():
                                print(f"        - {k}: {v}")
                        else:
                            print(f"    • {key}: {value}")
            else:
                print("  (No function called - might be a general response)")
            
            print("\n📈 CHART:")
            if response.get('chart_config'):
                config = response['chart_config']
                print(f"  Type: {config.get('chart_type', 'none')}")
                print(f"  Title: {config.get('title', 'none')}")
            else:
                print("  (No chart suggested)")
            
            results.append({
                'question': test['question'],
                'success': True,
                'answer': response['answer']
            })
            
            print("\n✅ Test passed!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'question': test['question'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n✅ Passed: {success_count}/{len(results)}")
    print(f"❌ Failed: {len(results) - success_count}/{len(results)}")
    
    print("\n📝 MANUAL VERIFICATION STEPS:")
    print("-" * 70)
    print("\nNow manually verify the answers against your CSV files:\n")
    
    print("1. Open fixtures/actuals.csv")
    print("   - Filter for month = '2025-01'")
    print("   - Sum 'amount' where account_category = 'Revenue'")
    print("   - Sum 'amount' where account_category = 'COGS'")
    print("   - Convert to USD using fixtures/fx.csv rates\n")
    
    print("2. Open fixtures/budget.csv")
    print("   - Filter for month = '2025-01'")
    print("   - Sum 'amount' where account_category = 'Revenue'")
    print("   - Convert to USD using fixtures/fx.csv rates\n")
    
    print("3. Compare your manual calculations with the AI's answers above")
    print("   - They should match (within rounding)")
    
    print("\n" + "=" * 70)
    
    if success_count == len(results):
        print("✅ ALL TESTS PASSED - Ready for Streamlit!")
        print("\nRun: streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed - check errors above")
    
    print("=" * 70)

if __name__ == "__main__":
    test_agent()



# #!/usr/bin/env python3
# """
# Test the agent with a real API call to OpenAI.
# This will use API credits (~$0.01).
# """

# import os
# from openai_cfo_agent import OpenAICFOAgent

# def test_agent():
#     # Get API key
#     api_key = os.getenv('OPENAI_API_KEY')
#     if not api_key:
#         print("❌ Error: OPENAI_API_KEY not set")
#         print("Set it with: export OPENAI_API_KEY='sk-proj-...'")
#         return
    
#     print("=" * 60)
#     print("Testing CFO Agent with Real Query")
#     print("=" * 60)
#     print("\nThis will make a real API call to OpenAI (~$0.01)")
#     print("Initializing agent...")
    
#     # Initialize agent
#     try:
#         agent = OpenAICFOAgent(api_key)
#         print("✅ Agent initialized\n")
#     except Exception as e:
#         print(f"❌ Failed to initialize agent: {e}")
#         return
    
#     # Test question
#     question = "What was our revenue vs budget for Q2 2025?"
    
#     print(f"Question: {question}")
#     print("\nWaiting for GPT-4 response...")
#     print("(This may take 3-5 seconds)\n")
    
#     try:
#         response = agent.ask(question)
        
#         print("=" * 60)
#         print("✅ SUCCESS!")
#         print("=" * 60)
        
#         print("\n📊 ANSWER:")
#         print(response['answer'])
        
#         print("\n📈 RAW DATA:")
#         for func_name, data in response['data'].items():
#             print(f"\n  Function: {func_name}")
#             for key, value in data.items():
#                 if isinstance(value, float):
#                     print(f"    {key}: ${value:,.2f}")
#                 else:
#                     print(f"    {key}: {value}")
        
#         print("\n🎨 CHART CONFIG:")
#         if response['chart_config']:
#             config = response['chart_config']
#             print(f"  Type: {config.get('chart_type')}")
#             print(f"  Title: {config.get('title')}")
#             print(f"  Labels: {config.get('data', {}).get('labels')}")
#             print(f"  Values: {config.get('data', {}).get('values')}")
#         else:
#             print("  No chart generated")
        
#         print("\n" + "=" * 60)
#         print("✅ Test completed successfully!")
#         print("=" * 60)
#         print("\nReady to run: streamlit run streamlit_app.py")
        
#     except Exception as e:
#         print(f"\n❌ Error during query: {e}")
#         import traceback
#         print("\nFull error:")
#         traceback.print_exc()

# if __name__ == "__main__":
#     test_agent()