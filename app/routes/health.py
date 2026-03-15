from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Social Post System API"
    }


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Social Post System API",
        "version": "1.0.0",
        "documentation": "/docs"
    }
