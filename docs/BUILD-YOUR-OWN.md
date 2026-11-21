# Build your own from scratch: Cloud Identity Access Automation

Your own Entra joiner/leaver lab using two fictional accounts, a reviewed CSV and exact account-ID cleanup.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

## Prerequisites

A separate test Entra tenant/domain you administer, Microsoft Graph PowerShell and permission for the selected user lifecycle operations. Do not use real employees or a production-wide identity feed.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

## Create your project folder

Choose a new folder name. These first commands create a blank project; an optional `git init` gives it its own history. Create parent directories in your editor when a later step introduces a nested file.

```bash
mkdir my-cloud-identity-access-automation
cd my-cloud-identity-access-automation
git init
```

Create `.gitignore` before saving credentials or build outputs:

```gitignore
.venv/
node_modules/
.env
.env.*
local.settings.json
credentials.json
token.json
*.pem
*.key
*.tfstate*
*.tfplan
.terraform/
private*/
captures/
backups/
batch.json
reports/
out/
app-config.local.yaml
```

The source/file snippets are a starting implementation you type or paste into the named files. Replace `YOUR_*`, names, regions and addresses only with values from your own lab; do not place real client/employee records in a test project. Keep your terminal in this project root unless a step explicitly changes directory.

Before a first commit, set your own repository-local author with `git config user.name "YOUR_NAME"` and `git config user.email "YOUR_PUBLIC_COMMIT_EMAIL"`. Review `git status --short` and the staged diff before publishing; ignored local files are not a substitute for reviewing what you upload.

## Step 1 — Define the lifecycle input

**Where:** Your new project folder.

Choose your test tenant's verified domain and create users.csv below with unique fictional names. Define creation, disabling and deletion as distinct steps; a job title must not silently grant an administrator role.

Create **`users.csv`** with the following contents:

```csv
UserPrincipalName,DisplayName,MailNickname
lab.joiner01@YOUR_VERIFIED_DOMAIN,Lab Joiner One,lab.joiner01
lab.joiner02@YOUR_VERIFIED_DOMAIN,Lab Joiner Two,lab.joiner02
```

**Check before continuing:** The CSV identifies only the two accounts you intend to create.

## Step 2 — Inspect the input before connecting

**Where:** PowerShell in your folder.

Import the CSV and reject missing/duplicate user principal names. Review the two rows manually and replace the placeholder domain before making any directory request.

```powershell
$rows = Import-Csv -LiteralPath ./users.csv
if ($rows.Count -ne 2) { throw 'Expected exactly two lab rows' }
if ($rows | Where-Object { -not $_.UserPrincipalName -or -not $_.DisplayName }) { throw 'Missing field' }
if ($rows | Group-Object UserPrincipalName | Where-Object Count -gt 1) { throw 'Duplicate user' }
if ($rows.UserPrincipalName -match 'YOUR_VERIFIED_DOMAIN') { throw 'Replace the lab domain' }
$domain = Read-Host 'Your verified isolated test-tenant domain'
$allowed = @("lab.joiner01@$domain", "lab.joiner02@$domain")
if ($domain -notmatch '^[a-zA-Z0-9.-]+$') { throw 'Invalid domain syntax' }
if ($rows | Where-Object { $_.UserPrincipalName -notin $allowed }) { throw 'Unexpected account outside the two-user lab' }
$rows | Select-Object UserPrincipalName, DisplayName
```

**Check before continuing:** The proposed lifecycle scope is exactly your two fictional users.

## Step 3 — Connect with the required test authority

**Where:** Your PowerShell session and Entra consent.

Create lab-context.ps1 below, install the Graph Users module and connect to your exact test tenant. The helper checks the tenant and delegated scope; the signed-in operator must also hold the appropriate directory role for the two fictional accounts.

Create **`lab-context.ps1`** with the following contents:

```powershell
function Assert-LabContext {
    param([Parameter(Mandatory=$true)][guid]$TenantId)
    $context = Get-MgContext
    if (-not $context -or $TenantId -eq [guid]::Empty -or $context.TenantId -ne $TenantId.ToString()) {
        throw 'Stop: the Graph session is not the selected test tenant'
    }
    if ($context.AuthType -ne 'Delegated' -or $context.Scopes -notcontains 'User.ReadWrite.All') {
        throw 'Stop: the required delegated test context is missing'
    }
}
```

```powershell
Install-Module Microsoft.Graph.Users -Scope CurrentUser
. ./lab-context.ps1
$expectedTenant = 'YOUR_TEST_TENANT_ID'
if ($expectedTenant -eq 'YOUR_TEST_TENANT_ID') { throw 'Replace the test tenant ID first' }
try { $parsedTenant = [guid]$expectedTenant } catch { throw 'Use the test tenant GUID, not a name/domain' }
if ($parsedTenant -eq [guid]::Empty) { throw 'The test tenant must not be empty' }
$expectedTenant = $parsedTenant.ToString()
Connect-MgGraph -TenantId $expectedTenant -Scopes 'User.ReadWrite.All' -ContextScope Process
Assert-LabContext -TenantId $expectedTenant
```

**Check before continuing:** The context shows your intended tenant and permission scope.

## Step 4 — Create one controlled test account at a time

**Where:** The same PowerShell session.

Run the context guard immediately before creating a selected row. Retain each successful returned ID in the private CSV below; if creation succeeds but local journaling fails, reconcile that exact UPN in the same tenant and audit logs before retrying, and never adopt a pre-existing account for cleanup.

```powershell
Assert-LabContext -TenantId $expectedTenant
$row = $rows[0] # Deliberately select the second reviewed row only when ready.
$existing = Get-MgUser -Filter "userPrincipalName eq '$($row.UserPrincipalName)'"
if ($existing) { throw 'Account exists; reconcile the prior outcome instead of creating/adopting it' }
$secure = Read-Host 'Temporary password for this fictional user' -AsSecureString
$password = [System.Net.NetworkCredential]::new('', $secure).Password
try {
    $created = New-MgUser -AccountEnabled:$true -DisplayName $row.DisplayName `
      -UserPrincipalName $row.UserPrincipalName -MailNickname $row.MailNickname `
      -PasswordProfile @{Password=$password;ForceChangePasswordNextSignIn=$true} -ErrorAction Stop
} finally {
    $password = $null
    $secure = $null
}
New-Item -ItemType Directory -Path ./private-state -Force | Out-Null
$created | Select-Object Id, UserPrincipalName | Export-Csv `
  -LiteralPath ./private-state/created-users.csv -NoTypeInformation -Append
$created | Select-Object Id, UserPrincipalName
```

**Check before continuing:** Each returned ID corresponds to one reviewed fictional row.

## Step 5 — Exercise the leaver boundary

**Where:** Your recorded exact test account ID.

Recheck the test tenant, select an ID saved by this lab and compare its current UPN with the private journal before disabling it. Test downstream membership/session/application effects separately; the directory field alone does not prove immediate token revocation.

```powershell
Assert-LabContext -TenantId $expectedTenant
$createdIds = Import-Csv -LiteralPath ./private-state/created-users.csv
$targetId = 'YOUR_CREATED_LAB_USER_ID'
$target = @($createdIds | Where-Object Id -eq $targetId)
if ($target.Count -ne 1) { throw 'Select exactly one ID recorded by this lab' }
$actual = Get-MgUser -UserId $targetId -Property Id,UserPrincipalName,AccountEnabled
if ($actual.UserPrincipalName -ne $target[0].UserPrincipalName) { throw 'Recorded user does not match' }
Update-MgUser -UserId $targetId -AccountEnabled:$false
Get-MgUser -UserId $targetId -Property Id,UserPrincipalName,AccountEnabled
```

**Check before continuing:** The selected user is disabled and unrelated accounts are unchanged.

## Step 6 — Capture evidence and remove only your test identities

**Where:** Entra audit logs and your private ID record.

Inspect the actual create/disable events and save a value-free lifecycle diagram. Remove the two exact created test IDs only when finished, disconnect Graph and retain no password or token in your public project.

**Check before continuing:** You can explain request → validation → authorized directory operation → readback → audit evidence.

## Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. The architecture diagram explains the design; record your own results rather than treating it as execution evidence.

## Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

## Official implementation references

- [learn.microsoft.com — get-started](https://learn.microsoft.com/en-us/powershell/microsoftgraph/get-started)
- [learn.microsoft.com — users-lifecycle-workflow-overview](https://learn.microsoft.com/en-us/entra/identity/users/users-lifecycle-workflow-overview)
- [learn.microsoft.com — get-mgcontext?view=graph-powershell-1.0](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.authentication/get-mgcontext?view=graph-powershell-1.0)
