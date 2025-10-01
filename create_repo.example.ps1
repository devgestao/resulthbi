$token = "YOUR_GITHUB_TOKEN"
$repoName = "resulthbi"
$description = "Dashboard de análise de dados comerciais integrado com o sistema Resulth"

$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token $token"
}

$body = @{
    name = $repoName
    description = $description
    private = $false
} | ConvertTo-Json

# Criar repositório
$response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
