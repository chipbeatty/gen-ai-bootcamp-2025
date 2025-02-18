package middleware

import (
	"log"
	"runtime/debug"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
)

// Recovery middleware handles panics and converts them to errors
func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				// Log the stack trace
				log.Printf("Panic recovered: %v\nStack trace:\n%s", err, debug.Stack())

				// Create an internal server error
				appErr := errors.NewInternalError(
					"An unexpected error occurred",
					nil,
				)

				// Add the error to the context
				_ = c.Error(appErr)

				// Stop the request chain
				c.Abort()
			}
		}()

		c.Next()
	}
}
