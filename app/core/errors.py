from fastapi import HTTPException

class AIProviderError(Exception):
    pass

class GenerationValidationError(Exception):
    pass

def provider_http_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=502, detail=f"AI provider error: {str(exc)[:300]}")
