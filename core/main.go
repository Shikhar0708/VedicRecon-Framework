package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"
	"sync"
)

// --- CONFIG STRUCT ---
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

const (
	IDX_TARGET_ID     = 0
	IDX_INPUT_VALUE   = 2
	IDX_ASSIGNED_PORT = 10
)

func main() {

	// ---------------- FLAGS ----------------
	registryPath := flag.String("registry", "", "Path to targets.csv (required)")
	configPath := flag.String("config", "config/profiles.json", "Path to profiles.json")
	wordlistPath := flag.String("wordlist", "", "Path to wordlist (Phase 6)")
	fuzzEnabled := flag.Bool("fuzz", false, "Execute Phase 6 enumeration")
	globalPort := flag.String("port", "", "Scan a single port only (diagnostic override)")
	flag.Parse()

	if *registryPath == "" {
		fmt.Println("[!] Error: --registry is required")
		os.Exit(1)
	}

	// ---------------- LOAD CONFIG ----------------
	cfgFile, err := os.ReadFile(*configPath)
	if err != nil {
		fmt.Printf("[!] Could not read config: %v\n", err)
		os.Exit(1)
	}

	var cfg Config
	if err := json.Unmarshal(cfgFile, &cfg); err != nil {
		fmt.Printf("[!] Invalid config JSON: %v\n", err)
		os.Exit(1)
	}

	// ---------------- OPEN REGISTRY ----------------
	file, err := os.Open(*registryPath)
	if err != nil {
		fmt.Printf("[!] Could not open registry: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Read() // skip header

	// ---------------- BUILD IP → PORT SET ----------------
	type Target struct {
		ID    string
		IP    string
		Ports map[string]bool
	}

	targets := make(map[string]*Target)

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil || len(record) < 3 {
			continue
		}

		id := record[IDX_TARGET_ID]
		ip := record[IDX_INPUT_VALUE]

		if _, exists := targets[ip]; !exists {
			targets[ip] = &Target{
				ID:    id,
				IP:    ip,
				Ports: make(map[string]bool),
			}
		}

		if len(record) > IDX_ASSIGNED_PORT {
			port := strings.TrimSpace(record[IDX_ASSIGNED_PORT])
			if port != "" {
				targets[ip].Ports[port] = true
			}
		}
	}

	// ---------------- CONCURRENCY ----------------
	semaphore := make(chan struct{}, 5)
	var wg sync.WaitGroup

	// ---------------- SCAN EACH IP ONCE ----------------
	for _, t := range targets {
		wg.Add(1)

		go func(target *Target) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			// ---------------- PORT RESOLUTION ----------------
			effectivePort := ""

			if *globalPort != "" {
				effectivePort = *globalPort
			} else if len(target.Ports) > 0 {
				var ports []string
				for p := range target.Ports {
					ports = append(ports, p)
				}
				effectivePort = strings.Join(ports, ",")
			}

			// ---------------- PROFILE SELECTION (FIX) ----------------
			scanProfile := "framework_aggressive"
			if effectivePort != "" {
				scanProfile = "framework_diagnostic"
			}

			fmt.Printf(
				"[*] Scanning %s | Profile=%s | Ports=%s\n",
				target.IP,
				scanProfile,
				func() string {
					if effectivePort == "" {
						return "FULL"
					}
					return effectivePort
				}(),
			)

			if !*fuzzEnabled {
				RunRecon(
					target.IP,
					target.ID,
					cfg.Nmap.ScanProfiles[scanProfile].Flags,
					*registryPath,
					effectivePort,
				)
			} else if *wordlistPath != "" {
				profile := cfg.Ffuf.Profiles["stealth"]
				RunEnumeration(
					target.IP,
					*wordlistPath,
					"stealth",
					profile.Extensions,
					profile.Threads,
					profile.Delay,
				)
			}

		}(t)
	}

	wg.Wait()
	fmt.Println("\n[+] All targets processed exactly once.")
}
