from .home import router as home_router
from .student import router as student_router
from .teacher import router as teacher_router

__all__ = [home_router, student_router, teacher_router]
