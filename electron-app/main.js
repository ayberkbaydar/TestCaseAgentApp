const { app, BrowserWindow } = require("electron");
const { spawn, execSync } = require("child_process");
const path = require("path");
const os = require("os");

let python;

function killPortProcess(port) {
  try {
    if (os.platform()=="win32"){
      const stdout = execSync(`netstat -ano | findstr :${port}`).toString();
      const lines = stdout.split("\n").filter(line => line.trim() !== "");
      lines.forEach(line => {
        const pid = line.trim().split(/\s+/).pop();
        console.log(`Killing process on port ${port}: PID ${pid}`);
        execSync(`taskkill /PID ${pid} /F`);
    });
    }
    else if(os.platform()=="darwin" || os.platform()=="linux"){
      const stdout = execSync(`lsof -ti tcp:${port}`).toString();
      const pids = stdout.split("\n").filter(Boolean);
      pids.forEach((pid) => {
        console.log(`Killing process on port ${port}: PID ${pid}`);
        process.kill(pid, "SIGKILL");
    });
    }
  } catch (error) {
    console.log(`No processes found on port ${port}.`);
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true
    }
  });

  // win.webContents.openDevTools(); 
  win.loadURL("http://localhost:8501");
}

app.whenReady().then(() => {
  killPortProcess(8501);



// DEVELOPMENT ENV
  const streamlitScript = path.resolve(__dirname, "../streamlit_app/app.py");
  let python;
  if(os.platform()=="win32"){
    python = spawn("C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python310\\python.exe", [
    "-m", "streamlit", "run", streamlitScript,
    "--server.headless", "true",
    "--browser.serverAddress", "localhost",
    "--browser.gatherUsageStats", "false"
]);
  }
  else if(os.platform()=="darwin" || os.platform()=="linux"){
    python = spawn("/Users/ayberkbaydar/.pyenv/shims/python3", ["-m", "streamlit", "run", streamlitScript]);
  }
  





// //PRODUCTION ENV
//   const streamlitScript = path.join(process.resourcesPath, "streamlit_app/app.py");
//   let pythonBin;
//   let python;
//   if(os.platform()=="win32"){
//     pythonBin = path.join(process.resourcesPath, "myenv","python.exe");
//     python = spawn(pythonBin, ["-m", "streamlit", "run", streamlitScript,
//     "--server.headless", "true",
//     "--browser.serverAddress", "localhost",
//     "--browser.gatherUsageStats", "false"
//     ], {
//       cwd: path.join(process.resourcesPath, "streamlit_app"),
//       shell:true
//     });
//   }else if(os.platform()=="darwin" || os.platform()=="linux"){
//     pythonBin = path.join(process.resourcesPath, "myenv/bin/python3.12");
//     python = spawn(pythonBin, ["-m", "streamlit", "run", streamlitScript], {
//       cwd: path.join(process.resourcesPath, "streamlit_app")
//     });
//   }

  

  



  python.stdout.on("data", (data) => {
    console.log(`PYTHON: ${data}`);
  });

  python.stderr.on("data", (data) => {
    console.error(`PYTHON ERROR: ${data}`);
  });

  python.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
    app.quit();
  });

  setTimeout(() => {
    createWindow();
  }, 3000);
});

app.on("before-quit", () => {
  if (python) {
    console.log("Killing streamlit process...");
    python.kill("SIGKILL");
  }
  // Ek olarak 8501 portu hâlâ açık mı kontrol et ve temizle
  killPortProcess(8501);
});
