<#
.SYNOPSIS
    Rejoue la chaine complete depuis un clone neuf.

.DESCRIPTION
    Le seul controle qui prouve qu'un tiers peut reproduire le projet.
    Contrairement a verif_depot.ps1, celui-ci s'arrete a la premiere etape
    en echec : chaque etape depend de la precedente, poursuivre n'apprendrait
    rien.

    Le dossier temporaire est supprime en cas de succes, conserve en cas
    d'echec pour permettre l'inspection.

.PARAMETER Branche
    Branche a tester. Par defaut main.

.PARAMETER Depot
    URL du depot distant.

.PARAMETER Conserver
    Conserve le dossier temporaire meme en cas de succes.

.EXAMPLE
    .\scripts\verif_clone.ps1
    .\scripts\verif_clone.ps1 -Branche feat/tests-unitaires
    .\scripts\verif_clone.ps1 -Conserver
#>

[CmdletBinding()]
param(
    [string]$Branche = 'main',
    [string]$Depot = 'https://github.com/matthiasbrz/collateral-lab.git',
    [switch]$Conserver
)

$ErrorActionPreference = 'Continue'
$depart = Get-Date

$horodatage = Get-Date -Format 'yyyyMMdd-HHmmss'
$travail = Join-Path $env:TEMP "collateral-verif-$horodatage"
$origine = Get-Location

function Titre($texte)  { Write-Host "`n$texte" -ForegroundColor Cyan }
function Note($texte)   { Write-Host "   $texte" -ForegroundColor DarkGray }
function Reussi($texte) { Write-Host "   ok - $texte" -ForegroundColor Green }

function Terminer($code, $message) {
    Set-Location $origine
    $duree = [int]((Get-Date) - $depart).TotalSeconds

    Write-Host ""
    if ($code -eq 0) {
        Write-Host "VERDICT : reproductible depuis un clone neuf ($duree s)." -ForegroundColor Green
        if ($Conserver) { Write-Host "Dossier conserve : $travail" -ForegroundColor DarkGray }
        elseif (Test-Path $travail) { Remove-Item $travail -Recurse -Force -ErrorAction SilentlyContinue }
    } else {
        Write-Host "VERDICT : $message" -ForegroundColor Red
        if (Test-Path $travail) {
            Write-Host "Dossier conserve pour inspection : $travail" -ForegroundColor Yellow
        }
    }
    exit $code
}

# Execute une commande native et s'arrete si son code retour n'est pas 0.
function Etape {
    param(
        [string]$Libelle,
        [scriptblock]$Action,
        [switch]$Silencieux
    )
    Write-Host "-> $Libelle" -ForegroundColor White

    # Python journalise sur stderr. PowerShell transforme toute ligne de stderr
    # d'une commande native en ErrorRecord et l'affiche. L'affectation ci-dessous
    # est locale a la fonction : elle ne modifie pas la session appelante.
    $ErrorActionPreference = 'SilentlyContinue'

    $global:LASTEXITCODE = 0
    $sortie = & $Action 2>&1 | ForEach-Object { $_.ToString() }
    $code = $LASTEXITCODE

    if ($code -ne 0) {
        @($sortie) | ForEach-Object { Write-Host "     $_" -ForegroundColor DarkGray }
        Terminer 1 "echec a l'etape : $Libelle"
    }
    if (-not $Silencieux -and $sortie) {
        @($sortie) | Select-Object -Last 3 | ForEach-Object { Note $_ }
    }
    return $sortie
}


# ============================================================================
Titre "0. Controles locaux, avant de cloner"
# ============================================================================

$modifications = @(& git status --porcelain)
if ($modifications) {
    Write-Host "   $($modifications.Count) modification(s) non commitee(s) :" -ForegroundColor Red
    @($modifications) | Select-Object -First 10 | ForEach-Object { Note $_ }
    Terminer 1 "le clone testerait un etat different de votre disque. Commitez d'abord."
}
Reussi "arbre de travail propre"

& git show-ref --verify --quiet "refs/remotes/origin/$Branche"
if ($LASTEXITCODE -ne 0) {
    Terminer 1 "la branche $Branche n'existe pas sur origin. Poussez-la d'abord."
}

$aPousser = ((& git rev-list --count "origin/$Branche..$Branche" 2>&1) -join '').Trim()
if ($LASTEXITCODE -eq 0 -and [int]$aPousser -gt 0) {
    Terminer 1 "$aPousser commit(s) non pousse(s) sur $Branche. Faites git push."
}
Reussi "branche $Branche a jour sur origin"


# ============================================================================
Titre "1. Clone neuf"
# ============================================================================

Etape "git clone ($Branche)" { git clone --branch $Branche --quiet $Depot $travail } -Silencieux
Set-Location $travail
Reussi $travail


# ============================================================================
Titre "2. Environnement isole"
# ============================================================================

Etape "creation du venv" { py -m venv .venv } -Silencieux
$python = Join-Path $travail '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { Terminer 1 "interpreteur introuvable apres creation du venv" }

# On appelle l'interpreteur par son chemin plutot que d'activer le venv :
# l'activation modifierait la session appelante.
Etape "mise a jour de pip" { & $python -m pip install --quiet --upgrade pip } -Silencieux
Etape "pip install -e .[dev]" { & $python -m pip install --quiet -e '.[dev]' } -Silencieux


# ============================================================================
Titre "3. Chaine complete"
# ============================================================================

Etape "collateral.download" { & $python -m collateral.download }
Etape "collateral.build"    { & $python -m collateral.build }
Etape "collateral.tests_donnees" { & $python -m collateral.tests_donnees }
Etape "pytest" { & $python -m pytest -q }


# ============================================================================
Titre "4. Signature du mart"
# ============================================================================

$fichierSignature = Join-Path $travail 'docs\signature_attendue.txt'
if (-not (Test-Path $fichierSignature)) {
    Terminer 1 "docs\signature_attendue.txt absent du depot. Il doit etre versionne."
}

$expression = "import duckdb; from collateral.config import BASE_DUCKDB; c = duckdb.connect(str(BASE_DUCKDB), read_only=True); r = c.execute('SELECT count(*), sum(hash(t)) FROM mart_prix_m2_reference t').fetchone(); c.close(); print(r[0], r[1])"
$obtenue = ((& $python -c $expression 2>&1) -join '').Trim()
if ($LASTEXITCODE -ne 0) {
    Note $obtenue
    Terminer 1 "signature illisible sur le clone"
}

$attendue = (Get-Content $fichierSignature -Raw).Trim()
if ($obtenue -ne $attendue) {
    Note "attendue : $attendue"
    Note "obtenue  : $obtenue"
    Terminer 1 "la chaine ne reproduit pas le resultat annonce"
}
Reussi "signature conforme : $attendue"

Terminer 0 ""