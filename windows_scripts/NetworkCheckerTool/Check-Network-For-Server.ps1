# network_check.ps1
# Este script verifica la configuración de red del cliente,
# la compara con una configuración de red de servidor predefinida,
# prueba la conectividad con el servidor y verifica el acceso a Internet.
Write-Host "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
Write-Host "`nVerificando información de red..." -ForegroundColor Cyan

# Definir la configuración de IP estática esperada del servidor
$serverIP = "192.168.1.146"
$serverSubnet = "192.168.1.0"
$serverGateway = "192.168.1.1"

# Obtener la configuración de red del adaptador activo
# Buscamos un adaptador que tenga una puerta de enlace predeterminada (es decir, esté activo y enrutando) y esté 'Up'.
$netAdapter = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null -and $_.NetAdapter.Status -eq 'Up' }

if (-not $netAdapter) {
    Write-Host "`nATENCION: No se detectó conexión de red activa. Por favor, revisa tu cable o Wi-Fi." -ForegroundColor Red
    exit # Salir del script si no se encuentra un adaptador activo
}

# Extraer la información de red del cliente
$clientIP = $netAdapter.IPv4Address.IPAddress
$clientGateway = $netAdapter.IPv4DefaultGateway.NextHop
$prefixLength = $netAdapter.IPv4Address.PrefixLength # No se usa estrictamente en este script, pero es bueno capturarla.

# Calcular la dirección de subred del cliente
# Esto convierte la IP a bytes, establece el último byte en 0 y lo convierte de nuevo a una cadena.
$clientSubnetBytes = [System.Net.IPAddress]::Parse($clientIP).GetAddressBytes()
# Para una subred /24 (común para 192.168.1.x), los primeros tres octetos definen la subred.
# Esta lógica asume una subred de clase C /24 o similar donde el último octeto es cero para la dirección de red.
# Un cálculo de subred más robusto implicaría una operación AND a nivel de bits con la máscara de subred.
# Sin embargo, para el propósito de este script de comparar con "192.168.1.0", este enfoque funciona.
$clientSubnetBytes[3] = 0 # Establecer el último octeto en 0 para la dirección de red
$clientSubnetStr = ($clientSubnetBytes -join ".")

# Mostrar información de red de forma amigable para el usuario
Write-Host "`nVerificando su configuración de red..." -ForegroundColor Cyan
Start-Sleep -Seconds 1 # Pausar por 1 segundo para una mejor experiencia de usuario

Write-Host "`nHola! Esta es la red de su equipo:" -ForegroundColor Yellow
Write-Host "------------------------------------------------------"
Write-Host "Su Dirección IP        : $clientIP"
Write-Host "Su Subred              : $clientSubnetStr"
Write-Host "Su Router (Puerta de Enlace): $clientGateway"
Write-Host "------------------------------------------------------"

# Verificar compatibilidad con la configuración de red esperada del servidor
$compatible = $false # Inicializar la bandera de compatibilidad
if ($clientSubnetStr -eq $serverSubnet -and $clientGateway -eq $serverGateway) {
    $compatible = $true
    Write-Host "`nCorrecto! Todo está bien. Su equipo está en la misma red que el servidor." -ForegroundColor Green
} else {
    Write-Host "`nATENCION: Su red es diferente a la configuración esperada del servidor." -ForegroundColor Red

    Write-Host "`nPara conectarse al servidor en $serverIP, asegúrese de lo siguiente:"
    Write-Host " - Su router debe usar:     $serverGateway"
    Write-Host " - Su rango de red debe comenzar con:     $serverSubnet"
    Write-Host "`nPor favor, entregue esta información a su técnico:"
    Write-Host "    > IP del Servidor Esperada : $serverIP"
    Write-Host "    > Subred Esperada          : $serverSubnet/24"
    Write-Host "    > Puerta de Enlace Esperada: $serverGateway"
} # Fin del bloque 'else' de verificación de compatibilidad de red

# Probar la accesibilidad del servidor (ping)
Write-Host "`nAhora verificando si el servidor ($serverIP) es accesible..." -ForegroundColor Cyan
Start-Sleep -Seconds 1 # Pausar por 1 segundo

# Test-Connection con -Quiet devuelve un booleano ($true si tiene éxito, $false si no)
$pingServer = Test-Connection -ComputerName $serverIP -Count 2 -Quiet -ErrorAction SilentlyContinue

if ($pingServer) {
    Write-Host "`nCorrecto! El servidor en $serverIP está EN LINEA y respondiendo a su equipo." -ForegroundColor Green
    if (-not $compatible) {
        Write-Host "Aunque la configuración de su red es diferente, el servidor sigue siendo accesible!" -ForegroundColor Yellow
    }
} else {
    Write-Host "`nERROR: El servidor en $serverIP NO es accesible desde su equipo." -ForegroundColor Red

    Write-Host "`nPosibles razones:"
    Write-Host " - Usted está en una red diferente."
    Write-Host " - El servidor está apagado o desconectado."
    Write-Host " - La configuración del firewall está bloqueando la conexión."

    Write-Host "`nPor favor, entregue esta información a su técnico para obtener ayuda."
} # Fin del bloque 'else' de accesibilidad del servidor

# Probar la conexión a Internet (intentando acceder a github.com)
Write-Host "`nVerificando si su equipo tiene acceso a Internet (github.com)..." -ForegroundColor Cyan
Start-Sleep -Seconds 1 # Pausar por 1 segundo

try {
    # Intentar invocar una solicitud web; si falla, el bloque catch lo maneja.
    # Se añadió -ErrorAction Stop para asegurar que los errores activen el bloque catch consistentemente.
    $github = Invoke-WebRequest -Uri "https://github.com" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "`nCorrecto! La conexión a Internet funciona. Su equipo puede acceder a GitHub.com." -ForegroundColor Green
} catch {
    Write-Host "`nERROR: Su equipo no puede acceder a Internet (GitHub no es accesible)." -ForegroundColor Red
    Write-Host "`nPor favor, revise:"
    Write-Host " - El router está conectado a Internet."
    Write-Host " - Ningún firewall está bloqueando el acceso."
    Write-Host " - Intente reiniciar su módem o router."
    Write-Host "`nEsta información puede ayudar a un técnico a diagnosticar el problema."
} # Fin del bloque 'try-catch' de conexión a Internet

# Resumen final de los detalles de red del cliente
Write-Host "`nResumen:"
Write-Host " - Su Dirección IP       : $clientIP"
Write-Host " - Su Subred             : $clientSubnetStr"
Write-Host " - Su Puerta de Enlace   : $clientGateway"

# Esperar antes de salir, pidiendo al usuario que presione una tecla
Write-Host "`nPresione cualquier tecla para salir..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") # Lee una pulsación de tecla sin mostrarla ni afectar el búfer de entrada de la consola.
Write-Host "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"