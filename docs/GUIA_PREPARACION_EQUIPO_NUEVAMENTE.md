# Guía de preparación del equipo NuevaMente

**Proyecto:** NuevaMente — Sistema Inteligente de Adaptación y Generación de Contenido Educativo
**Equipo:** G10 · Equipo 48
**Repositorio:** https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48
**Carpeta recomendada:** `C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48`

> Esta guía solo prepara tu computador: herramientas, descarga del repositorio y apertura en Google Antigravity.
> No cubre cómo hacer commits, ramas ni Pull Requests (eso irá en una guía aparte).

---

## Resumen rápido (4 pasos)

1. Abrir PowerShell.
2. Ejecutar el **Bloque 1** (comprueba herramientas).
3. Configurar tu identidad de Git (solo la primera vez).
4. Ejecutar el **Bloque 2** (crea la carpeta y descarga el proyecto) y abrir la carpeta en Antigravity.

---

## 1. Abrir PowerShell

1. Pulsa la tecla **Windows**.
2. Escribe `PowerShell`.
3. Haz clic en **Windows PowerShell** (no necesitas abrirlo como administrador).
4. Para comprobar que funciona, copia y pega:

```powershell
$PSVersionTable.PSVersion
```

Si aparece un número de versión (por ejemplo `5.1` o `7.x`), PowerShell funciona. **No necesitas instalar otra versión.**

---

## 2. Bloque 1 — Comprobar herramientas instaladas

Copia el bloque completo, pégalo en PowerShell y pulsa **Enter**. Solo **lee** información; no instala ni modifica nada.

```powershell
Write-Host "`n=== Comprobación de herramientas NuevaMente ===" -ForegroundColor Cyan

# PowerShell
Write-Host "[OK] PowerShell $($PSVersionTable.PSVersion)" -ForegroundColor Green

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    Write-Host "[OK] $(git --version)" -ForegroundColor Green
    $nombre = git config --global user.name
    $correo = git config --global user.email
    if ($nombre -and $correo) {
        Write-Host "[OK] Identidad Git: $nombre <$correo>" -ForegroundColor Green
    } else {
        Write-Host "[PENDIENTE] Falta configurar tu nombre/correo en Git (ver sección 3.2)." -ForegroundColor Yellow
    }
} else {
    Write-Host "[FALTA] Git no está instalado (ver sección 3.1)." -ForegroundColor Red
}

# Google Antigravity
$rutasAgy = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Antigravity\Antigravity.exe"),
    (Join-Path $env:ProgramFiles "Antigravity\Antigravity.exe")
)
$agy = $rutasAgy | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($agy) {
    Write-Host "[OK] Google Antigravity detectado en: $agy" -ForegroundColor Green
} else {
    Write-Host "[VERIFICAR] No se detectó Antigravity en las rutas estándar." -ForegroundColor Yellow
    Write-Host "            Comprueba si aparece en el menú Inicio escribiendo 'Antigravity'." -ForegroundColor Yellow
    Write-Host "            Si ya abre desde Inicio, no necesitas reinstalarlo. Si no está instalado, ver sección 3.4." -ForegroundColor Yellow
}

# Acceso a GitHub (solo lectura, no pide credenciales)
if ($git) {
    git ls-remote --heads https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48.git *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] El repositorio de GitHub es accesible." -ForegroundColor Green
    } else {
        Write-Host "[REVISAR] No se pudo consultar el repositorio (ver sección 3.3 y 8)." -ForegroundColor Yellow
    }
}
Write-Host "=== Fin de la comprobación ===`n" -ForegroundColor Cyan
```

Instala o configura **solo** lo que aparezca como `[FALTA]` o `[PENDIENTE]`.

---

## 3. Instalar o configurar lo que falte

### 3.1 Git (solo si aparece `[FALTA]`)

1. Abre https://git-scm.com/download/win
2. Descarga el instalador de 64 bits y ejecútalo.
3. Acepta las opciones predeterminadas (Next → Next → Install).
4. **Cierra PowerShell y ábrelo de nuevo**.
5. Comprueba:

```powershell
git --version
```

### 3.2 Identidad de Git (solo la primera vez)

Sustituye los valores de ejemplo por **tu nombre** y **el correo que usas en GitHub**:

```powershell
git config --global user.name "Nombre del integrante"
git config --global user.email "correo-configurado-en-GitHub"
```

Comprueba:

```powershell
git config --global --get user.name
git config --global --get user.email
```

### 3.3 GitHub (en el navegador)

1. Entra a https://github.com e inicia sesión con tu cuenta.
2. Abre https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48
3. Si ves los archivos del proyecto (`README.md`, `backend`, `frontend`…), tienes acceso de **lectura**.

> El acceso de lectura **no** garantiza permiso de escritura. Los permisos de escritura se comprobarán cuando sean necesarios.
> **Nunca** escribas contraseñas ni tokens en PowerShell ni los guardes en archivos del proyecto.

### 3.4 Google Antigravity (solo si no está instalado)

1. Antes de descargar, comprueba en el menú Inicio escribiendo `Antigravity`. Si la aplicación aparece y abre correctamente, **ya está lista y no necesitas reinstalarla**.
2. Si no está instalada, abre la página oficial: https://antigravity.google/download
3. Descarga la versión para **Windows** y ejecuta el instalador.
4. Abre Antigravity desde el menú Inicio (escribe `Antigravity`) e inicia sesión con tu cuenta de Google.
5. Vuelve a ejecutar el **Bloque 1** para comprobar el entorno.

---

## 4. Bloque 2 — Preparar la carpeta y descargar el proyecto

Este bloque puede ejecutarse **las veces que quieras**: si el proyecto ya existe, no lo vuelve a descargar ni sobrescribe nada. Si la carpeta existe pero contiene otra cosa, **se detiene** sin borrar ni mover archivos.

```powershell
$base    = "C:\HackathonONE_NuevaMente"
$destino = Join-Path $base "G10_Nuevamente_Equipo48"
$repoUrl = "https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48.git"

& {
    Write-Host "`n=== Preparación del proyecto NuevaMente ===" -ForegroundColor Cyan

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Git no está instalado. Instálalo (sección 3.1) y vuelve a ejecutar este bloque." -ForegroundColor Red
        return
    }

    if (-not (Test-Path $base)) {
        New-Item -ItemType Directory -Path $base | Out-Null
        Write-Host "[OK] Carpeta creada: $base" -ForegroundColor Green
    } else {
        Write-Host "[OK] La carpeta base ya existe: $base" -ForegroundColor Green
    }

    if (-not (Test-Path $destino)) {
        Write-Host "Descargando el repositorio (puede tardar unos minutos)..." -ForegroundColor Cyan
        git clone $repoUrl $destino
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] No se pudo clonar. Revisa tu conexión y tu acceso a GitHub (sección 8)." -ForegroundColor Red
            return
        }
        Write-Host "[OK] Repositorio descargado en: $destino" -ForegroundColor Green
    } else {
        if (-not (Test-Path (Join-Path $destino ".git"))) {
            Write-Host "[DETENIDO] La carpeta $destino existe pero NO es un repositorio Git." -ForegroundColor Red
            Write-Host "No se ha borrado ni movido nada. Revisa la sección 8 (caso 'La carpeta ya existe')." -ForegroundColor Yellow
            return
        }
        $origen = git -C $destino remote get-url origin 2>$null
        if ($origen -notmatch "No-Country-simulation/G10_Nuevamente_Equipo48") {
            Write-Host "[DETENIDO] La carpeta contiene otro repositorio: $origen" -ForegroundColor Red
            Write-Host "No se ha borrado ni movido nada. Revisa la sección 8." -ForegroundColor Yellow
            return
        }
        Write-Host "[OK] El repositorio ya estaba descargado. No se vuelve a clonar." -ForegroundColor Green
    }

    Set-Location $destino
    Write-Host "`nUbicación actual: $(Get-Location)" -ForegroundColor Cyan
    Write-Host "Rama actual:      $(git branch --show-current)" -ForegroundColor Cyan
    Write-Host "Origen remoto:    $(git remote get-url origin)" -ForegroundColor Cyan
    Write-Host "=== Listo. Ahora abre esta carpeta en Antigravity (sección 5) ===`n" -ForegroundColor Green
}
```

---

## 5. Abrir el proyecto en Google Antigravity

1. Abre **Google Antigravity** desde el menú Inicio.
2. Usa la opción para **abrir una carpeta** (Open Folder / Abrir carpeta).
3. Selecciona exactamente:
   `C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48`
4. Confirma con **Seleccionar carpeta**.

**Importante:** abre la **raíz** del repositorio, no `frontend` ni `backend` por separado.

**Cómo comprobar que es la carpeta correcta:** en el explorador de archivos de Antigravity debes ver, en el primer nivel:

```
agents/
backend/
frontend/
rag_core/
.env.example
LICENSE
README.md
requirements.txt
```

Si en el primer nivel solo ves `app.py` o `app/`, abriste una subcarpeta: vuelve al paso 2 y elige la raíz.

---

## 6. Carpetas del proyecto

Rutas verificadas en el repositorio (rama `main`):

| Componente | Ruta | Para qué sirve |
| --- | --- | --- |
| Frontend (Streamlit) | `frontend/app.py` | Interfaz web: carga de archivos, selección de perfil/formato y visualización de resultados. |
| Backend (FastAPI) | `backend/backend/app/` | API principal. Punto de entrada: `backend/backend/app/main.py`. |
| Endpoints de la API | `backend/backend/app/api/v1/endpoints/` | `health.py`, `files.py` (carga de documentos), `adaptacion.py` (generación). |
| Servicios | `backend/backend/app/services/` | `document_service.py`, `rag_service.py`, `llm_service.py`, `agent_service.py`, `oci_service.py`. |
| Esquemas de datos | `backend/backend/app/schemas/` | Modelos Pydantic de entrada y salida. |
| Configuración del backend | `backend/backend/app/core/` | `config.py` (variables de entorno) y `exceptions.py`. |
| Agentes (prototipo) | `agents/graph.py` | Grafo de agentes. |
| Núcleo RAG (prototipo) | `rag_core/pipeline.py` | Pipeline RAG de referencia. |
| Pruebas automatizadas | `backend/backend/tests/` | Pruebas `pytest` (`test_*.py`, `conftest.py`). |
| Dependencias | `requirements.txt` y `backend/backend/requirements.txt` | Paquetes Python del proyecto y del backend. |
| Plantilla de variables | `.env.example` | Ejemplo de configuración. **No** guardes claves reales en el repositorio. |
| Corpus y metadatos | `_revision_corpus_fase05/` | **No está en `main`.** Se encuentra en la rama remota `origin/data-analytics-corpus` (documentos, inventario, matriz y reportes). |

> **Nota sobre el corpus:** La preparación inicial del computador **no requiere** descargar la rama `data-analytics-corpus` ni el corpus documental. El objetivo de esta guía es dejar listo el entorno de trabajo y el repositorio principal en `main`. La descarga o vinculación del corpus se resolverá en el procedimiento de trabajo correspondiente.

### Moverse entre carpetas desde PowerShell

```powershell
# Ir a la raíz del proyecto
Set-Location "C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48"
Get-Location

# Ir al backend
Set-Location ".\backend\backend"
Get-Location

# Volver a la raíz
Set-Location "C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48"

# Ir al frontend
Set-Location ".\frontend"
Get-Location
```

`Set-Location` cambia de carpeta; `Get-Location` muestra dónde estás.

---

## 7. Comprobación final del entorno

Ejecuta este bloque **desde la raíz de tu repositorio**. Si elegiste la ruta recomendada, el primer comando entra directamente en ella. Si elegiste otra carpeta, sustituye la ruta de `Set-Location` por tu ubicación real (o sitúate manualmente en la raíz de tu clon antes de ejecutarlo).

Solo consulta información; no cambia de rama ni modifica archivos.

```powershell
# Si usaste la ruta recomendada (ajusta si usaste otra carpeta):
Set-Location "C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48"

Get-Location
git status
git branch --show-current
git branch -a
git remote -v
```

| Comando | Qué comprueba |
| --- | --- |
| `Get-Location` | Que estás en `C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48`. |
| `git status` | Que Git reconoce la carpeta como repositorio y si hay cambios locales. |
| `git branch --show-current` | La rama en la que estás (normalmente `main` tras clonar). |
| `git branch -a` | Las ramas locales y remotas disponibles (`main`, `dev`, `feature/...`, `data-analytics-corpus`, etc.). |
| `git remote -v` | Que el origen es `https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48.git`. |

**Lista de verificación final:**

- [ ] Bloque 1 muestra `[OK]` en PowerShell, Git, identidad, Antigravity y GitHub.
- [ ] `git remote -v` apunta al repositorio de NuevaMente.
- [ ] `Get-Location` muestra la carpeta recomendada.
- [ ] Antigravity tiene abierta la **raíz** del repositorio.
- [ ] Puedes localizar `frontend/`, `backend/backend/app/`, `backend/backend/tests/` y sabes que el corpus está en la rama `data-analytics-corpus` (sin requerir descargarlo en esta preparación inicial).

---

## 8. Solución de problemas básicos

| Problema | Cómo comprobarlo | Siguiente paso seguro |
| --- | --- | --- |
| PowerShell no se abre o no ejecuta el comando | Al pegar `$PSVersionTable.PSVersion` no aparece versión. | Abre **Windows PowerShell** desde Inicio (no "ISE"). Pega el bloque completo y pulsa Enter. Si el bloque aparece con `>>`, pulsa Enter otra vez. |
| `git` no se reconoce como comando | `git --version` muestra "no se reconoce". | Instala Git (3.1) y **cierra y vuelve a abrir** PowerShell. |
| GitHub no permite ver el repositorio | En el navegador aparece "404" estando con sesión iniciada. | Confirma que usas la cuenta correcta y pide al coordinador que te agregue al repositorio. |
| La carpeta ya existe y no corresponde al repositorio | Bloque 2 muestra `[DETENIDO]`. | El script protege los archivos y no borra nada. Puedes cambiar la variable `$base` en el script a otra carpeta vacía (por ejemplo `C:\NuevaMente_Equipo48`), o mover/reubicar manualmente la carpeta existente si correspondía a otro proyecto. |
| La clonación falla | Bloque 2 muestra `[ERROR] No se pudo clonar`. | Verifica tu conexión abriendo el repositorio en el navegador. Si se abrió una ventana de inicio de sesión de GitHub, complétala en el navegador. Vuelve a ejecutar el Bloque 2. |
| Antigravity no está instalado o no encuentra la carpeta | Bloque 1 muestra `[FALTA]` para Antigravity, o la carpeta no aparece al abrirla. | Instala desde https://antigravity.google/download. Comprueba la ruta con `Test-Path "C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48"` (debe decir `True`). |
| Se abrió una subcarpeta equivocada | En Antigravity solo ves `app.py` o `app/` en el primer nivel. | Usa **Abrir carpeta** de nuevo y selecciona `C:\HackathonONE_NuevaMente\G10_Nuevamente_Equipo48`. |

---

Con esto tu computador queda preparado: herramientas comprobadas, proyecto descargado y abierto en Antigravity desde la carpeta raíz.
