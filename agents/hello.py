#!/usr/bin/env python3

def greet(name: str) -> str:
    """
    Return a greeting message.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting string
    """
    return f"Hello, {name}!"

def main() -> None:
    """
    Main function that runs when the script is executed directly.
    """
    print(greet("World"))

if __name__ == "__main__":
    main()