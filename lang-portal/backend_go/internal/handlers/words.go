package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
	"lang-portal/internal/service"
)

type WordHandler struct {
	service *service.WordService
}

func NewWordHandler(service *service.WordService) *WordHandler {
	return &WordHandler{service: service}
}

// GetWords handles the /api/words endpoint
func (h *WordHandler) GetWords(c *gin.Context) {
	// Parse and validate pagination parameters
	page, err := strconv.Atoi(c.DefaultQuery("page", "1"))
	if err != nil || page < 1 {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid page number",
			"Page number must be a positive integer",
			map[string]string{"page": c.Query("page")},
		))
		return
	}

	itemsPerPage, err := strconv.Atoi(c.DefaultQuery("items_per_page", "100"))
	if err != nil || itemsPerPage < 1 || itemsPerPage > 100 {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid items per page",
			"Items per page must be between 1 and 100",
			map[string]string{"items_per_page": c.Query("items_per_page")},
		))
		return
	}

	words, err := h.service.GetWords(page, itemsPerPage)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch words", err))
		return
	}

	// Check if there are any words in the result
	if len(words.Items) == 0 && words.TotalItems > 0 && page > 1 {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid page number",
			"The requested page number exceeds the total number of pages",
			map[string]interface{}{
				"page":        page,
				"total_pages": words.TotalPages,
			},
		))
		return
	}

	c.JSON(http.StatusOK, words)
}

// GetWordByID handles the /api/words/:id endpoint
func (h *WordHandler) GetWordByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid word ID",
			"The word ID must be a valid number",
			map[string]string{"id": c.Param("id")},
		))
		return
	}

	word, err := h.service.GetWordByID(id)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch word", err))
		return
	}
	if word == nil {
		_ = c.Error(errors.NewNotFoundError(
			"Word not found",
			"The requested word does not exist",
		))
		return
	}

	c.JSON(http.StatusOK, word)
}
