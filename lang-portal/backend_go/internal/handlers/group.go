package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
	"lang-portal/internal/service"
)

type GroupHandler struct {
	service *service.GroupService
}

func NewGroupHandler(service *service.GroupService) *GroupHandler {
	return &GroupHandler{service: service}
}

// GetGroups handles GET /api/groups
func (h *GroupHandler) GetGroups(c *gin.Context) {
	groups, err := h.service.GetGroups()
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch groups", err))
		return
	}
	c.JSON(http.StatusOK, groups)
}

// GetGroupByID handles GET /api/groups/:id
func (h *GroupHandler) GetGroupByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid group ID",
			"The group ID must be a valid number",
			map[string]string{"id": c.Param("id")},
		))
		return
	}

	group, err := h.service.GetGroupByID(id)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch group", err))
		return
	}
	if group == nil {
		_ = c.Error(errors.NewNotFoundError(
			"Group not found",
			"The requested group does not exist",
		))
		return
	}
	c.JSON(http.StatusOK, group)
}

// CreateGroup handles POST /api/groups
func (h *GroupHandler) CreateGroup(c *gin.Context) {
	var input struct {
		Name string `json:"name" binding:"required,min=1,max=100"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		_ = c.Error(errors.NewValidationError(
			"Invalid group data",
			"The provided group data is invalid",
			map[string]string{"name": "Name is required and must be between 1 and 100 characters"},
		))
		return
	}

	group, err := h.service.CreateGroup(input.Name)
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to create group", err))
		return
	}

	c.JSON(http.StatusCreated, group)
}

// AddWordToGroup handles POST /api/groups/:id/words
func (h *GroupHandler) AddWordToGroup(c *gin.Context) {
	groupID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid group ID",
			"The group ID must be a valid number",
			map[string]string{"id": c.Param("id")},
		))
		return
	}

	var input struct {
		WordID int `json:"word_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		_ = c.Error(errors.NewValidationError(
			"Invalid word data",
			"The word ID is required",
			map[string]string{"word_id": "Word ID is required"},
		))
		return
	}

	if err := h.service.AddWordToGroup(input.WordID, groupID); err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to add word to group", err))
		return
	}

	c.Status(http.StatusNoContent)
}

// RemoveWordFromGroup handles DELETE /api/groups/:groupId/words/:wordId
func (h *GroupHandler) RemoveWordFromGroup(c *gin.Context) {
	groupID, err := strconv.Atoi(c.Param("groupId"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid group ID",
			"The group ID must be a valid number",
			map[string]string{"groupId": c.Param("groupId")},
		))
		return
	}

	wordID, err := strconv.Atoi(c.Param("wordId"))
	if err != nil {
		_ = c.Error(errors.NewInvalidInputError(
			"Invalid word ID",
			"The word ID must be a valid number",
			map[string]string{"wordId": c.Param("wordId")},
		))
		return
	}

	if err := h.service.RemoveWordFromGroup(wordID, groupID); err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to remove word from group", err))
		return
	}

	c.Status(http.StatusNoContent)
}
