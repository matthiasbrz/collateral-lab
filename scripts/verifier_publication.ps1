<#
.SYNOPSIS
    Verifie que le catalogue publie est posterieur a la fusion d'une PR.

.DESCRIPTION
    Compare deux instants : le generated_at du manifest publie, en UTC, et
    l'heure de fusion de la PR, lue sur son commit de fusion dans origin/main.
    Echoue si la publication precede la fusion. Juste apres une fusion, un
    echec est normal : construction-et-publication n'a pas encore deploye.

    Limite : la garde prouve qu'une publication a suivi la fusion, pas
    qu'elle a ete construite depuis ce commit. Deux fusions plus rapprochees
    que la duree d'une construction ne se distinguent pas.

    Constat du 28/10 : publication a 20:43 UTC, fusion de la PR n.102 a
    20:58 UTC, verification crue a tort. Le 14/10, un cache avait deja trompe
    la lecture. Regle 12 : la verification s'ecrit, elle ne se refait plus a
    la main.

.PARAMETER PR
    Numero de la PR fusionnee dans main.

.PARAMETER Publie
    generated_at a comparer, pour rejouer un cas passe. Par defaut : celui du
    manifest publie.

.EXAMPLE
    .\scripts\verifier_publication.ps1 -PR 104
    .\scripts\verifier_publication.ps1 -PR 102 -Publie 2026-10-28T20:43:50.594868Z
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][int]$PR,
    [string]$Publie
)

$manifeste = 'https://matthiasbrz.github.io/collateral-lab/manifest.json'
$culture = [Globalization.CultureInfo]::InvariantCulture

& git fetch --quiet origin 2>$null
$fusion = ((& git log origin/main -1 --format=%cI --grep "^Merge pull request #$PR ") -join '').Trim()
if (-not $fusion) {
    Write-Host "[ECHEC ] PR n.$PR : aucun commit de fusion dans origin/main" -ForegroundColor Red
    exit 1
}

if (-not $Publie) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $brut = (Invoke-WebRequest "$($manifeste)?v=$(Get-Random)" -UseBasicParsing).Content
    $Publie = [regex]::Match($brut, '"generated_at":\s*"([^"]+)"').Groups[1].Value
    if (-not $Publie) {
        Write-Host "[ECHEC ] generated_at introuvable dans $manifeste" -ForegroundColor Red
        exit 1
    }
}

$tFusion = [datetimeoffset]::Parse($fusion, $culture)
$tPublie = [datetimeoffset]::Parse($Publie, $culture)
Write-Host ('{0}{1,-21} : {2} UTC' -f (' ' * 2), "fusion de la PR n.$PR", $tFusion.UtcDateTime.ToString('yyyy-MM-dd HH:mm:ss'))
Write-Host ('{0}{1,-21} : {2} UTC' -f (' ' * 2), 'catalogue publie', $tPublie.UtcDateTime.ToString('yyyy-MM-dd HH:mm:ss'))

if ($tPublie -lt $tFusion) {
    Write-Host "[ECHEC ] le catalogue publie precede la fusion : ce n'est pas encore le bon" -ForegroundColor Red
    exit 1
}
Write-Host ('[{0,-6}] le catalogue publie suit la fusion de la PR n.{1}' -f 'OK', $PR) -ForegroundColor Green
exit 0
