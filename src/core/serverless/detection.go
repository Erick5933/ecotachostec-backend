package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

// DetectionRequest estructura de solicitud de detección
type DetectionRequest struct {
	TachoID        string    `json:"tacho_id"`
	ImageURL       string    `json:"image_url"`
	Classification string    `json:"classification"`
	Confidence     float32   `json:"confidence"`
	Timestamp      time.Time `json:"timestamp"`
	UserID         string    `json:"user_id,omitempty"`
	LocationLat    float64   `json:"location_lat,omitempty"`
	LocationLon    float64   `json:"location_lon,omitempty"`
}

// DetectionResponse respuesta de la función
type DetectionResponse struct {
	Success   bool        `json:"success"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
	Error     string      `json:"error,omitempty"`
}

// BackendConfig configuración para conectar con el backend
type BackendConfig struct {
	URL      string
	Timeout  time.Duration
	RetryMax int
}

// ProcessDetectionWithBackend procesa una detección y la registra en el backend
func ProcessDetectionWithBackend(request *DetectionRequest, backendCfg *BackendConfig) (*DetectionResponse, error) {
	fmt.Printf("🔍 Procesando detección para tacho %s (confianza: %.2f)\n", request.TachoID, request.Confidence)

	// Validar entrada
	if request.TachoID == "" {
		return &DetectionResponse{
			Success: false,
			Error:   "tacho_id es requerido",
		}, fmt.Errorf("tacho_id vacío")
	}

	if request.Classification == "" {
		return &DetectionResponse{
			Success: false,
			Error:   "classification es requerida",
		}, fmt.Errorf("classification vacía")
	}

	// Mapeo de clasificaciones
	categoryMap := map[string]string{
		"organico":    "organico",
		"organic":     "organico",
		"inorganico":  "inorganico",
		"inorganic":   "inorganico",
		"reciclable":  "reciclable",
		"recyclable":  "reciclable",
	}

	classification := request.Classification
	if mapped, exists := categoryMap[classification]; exists {
		classification = mapped
	}

	// Registrar en backend
	endpoint := fmt.Sprintf("%s/api/detecciones/", backendCfg.URL)

	payload := map[string]interface{}{
		"tacho_id":       request.TachoID,
		"clasificacion":  classification,
		"confianza":      request.Confidence * 100, // Convertir a porcentaje
		"timestamp":      request.Timestamp,
		"usuario_id":     request.UserID,
		"latitud":        request.LocationLat,
		"longitud":       request.LocationLon,
		"imagen_url":     request.ImageURL,
	}

	payloadBytes, _ := json.Marshal(payload)

	// Intentar con reintentos
	var resp *http.Response
	var err error

	for attempt := 1; attempt <= backendCfg.RetryMax; attempt++ {
		client := &http.Client{Timeout: backendCfg.Timeout}

		resp, err = client.Post(
			endpoint,
			"application/json",
			bytes.NewBuffer(payloadBytes),
		)

		if err == nil && resp.StatusCode == http.StatusCreated {
			fmt.Printf("✅ Detección registrada en backend (intento %d)\n", attempt)
			break
		}

		if attempt < backendCfg.RetryMax {
			fmt.Printf("⏳ Reintentando registro en backend... (intento %d/%d)\n", attempt, backendCfg.RetryMax)
			time.Sleep(2 * time.Second)
		}
	}

	if err != nil {
		fmt.Printf("⚠️  No se pudo registrar en backend: %v\n", err)
		// Continuar de todas formas - guardar localmente
	} else if resp != nil {
		defer resp.Body.Close()
	}

	// Respuesta exitosa
	result := map[string]interface{}{
		"tacho_id":       request.TachoID,
		"classification": classification,
		"confidence":     request.Confidence,
		"processed_at":   time.Now(),
		"status":         "processed",
		"registered":     err == nil,
	}

	return &DetectionResponse{
		Success: true,
		Message: "Detección procesada exitosamente",
		Data:    result,
	}, nil
}

// HTTP Handler para detecciones
func HandleDetection(backendCfg *BackendConfig) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			json.NewEncoder(w).Encode(DetectionResponse{
				Success: false,
				Error:   "Solo POST es permitido",
			})
			return
		}

		// Parsear request
		body, _ := io.ReadAll(r.Body)
		defer r.Body.Close()

		var req DetectionRequest
		if err := json.Unmarshal(body, &req); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(DetectionResponse{
				Success: false,
				Error:   fmt.Sprintf("JSON inválido: %v", err),
			})
			return
		}

		// Si no tiene timestamp, usar hora actual
		if req.Timestamp.IsZero() {
			req.Timestamp = time.Now()
		}

		// Procesar
		resp, err := ProcessDetectionWithBackend(&req, backendCfg)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Printf("Error procesando detección: %v\n", err)
		} else {
			w.WriteHeader(http.StatusOK)
		}

		json.NewEncoder(w).Encode(resp)
	}
}

// Health check endpoint
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "healthy",
		"service": "ecotachos-serverless-detection",
		"time":    time.Now(),
		"version": "1.0",
	})
}

// Stats endpoint
var stats = struct {
	TotalRequests   int64
	SuccessfulCount int64
	FailedCount     int64
	StartTime       time.Time
}{
	StartTime: time.Now(),
}

func HandleStats(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	uptime := time.Since(stats.StartTime)
	successRate := 0.0
	if stats.TotalRequests > 0 {
		successRate = float64(stats.SuccessfulCount) / float64(stats.TotalRequests) * 100
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"total_requests":   stats.TotalRequests,
		"successful":       stats.SuccessfulCount,
		"failed":           stats.FailedCount,
		"success_rate":     fmt.Sprintf("%.2f%%", successRate),
		"uptime_seconds":   uptime.Seconds(),
		"start_time":       stats.StartTime,
	})
}

// Info endpoint
func HandleInfo(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"service":       "ECOTACHOS Serverless Detection Function",
		"version":       "1.0",
		"description":   "Función serverless para procesar detecciones de IA de clasificación de residuos",
		"endpoints":     []string{"/detect", "/health", "/stats", "/info"},
		"backend_url":   os.Getenv("BACKEND_URL"),
		"port":          os.Getenv("PORT"),
		"environment":   os.Getenv("ENVIRONMENT"),
	})
}

func main() {
	// Configuración
	port := os.Getenv("PORT")
	if port == "" {
		port = "9000"
	}

	backendURL := os.Getenv("BACKEND_URL")
	if backendURL == "" {
		backendURL = "http://localhost:8000"
	}

	backendCfg := &BackendConfig{
		URL:      backendURL,
		Timeout:  10 * time.Second,
		RetryMax: 3,
	}

	fmt.Println("🚀 Iniciando Serverless Detection Function")
	fmt.Printf("   Puerto: %s\n", port)
	fmt.Printf("   Backend: %s\n", backendURL)

	// Rutas
	http.HandleFunc("/detect", HandleDetection(backendCfg))
	http.HandleFunc("/health", HandleHealth)
	http.HandleFunc("/stats", HandleStats)
	http.HandleFunc("/info", HandleInfo)
	http.HandleFunc("/", HandleInfo)

	// Iniciar servidor
	server := &http.Server{
		Addr:         fmt.Sprintf(":%s", port),
		Handler:      http.DefaultServeMux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	fmt.Printf("✅ Servidor escuchando en http://localhost:%s\n", port)
	fmt.Println("\n📋 Endpoints disponibles:")
	fmt.Println("   POST   /detect  - Procesar detección de residuos")
	fmt.Println("   GET    /health  - Health check")
	fmt.Println("   GET    /stats   - Estadísticas de la función")
	fmt.Println("   GET    /info    - Información del servicio")

	if err := server.ListenAndServe(); err != nil {
		fmt.Printf("❌ Error en servidor: %v\n", err)
		os.Exit(1)
	}
}
