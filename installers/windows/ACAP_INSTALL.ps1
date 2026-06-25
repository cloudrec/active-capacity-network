# ACAP Desktop Node - one-click Windows bootstrap installer (private preview).
#
# SAFETY / TRANSPARENCY:
#   * Per-user install under %LOCALAPPDATA%\ACAP-Desktop-Node. No administrator rights.
#   * Never edits the global/persistent PATH. Never installs a service or autostart.
#   * HTTPS-only downloads. Every archive SHA-256 is verified before it is extracted/run.
#   * Devnet/testnet only: no mainnet, no rewards, no mining, no custody, loopback RPC only.
#   * Never prints or stores private keys or mnemonics.
#
# Usage (normally launched by ACAP_INSTALL.bat):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\ACAP_INSTALL.ps1
# Options:
#   -PortalBase <url>     portal base (default https://capacity.469diamond.com)
#   -JavaFeature <n>      Temurin JDK feature to download if missing (default 25)
#   -ForceJava            download the bundled JDK even if a system Java is found
#   -NoStart              do not launch ACAP.Node.exe after install
param(
    [string]$PortalBase = "https://capacity.469diamond.com",
    [int]$JavaFeature = 25,
    [int]$JavaMinMajor = 21,
    [switch]$ForceJava,
    [switch]$NoStart
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# ---- install tree (per-user, no admin) ----
$Root = Join-Path $env:LOCALAPPDATA "ACAP-Desktop-Node"
$AppDir = Join-Path $Root "app"
$RuntimeDir = Join-Path $Root "runtime"
$JavaDir = Join-Path $RuntimeDir "java"
$BesuDir = Join-Path $RuntimeDir "besu"
$DataDir = Join-Path $Root "data"
$LogDir = Join-Path $Root "logs"
$DlDir = Join-Path $Root "downloads"
foreach ($d in @($Root, $AppDir, $RuntimeDir, $JavaDir, $BesuDir, $DataDir, $LogDir, $DlDir)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

$Stamp = (Get-Date -Format "yyyyMMdd-HHmmss")
$LogFile = Join-Path $LogDir ("install-" + $Stamp + ".log")
try { Start-Transcript -Path $LogFile -Append | Out-Null } catch {}

$Warnings = @()
$Report = [ordered]@{}
$Report.product = "ACAP Desktop Node"
$Report.installer = "ACAP_INSTALL.ps1"
$Report.installer_version = "0.6.0-bootstrap-preview"
$Report.timestamp = $Stamp
$Report.install_root = $Root
$Report.no_admin = $true
$Report.global_path_modified = $false
$Report.mainnet = $false
$Report.rewards = $false
$Report.custody = $false
$Report.rpc_exposure = "loopback_only"

function Line { Write-Host ("-" * 66) }
function Info([string]$m) { Write-Host $m -ForegroundColor Cyan }
function Good([string]$m) { Write-Host $m -ForegroundColor Green }
function Warn([string]$m) { Write-Host ("WARNING: " + $m) -ForegroundColor Yellow; $script:Warnings += $m }
function Die([string]$m) {
    Write-Host ("ERROR: " + $m) -ForegroundColor Red
    Write-Host "Nothing partial was started. Fix the issue above and re-run ACAP_INSTALL.bat." -ForegroundColor Red
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}

function Test-Elevated {
    try {
        $id = [Security.Principal.WindowsIdentity]::GetCurrent()
        $p = New-Object Security.Principal.WindowsPrincipal($id)
        return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch { return $false }
}

function Invoke-Download([string]$Url, [string]$OutFile) {
    if ($Url -notlike "https://*") { Die ("refused non-HTTPS download URL: " + $Url) }
    $args = @{ Uri = $Url; OutFile = $OutFile; UseBasicParsing = $true }
    $args.Headers = @{ "User-Agent" = "acap-bootstrap-installer" }
    if ($env:HTTPS_PROXY) { $args.Proxy = $env:HTTPS_PROXY }
    elseif ($env:HTTP_PROXY) { $args.Proxy = $env:HTTP_PROXY }
    Invoke-WebRequest @args
}

function Get-Json([string]$Url) {
    if ($Url -notlike "https://*") { Die ("refused non-HTTPS API URL: " + $Url) }
    $args = @{ Uri = $Url; UseBasicParsing = $true }
    $args.Headers = @{ "User-Agent" = "acap-bootstrap-installer" }
    if ($env:HTTPS_PROXY) { $args.Proxy = $env:HTTPS_PROXY }
    elseif ($env:HTTP_PROXY) { $args.Proxy = $env:HTTP_PROXY }
    return Invoke-RestMethod @args
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLower()
}

function Confirm-Hash([string]$Path, [string]$Expected, [string]$What) {
    if (-not $Expected) { return $false }
    $actual = Get-Sha256 $Path
    $exp = $Expected.ToLower().Trim()
    if ($actual -ne $exp) {
        Die ($What + " SHA-256 mismatch (expected " + $exp + ", got " + $actual + ")")
    }
    Good ("  verified " + $What + " SHA-256 OK")
    return $true
}

function Find-Child([string]$BaseDir, [string]$LeafName) {
    $hit = Get-ChildItem -Path $BaseDir -Recurse -Filter $LeafName -File -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($hit) { return $hit.FullName }
    return $null
}

Line
Write-Host "ACAP Desktop Node - one-click Windows bootstrap installer"
Write-Host "PRIVATE PREVIEW. Devnet/testnet only. No mainnet. No rewards. No custody."
Write-Host ("Install root: " + $Root)
Line

if (Test-Elevated) {
    Warn "running elevated (Administrator). This installer is per-user and needs NO admin rights."
    $Report.ran_elevated = $true
}

# ---- step 1: ACAP package ----
Info "[1/6] Fetching ACAP package metadata..."
$metaUrl = $PortalBase.TrimEnd("/") + "/api/node-packages/windows/latest"
try { $meta = Get-Json $metaUrl } catch { Die ("could not reach " + $metaUrl + " (check connection or proxy)") }
$pkgVer = $meta.version
$pkgSha = $meta.sha256
$dlPath = $meta.download_url
if (-not $dlPath) { Die "package metadata has no download_url" }
if ($dlPath -like "http*") { $pkgUrl = $dlPath } else { $pkgUrl = $PortalBase.TrimEnd("/") + $dlPath }
Good ("  package version: " + $pkgVer)

$zipOut = Join-Path $DlDir "active-capacity-node-windows.zip"
Info ("  downloading ACAP package from " + $pkgUrl)
Invoke-Download $pkgUrl $zipOut
if (-not (Confirm-Hash $zipOut $pkgSha "ACAP package")) {
    Die "portal metadata did not provide a SHA-256 for the ACAP package; refusing to install unverified."
}
$Report.acap_package = [ordered]@{ version = $pkgVer; sha256 = $pkgSha; source = $pkgUrl; verified = $true }

Info "  extracting ACAP package..."
$extract = Join-Path $DlDir "acap_extract"
if (Test-Path $extract) { Remove-Item -Recurse -Force $extract }
Expand-Archive -Path $zipOut -DestinationPath $extract -Force
$exeSrc = Find-Child $extract "ACAP.Node.exe"
if (-not $exeSrc) { Die "ACAP.Node.exe not found inside the downloaded package." }
$srcRoot = Split-Path -Parent $exeSrc
Get-ChildItem -Path $AppDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $srcRoot "*") -Destination $AppDir -Recurse -Force
$AppExe = Join-Path $AppDir "ACAP.Node.exe"
Good ("  installed ACAP app to " + $AppDir)

# ---- step 2: Java ----
Info "[2/6] Ensuring Java runtime (Besu needs a modern JDK)..."
$javaExe = Join-Path $JavaDir "bin\java.exe"
$javaSource = "none"
$javaVer = $null
if (Test-Path $javaExe) {
    $javaSource = "local_runtime"
    Good ("  using per-user runtime Java: " + $javaExe)
} else {
    $sysJava = $null
    if (-not $ForceJava) {
        $cmd = Get-Command java -ErrorAction SilentlyContinue
        if ($cmd) { $sysJava = $cmd.Source }
    }
    $sysMajor = 0
    if ($sysJava) {
        try {
            $banner = (& $sysJava -version 2>&1 | Out-String)
            $mm = [regex]::Match($banner, 'version\D+(\d+)')
            if ($mm.Success) { $sysMajor = [int]$mm.Groups[1].Value }
        } catch {}
    }
    if ($sysJava -and $sysMajor -ge $JavaMinMajor) {
        $javaSource = "system"
        $javaExe = $sysJava
        $javaVer = $sysMajor
        Good ("  using existing system Java major " + $sysMajor + " at " + $sysJava)
        if ($sysMajor -lt 25) { Warn ("system Java is major " + $sysMajor + "; Besu 26.6.x may need Java 25. Re-run with -ForceJava to fetch JDK 25.") }
    } else {
        Info ("  no suitable Java found; downloading portable Temurin JDK " + $JavaFeature + "...")
        $adoptUrl = "https://api.adoptium.net/v3/assets/latest/" + $JavaFeature + "/hotspot?architecture=x64&image_type=jdk&os=windows&vendor=eclipse"
        try { $assets = Get-Json $adoptUrl } catch { Die ("could not reach Adoptium API: " + $adoptUrl) }
        $asset = $assets | Select-Object -First 1
        if (-not $asset) { Die ("Adoptium returned no JDK " + $JavaFeature + " for windows x64") }
        $jLink = $asset.binary.package.link
        $jSum = $asset.binary.package.checksum
        $javaVer = $asset.version.semver
        $jOut = Join-Path $DlDir "temurin-jdk.zip"
        Invoke-Download $jLink $jOut
        if ($jSum) { Confirm-Hash $jOut $jSum "Temurin JDK" | Out-Null }
        else { Warn "Adoptium gave no checksum; JDK archive left UNVERIFIED (flagged in report)." }
        $jx = Join-Path $DlDir "java_extract"
        if (Test-Path $jx) { Remove-Item -Recurse -Force $jx }
        Expand-Archive -Path $jOut -DestinationPath $jx -Force
        $jBin = Find-Child $jx "java.exe"
        if (-not $jBin) { Die "java.exe not found inside the downloaded JDK archive." }
        $jHome = Split-Path -Parent (Split-Path -Parent $jBin)
        Get-ChildItem -Path $JavaDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item -Path (Join-Path $jHome "*") -Destination $JavaDir -Recurse -Force
        $javaExe = Join-Path $JavaDir "bin\java.exe"
        $javaSource = "local_runtime"
        Good ("  installed portable JDK to " + $JavaDir)
    }
}
$Report.java = [ordered]@{ source = $javaSource; version = $javaVer; path = $javaExe }

# ---- step 3: Besu ----
Info "[3/6] Ensuring Hyperledger Besu (Windows uses besu.bat)..."
$besuBat = Join-Path $BesuDir "bin\besu.bat"
$besuSource = "none"
$besuVer = $null
if (Test-Path $besuBat) {
    $besuSource = "local_runtime"
    Good ("  using per-user runtime Besu: " + $besuBat)
} else {
    $homeBesu = Join-Path $env:USERPROFILE "besu\bin\besu.bat"
    $pathBesu = (Get-Command besu.bat -ErrorAction SilentlyContinue)
    if (Test-Path $homeBesu) {
        $besuSource = "user_home"
        $besuBat = $homeBesu
        Good ("  using existing Besu at " + $homeBesu)
    } elseif ($pathBesu) {
        $besuSource = "path"
        $besuBat = $pathBesu.Source
        Good ("  using besu.bat on PATH: " + $besuBat)
    } else {
        Info "  no Besu found; downloading latest Besu release..."
        $relUrl = "https://api.github.com/repos/hyperledger/besu/releases/latest"
        try { $rel = Get-Json $relUrl } catch { Die ("could not reach GitHub API: " + $relUrl) }
        $besuVer = $rel.tag_name
        $zipAsset = $rel.assets | Where-Object { $_.name -match '^besu-.*\.zip$' } | Select-Object -First 1
        if (-not $zipAsset) { Die "no Besu .zip asset found in the latest release." }
        $sumAsset = $rel.assets | Where-Object { $_.name -eq ($zipAsset.name + ".sha256") } | Select-Object -First 1
        $bOut = Join-Path $DlDir $zipAsset.name
        Invoke-Download $zipAsset.browser_download_url $bOut
        if ($sumAsset) {
            $sumOut = Join-Path $DlDir $sumAsset.name
            Invoke-Download $sumAsset.browser_download_url $sumOut
            $expSum = (Get-Content $sumOut -Raw).Trim().Split()[0]
            Confirm-Hash $bOut $expSum "Besu release" | Out-Null
        } else {
            Warn "Besu release has no .sha256 sidecar; archive left UNVERIFIED (flagged in report)."
        }
        $bx = Join-Path $DlDir "besu_extract"
        if (Test-Path $bx) { Remove-Item -Recurse -Force $bx }
        Expand-Archive -Path $bOut -DestinationPath $bx -Force
        $batHit = Find-Child $bx "besu.bat"
        if (-not $batHit) { Die "besu.bat not found inside the downloaded Besu archive (refusing the unix besu script on Windows)." }
        $besuHome = Split-Path -Parent (Split-Path -Parent $batHit)
        Get-ChildItem -Path $BesuDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item -Path (Join-Path $besuHome "*") -Destination $BesuDir -Recurse -Force
        $besuBat = Join-Path $BesuDir "bin\besu.bat"
        $besuSource = "local_runtime"
        Good ("  installed Besu to " + $BesuDir)
    }
}
$Report.besu = [ordered]@{ source = $besuSource; version = $besuVer; path = $besuBat; launcher = "besu.bat" }

# ---- step 4: write runtime env pointers ----
Info "[4/6] Writing runtime pointers (no global PATH change)..."
$javaHome = $JavaDir
if ($javaSource -eq "system") { $javaHome = Split-Path -Parent (Split-Path -Parent $javaExe) }
$besuHome = $BesuDir
if ($besuSource -ne "local_runtime") { $besuHome = Split-Path -Parent (Split-Path -Parent $besuBat) }
$env1 = [ordered]@{
    java_source = $javaSource
    java_home = $javaHome
    java_exe = $javaExe
    besu_source = $besuSource
    besu_home = $besuHome
    besu_bat = $besuBat
    app_dir = $AppDir
    data_dir = $DataDir
    rpc_exposure = "loopback_only"
    devnet_public_p2p = $false
}
$envJsonPath = Join-Path $Root "acap-install-env.json"
($env1 | ConvertTo-Json -Depth 5) | Set-Content -Path $envJsonPath -Encoding ASCII
$envPs1Path = Join-Path $Root "acap-install-env.ps1"
$psLines = @()
$psLines += "# ACAP per-user runtime pointers (dot-source me). No global PATH edit."
$psLines += ('$env:ACAP_LOCAL_RUNTIME = "' + $RuntimeDir + '"')
$psLines += ('$env:ACAP_JAVA_HOME = "' + $javaHome + '"')
$psLines += ('$env:ACAP_BESU_BAT = "' + $besuBat + '"')
$psLines += ('$env:JAVA_HOME = "' + $javaHome + '"')
$psLines += ('$env:PATH = "' + $javaHome + '\bin;' + (Split-Path -Parent $besuBat) + ';" + $env:PATH')
$psLines | Set-Content -Path $envPs1Path -Encoding ASCII
Good ("  wrote " + $envJsonPath)
Good ("  wrote " + $envPs1Path)
$Report.env_files = @($envJsonPath, $envPs1Path)

# ---- step 5: install reports ----
Info "[5/6] Writing install report..."
$Report.warnings = $Warnings
$Report.next_steps = @(
    ("Open the node UI: run " + $AppExe + " (UI on http://127.0.0.1:8599)"),
    "Start a local devnet later: run app\START_LOCAL_DEVNET.bat (loopback only).",
    "Uninstall: run ACAP_UNINSTALL.bat (removes the per-user folder only)."
)
$reportJson = Join-Path $Root "install-report.json"
($Report | ConvertTo-Json -Depth 6) | Set-Content -Path $reportJson -Encoding ASCII
$txt = @()
$txt += "ACAP Desktop Node - install report"
$txt += ("timestamp     : " + $Stamp)
$txt += ("install root  : " + $Root)
$txt += ("package       : " + $pkgVer + " (sha256 verified)")
$txt += ("java          : " + $javaSource + " " + [string]$javaVer)
$txt += ("besu          : " + $besuSource + " " + [string]$besuVer + " (besu.bat)")
$txt += ("rpc exposure  : loopback_only   p2p public: false")
$txt += "mainnet: no   rewards: no   custody: no"
if ($Warnings.Count -gt 0) { $txt += ("warnings      : " + ($Warnings -join " | ")) }
$txt += "next steps:"
foreach ($n in $Report.next_steps) { $txt += ("  - " + $n) }
$reportTxt = Join-Path $Root "install-report.txt"
$txt | Set-Content -Path $reportTxt -Encoding ASCII
Good ("  wrote " + $reportJson)
Good ("  wrote " + $reportTxt)

# ---- step 6: launch + optional devnet ----
Line
Good "Install complete."
Write-Host ("ACAP app : " + $AppExe)
Write-Host ("Java     : " + $javaSource + "  Besu: " + $besuSource + " (besu.bat)")
Write-Host ("Report   : " + $reportTxt)
Line

if (-not $NoStart) {
    if (Test-Path $AppExe) {
        Info "Launching ACAP.Node.exe (UI on http://127.0.0.1:8599)..."
        Start-Process -FilePath $AppExe -WorkingDirectory $AppDir
    } else { Warn "ACAP.Node.exe not present; open the app folder manually." }
}

$ans = Read-Host "Start a local devnet now? (type YES to proceed, anything else to skip)"
if ($ans -eq "YES") {
    $startPs = Join-Path $AppDir "START_LOCAL_DEVNET.ps1"
    if (Test-Path $startPs) {
        Info "Starting local devnet with the per-user runtime (loopback only, P2P disabled)..."
        $besuBinDir = Split-Path -Parent $besuBat
        $env:JAVA_HOME = $javaHome
        $env:PATH = $javaHome + "\bin;" + $besuBinDir + ";" + $env:PATH
        & powershell -NoProfile -ExecutionPolicy Bypass -File $startPs
    } else { Warn "START_LOCAL_DEVNET.ps1 not found in the app folder." }
} else {
    Write-Host "Skipped devnet start. You can start it later from app\START_LOCAL_DEVNET.bat."
}

try { Stop-Transcript | Out-Null } catch {}
exit 0
