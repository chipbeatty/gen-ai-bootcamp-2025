package middleware

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
)

// ValidatePagination validates pagination parameters
func ValidatePagination() gin.HandlerFunc {
	return func(c *gin.Context) {
		page := c.DefaultQuery("page", "1")
		itemsPerPage := c.DefaultQuery("items_per_page", "100")

		// Validate page
		pageNum, err := strconv.Atoi(page)
		if err != nil || pageNum < 1 {
			_ = c.Error(errors.NewInvalidInputError(
				"Invalid page number",
				"Page number must be a positive integer",
				map[string]string{"page": page},
			))
			c.Abort()
			return
		}

		// Validate items per page
		itemsNum, err := strconv.Atoi(itemsPerPage)
		if err != nil || itemsNum < 1 || itemsNum > 100 {
			_ = c.Error(errors.NewInvalidInputError(
				"Invalid items per page",
				"Items per page must be between 1 and 100",
				map[string]string{"items_per_page": itemsPerPage},
			))
			c.Abort()
			return
		}

		c.Next()
	}
}

// ValidateID validates ID parameters
func ValidateID(paramName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		id := c.Param(paramName)
		if id == "" {
			_ = c.Error(errors.NewInvalidInputError(
				"Missing ID parameter",
				"The ID parameter is required",
				map[string]string{paramName: "missing"},
			))
			c.Abort()
			return
		}

		idNum, err := strconv.Atoi(id)
		if err != nil || idNum < 1 {
			_ = c.Error(errors.NewInvalidInputError(
				"Invalid ID",
				"ID must be a positive integer",
				map[string]string{paramName: id},
			))
			c.Abort()
			return
		}

		c.Next()
	}
}

// ValidateContentType ensures the request has the correct content type
func ValidateContentType(contentType string) gin.HandlerFunc {
	return func(c *gin.Context) {
		if c.Request.Method == http.MethodPost || c.Request.Method == http.MethodPut {
			if ct := c.GetHeader("Content-Type"); ct != contentType {
				_ = c.Error(errors.NewInvalidInputError(
					"Invalid Content-Type",
					"Request must include correct Content-Type header",
					map[string]string{
						"expected": contentType,
						"received": ct,
					},
				))
				c.Abort()
				return
			}
		}
		c.Next()
	}
}
