$root = "c:\Users\Alok Singh\Desktop\smart_education_system-main"
$src = "$root\smart_education_system-main\smarteducation"

# Create target directories
$dirs = @(
    "$root\frontend\templates\accounts",
    "$root\frontend\templates\students",
    "$root\frontend\templates\dashboards",
    "$root\frontend\templates\ml",
    "$root\frontend\templates\notifications",
    "$root\frontend\templates\advanced_features",
    "$root\frontend\static\css",
    "$root\frontend\static\js",
    "$root\frontend\static\images",
    "$root\frontend\media\avatars",
    "$root\backend\smarteducation",
    "$root\backend\accounts\migrations",
    "$root\backend\accounts\templates",
    "$root\backend\students\migrations",
    "$root\backend\students\templates\students",
    "$root\backend\dashboards\migrations",
    "$root\backend\dashboards\templates\dashboards",
    "$root\backend\api\migrations",
    "$root\backend\ml\migrations",
    "$root\backend\ml\management\commands",
    "$root\backend\ml\saved_models",
    "$root\backend\ml\templates\ml",
    "$root\backend\notifications\migrations",
    "$root\backend\notifications\templates\notifications",
    "$root\backend\advanced_features\migrations",
    "$root\backend\advanced_features\templates\advanced_features",
    "$root\backend\scripts",
    "$root\database\migrations\accounts",
    "$root\database\migrations\students",
    "$root\database\migrations\dashboards",
    "$root\database\migrations\api",
    "$root\database\migrations\ml",
    "$root\database\migrations\notifications",
    "$root\database\migrations\advanced_features"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "Directories created."

# ===== FRONTEND =====
# base.html
Copy-Item "$src\templates\base.html" "$root\frontend\templates\base.html" -Force
# home.html
Copy-Item "$src\students\templates\home.html" "$root\frontend\templates\home.html" -Force

# Account templates
Copy-Item "$src\accounts\templates\login.html" "$root\frontend\templates\accounts\login.html" -Force
Copy-Item "$src\accounts\templates\signup.html" "$root\frontend\templates\accounts\signup.html" -Force
Copy-Item "$src\accounts\templates\profile.html" "$root\frontend\templates\accounts\profile.html" -Force
Copy-Item "$src\accounts\templates\profile_edit.html" "$root\frontend\templates\accounts\profile_edit.html" -Force

# Student templates
Get-ChildItem "$src\students\templates\students\*" | Copy-Item -Destination "$root\frontend\templates\students\" -Force

# Dashboard templates
Get-ChildItem "$src\dashboards\templates\dashboards\*" | Copy-Item -Destination "$root\frontend\templates\dashboards\" -Force

# ML templates
Get-ChildItem "$src\ml\templates\ml\*" | Copy-Item -Destination "$root\frontend\templates\ml\" -Force

# Notification templates
Get-ChildItem "$src\notifications\templates\notifications\*" | Copy-Item -Destination "$root\frontend\templates\notifications\" -Force

# Advanced features templates
Get-ChildItem "$src\advanced_features\templates\advanced_features\*" | Copy-Item -Destination "$root\frontend\templates\advanced_features\" -Force

# Media
if (Test-Path "$src\media") {
    Copy-Item "$src\media\*" "$root\frontend\media\" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Frontend files copied."

# ===== BACKEND =====
# Django project config
Copy-Item "$src\smarteducation\__init__.py" "$root\backend\smarteducation\__init__.py" -Force
Copy-Item "$src\smarteducation\settings.py" "$root\backend\smarteducation\settings.py" -Force
Copy-Item "$src\smarteducation\urls.py" "$root\backend\smarteducation\urls.py" -Force
Copy-Item "$src\smarteducation\wsgi.py" "$root\backend\smarteducation\wsgi.py" -Force
Copy-Item "$src\smarteducation\asgi.py" "$root\backend\smarteducation\asgi.py" -Force
Copy-Item "$src\smarteducation\celery.py" "$root\backend\smarteducation\celery.py" -Force
Copy-Item "$src\smarteducation\context_processors.py" "$root\backend\smarteducation\context_processors.py" -Force

# Root-level backend files
Copy-Item "$src\manage.py" "$root\backend\manage.py" -Force
Copy-Item "$src\requirements.txt" "$root\backend\requirements.txt" -Force
Copy-Item "$src\Dockerfile" "$root\backend\Dockerfile" -Force
Copy-Item "$src\docker-compose.yml" "$root\backend\docker-compose.yml" -Force
Copy-Item "$src\.env" "$root\backend\.env" -Force
Copy-Item "$src\.env.example" "$root\backend\.env.example" -Force

# accounts app
$accountsFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py")
foreach ($f in $accountsFiles) {
    Copy-Item "$src\accounts\$f" "$root\backend\accounts\$f" -Force
}
Get-ChildItem "$src\accounts\migrations\*" -File | Copy-Item -Destination "$root\backend\accounts\migrations\" -Force
Get-ChildItem "$src\accounts\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\accounts\" -Force

# students app
$studentsFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py", "pdf.py")
foreach ($f in $studentsFiles) {
    Copy-Item "$src\students\$f" "$root\backend\students\$f" -Force
}
Get-ChildItem "$src\students\migrations\*" -File | Copy-Item -Destination "$root\backend\students\migrations\" -Force
Get-ChildItem "$src\students\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\students\" -Force

# dashboards app
$dashboardsFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py")
foreach ($f in $dashboardsFiles) {
    Copy-Item "$src\dashboards\$f" "$root\backend\dashboards\$f" -Force
}
Get-ChildItem "$src\dashboards\migrations\*" -File | Copy-Item -Destination "$root\backend\dashboards\migrations\" -Force
Get-ChildItem "$src\dashboards\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\dashboards\" -Force

# api app
$apiFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py", "serializers.py")
foreach ($f in $apiFiles) {
    Copy-Item "$src\api\$f" "$root\backend\api\$f" -Force
}
Get-ChildItem "$src\api\migrations\*" -File | Copy-Item -Destination "$root\backend\api\migrations\" -Force
Get-ChildItem "$src\api\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\api\" -Force

# ml app
$mlFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py", "predictor.py", "genai.py")
foreach ($f in $mlFiles) {
    Copy-Item "$src\ml\$f" "$root\backend\ml\$f" -Force
}
Get-ChildItem "$src\ml\migrations\*" -File | Copy-Item -Destination "$root\backend\ml\migrations\" -Force
Get-ChildItem "$src\ml\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\ml\" -Force
# ML management commands
if (Test-Path "$src\ml\management\commands") {
    Get-ChildItem "$src\ml\management\commands\*" -File -ErrorAction SilentlyContinue | Copy-Item -Destination "$root\backend\ml\management\commands\" -Force
}
# ML __init__.py for management
if (-not (Test-Path "$root\backend\ml\management\__init__.py")) {
    "" | Out-File "$root\backend\ml\management\__init__.py" -Encoding utf8
}
if (-not (Test-Path "$root\backend\ml\management\commands\__init__.py")) {
    "" | Out-File "$root\backend\ml\management\commands\__init__.py" -Encoding utf8
}
# ML saved models
if (Test-Path "$src\ml\saved_models") {
    Get-ChildItem "$src\ml\saved_models\*" -ErrorAction SilentlyContinue | Copy-Item -Destination "$root\backend\ml\saved_models\" -Recurse -Force
}

# notifications app
$notifFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py", "email.py", "sms.py", "whatsapp.py")
foreach ($f in $notifFiles) {
    Copy-Item "$src\notifications\$f" "$root\backend\notifications\$f" -Force
}
Get-ChildItem "$src\notifications\migrations\*" -File | Copy-Item -Destination "$root\backend\notifications\migrations\" -Force
Get-ChildItem "$src\notifications\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\notifications\" -Force

# advanced_features app
$advFiles = @("__init__.py", "admin.py", "apps.py", "models.py", "tests.py", "urls.py", "views.py")
foreach ($f in $advFiles) {
    Copy-Item "$src\advanced_features\$f" "$root\backend\advanced_features\$f" -Force
}
Get-ChildItem "$src\advanced_features\migrations\*" -File | Copy-Item -Destination "$root\backend\advanced_features\migrations\" -Force
Get-ChildItem "$src\advanced_features\migrations\*" -File | Copy-Item -Destination "$root\database\migrations\advanced_features\" -Force

# scripts
Copy-Item "$src\populate_all_demo.py" "$root\backend\scripts\populate_all_demo.py" -Force
Copy-Item "$src\populate_demo_advanced.py" "$root\backend\scripts\populate_demo_advanced.py" -Force
Copy-Item "$src\fix_parent.py" "$root\backend\scripts\fix_parent.py" -Force
Copy-Item "$src\clear_predictions.py" "$root\backend\scripts\clear_predictions.py" -Force
Copy-Item "$src\run_predictions.py" "$root\backend\scripts\run_predictions.py" -Force

Write-Host "Backend files copied."

# ===== DATABASE =====
Copy-Item "$src\db.sqlite3" "$root\database\db.sqlite3" -Force

Write-Host "Database files copied."

# ===== ROOT =====
Copy-Item "$src\..\..gitignore" "$root\.gitignore" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Restructuring complete! ==="
Write-Host "New structure created in: $root"
Write-Host "  - frontend/  (templates, static, media)"
Write-Host "  - backend/   (Django apps, config, scripts)"
Write-Host "  - database/  (SQLite DB, migrations reference)"
