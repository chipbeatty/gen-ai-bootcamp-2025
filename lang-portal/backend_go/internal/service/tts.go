package service

import (
	texttospeech "cloud.google.com/go/texttospeech/apiv1"
	"cloud.google.com/go/texttospeech/apiv1/texttospeechpb"
	"context"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
)

type TTSService struct {
	client *texttospeech.Client
}

func NewTTSService() (*TTSService, error) {
	ctx := context.Background()
	client, err := texttospeech.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to create client: %v", err)
	}

	return &TTSService{client: client}, nil
}

func (s *TTSService) GeneratePronunciation(text string) (string, error) {
	ctx := context.Background()

	// Create the audio directory if it doesn't exist
	audioDir := "static/audio"
	if err := os.MkdirAll(audioDir, 0755); err != nil {
		return "", fmt.Errorf("failed to create audio directory: %v", err)
	}

	// Generate a filename based on the text
	filename := fmt.Sprintf("%s.mp3", text)
	audioPath := filepath.Join(audioDir, filename)

	// Check if the file already exists
	if _, err := os.Stat(audioPath); err == nil {
		return fmt.Sprintf("/audio/%s", filename), nil
	}

	// Configure the synthesis input
	req := &texttospeechpb.SynthesizeSpeechRequest{
		Input: &texttospeechpb.SynthesisInput{
			InputSource: &texttospeechpb.SynthesisInput_Text{Text: text},
		},
		Voice: &texttospeechpb.VoiceSelectionParams{
			LanguageCode: "fr-FR",
			Name:        "fr-FR-Neural2-A", // Using a neural voice for better quality
		},
		AudioConfig: &texttospeechpb.AudioConfig{
			AudioEncoding: texttospeechpb.AudioEncoding_MP3,
			SpeakingRate: 0.9, // Slightly slower for better pronunciation
			Pitch:        0,   // Normal pitch
		},
	}

	// Perform the text-to-speech request
	resp, err := s.client.SynthesizeSpeech(ctx, req)
	if err != nil {
		return "", fmt.Errorf("failed to synthesize speech: %v", err)
	}

	// Write the audio content to file
	if err := ioutil.WriteFile(audioPath, resp.AudioContent, 0644); err != nil {
		return "", fmt.Errorf("failed to write audio file: %v", err)
	}

	return fmt.Sprintf("/audio/%s", filename), nil
}

func (s *TTSService) Close() error {
	return s.client.Close()
}
