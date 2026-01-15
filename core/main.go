package main

import (
    "encoding/csv"
    "encoding/json"
    "flag"
    "fmt"
    "io"
    "os"
    "sync"
)

// --- THIS MUST BE HERE (OUTSIDE main) ---
type Config struct {
    Nmap struct {
        ScanProfiles map[string]struct {
            Flags string `json:"flags"`
        } `json:"scan_profiles"`
    } `json:"nmap"`
    Ffuf struct {
        Profiles map[string]struct {
            Threads    int     `json:"threads"`
            Delay      float64 `json:"delay"`
            Extensions string  `json:"extensions"`
        } `json:"profiles"`
    } `json:"ffuf"`
}

func main() {
    // Your flags...
    registryPath := flag.String("registry", "", "Path to targets.csv")
    // Fix the default path to be relative to the PROJECT ROOT
    configPath := flag.String("config", "config/profiles.json", "Path to profiles.json")
    wordlistPath := flag.String("wordlist", "", "Path to wordlist")
    fuzzEnabled := flag.Bool("fuzz", false, "Execute Phase 6 Enumeration")
    flag.Parse()

    if *registryPath == "" {
        fmt.Println("[!] Error: --registry path is required.")
        os.Exit(1)
    }

    // LOUD ERROR HANDLING: Config
    cfgFile, err := os.ReadFile(*configPath)
    if err != nil {
        fmt.Printf("[!] Critical: Could not read config at %s: %v\n", *configPath, err)
        os.Exit(1)
    }

    var cfg Config
    if err := json.Unmarshal(cfgFile, &cfg); err != nil {
        fmt.Printf("[!] Critical: JSON Malformed in %s: %v\n", *configPath, err)
        os.Exit(1)
    }

    // LOUD ERROR HANDLING: Registry
    file, err := os.Open(*registryPath)
    if err != nil {
        fmt.Printf("[!] Critical: Could not open registry at %s: %v\n", *registryPath, err)
        os.Exit(1)
    }
    defer file.Close()
	reader := csv.NewReader(file)
	reader.Read() // Skip Header

	// --- CONCURRENCY CONTROL ---
	// Limit to 5 concurrent target scans to prevent network saturation
	semaphore := make(chan struct{}, 5) 
	var wg sync.WaitGroup

	for {
		record, err := reader.Read()
		if err == io.EOF { break }
		if err != nil { continue }

		targetID := record[0]
		targetIP := record[2]

		wg.Add(1)
		go func(id string, ip string) {
			defer wg.Done()
			semaphore <- struct{}{}        // Acquire slot
			defer func() { <-semaphore }() // Release slot

			if !*fuzzEnabled {
				// --- PHASES 2, 4, 5 ---
                RunRecon(ip, id, cfg.Nmap.ScanProfiles["aggressive"].Flags, *registryPath)
			} else {
				// --- PHASE 6 ---
				if *wordlistPath != "" {
					profile := cfg.Ffuf.Profiles["stealth"]
					RunEnumeration(ip, *wordlistPath, "stealth", profile.Extensions, profile.Threads, profile.Delay)
				}
			}
		}(targetID, targetIP)
	}

	wg.Wait()
	fmt.Println("\n[+] All targets in registry processed.")
}