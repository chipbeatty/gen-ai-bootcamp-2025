package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
	"lang-portal/internal/service"
)

type StudyHandler struct {
	service *service.StudyService
}

func NewStudyHandler(service *service.StudyService) *StudyHandler {
	return &StudyHandler{service: service}
}

// CreateStudySession handles POST /api/study/sessions
func (h *StudyHandler) CreateStudySession(c *gin.Context) {
	var input struct {
		GroupID int `json:"group_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		_ = c.Error(errors.NewValidationError(
			"Invalid study session data",
			"The group ID is required",
			map[string]string{"group_id": "Group ID is required"},
		))
		return
	}

	session, err := h.service.CreateStudySession(input.GroupID)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to create study session", err))
		return
	}

	c.JSON(http.StatusCreated, session)
}

// AddWordReview handles POST /api/study/sessions/:id/reviews
func (h *StudyHandler) AddWordReview(c *gin.Context) {
	sessionID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid session ID",
			"The session ID must be a valid number",
			map[string]string{"id": c.Param("id")},
		))
		return
	}

	var input struct {
		WordID  int  `json:"word_id" binding:"required"`
		Correct bool `json:"correct" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		_ = c.Error(errors.NewValidationError(
			"Invalid word review data",
			"Both word ID and correct status are required",
			map[string]interface{}{
				"word_id": "Word ID is required",
				"correct": "Correct status is required",
			},
		))
		return
	}

	review, err := h.service.AddWordReview(sessionID, input.WordID, input.Correct)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to add word review", err))
		return
	}

	c.JSON(http.StatusCreated, review)
}

// GetSessionReviews handles GET /api/study/sessions/:id/reviews
func (h *StudyHandler) GetSessionReviews(c *gin.Context) {
	sessionID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid session ID",
			"The session ID must be a valid number",
			map[string]string{"id": c.Param("id")},
		))
		return
	}

	reviews, err := h.service.GetSessionReviews(sessionID)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch session reviews", err))
		return
	}

	if len(reviews) == 0 {
		_ = c.Error(errors.NewNotFoundError(
			"No reviews found",
			"The study session has no recorded reviews",
		))
		return
	}

	c.JSON(http.StatusOK, reviews)
}
