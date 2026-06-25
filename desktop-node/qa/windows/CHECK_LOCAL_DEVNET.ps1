# CHECK_LOCAL_DEVNET.ps1 (QA) - read-only loopback probe of a RUNNING local devnet.
# This does NOT start anything. Run it AFTER you have started the devnet yourself with the
# package's START_LOCAL_DEVNET.bat. It only queries 127.0.0.1 (no public/remote RPC) for
# chain id / block height / peer count. A single-validator devnet shows peer_count 0 (normal).
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$checks = @()

Write-Host "ACAP QA - local devnet loopback check (127.0.0.1 only)" -ForegroundColor Cyan
Write-Host "  (This never starts a node. Start it first with START_LOCAL_DEVNET.bat if needed.)" -ForegroundColor DarkGray

$chk = Invoke-QaPython $py $pkg "acap_node_manager.py" @("check")
if ($null -eq $chk) {
    $checks += New-QaCheck "devnet_probe" "Devnet loopback probe" "FAIL" "could not run acap_node_manager.py check" `
        "Ensure Python is available (bundled runtime/python or system)."
} elseif (-not $chk.connected) {
    $checks += New-QaCheck "devnet_connected" "Local devnet RPC reachable" "WARN" `
        "no loopback RPC answered (devnet not running yet?)" `
        "Start it first: run START_LOCAL_DEVNET.bat (needs Java 17+ and Besu), then re-run this check."
} else {
    $okChain = ([string]$chk.chain_id -eq "469469")
    $checks += New-QaCheck "devnet_connected" "Local devnet RPC reachable" "PASS" "loopback RPC answered"
    $checks += New-QaCheck "devnet_chain" "Chain id 469469" ($(if($okChain){"PASS"}else{"FAIL"})) ("chain_id=" + $chk.chain_id) ""
    $bh = [int]($chk.block_height)
    $checks += New-QaCheck "devnet_block" "Block height present" ($(if($null -ne $chk.block_height){"PASS"}else{"WARN"})) ("block_height=" + $chk.block_height) `
        "Run this check twice ~10s apart - height should increase as blocks are produced."
    $checks += New-QaCheck "devnet_peers" "Peer count" "PASS" ("peer_count=" + $chk.peer_count + " (0 is normal for a single-validator devnet)")
}

# P2P exposure audit: port 30303 must NOT be listening on a non-loopback interface.
$audit = Invoke-QaPython $py $pkg "acap_node_manager.py" @("p2p-audit")
if ($null -eq $audit -or -not $audit.checked) {
    $checks += New-QaCheck "devnet_p2p_exposure" "P2P not on a public interface (port 30303)" "WARN" `
        "could not audit (netstat unavailable)" "Run 'netstat -ano | findstr :30303' manually; nothing should LISTEN on a non-loopback interface."
} elseif ($audit.public_listener) {
    $checks += New-QaCheck "devnet_p2p_exposure" "P2P not on a public interface (port 30303)" "FAIL" `
        $audit.note "Set p2p-enabled=false in runtime\devnet\config.toml and restart the devnet."
} else {
    $checks += New-QaCheck "devnet_p2p_exposure" "P2P not on a public interface (port 30303)" "PASS" $audit.note
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "local_devnet"; checks = $checks }
