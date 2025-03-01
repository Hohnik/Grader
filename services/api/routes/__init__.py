from .root import router as root_router
from .student import router as student_router
from .teacher import router as teacher_router

__all__ = ["student_router", "teacher_router", "root_router"]
