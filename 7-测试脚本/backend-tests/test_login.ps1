# 测试登录接口
Write-Host "正在测试登录接口..."
Start-Sleep -Seconds 2

try {
    $body = @{
        username = "admin"
        password = "admin"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri http://127.0.0.1:5000/api/login `
        -Method POST `
        -Body $body `
        -ContentType 'application/json' `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    Write-Host "状态: $($response.StatusCode)"
    Write-Host "响应:"
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "错误状态: $($_.Exception.Response.StatusCode.Value__)"
    Write-Host "响应:"
    try {
        $_.Exception.Response.Content.ReadAsStream() | ConvertFrom-Json | ConvertTo-Json
    } catch {
        $_.Exception.Message
    }
}
