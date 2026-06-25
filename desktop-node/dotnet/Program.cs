// ACAP Desktop Node — native Windows launcher (ACAP.Node.exe).
//
// STANDALONE-SAFE: the launcher EMBEDS the Python node resources (acap_desktop.py,
// acap_wallet.py, acap_node_manager.py, acap_besu_wallet.py, acap_keccak.py,
// web/index.html, lab_config.example.json). If the companion files are not present
// next to the EXE, it extracts the embedded copies into the user data dir on first
// launch and runs from there — so a single, copied-alone ACAP.Node.exe works.
//
// It boots the stdlib-Python desktop node (acap_desktop.py) on 127.0.0.1 ONLY. It does
// NOT touch mainnet, holds no keys, exposes no public RPC. The single EXE still needs a
// Python 3 interpreter (the bundled embedded Python ships only in the full ZIP); if
// Python is missing it explains how to get it and exits.
//
// Build (cross-compiled on Linux with the .NET 8 SDK):
//   dotnet publish -c Release -r win-x64
//
using System.Diagnostics;
using System.Reflection;

const string DefaultPort = "8599";
const string ExtractVersion = "0.5.4-p2p-loopback-fix-preview";   // bump to force re-extract on update
const string ResPrefix = "acapres/";                  // embedded-resource logical-name prefix

string baseDir = AppContext.BaseDirectory;

// Resolve the runtime dir that holds acap_desktop.py: companion next to the EXE if
// present, else the extracted copy in the user data dir (extracted here if missing/stale).
string? runtimeDir = ResolveRuntimeDir(baseDir, out string resolveNote);
if (runtimeDir is null)
{
    Console.Error.WriteLine(
        "ERROR: could not locate or extract the ACAP node files.\n" + resolveNote);
    Pause();
    return 2;
}
string script = Path.Combine(runtimeDir, "acap_desktop.py");
Console.WriteLine($"Node files: {resolveNote}");

// Find a Python interpreter. Order: BUNDLED runtime next to the EXE (full ZIP only),
// then py launcher, python, python3.
var (pyExe, pyPrefix, pySource) = FindPython(baseDir);
if (pyExe is null)
{
    Console.WriteLine("ACAP Desktop Node — private preview (devnet/testnet only).");
    Console.WriteLine();
    Console.WriteLine("No Python runtime was found. The node logic runs on Python 3 (stdlib only).");
    Console.WriteLine("This single EXE does not embed a Python interpreter. Two options:");
    Console.WriteLine("  1) Install Python 3 from https://www.python.org/downloads/");
    Console.WriteLine("     (tick \"Add python.exe to PATH\" on the first installer screen), then re-run; OR");
    Console.WriteLine("  2) Download the full ZIP package — it bundles an embedded Python (no install needed).");
    Pause();
    return 3;
}
Console.WriteLine($"Python runtime: {pySource}.");

// Build the argument list: [py-prefix...] script [passthrough args]. Default --port if none given.
var psi = new ProcessStartInfo { FileName = pyExe, UseShellExecute = false, WorkingDirectory = runtimeDir };
foreach (var p in pyPrefix) psi.ArgumentList.Add(p);
psi.ArgumentList.Add(script);

bool hasPort = args.Any(a => a == "--port");
foreach (var a in args) psi.ArgumentList.Add(a);
if (!hasPort) { psi.ArgumentList.Add("--port"); psi.ArgumentList.Add(DefaultPort); }

Console.WriteLine("ACAP Desktop Node — private preview (devnet/testnet only, no mainnet, no rewards).");
Console.WriteLine($"Launching local node UI on http://127.0.0.1:{(hasPort ? "<port>" : DefaultPort)}/ (loopback only).");
Console.WriteLine("Close this window or press Ctrl+C to stop the node.");
Console.WriteLine();

try
{
    using var proc = Process.Start(psi);
    if (proc is null) { Console.Error.WriteLine("ERROR: failed to start Python."); Pause(); return 4; }
    proc.WaitForExit();
    return proc.ExitCode;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"ERROR: could not launch the node: {ex.Message}");
    Pause();
    return 5;
}

// ---- helpers ----

// Returns the dir containing acap_desktop.py (companion or extracted), or null on failure.
static string? ResolveRuntimeDir(string baseDir, out string note)
{
    // 1) Companion files next to the EXE (or one level down) — the unpacked-ZIP case.
    string a = Path.Combine(baseDir, "acap_desktop.py");
    if (File.Exists(a)) { note = "companion (next to EXE)"; return baseDir; }
    string sub = Path.Combine(baseDir, "active-capacity-node-windows");
    if (File.Exists(Path.Combine(sub, "acap_desktop.py"))) { note = "companion (unpacked subfolder)"; return sub; }

    // 2/3) Extracted copy in the user data dir — extract embedded resources if missing/stale.
    string rt = UserRuntimeDir();
    try
    {
        Directory.CreateDirectory(rt);
        string stamp = Path.Combine(rt, ".extract_version");
        bool fresh = File.Exists(Path.Combine(rt, "acap_desktop.py"))
                     && File.Exists(stamp) && File.ReadAllText(stamp).Trim() == ExtractVersion;
        if (!fresh)
        {
            int n = ExtractEmbedded(rt);
            if (n == 0) { note = "no embedded node resources found in this EXE."; return null; }
            File.WriteAllText(stamp, ExtractVersion);
            note = $"extracted {n} embedded file(s) to {rt}";
        }
        else
        {
            note = $"extracted runtime ({rt})";
        }
        return File.Exists(Path.Combine(rt, "acap_desktop.py")) ? rt : null;
    }
    catch (Exception ex)
    {
        note = $"extraction failed: {ex.Message}";
        return null;
    }
}

static string UserRuntimeDir()
{
    string baseDir;
    if (OperatingSystem.IsWindows())
    {
        string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        baseDir = string.IsNullOrEmpty(appData)
            ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "AppData", "Roaming")
            : appData;
        return Path.Combine(baseDir, "ACAP-Desktop-Node", "runtime");
    }
    string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
    return Path.Combine(home, ".acap-desktop-node", "runtime");
}

// Writes every embedded "acapres/..." resource under destDir, preserving subpaths. Returns count.
static int ExtractEmbedded(string destDir)
{
    var asm = Assembly.GetExecutingAssembly();
    int count = 0;
    foreach (string name in asm.GetManifestResourceNames())
    {
        if (!name.StartsWith(ResPrefix, StringComparison.Ordinal)) continue;
        string rel = name.Substring(ResPrefix.Length).Replace('\\', '/');
        string outPath = Path.Combine(destDir, rel.Replace('/', Path.DirectorySeparatorChar));
        Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
        using Stream? s = asm.GetManifestResourceStream(name);
        if (s is null) continue;
        using var fs = File.Create(outPath);
        s.CopyTo(fs);
        count++;
    }
    return count;
}

static (string? exe, string[] prefix, string source) FindPython(string baseDir)
{
    // 1) Prefer the bundled embedded runtime (full ZIP only) — no system Python required.
    string bundled = Path.Combine(baseDir, "runtime", "python", "python.exe");
    if (File.Exists(bundled) && CanRun(bundled, "--version"))
        return (bundled, Array.Empty<string>(), "bundled (runtime/python/python.exe)");
    // 2) Fall back to a system interpreter: "py -3", then python / python3 on PATH.
    if (CanRun("py", "-3 --version")) return ("py", new[] { "-3" }, "system (py -3)");
    if (CanRun("python", "--version")) return ("python", Array.Empty<string>(), "system (python)");
    if (CanRun("python3", "--version")) return ("python3", Array.Empty<string>(), "system (python3)");
    return (null, Array.Empty<string>(), "none");
}

static bool CanRun(string exe, string args)
{
    try
    {
        var psi = new ProcessStartInfo
        {
            FileName = exe,
            Arguments = args,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        using var p = Process.Start(psi);
        if (p is null) return false;
        p.WaitForExit(5000);
        return p.HasExited && p.ExitCode == 0;
    }
    catch { return false; }
}

static void Pause()
{
    Console.WriteLine();
    Console.Write("Press Enter to close...");
    try { Console.ReadLine(); } catch { /* no console */ }
}
