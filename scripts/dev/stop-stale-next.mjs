import { execFileSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, "../..");
const normalizedNextRoot = `${repositoryRoot.replaceAll("\\", "/").toLowerCase()}/node_modules/next/dist/`;

function isRepositoryNextProcess(commandLine = "") {
  const normalized = commandLine.replaceAll("\\", "/").toLowerCase();
  if (!normalized.includes(normalizedNextRoot)) return false;

  return normalized.includes("/bin/next") || normalized.includes("/server/lib/start-server.js");
}

function listWindowsProcesses() {
  const query = [
    "$ErrorActionPreference = 'Stop';",
    "Get-CimInstance Win32_Process |",
    "  Select-Object ProcessId, ParentProcessId, Name, CommandLine |",
    "  ConvertTo-Json -Compress",
  ].join(" ");
  const output = execFileSync(
    "powershell.exe",
    ["-NoProfile", "-NonInteractive", "-Command", query],
    { encoding: "utf8", windowsHide: true },
  ).trim();

  if (!output) return [];
  const parsed = JSON.parse(output);
  const rows = Array.isArray(parsed) ? parsed : [parsed];
  return rows.map((row) => ({
    pid: Number(row.ProcessId),
    parentPid: Number(row.ParentProcessId),
    commandLine: row.CommandLine ?? "",
  }));
}

function listUnixProcesses() {
  const output = execFileSync("ps", ["-axo", "pid=,ppid=,command="], { encoding: "utf8" });
  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const match = line.match(/^(\d+)\s+(\d+)\s+(.*)$/);
      return match
        ? { pid: Number(match[1]), parentPid: Number(match[2]), commandLine: match[3] }
        : null;
    })
    .filter(Boolean);
}

function stopWindowsProcessTrees(processes) {
  const matchedIds = new Set(processes.map(({ pid }) => pid));
  const roots = processes.filter(({ parentPid }) => !matchedIds.has(parentPid));

  for (const { pid } of roots) {
    try {
      execFileSync("taskkill.exe", ["/PID", String(pid), "/T", "/F"], {
        stdio: "ignore",
        windowsHide: true,
      });
    } catch {
      // A process may finish naturally between discovery and termination.
    }
  }
}

function stopUnixProcesses(processes) {
  for (const { pid } of [...processes].sort((a, b) => b.pid - a.pid)) {
    try {
      process.kill(pid, "SIGTERM");
    } catch {
      // A process may finish naturally between discovery and termination.
    }
  }
}

let allProcesses;
try {
  allProcesses = process.platform === "win32" ? listWindowsProcesses() : listUnixProcesses();
} catch (error) {
  console.error(`[dev] Could not inspect stale Next.js processes: ${error.message}`);
  process.exitCode = 1;
  process.exit();
}

const staleProcesses = allProcesses.filter(
  ({ pid, commandLine }) => pid !== process.pid && isRepositoryNextProcess(commandLine),
);

if (staleProcesses.length === 0) {
  console.log("[dev] No stale Breeze Next.js server found.");
  process.exit();
}

if (process.platform === "win32") {
  stopWindowsProcessTrees(staleProcesses);
} else {
  stopUnixProcesses(staleProcesses);
}

console.log(
  `[dev] Stopped stale Breeze Next.js server process${staleProcesses.length === 1 ? "" : "es"}: ${staleProcesses
    .map(({ pid }) => pid)
    .join(", ")}`,
);
