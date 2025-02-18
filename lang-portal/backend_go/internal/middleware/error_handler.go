package middleware

import (
	"database/sql"
	"errors"
	"log"
	"net/http"
	"runtime/debug"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	apperrors "lang-portal/internal/errors"
)

// ErrorHandler middleware handles all errors in a consistent way
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Process request
		c.Next()

		// Error handling
		if len(c.Errors) > 0 {
			err := c.Errors.Last().Err
			handleError(c, err)
		}
	}
}

// handleError processes different types of errors and sends appropriate responses
func handleError(c *gin.Context, err error) {
	// Check if it's already an AppError
	if appErr, ok := apperrors.IsAppError(err); ok {
		// Log internal error if present
		if appErr.Internal != nil {
			log.Printf("Internal error: %v\nStack trace:\n%s", appErr.Internal, debug.Stack())
		}

		c.JSON(appErr.Code, gin.H{
			"error": gin.H{
				"type":    appErr.Type,
				"message": appErr.Message,
				"detail":  appErr.Detail,
				"data":    appErr.Data,
			},
		})
		return
	}

	// Handle specific error types
	switch {
	case errors.Is(err, sql.ErrNoRows):
		appErr := apperrors.NewNotFoundError(
			"Resource not found",
			"The requested resource could not be found",
		)
		c.JSON(appErr.Code, gin.H{"error": appErr})

	case errors.As(err, &validator.ValidationErrors{}):
		validationErrors := err.(validator.ValidationErrors)
		appErr := apperrors.NewValidationError(
			"Validation failed",
			"One or more fields failed validation",
			formatValidationErrors(validationErrors),
		)
		c.JSON(appErr.Code, gin.H{"error": appErr})

	default:
		// Log unexpected errors
		log.Printf("Unexpected error: %v\nStack trace:\n%s", err, debug.Stack())

		// Return a generic error message
		appErr := apperrors.NewInternalError(
			"An unexpected error occurred",
			err,
		)
		c.JSON(http.StatusInternalServerError, gin.H{"error": appErr})
	}
}

// formatValidationErrors converts validator.ValidationErrors to a more user-friendly format
func formatValidationErrors(errors validator.ValidationErrors) []map[string]string {
	var formattedErrors []map[string]string
	for _, err := range errors {
		formattedErrors = append(formattedErrors, map[string]string{
			"field":   err.Field(),
			"tag":     err.Tag(),
			"value":   err.Param(),
			"message": getValidationErrorMessage(err),
		})
	}
	return formattedErrors
}

// getValidationErrorMessage returns a user-friendly message for validation errors
func getValidationErrorMessage(err validator.FieldError) string {
	switch err.Tag() {
	case "required":
		return "This field is required"
	case "min":
		return "Value is below minimum length"
	case "max":
		return "Value exceeds maximum length"
	case "email":
		return "Invalid email format"
	default:
		return "Invalid value"
	}
}
