import os
import sys
from dotenv import load_dotenv
from src.controller import DiscussionController
from src.interface import ModeratorInterface

def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        sys.exit(1)
        
    try:
        controller = DiscussionController(api_key)
        interface = ModeratorInterface(controller)
        interface.run_loop()
    except Exception as e:
        print(f"Fatal Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
