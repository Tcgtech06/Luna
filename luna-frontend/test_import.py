import sys
print("Python path:")
for p in sys.path[:5]:
    print(f"  {p}")

print("\nTrying to import backend...")
try:
    import backend
    print(f"Backend module: {backend}")
    print(f"Backend __file__: {backend.__file__}")
    print(f"Backend dir: {dir(backend)}")
    if hasattr(backend, 'app'):
        print(f"App found: {backend.app}")
    else:
        print("ERROR: No 'app' attribute found!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
