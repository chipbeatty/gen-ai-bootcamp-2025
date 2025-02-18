package errors

import (
	"fmt"
	"net/http"
)

// AppError represents an application error with additional context
type AppError struct {
	Code       int         `json:"-"`          // HTTP status code
	Message    string      `json:"message"`    // User-facing error message
	Detail     string      `json:"detail"`     // Detailed error message
	Type       string      `json:"type"`       // Error type for categorization
	Data       interface{} `json:"data"`       // Additional error data
	Internal   error       `json:"-"`          // Internal error (not exposed to user)
}

// Error implements the error interface
func (e *AppError) Error() string {
	if e.Internal != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Internal)
	}
	return e.Message
}

// Common error types
const (
	TypeNotFound          = "NOT_FOUND"
	TypeValidation        = "VALIDATION_ERROR"
	TypeDatabase          = "DATABASE_ERROR"
	TypeInternal         = "INTERNAL_ERROR"
	TypeInvalidInput     = "INVALID_INPUT"
	TypeUnauthorized     = "UNAUTHORIZED"
	TypeForbidden        = "FORBIDDEN"
)

// NewNotFoundError creates a new not found error
func NewNotFoundError(message string, detail string) *AppError {
	return &AppError{
		Code:    http.StatusNotFound,
		Message: message,
		Detail:  detail,
		Type:    TypeNotFound,
	}
}

// NewValidationError creates a new validation error
func NewValidationError(message string, detail string, data interface{}) *AppError {
	return &AppError{
		Code:    http.StatusBadRequest,
		Message: message,
		Detail:  detail,
		Type:    TypeValidation,
		Data:    data,
	}
}

// NewDatabaseError creates a new database error
func NewDatabaseError(message string, err error) *AppError {
	return &AppError{
		Code:     http.StatusInternalServerError,
		Message:  "Database operation failed",
		Detail:   message,
		Type:     TypeDatabase,
		Internal: err,
	}
}

// NewInternalError creates a new internal server error
func NewInternalError(message string, err error) *AppError {
	return &AppError{
		Code:     http.StatusInternalServerError,
		Message:  message,
		Detail:   "An internal server error occurred",
		Type:     TypeInternal,
		Internal: err,
	}
}

// NewInvalidInputError creates a new invalid input error
func NewInvalidInputError(message string, detail string, data interface{}) *AppError {
	return &AppError{
		Code:    http.StatusBadRequest,
		Message: message,
		Detail:  detail,
		Type:    TypeInvalidInput,
		Data:    data,
	}
}

// IsAppError checks if an error is an AppError
func IsAppError(err error) (*AppError, bool) {
	appErr, ok := err.(*AppError)
	return appErr, ok
}
