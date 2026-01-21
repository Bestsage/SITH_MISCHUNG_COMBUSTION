
import sys
import os
import argparse
import customtkinter as ctk

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Rocket Motor Design Plotter - Launch Configuration")
    parser.add_argument("--safe", action="store_true", help="Launch in safe mode (disable advanced libraries like RocketCEA/CAD)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    parser.add_argument("--scale", type=float, default=None, help="Force UI scaling factor (e.g. 1.0, 1.5, 2.0)")
    parser.add_argument("--theme", type=str, default="dark", help="UI Theme (dark/light)")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print(f"🚀 Initializing Rocket App v6.3...")
    
    if args.debug:
        print(f"🔧 Debug mode enabled")
        os.environ["ROCKET_DEBUG"] = "1"
        
    if args.safe:
        print(f"🛡️ SAFE MODE ACTIVE: Advanced extensions disabled")
        os.environ["ROCKET_SAFE_MODE"] = "1"
        
    if args.scale:
        print(f"🖥️ Forcing UI Scale: {args.scale}")
        # We need to set this environment variable because some logic in utils might use it
        os.environ["CUSTOMTKINTER_SCALE"] = str(args.scale)
        ctk.set_widget_scaling(args.scale)
        ctk.set_window_scaling(args.scale)
    
    ctk.set_appearance_mode(args.theme)
    ctk.set_default_color_theme("dark-blue")
    
    try:
        from core.app import RocketApp
        
        root = ctk.CTk()
        root.title("Loading...")
        
        # Configure global styling that depends on root
        root.configure(fg_color="#000000") # Match BG_MAIN
        
        app = RocketApp(root)
        
        print("✅ App successfully initialized")
        root.mainloop()
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
