import json
from backend.triage_service import execute_triage

def main():
    print("=" * 50)
    print("🏡 Real Estate AI Triage - Command Line Tester")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 50)

    while True:
        print("\n")
        user_input = input("Enter a test inquiry: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting tester. Goodbye! 👋")
            break

        if not user_input.strip():
            continue

        print("\n🤖 Agents are analyzing...")
        try:
            # This calls the exact same function your FastAPI server uses!
            result = execute_triage(user_input)
            
            print("\n✅ Analysis Complete:")
            # Print the dictionary nicely formatted
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        print("-" * 50)

if __name__ == "__main__":
    main()