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

Install/import Microsoft.Graph.Users and connect to the exact test tenant with User.ReadWrite.All delegated scope under an appropriately authorized test administrator. Verify Get-MgContext before changing anything; Graph consent and the signed-in administrator's role both matter.

```powershell
Install-Module Microsoft.Graph.Users -Scope CurrentUser
Connect-MgGraph -TenantId 'YOUR_TEST_TENANT_ID' -Scopes 'User.ReadWrite.All'
Get-MgContext
```

**Check before continuing:** The context shows your intended tenant and permission scope.

## Step 4 — Create one controlled test account at a time

**Where:** The same PowerShell session.

Check that the exact UPN does not already exist, prompt privately for a temporary lab password and create the account. Repeat deliberately for the second row and retain the returned IDs privately; never print/store a password in the CSV or commit history.

```powershell
$row = $rows[0]
$existing = Get-MgUser -Filter "userPrincipalName eq '$($row.UserPrincipalName)'"
if ($existing) { throw 'Account already exists; reconcile rather than duplicate' }
$secure = Read-Host 'Temporary password for this fictional user' -AsSecureString
$password = [System.Net.NetworkCredential]::new('', $secure).Password
$created = New-MgUser -AccountEnabled:$true -DisplayName $row.DisplayName `
  -UserPrincipalName $row.UserPrincipalName -MailNickname $row.MailNickname `
  -PasswordProfile @{Password=$password;ForceChangePasswordNextSignIn=$true}
$password = $null
$created | Select-Object Id, UserPrincipalName
```

**Check before continuing:** Each returned ID corresponds to one reviewed fictional row.

## Step 5 — Exercise the leaver boundary

**Where:** Your recorded exact test account ID.

Disable only the selected lab account and read it back. Test membership/session/app access separately if you add those features; AccountEnabled=false is not proof that every previously issued token or downstream account is immediately gone.

```powershell
Update-MgUser -UserId 'YOUR_CREATED_LAB_USER_ID' -AccountEnabled:$false
Get-MgUser -UserId 'YOUR_CREATED_LAB_USER_ID' -Property Id,UserPrincipalName,AccountEnabled
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

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. Existing portfolio images are references, not evidence that you performed these steps.

## Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

## Official implementation references

- [learn.microsoft.com — get-started](https://learn.microsoft.com/en-us/powershell/microsoftgraph/get-started)
- [learn.microsoft.com — users-lifecycle-workflow-overview](https://learn.microsoft.com/en-us/entra/identity/users/users-lifecycle-workflow-overview)

The walkthrough layout follows the prerequisites → creation/configuration → test → verification → troubleshooting → cleanup pattern of the [Splunk project reference](https://github.com/davidharris6/splunk-siem-log-analysis). Its Splunk-specific settings are not copied into unrelated projects.
