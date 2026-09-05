<#
.SYNOPSIS
    Verifie l'etat du depot collateral-lab. Ne modifie rien sans -Nettoyer.

.DESCRIPTION
    Huit familles de controles : environnement, configuration, arborescence,
    fichiers parasites, gouvernance des donnees, qualite du code,
    chaine de production, etat Git.

    Code retour 0 si tout passe, 1 sinon.

.PARAMETER Nettoyer
    Supprime les parasites detectes : __pycache__, .ruff_cache, .pytest_cache,
    src/data, bases egarees. Sans ce drapeau, ils sont seulement signales.

.PARAMETER Rapide
    Saute la reconstruction de l'entrepot et les tests de donnees.

.EXAMPLE
    .\scripts\verif_depot.ps1
    .\scripts\verif_depot.ps1 -Nettoyer
    .\scripts\verif_depot.ps1 -Rapide
#>

[CmdletBinding()]
param(
    [switch]$Nettoyer,
    [switch]$Rapide
)

$script:echecs = 0

function Section($titre)  { Write-Host "`n$titre" -ForegroundColor Cyan }
function Ok($message)     { Write-Host "  [OK    ] $message" -ForegroundColor Green }
function Alerte($message) { Write-Host "  [ALERTE] $message" -ForegroundColor Yellow }
function Echec($message)  { Write-Host "  [ECHEC ] $message" -ForegroundColor Red; $script:echecs++ }
function Detail($lignes)  { $lignes | ForEach-Object { Write-Host "           $_" -ForegroundColor DarkGray } }

# --- Ancrage : on remonte jusqu'a pyproject.toml, on ne compte pas les niveaux ---
$racine = $PSScriptRoot
while ($racine -and -not (Test-Path (Join-Path $racine 'pyproject.toml'))) {
    $racine = Split-Path -Parent $racine
}
if (-not $racine) {
    Write-Host "[ECHEC ] racine introuvable : aucun pyproject.toml depuis $PSScriptRoot" -ForegroundColor Red
    exit 1
}
Set-Location $racine
Write-Host "Depot : $racine" -ForegroundColor White


# ============================================================================
Section "1. Environnement"
# ============================================================================

if ($env:VIRTUAL_ENV) {
    Ok "environnement virtuel actif : $(Split-Path -Leaf $env:VIRTUAL_ENV)"
} else {
    Echec "aucun environnement virtuel actif - lancez .\.venv\Scripts\Activate.ps1"
}

$versionPython = (& python --version 2>&1) -join ''
if ($LASTEXITCODE -eq 0) { Ok $versionPython } else { Echec "python introuvable" }

$cheminPaquet = (& python -c "import collateral; print(collateral.__file__)" 2>&1) -join ''
if ($LASTEXITCODE -eq 0) {
    Ok "paquet importable : $cheminPaquet"
} else {
    Echec "paquet collateral non importable - lancez pip install -e .[dev]"
    Detail $cheminPaquet
}


# ============================================================================
Section "2. Configuration"
# ============================================================================

# Constantes definies deux fois : le bug qui a coute l'apres-midi du 28/08.
$fichierConfig = Join-Path $racine 'src\collateral\config.py'
if (Test-Path $fichierConfig) {
    $doublons = Select-String -Path $fichierConfig -Pattern '^([A-Z_][A-Z0-9_]*)\s*=' |
        ForEach-Object { $_.Matches[0].Groups[1].Value } |
        Group-Object | Where-Object { $_.Count -gt 1 }

    if ($doublons) {
        Echec "constantes definies plusieurs fois dans config.py (la derniere gagne)"
        Detail ($doublons | ForEach-Object { "$($_.Name) : $($_.Count) affectations" })
    } else {
        Ok "aucune constante dupliquee dans config.py"
    }
} else {
    Echec "src\collateral\config.py introuvable"
}

$racineCalculee = ((& python -c "from collateral import config; print(config.RACINE)" 2>&1) -join '').Trim()
if ($LASTEXITCODE -eq 0) {
    if ($racineCalculee.TrimEnd('\') -ieq $racine.TrimEnd('\')) {
        Ok "config.RACINE = $racineCalculee"
    } else {
        Echec "config.RACINE pointe ailleurs que la racine du depot"
        Detail @("attendu : $racine", "obtenu  : $racineCalculee")
    }
} else {
    Echec "config.RACINE illisible"
    Detail $racineCalculee
}


# ============================================================================
Section "3. Arborescence"
# ============================================================================

$attendus = @(
    'pyproject.toml', 'README.md', 'JOURNAL.md', '.gitignore',
    'src\collateral\__init__.py', 'src\collateral\config.py', 'src\collateral\journal.py',
    'src\collateral\db.py', 'src\collateral\sql.py', 'src\collateral\controle.py',
    'src\collateral\download.py', 'src\collateral\build.py', 'src\collateral\tests_donnees.py'
)
$absents = @($attendus | Where-Object { -not (Test-Path (Join-Path $racine $_)) })
if ($absents) {
    Echec "$($absents.Count) fichier(s) attendu(s) absent(s)"
    Detail $absents
} else {
    Ok "$($attendus.Count) fichiers attendus presents"
}

# -Filter ne connait pas les classes de caracteres : on filtre avec une regex.
function Compter($chemin, $motif) {
    if (-not (Test-Path $chemin)) { return @() }
    return @(Get-ChildItem -Path $chemin -File | Where-Object { $_.Name -match $motif })
}

$scriptsSql = Compter (Join-Path $racine 'sql') '^\d\d_.*\.sql$'
if ($scriptsSql.Count -gt 0) { Ok "$($scriptsSql.Count) scripts de transformation dans sql\" }
else { Echec "aucun script sql\NN_*.sql" }

$testsDonnees = Compter (Join-Path $racine 'tests\donnees') '^\d\d_.*\.sql$'
if ($testsDonnees.Count -gt 0) { Ok "$($testsDonnees.Count) tests de donnees dans tests\donnees\" }
else { Echec "aucun test tests\donnees\NN_*.sql" }

$testsUnitaires = Compter (Join-Path $racine 'tests\unitaires') '^test.*\.py$'
if ($testsUnitaires.Count -gt 0) { Ok "$($testsUnitaires.Count) fichiers de tests unitaires" }
else { Echec "aucun fichier tests\unitaires\test_*.py" }


# ============================================================================
Section "4. Fichiers parasites"
# ============================================================================

$parasites = @()
$parasites += Get-Item (Join-Path $racine 'src\data') -ErrorAction SilentlyContinue
$parasites += Get-ChildItem -Path (Join-Path $racine 'src') -Recurse -Include '*.duckdb', '*.duckdb.wal', '*.csv', '*.csv.gz' -ErrorAction SilentlyContinue
$parasites += Get-ChildItem -Path $racine -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue
$parasites += Get-ChildItem -Path $racine -Recurse -Directory -Filter '.ruff_cache' -ErrorAction SilentlyContinue
$parasites += Get-ChildItem -Path $racine -Recurse -Directory -Filter '.pytest_cache' -ErrorAction SilentlyContinue
$parasites = @($parasites | Where-Object { $_ -and $_.FullName -notlike "*\.venv\*" })
# Bases DuckDB egarees : une seule est legitime.
$baseLegitime = Join-Path $racine 'collateral.duckdb'
$parasites += Get-ChildItem -Path $racine -Recurse -Include '*.duckdb', '*.duckdb.wal' -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -ne $baseLegitime }

if ($parasites) {
    if ($Nettoyer) {
        $parasites | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
        Ok "$($parasites.Count) parasite(s) supprime(s)"
        Detail ($parasites | ForEach-Object { $_.FullName.Replace($racine, '.') })
    } else {
        Alerte "$($parasites.Count) parasite(s) detecte(s) - relancez avec -Nettoyer"
        Detail ($parasites | ForEach-Object { $_.FullName.Replace($racine, '.') })
    }
} else {
    Ok "aucun fichier parasite"
}


# ============================================================================
Section "5. Gouvernance des donnees (regle 4)"
# ============================================================================

$suivis = @(& git ls-files | Where-Object { $_ -match '\.(csv|gz|zip|parquet|duckdb)$' })
if ($suivis) {
    Echec "DONNEES VERSIONNEES - violation de la regle 4"
    Detail $suivis
} else {
    Ok "aucune donnee versionnee"
}

$artefacts = @(& git ls-files | Where-Object { $_ -match 'egg-info|__pycache__|\.venv/' })
if ($artefacts) {
    Echec "artefacts de build suivis par Git"
    Detail (@($artefacts | Select-Object -First 5) + "correctif : git rm -r --cached le_chemin")
} else {
    Ok "aucun artefact de build suivi"
}


# ============================================================================
Section "6. Qualite du code"
# ============================================================================

# pytest d'abord : il ne depend de rien et dure une seconde.
$sortiePytest = & pytest -q 2>&1
if ($LASTEXITCODE -eq 0) {
    Ok "pytest"
    Detail (@($sortiePytest) | Select-Object -Last 1)
} else {
    Echec "pytest"
    Detail $sortiePytest
}

$sortieRuff = & ruff check . 2>&1
if ($LASTEXITCODE -eq 0) { Ok "ruff check" } else { Echec "ruff check"; Detail $sortieRuff }

$sortieFormat = & ruff format --check . 2>&1
if ($LASTEXITCODE -eq 0) { Ok "ruff format --check" } else { Echec "ruff format --check"; Detail $sortieFormat }


# ============================================================================
Section "7. Chaine de production"
# ============================================================================

if ($Rapide) {
    Alerte "chaine non verifiee (-Rapide)"
} else {
    $sortieBuild = & python -m collateral.build 2>&1
    if ($LASTEXITCODE -eq 0) { Ok "collateral.build" }
    else { Echec "collateral.build"; Detail $sortieBuild }

    $sortieTests = & python -m collateral.tests_donnees 2>&1
    if ($LASTEXITCODE -eq 0) {
        Ok "collateral.tests_donnees"
        Detail (@($sortieTests) | Select-Object -Last 1)
    } else {
        Echec "collateral.tests_donnees"
        Detail $sortieTests
    }

    # Signature : preuve mecanique de non-regression (regle 9).
    $expression = "import duckdb; from collateral.config import BASE_DUCKDB; c = duckdb.connect(str(BASE_DUCKDB), read_only=True); r = c.execute('SELECT count(*), sum(hash(t)) FROM mart_prix_m2_reference t').fetchone(); c.close(); print(r[0], r[1])"
    $signatureObtenue = ((& python -c $expression 2>&1) -join '').Trim()
    $fichierSignature = Join-Path $racine 'docs\signature_attendue.txt'

    if ($LASTEXITCODE -ne 0) {
        Echec "signature illisible"
        Detail $signatureObtenue
    } elseif (-not (Test-Path $fichierSignature)) {
        Alerte "docs\signature_attendue.txt absent - signature actuelle : $signatureObtenue"
        Detail @("pour l'ancrer : Set-Content docs\signature_attendue.txt -Value '$signatureObtenue'")
    } else {
        $signatureAttendue = (Get-Content $fichierSignature -Raw).Trim()
        if ($signatureObtenue -eq $signatureAttendue) {
            Ok "signature inchangee : $signatureAttendue"
        } else {
            Echec "SIGNATURE MODIFIEE"
            Detail @(
                "attendue : $signatureAttendue",
                "obtenue  : $signatureObtenue",
                "si le changement est voulu, mettez a jour docs\signature_attendue.txt",
                "dans le meme commit que la modification qui le provoque."
            )
        }
    }
}

# ============================================================================
Section "8. Graphe dbt"
# ============================================================================

$dossierModeles = Join-Path $racine 'transform\models'
$modeles = @(Get-ChildItem -Path $dossierModeles -Recurse -Filter '*.sql' -ErrorAction SilentlyContinue)

if ($modeles.Count -eq 0) {
    Echec "aucun modele sous transform\models - le controle n'a rien examine"
} else {
    # Toute table du projet citee sans ref() ni source() est une arete manquante.
    $motifEnDur = '(FROM|JOIN)\s+(raw_|stg_|agg_|dim_|mart_|ref_)'
    $enDur = @($modeles | Select-String -Pattern $motifEnDur)

    if ($enDur) {
        Echec "$($enDur.Count) reference(s) en dur dans les modeles dbt"
        Detail ($enDur | ForEach-Object { "$($_.Filename):$($_.LineNumber)  $($_.Line.Trim())" })
    } else {
        Ok "$($modeles.Count) modeles examines, aucune reference en dur"
    }
}


# ============================================================================
Section "9. Etat Git"
# ============================================================================

$branche = ((& git rev-parse --abbrev-ref HEAD 2>&1) -join '').Trim()
Ok "branche : $branche"

$modifications = @(& git status --porcelain)
if ($modifications) {
    Alerte "$($modifications.Count) modification(s) non commitee(s)"
    Detail (@($modifications) | Select-Object -First 10)
} else {
    Ok "arbre de travail propre"
}

# On evite la notation @{u} : PowerShell y voit un debut de table de hachage.
& git show-ref --verify --quiet "refs/remotes/origin/$branche"
if ($LASTEXITCODE -eq 0) {
    $aPousser = ((& git rev-list --count "origin/$branche..HEAD") -join '').Trim()
    if ([int]$aPousser -gt 0) { Alerte "$aPousser commit(s) non pousse(s) - git push" }
    else { Ok "rien a pousser" }
} else {
    Alerte "branche sans suivi distant - git push -u origin $branche"
}


# ============================================================================
Write-Host ""
if ($script:echecs -eq 0) {
    Write-Host "VERDICT : depot conforme." -ForegroundColor Green
    exit 0
} else {
    Write-Host "VERDICT : $($script:echecs) controle(s) en echec." -ForegroundColor Red
    exit 1
}