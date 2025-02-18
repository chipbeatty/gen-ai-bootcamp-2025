package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"lang-portal/internal/errors"
	"lang-portal/internal/service"
)

type DashboardHandler struct {
	studyService *service.StudyService
}

func NewDashboardHandler(studyService *service.StudyService) *DashboardHandler {
	return &DashboardHandler{studyService: studyService}
}

// GetLastStudySession handles the /api/dashboard/last_study_session endpoint
func (h *DashboardHandler) GetLastStudySession(c *gin.Context) {
	session, err := h.studyService.GetLastStudySession()
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch last study session", err))
		return
	}
	if session == nil {
		_ = c.Error(errors.NewNotFoundError(
			"No study sessions found",
			"There are no recorded study sessions in the system",
		))
		return
	}
	c.JSON(http.StatusOK, session)
}

// GetStudyProgress handles the /api/dashboard/study_progress endpoint
func (h *DashboardHandler) GetStudyProgress(c *gin.Context) {
	progress, err := h.studyService.GetStudyProgress()
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch study progress", err))
		return
	}

	// Add additional context if no progress is found
	if progress.TotalWordsStudied == 0 && progress.TotalAvailableWords == 0 {
		_ = c.Error(errors.NewNotFoundError(
			"No study progress found",
			"There is no recorded study progress in the system",
		))
		return
	}

	c.JSON(http.StatusOK, progress)
}

// GetQuickStats handles the /api/dashboard/quick-stats endpoint
func (h *DashboardHandler) GetQuickStats(c *gin.Context) {
	stats, err := h.studyService.GetQuickStats()
	if err != nil {
		_ = c.Error(errors.NewDatabaseError("Failed to fetch quick stats", err))
		return
	}

	// Add additional context if no stats are found
	if stats.TotalStudySessions == 0 {
		_ = c.Error(errors.NewNotFoundError(
			"No statistics available",
			"There are no recorded study sessions to generate statistics",
		))
		return
	}

	c.JSON(http.StatusOK, stats)
}
