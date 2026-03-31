import os
import importlib
import sys

# Ensure 'app' is in path
sys.path.append(os.getcwd())

def test_imports(start_path="app"):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file).replace(os.sep, ".")[:-3]
                try:
                    print(f"Importing {module_path}...")
                    importlib.import_module(module_path)
                except Exception as e:
                    print(f"FAILED to import {module_path}: {e}")
                    import traceback
                    traceback.print_exc()

if __name__ == "__main__":
    test_imports()
