try:
    print("Importing domain...")
    from app.models import domain
    print("Importing schemas...")
    from app.models import schemas
    print("Importing auth...")
    from app.api.endpoints import auth
    print("Importing internships...")
    from app.api.endpoints import internships
    print("Importing resume...")
    from app.api.endpoints import resume
    print("Importing matching...")
    from app.api.endpoints import matching
    print("Importing cover_letter...")
    from app.api.endpoints import cover_letter
    print("All imports successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
