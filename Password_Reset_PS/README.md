# Active Directory Forced Password Reset Script

A streamlined, robust PowerShell automation script designed for Active Directory (AD) domain administrators. This script queries all active (enabled) AD user accounts and enforces a mandatory password change on their next logon attempt (`ChangePasswordAtLogon = $true`).

---

## Features

- **Active Directory Module Check**: Explicitly imports the `ActiveDirectory` module to ensure required cmdlets (`Get-ADUser`, `Set-ADUser`) are available.
- **Enabled User Filtering**: Uses `-Filter {Enabled -eq $true}` to isolate active domain user accounts, ignoring disabled or decommissioned accounts.
- **Error Handling**: Implements a `try / catch` block per user object to catch execution errors (e.g., elevated domain admin protection, permission issues, missing identity attributes) without interrupting the overall execution loop.
- **Visual Status Reporting**: Outputs color-coded console logs (`Green` for successful enforcement, `Red` for failures with exception details) to provide real-time operational feedback.

---

## Prerequisites

- **Operating System**: Windows Server with Active Directory Domain Services (AD DS) or Windows Client with Remote Server Administration Tools (RSAT) installed.
- **PowerShell Version**: PowerShell 5.1 or PowerShell 7+.
- **Permissions**: Domain Administrator or delegated AD permissions with rights to modify user account attributes (specifically `pwdLastSet`).

---

## Installation & Setup

1. **Save the Script**: Save the script file as `Enforce-ADPasswordReset.ps1`:
   ```powershell
   New-Item -Path ".\Enforce-ADPasswordReset.ps1" -ItemType File
   ```

2. **Set Execution Policy**: Ensure PowerShell allows script execution:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```

---

## Usage Instructions

Run the script from an elevated PowerShell terminal (Run as Administrator):

```powershell
.\Enforce-ADPasswordReset.ps1
```

### Script Execution Flow:

1. **Module Import**: Loads the `ActiveDirectory` PowerShell module via `Import-Module ActiveDirectory`.
2. **Account Query**: Executes `Get-ADUser -Filter {Enabled -eq $true}` to compile the array of active domain accounts.
3. **Loop & Enforcement**:
   - Iterates through each user object (`$user`).
   - Executes `Set-ADUser -Identity $user.SamAccountName -ChangePasswordAtLogon $true`.
   - On success: Displays a green confirmation message with the user's `SamAccountName`.
   - On failure: Displays a red error message detailing the exception message (`$_`).
4. **Completion Summary**: Logs a final status message indicating completion of the batch processing.

---

## Code Reference

```powershell
# This is my Powershell script to reset all users passwords.

Import-Module ActiveDirectory # Only needed if for whatever reason you do not allready have this imported

$users = Get-ADUser -Filter {Enabled -eq $true} # Getting a list of all users in AD who are enabled

foreach ($user in $users) { # Loop for resetting the password for all users
    try { # The code in this statement will attempt to reset the passowrd if it encounters a error it goes to the catch statement
        Set-ADUser -Identity $user.SamAccountName -ChangePasswordAtLogon $true -PassThru
        Write-Host "Password reset enforced for: $($user.SamAccountName)" -ForegroundColor Green
    } catch { # This code is ran if it fails to reset the password for a user
        Write-Host "Failed to reset password for: $($user.SamAccountName) - $_" -ForegroundColor Red
    }
}

Write-Host "Password reset requirement applied to all enabled users." # This line displays when the code is done running
```

---

## Security & Practical Considerations

- **Scope Impact**: Running this script against an entire domain forces **all** enabled users to change their passwords. Use with caution during incident response, credential compromise remediation, or scheduled baseline policy shifts.
- **Service Accounts**: Ensure service accounts or automated system accounts are either disabled or excluded from this policy, as forcing a password change on interactive service accounts can break scheduled jobs or background processes.
- **Targeted OU Filtering**: If you wish to target a specific Organizational Unit (OU) rather than the entire domain, modify the `Get-ADUser` call:
  ```powershell
  $users = Get-ADUser -Filter {Enabled -eq $true} -SearchBase "OU=Employees,DC=domain,DC=com"
  ```

---

## License

MIT License. Free for personal, enterprise IT administration, and incident response deployments.
