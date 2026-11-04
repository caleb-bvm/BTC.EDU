# Deja lista la red Polar de regtest: contenedores activos, alice conectada a bob, nodos sincronizados y canal activo.
# Se puede repetir sin efectos adicionales. No inicia Docker Desktop ni Polar.
[CmdletBinding()]
param(
    [string]$Network = 'polar-n1',
    [string]$RpcUser = 'polaruser',
    [string]$RpcPassword = 'polarpass'
)

$ErrorActionPreference = 'Stop'
$buyer = "$Network-alice"
$merchant = "$Network-bob"
$backend = "$Network-backend1"
$lncli = @('lncli', '--network', 'regtest', '--lnddir=/home/lnd/.lnd')

function Invoke-Node([string]$Container, [string[]]$Arguments) {
    $output = & docker exec $Container @lncli @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { return $null }
    try { return ($output | Out-String | ConvertFrom-Json) } catch { return $null }
}

& docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker no responde. Abre Docker Desktop y Polar y vuelve a ejecutar el script.' }

foreach ($name in @($backend, $buyer, $merchant)) {
    $state = & docker inspect -f '{{.State.Running}}' $name 2>$null
    if ($LASTEXITCODE -ne 0) { throw "No existe el contenedor $name. Crea o inicia la red en Polar." }
    if ($state -ne 'true') {
        Write-Host "Iniciando $name..."
        & docker start $name | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "No se pudo iniciar $name." }
    }
}

# LND tarda unos segundos en responder tras arrancar el contenedor.
$merchantInfo = $null
for ($attempt = 0; $attempt -lt 60 -and $null -eq $merchantInfo; $attempt++) {
    $merchantInfo = Invoke-Node $merchant @('getinfo')
    if ($null -eq $merchantInfo) { Start-Sleep -Seconds 1 }
}
if ($null -eq $merchantInfo -or $null -eq (Invoke-Node $buyer @('getinfo'))) { throw 'Los nodos de Polar no responden.' }

$peers = Invoke-Node $buyer @('listpeers')
if (-not ($peers.peers | Where-Object { $_.pub_key -eq $merchantInfo.identity_pubkey })) {
    Write-Host 'Conectando alice con bob...'
    $null = Invoke-Node $buyer @('connect', "$($merchantInfo.identity_pubkey)@$($merchant):9735")
}

$synced = (Invoke-Node $buyer @('getinfo')).synced_to_chain -and (Invoke-Node $merchant @('getinfo')).synced_to_chain
if (-not $synced) {
    # Tras una pausa larga LND marca la cadena como antigua; un bloque nuevo en regtest la actualiza.
    Write-Host 'Minando un bloque de regtest para sincronizar los nodos...'
    $rpc = @('bitcoin-cli', '-regtest', "-rpcuser=$RpcUser", "-rpcpassword=$RpcPassword")
    $address = (& docker exec $backend @rpc getnewaddress 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $address) { throw 'No se pudo usar bitcoind de Polar.' }
    & docker exec $backend @rpc generatetoaddress 1 $address | Out-Null
}

$active = $false
for ($attempt = 0; $attempt -lt 30 -and -not $active; $attempt++) {
    $buyerInfo = Invoke-Node $buyer @('getinfo')
    $active = $buyerInfo.synced_to_chain -and $buyerInfo.num_active_channels -ge 1
    if (-not $active) { Start-Sleep -Seconds 1 }
}
if ($active) {
    Write-Host 'Polar listo: alice y bob conectados, con canal activo.'
} else {
    Write-Warning 'alice no tiene un canal activo con bob. Revisa los canales en Polar; las facturas se crearán, pero no podrán pagarse.'
}
