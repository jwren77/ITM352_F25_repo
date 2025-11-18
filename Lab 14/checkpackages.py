packages = ["scipy", "statsmodels", "matplotlib"]

for pkg in packages:
    try:
        __import__(pkg)
        print(f"{pkg} is installed.")
    except ImportError:
        print(f"{pkg} is NOT installed. Install with: pip install {pkg}")