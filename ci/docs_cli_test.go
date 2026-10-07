package cli

// Copied into the checked-out CLI package by templates CI. Execute uses the
// real Cobra command tree, but replaces every handler/hook before parsing:
// this test must never connect to a host, fetch an image or change live state.

import (
	"encoding/json"
	"io"
	"os"
	"testing"

	"github.com/spf13/cobra"
	"github.com/useteploy/teploy/internal/config"
)

func TestCatalogDocumentationAdmission(t *testing.T) {
	path := os.Getenv("TEMPLATES_DOC_FIXTURES")
	if path == "" {
		t.Fatal("TEMPLATES_DOC_FIXTURES is required")
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var fixtures struct {
		Cases []struct {
			Source  string   `json:"source"`
			Args    []string `json:"args"`
			Ingress string   `json:"ingress"`
		} `json:"cases"`
		BackupManifest string `json:"backup_manifest"`
	}
	if err := json.Unmarshal(data, &fixtures); err != nil {
		t.Fatal(err)
	}
	if len(fixtures.Cases) == 0 {
		t.Fatal("no documentation examples")
	}
	for _, fixture := range fixtures.Cases {
		t.Run(fixture.Source, func(t *testing.T) {
			root := NewRootCmd("docs-test")
			root.SetOut(io.Discard)
			root.SetErr(io.Discard)
			called := false
			var disableEffects func(*cobra.Command)
			disableEffects = func(cmd *cobra.Command) {
				cmd.PersistentPreRun = nil
				cmd.PersistentPreRunE = nil
				cmd.PreRun = nil
				cmd.PreRunE = nil
				cmd.PostRun = nil
				cmd.PostRunE = nil
				cmd.PersistentPostRun = nil
				cmd.PersistentPostRunE = nil
				if cmd.Run != nil || cmd.RunE != nil {
					cmd.Run = nil
					cmd.RunE = func(cmd *cobra.Command, args []string) error {
						called = true
						if cmd.CommandPath() == "teploy template install" {
							domain, _ := cmd.Flags().GetString("domain")
							server, _ := cmd.Flags().GetString("server")
							port, _ := cmd.Flags().GetInt("port")
							if server == "" {
								t.Fatal("install example requires --server")
							}
							cfg := &config.AppConfig{Ingress: fixture.Ingress, Port: 11434}
							return applyTemplateOverrides(cfg, domain, server, port)
						}
						return nil
					}
				}
				for _, child := range cmd.Commands() {
					disableEffects(child)
				}
			}
			disableEffects(root)
			root.SetArgs(fixture.Args)
			if err := root.Execute(); err != nil {
				t.Fatalf("documented command rejected: %v", err)
			}
			if !called {
				t.Fatal("example did not resolve to an executable command")
			}
		})
	}
	t.Run("backup-only-manifest", func(t *testing.T) {
		cfg, err := config.ParseAppBytes([]byte(fixtures.BackupManifest))
		if err != nil {
			t.Fatal(err)
		}
		if cfg.App != "ghost" || cfg.Server != "my-server" || cfg.Accessories["db"].Image != "mysql:8" {
			t.Fatalf("unexpected backup-only example: %#v", cfg)
		}
	})
}
