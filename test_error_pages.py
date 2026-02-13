"""
Test views for error pages - Add these temporarily to main/urls.py to test error pages
"""
from django.shortcuts import render

def test_404(request):
    """Test 404 error page"""
    return render(request, '404.html', status=404)

def test_403(request):
    """Test 403 error page"""
    return render(request, '403.html', status=403)

def test_400(request):
    """Test 400 error page"""
    return render(request, '400.html', status=400)

def test_500(request):
    """Test 500 error page"""
    return render(request, '500.html', status=500)

# Add these to main/urls.py for testing:
# path('test-404/', test_404, name='test_404'),
# path('test-403/', test_403, name='test_403'),
# path('test-400/', test_400, name='test_400'),
# path('test-500/', test_500, name='test_500'),
