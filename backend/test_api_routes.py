"""Test script to verify API routes are registered"""

from app.main import app

def test_routes():
    """Print all registered routes"""
    print("Registered API Routes:")
    print("=" * 80)
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"{methods:15} {route.path}")
    
    print("=" * 80)
    print(f"Total routes: {len(app.routes)}")

if __name__ == "__main__":
    test_routes()
