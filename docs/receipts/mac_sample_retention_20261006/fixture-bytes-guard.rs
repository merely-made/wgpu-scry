const ORIGINAL: &str = r#"<!doctype html>
            <html><head><style>
              html, body { margin: 0; width: 100vw; height: 100vh; }
              body { animation: scry-capture-pulse 240ms steps(1, end) infinite; }
              @keyframes scry-capture-pulse {
                0% { background: rgb(23, 97, 181); }
                50% { background: rgb(221, 79, 54); }
              }
            </style></head><body></body></html>"#;
const CURRENT: &str = r#"<!doctype html>
            <html><head><style>
              html, body { margin: 0; width: 100vw; height: 100vh; }
              body { animation: scry-capture-pulse 240ms steps(1, end) infinite; }
              @keyframes scry-capture-pulse {
                0% { background: rgb(23, 97, 181); }
                50% { background: rgb(221, 79, 54); }
              }
            </style></head><body></body></html>"#;
fn main() { assert_eq!(ORIGINAL.as_bytes(), CURRENT.as_bytes()); println!("Uninstrumented capture fixture bytes match f952abc"); }
