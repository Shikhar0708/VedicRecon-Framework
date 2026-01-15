package main

import (
	"bufio"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// RunEnumeration handles Phase 6: Directory & Endpoint Fuzzing
func RunEnumeration(target string, wordlist string, profileName string, extensions string, threads int, delay float64) {
	fmt.Printf("\n--- [ PHASE 6: ENUMERATION | PROFILE: %s ] ---\n", profileName)
	fmt.Printf("[*] Target: %s | Threads: %d | Delay: %.2fs\n", target, threads, delay)

	file, err := os.Open(wordlist)
	if err != nil {
		fmt.Printf("[!] Wordlist Error: %v\n", err)
		return
	}
	defer file.Close()

	var wg sync.WaitGroup
	// Semaphore to limit concurrent requests
	sem := make(chan struct{}, threads)
	scanner := bufio.NewScanner(file)

	// Industrial Grade: Custom HTTP Client with Timeout
	// Prevents goroutines from hanging forever on slow responses
	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	sleepDuration := time.Duration(delay * 1000) * time.Millisecond
	
	count := 0
	startTime := time.Now()

	for scanner.Scan() {
		path := scanner.Text()
		path = strings.TrimSpace(path)
		if path == "" || strings.HasPrefix(path, "#") {
			continue
		}

		// THE CRITICAL FIX: Acquire slot BEFORE spawning goroutine
		// This prevents creating 50,000 idle goroutines in memory
		sem <- struct{}{}
		
		count++
		if count%100 == 0 {
			fmt.Printf("\r[*] Progress: %d requests processed...", count)
		}

		wg.Add(1)
		go func(p string) {
			defer wg.Done()
			defer func() { <-sem }() // Release slot when done

			if sleepDuration > 0 {
				time.Sleep(sleepDuration)
			}

			// Construct URL (Protocol detector could be added here)
			url := fmt.Sprintf("http://%s/%s", target, p)
			
			resp, err := client.Get(url)
			if err != nil {
				// Silent fail on network errors to keep terminal clean
				return
			}
			defer resp.Body.Close()

			// Deterministic Classification
			// 200 = Success, 301/302 = Redirect, 401/403 = Forbidden (Still interesting)
			if resp.StatusCode != 404 {
				// Clear the progress line before printing a hit
				fmt.Printf("\r[+] Phase 6 Hit: %d | %s\n", resp.StatusCode, url)
			}
		}(path)
	}

	wg.Wait()
	duration := time.Since(startTime)
	fmt.Printf("\r[+] Phase 6 Complete. %d requests in %v.\n", count, duration)
}