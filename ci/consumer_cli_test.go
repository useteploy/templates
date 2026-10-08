package template

// Copied into an immutable CLI fixture by catalog CI, never into a live checkout.
import (
	"context"
	"gopkg.in/yaml.v3"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"testing"

	"github.com/useteploy/teploy/internal/config"
)

func TestCatalogConnectionAndPersistenceConsumers(t *testing.T) {
	root := os.Getenv("TEMPLATES_REPO_DIR")
	if root == "" {
		t.Fatal("TEMPLATES_REPO_DIR is required")
	}
	server := httptest.NewServer(http.FileServer(http.Dir(root)))
	defer server.Close()
	registry := NewRegistry()
	registry.SetBaseURL(server.URL)
	for _, password := range []string{"secret#suffix", "slash/question?percent%invalid", "at@colon:quote'back\\slash", "generate", "auto", "$UNSET_CATALOG_FIXTURE", "secret:literal", "true", "line\nbreak"} {
		content, _, err := registry.Fetch(context.Background(), "lullmail", map[string]string{"domain": "mail.test", "db_password": password})
		if err != nil {
			t.Fatal(err)
		}
		app, err := config.ParseAppBytes([]byte(content))
		if err != nil {
			t.Fatal(err)
		}
		// The password is deliberately not URI userinfo; both processes consume
		// the same literal scalar independently of URL delimiter parsing.
		var values map[string]interface{}
		// Use YAML fields here so both env and the newer env_literal are checked
		// across CLI consumer versions without weakening scalar comparisons.
		if err := yaml.Unmarshal([]byte(content), &values); err != nil {
			t.Fatal(err)
		}
		env := catalogEnv(values)
		dsn, err := url.Parse(env["DATABASE_URL"].(string))
		if err != nil {
			t.Fatal(err)
		}
		if dsn.Host != "lullmail-db:5432" || dsn.User.Username() != "lull" || dsn.Fragment != "" {
			t.Fatal("DSN authority altered")
		}
		if _, has := dsn.User.Password(); has {
			t.Fatal("password embedded in URI")
		}
		db := values["accessories"].(map[string]interface{})["db"].(map[string]interface{})
		if env["PGPASSWORD"] != password || catalogEnv(db)["POSTGRES_PASSWORD"] != password {
			t.Fatal("password changed between consumers")
		}
		if app.App != "lullmail" {
			t.Fatal("wrong app parsed")
		}
	}
	content, _, err := registry.Fetch(context.Background(), "wordpress", map[string]string{"domain": "blog.test", "db_password": "hexfixture"})
	if err != nil {
		t.Fatal(err)
	}
	app, err := config.ParseAppBytes([]byte(content))
	if err != nil {
		t.Fatal(err)
	}
	if app.Volumes["wordpress"] != "/var/www/html" {
		t.Fatal("WordPress persistence missing")
	}
	if _, err := os.Stat(filepath.Join(root, "wordpress", "README.md")); err != nil {
		t.Fatal("migration instructions missing")
	}
}

func catalogEnv(values map[string]interface{}) map[string]interface{} {
	result := map[string]interface{}{}
	for _, field := range []string{"env", "env_literal"} {
		if values, ok := values[field].(map[string]interface{}); ok {
			for key, value := range values {
				result[key] = value
			}
		}
	}
	return result
}
