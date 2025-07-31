"""Keychain environment variable management."""
import subprocess
import os
import sys


class KeychainEnv:
    """Manage environment variables in macOS Keychain."""
    
    def __init__(self, prefix="mailpilot"):
        """Initialize with service prefix."""
        self.prefix = prefix
    
    def set_var(self, key: str, value: str):
        """Set a variable in the keychain."""
        service_name = f"{self.prefix}_{key}"
        
        # Delete existing if present
        subprocess.run([
            "security", "delete-generic-password",
            "-s", service_name
        ], capture_output=True)
        
        # Add new value
        result = subprocess.run([
            "security", "add-generic-password",
            "-s", service_name,
            "-a", os.environ.get("USER", "user"),
            "-w", value
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Set {key} in keychain")
        else:
            print(f"✗ Failed to set {key}: {result.stderr}")
    
    def get_var(self, key: str) -> str:
        """Get a variable from the keychain."""
        service_name = f"{self.prefix}_{key}"
        
        result = subprocess.run([
            "security", "find-generic-password",
            "-s", service_name,
            "-w"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    
    def load_all_to_env(self):
        """Load all mailpilot variables to environment."""
        # Common keys to check
        keys = ["OPENAI_API_KEY"]
        
        for key in keys:
            value = self.get_var(key)
            if value:
                os.environ[key] = value


def main():
    """CLI interface for keychain management."""
    if len(sys.argv) < 2:
        print("Usage: python keychain_env.py [set|get] KEY [VALUE]")
        sys.exit(1)
    
    kc = KeychainEnv()
    command = sys.argv[1]
    
    if command == "set" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        kc.set_var(key, value)
    
    elif command == "get" and len(sys.argv) >= 3:
        key = sys.argv[2]
        value = kc.get_var(key)
        if value:
            print(value)
        else:
            print(f"Key {key} not found in keychain")
            sys.exit(1)
    
    else:
        print("Invalid command")
        sys.exit(1)


if __name__ == "__main__":
    main()