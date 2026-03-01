package com.tailspintoys.exception;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.util.Map;

/**
 * Global exception handler for REST controllers.
 * Translates framework exceptions into API-friendly error responses.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Handles type mismatch for path variables (e.g. /api/games/invalid-id).
     * Returns 400 Bad Request with a descriptive error message.
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<Map<String, String>> handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
        String message = String.format("Invalid value '%s' for parameter '%s'", ex.getValue(), ex.getName());
        return ResponseEntity.badRequest().body(Map.of("error", message));
    }
}
