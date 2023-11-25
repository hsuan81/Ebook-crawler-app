// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
// use std::process::Command as StdCommand;
use tauri::api::process::{Command, CommandEvent};
use tauri::WindowEvent;
use tauri::Manager; // Needed for app.get_window()
use std::process::Child;
use std::sync::{Arc, Mutex};


// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
// #[tauri::command]
// fn greet(name: &str) -> String {
//     format!("Hello, {}! You've been greeted from Rust!", name)
// }

// struct BackgroundTask {
//     child: Arc<Mutex<Option<std::process::Child>>>,
// }

// impl BackgroundTask {
//     fn new() -> Self {
//         BackgroundTask {
//             child: Arc::new(Mutex::new(None)),
//         }
//     }
// }


#[tauri::command]
async fn py_get_epub(epub_path: String, child_arc: tauri::State<'_, Arc<Mutex<Option<Child>>>>) -> Result<String, String> {
    println!("Rust: Getting EPUB");
    // let app_data_directory = app_data_dir().expect("Failed to get app data directory");
    // println!("App data directory: {:?}", app_data_directory);
    let (mut rx, _child) = Command::new_sidecar("spider")
        .expect("Failed to create the command")   
        .args(["get", &epub_path])
        .spawn()
        .expect("Failed to spawn backend");


    // Store the child process in the state.
    // if let Ok(mut guard) = background_task.child.lock() {
    //     *guard = Some(_child);
    // } else {
    //     eprintln!("Failed to acquire lock on background task state");
    //     // Handle the error, e.g., by sending a message back to the frontend.
    // }
    
    let mut result = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            result = line.clone();
            // println!("Python: {}", line);
            // format!("Python: {}", line);
            // break; // As in the previous example, this only lets python send one line which may not be ideal
        }
    }
    
    Err::<String, _>("Something wrong with the getting process");
    Ok(result)
}

#[tauri::command]
async fn py_update_epub(epub_path: String, input_path: String, child_arc: tauri::State<'_, Arc<Mutex<Option<Child>>>>) -> Result<String, String> {
    println!("Rust: Updating EPUB");
    let (mut rx, _child) = Command::new_sidecar("spider")
        .expect("Failed to create the command")  
        .args(["update", &epub_path, &input_path])
        .spawn()
        .expect("Failed to spawn backend");

    // Store the child process in the state.
    // if let Ok(mut guard) = background_task.child.lock() {
    //     *guard = Some(_child);
    // } else {
    //     eprintln!("Failed to acquire lock on background task state");
    //     // Handle the error, e.g., by sending a message back to the frontend.
    // }
    
    let mut result = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            result = line.clone();            
        }
    }
    Err::<String, _>("Something wrong with the updaint process");
    Ok(result)
}

// fn main() {
//     tauri::Builder::default()
//         .invoke_handler(tauri::generate_handler![py_get_epub, py_update_epub])
//         .run(tauri::generate_context!())
//         .expect("error while running tauri application");
// }

fn main() {
    let child_arc = Arc::new(Mutex::new(None::<Child>)); // Arc to share the child process handle
    tauri::Builder::default()
        .manage(child_arc.clone()) // AAdd the Arc to the state so it can be accessed within the command
        .setup(move |app| {
            let window = app.get_window("main").unwrap();
            window.on_window_event(move |event| match event {
                WindowEvent::CloseRequested { api, .. } => {
                    // Handle the close event, e.g., kill the child process
                    // let background_task = app.state::<BackgroundTask>();
                    let mut child_guard = child_arc.lock().unwrap();
                    // if let Ok(mut guard) = background_task.child.lock() {
                    if let Some(child) = child_guard.as_mut() {
                            // Attempt to gracefully close the child process.
                            // Replace this with your own logic if needed.
                            // match child.kill() {
                            //     Ok(_) => println!("Sidecar process terminated successfully"),
                            //     Err(e) => eprintln!("Failed to terminate sidecar process: {:?}", e),
                            // }
                            child.kill().expect("Failed to kill the child process");
                        }
                        api.prevent_close(); // Prevent the window from closing immediately
                    // } else {
                    //     eprintln!("Failed to acquire lock on background task state");
                    //     // Handle the error, e.g., by emitting an event to the frontend.
                    }
                    // _ => {}
                    // api.prevent_close(); // Prevent the window from closing immediately.
            // }
                _ => {}
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![py_get_epub, py_update_epub])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}