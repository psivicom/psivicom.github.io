// wendy-go/cmd/fix-zulu/main.go
// SPDX-License-Identifier: EUPL-1.2
// SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

package main

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

var (
	patterns = []*regexp.Regexp{
		regexp.MustCompile(`(?i)\*Last updated:\s*(.*?)\*`),
		regexp.MustCompile(`(?i)created:\s*([^\n]+)`),
		regexp.MustCompile(`(?i)updated:\s*([^\n]+)`),
		regexp.MustCompile(`(?i)date:\s*([^\n]+)`),
	}
	zuluFormatRegex = regexp.MustCompile(`^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`)
)

func main() {
	root := "."
	if len(os.Args) > 1 {
		root = os.Args[1]
	}

	fixedCount := 0

	filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if d.IsDir() {
			// Skip hidden directories like .git and node_modules
			if strings.HasPrefix(d.Name(), ".") && path != "." {
				return filepath.SkipDir
			}
			return nil
		}

		ext := strings.ToLower(filepath.Ext(path))
		isMd := ext == ".md"
		// Only process CSVs if they are inside the 'data' directory
		isCsv := ext == ".csv" && strings.HasPrefix(filepath.ToSlash(path), "data/")

		if !isMd && !isCsv {
			return nil
		}

		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}

		original := string(content)
		modified := original

		for _, re := range patterns {
			modified = re.ReplaceAllStringFunc(modified, func(match string) string {
				submatches := re.FindStringSubmatch(match)
				if len(submatches) < 2 {
					return match
				}
				
				raw := strings.TrimSpace(submatches[1])
				raw = strings.Trim(raw, "\"'")

				// If it's already perfectly formatted, skip it
				if zuluFormatRegex.MatchString(raw) {
					return match
				}

				// Parse the timestamp
				t, err := parseTime(raw)
				if err != nil {
					return match // Can't parse, leave it alone
				}

				// Convert to UTC and format to .sssZ
				t = t.UTC()
				ms := t.Nanosecond() / 1000000
				newTime := fmt.Sprintf("%d-%02d-%02dT%02d:%02d:%02d.%03dZ",
					t.Year(), t.Month(), t.Day(),
					t.Hour(), t.Minute(), t.Second(), ms)

				return strings.Replace(match, raw, newTime, 1)
			})
		}

		if modified != original {
			os.WriteFile(path, []byte(modified), 0644)
			fmt.Printf("⚡ Fixed %s\n", path)
			fixedCount++
		}
		return nil
	})

	fmt.Printf("✅ Sweep complete. Normalized %d files.\n", fixedCount)
}

// parseTime attempts to parse a string using common standard layouts.
// This replaces Python's dateutil with zero external dependencies.
func parseTime(s string) (time.Time, error) {
	layouts := []string{
		time.RFC3339,
		"2006-01-02T15:04:05Z",
		"2006-01-02T15:04:05",
		"2006-01-02 15:04:05",
		"2006-01-02",
		"01/02/2006",
		"Jan 2, 2006",
		"January 2, 2006",
		"02 Jan 2006",
		time.RFC1123,
		time.RFC822,
	}
	for _, layout := range layouts {
		if t, err := time.Parse(layout, s); err == nil {
			return t, nil
		}
	}
	return time.Time{}, fmt.Errorf("cannot parse timestamp")
}
