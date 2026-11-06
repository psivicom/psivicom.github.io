use std::fs;
use std::path::Path;
use tracing::info;

pub struct GeminiDaemon {
    capsule_path: String,
}

impl GeminiDaemon {
    pub fn new(capsule_path: String) -> Self {
        fs::create_dir_all(&capsule_path).expect("Failed to create capsule directory");
        Self { capsule_path }
    }

    pub async fn write_axiom(&mut self, uri: &str, content: &str) {
        // Extract filename from URI (e.g., gemini://wendy/capsule/learned.gmi -> learned.gmi)
        let filename = uri.split('/').last().unwrap_or("unknown.gmi");
        let path = Path::new(&self.capsule_path).join(filename);
        
        fs::write(&path, content).expect("Failed to write .gmi file");
        info!(target: "gemini_daemon", "committed axiom to disk | file={} | bytes={}", path.display(), content.len());
    }
}
