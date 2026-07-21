#This is my Powershell script to reset all users passwords.

Import-Module ActiveDirectory #Only needed if for whatever reason you do not allready have this imported

$users = Get-ADUser -Filter {Enabled -eq $true} #Getting a list of all users in AD who are enabled

foreach ($user in $users) { #Loop for resetting the password for all users
    try { #The code in this statement will attempt to reset the passowrd if it encounters a error it goes to the catch statement
        Set-ADUser -Identity $user.SamAccountName -ChangePasswordAtLogon $true -PassThru
        Write-Host "Password reset enforced for: $($user.SamAccountName)" -ForegroundColor Green
    } catch { #This code is ran if it fails to reset the password for a user
        Write-Host "Failed to reset password for: $($user.SamAccountName) - $_" -ForegroundColor Red
    }
}

Write-Host "Password reset requirement applied to all enabled users." #This line displays when the code is done running
