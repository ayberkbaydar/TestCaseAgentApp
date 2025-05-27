const { app, BrowserWindow } = require("electron");
const { spawn, execSync } = require("child_process");
const path = require("path");

let python;

function killPortProcess(port) {
  try {
    // macOS ve Linux için lsof ile portu kullanan PID'leri bul
    const stdout = execSync(`lsof -ti tcp:${port}`).toString();
    const pids = stdout.split("\n").filter(Boolean);
    pids.forEach((pid) => {
      console.log(`Killing process on port ${port}: PID ${pid}`);
      process.kill(pid, "SIGKILL");
    });
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
  // 🔴 Electron başlamadan önce 8501 portunu meşgul eden süreçleri öldür
  killPortProcess(8501);



// DEVELOPMENT ENV
//   const streamlitScript = path.resolve(__dirname, "../streamlit_app/app.py");
//   ✅ Streamlit'i tam Python yoluyla başlat
//   python = spawn("/Users/ayberkbaydar/.pyenv/shims/python3", ["-m", "streamlit", "run", streamlitScript]);


//PRODUCTION ENV
  const pythonBin = path.join(process.resourcesPath, "myenv/bin/python3.12");

  const streamlitScript = path.join(process.resourcesPath, "streamlit_app/app.py");

  const python = spawn(pythonBin, ["-m", "streamlit", "run", streamlitScript], {
    // cwd: process.resourcesPath
    cwd: path.join(process.resourcesPath, "streamlit_app")
});



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

  // Streamlit'in hazır olmasını bekleyip pencereyi aç
  setTimeout(() => {
    createWindow();
  }, 3000);
});

// 🔴 Uygulama kapatılırken streamlit sürecini öldür
app.on("before-quit", () => {
  if (python) {
    console.log("Killing streamlit process...");
    python.kill("SIGKILL");
  }
  // Ek olarak 8501 portu hâlâ açık mı kontrol et ve temizle
  killPortProcess(8501);
});
