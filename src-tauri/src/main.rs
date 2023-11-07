// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use tauri::api::process::{Command, CommandEvent};


// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
// #[tauri::command]
// fn greet(name: &str) -> String {
//     format!("Hello, {}! You've been greeted from Rust!", name)
// }

#[tauri::command]
async fn py_get_epub(action: String, epub_path: String) -> String {
    println!("Rust: Getting EPUB");
    // let app_data_directory = app_data_dir().expect("Failed to get app data directory");
    // println!("App data directory: {:?}", app_data_directory);
    let (mut rx, _child) = Command::new_sidecar("spider")
        .expect("Failed to create the command")   
        .args(["get", &action, &epub_path])
        .spawn()
        .expect("Failed to spawn backend");
    
    let mut result = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            result = line.clone();
            // println!("Python: {}", line);
            // format!("Python: {}", line);
            // break; // As in the previous example, this only lets python send one line which may not be ideal
        }
    }

    result
}

#[tauri::command]
async fn py_update_epub(action: String, epub_path: String, input_path: String) -> String {
    println!("Rust: Updating EPUB");
    let (mut rx, _child) = Command::new_sidecar("spider")
        .expect("Failed to create the command")  
        .args(["update", &action, &epub_path, &input_path])
        .spawn()
        .expect("Failed to spawn backend");
    
    let mut result = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            result = line.clone();            
        }
    }
    result
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![py_get_epub, py_update_epub])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
