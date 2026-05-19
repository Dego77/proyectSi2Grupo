$ErrorActionPreference = "Stop"

$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm"

$url = "http://127.0.0.1:8001/backup-restore/completo/backup"

$headers = @{
    "X-Backup-Token" = "mi_token_super_seguro_backup_2026"
}

$carpeta = "C:\Users\dilex\Desktop\proyectSi2Grupo\backend\backups"

if (!(Test-Path $carpeta)) {
    New-Item -ItemType Directory -Path $carpeta
}

$salida = "$carpeta\backup_completo_multiempresa_$fecha.zip"

Invoke-WebRequest `
    -Uri $url `
    -Headers $headers `
    -OutFile $salida

Write-Output "Backup completo generado correctamente: $salida"