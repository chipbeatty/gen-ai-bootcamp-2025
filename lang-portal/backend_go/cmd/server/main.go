package main

import (
	"database/sql"
	"log"

	"lang-portal/internal/handlers"
	"lang-portal/internal/middleware"
	"lang-portal/internal/service"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

func main() {
	// Initialize database
	db, err := sql.Open("sqlite3", "words.db")
	if err != nil {
		log.Fatal("Failed to open database:", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatal("Failed to ping database:", err)
	}

	// Initialize services
	studyService := service.NewStudyService(db)
	wordService := service.NewWordService(db)
	groupService := service.NewGroupService(db)

	// Initialize handlers
	dashboardHandler := handlers.NewDashboardHandler(studyService)
	wordHandler := handlers.NewWordHandler(wordService)
	groupHandler := handlers.NewGroupHandler(groupService)
	studyHandler := handlers.NewStudyHandler(studyService)

	// Initialize Gin
	r := gin.New()

	// Global middleware
	r.Use(middleware.Recovery())
	r.Use(middleware.Logger())
	r.Use(middleware.CORS())
	r.Use(middleware.ErrorHandler())

	// API routes will be grouped under /api
	api := r.Group("/api")

	// Dashboard routes
	api.GET("/dashboard/last_study_session", dashboardHandler.GetLastStudySession)
	api.GET("/dashboard/study_progress", dashboardHandler.GetStudyProgress)
	api.GET("/dashboard/quick-stats", dashboardHandler.GetQuickStats)

	// Words routes - with pagination validation
	api.GET("/words", middleware.ValidatePagination(), wordHandler.GetWords)
	api.GET("/words/:id", middleware.ValidateID("id"), wordHandler.GetWordByID)

	// Groups routes - with validation
	api.GET("/groups", groupHandler.GetGroups)
	api.GET("/groups/:id", middleware.ValidateID("id"), groupHandler.GetGroupByID)
	api.POST("/groups",
		middleware.ValidateContentType("application/json"),
		groupHandler.CreateGroup,
	)
	api.POST("/groups/:id/words",
		middleware.ValidateID("id"),
		middleware.ValidateContentType("application/json"),
		groupHandler.AddWordToGroup,
	)
	api.DELETE("/groups/:groupId/words/:wordId",
		middleware.ValidateID("groupId"),
		middleware.ValidateID("wordId"),
		groupHandler.RemoveWordFromGroup,
	)

	// Study routes - with validation
	api.POST("/study/sessions",
		middleware.ValidateContentType("application/json"),
		studyHandler.CreateStudySession,
	)
	api.POST("/study/sessions/:id/reviews",
		middleware.ValidateID("id"),
		middleware.ValidateContentType("application/json"),
		studyHandler.AddWordReview,
	)
	api.GET("/study/sessions/:id/reviews",
		middleware.ValidateID("id"),
		studyHandler.GetSessionReviews,
	)

	// Start the server
	if err := r.Run(":8081"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
