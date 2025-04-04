$usbEventIDs = @(2003, 2100)  #USB connect/disconnect event ID's
$fileEventIDs = @(4663, 4656) #File access event ID's

$usbEvents = Get-WinEvent -LogName System -ErrorAction SilentlyContinue | Where-Object { $_.Id -in $usbEventIDs } #Pulling USB connection and disconnection events from logs

$fileEvents = Get-WinEvent -LogName Security -ErrorAction SilentlyContinue | Where-Object { $_.Id -in $fileEventIDs } #Pulling file access events

if (!$usbEvents -and !$fileEvents) { #If statement making sure no erros occured while getting the logs
    Write-Host "No relevant USB or file transfer events found in logs." -ForegroundColor Yellow
    exit
}

$allEvents = @() #These 3 lines are merging the USB and file transfer events
if ($usbEvents) { $allEvents += $usbEvents }
if ($fileEvents) { $allEvents += $fileEvents }

$eventLogs = $allEvents | Select-Object TimeCreated, Id, Message #Formatting the output and selecting the details to be shown

Write-Host "=== USB and File Transfer Activity ===" -ForegroundColor Cyan #These 2 lines are displaying the results in the console
$eventLogs | Format-Table -AutoSize

$logFilePath = "$env:USERPROFILE\Desktop\USBActivityLog.csv" #Saving the results to a CSV file

try { #Trying to export the CSV file
    $eventLogs | Export-Csv -Path $logFilePath -NoTypeInformation -Force
    Write-Host "USB activity log saved to: $logFilePath" -ForegroundColor Green
} catch { #If there is a error in exporting this will run instead of crashing the script
    Write-Host "Failed to save USB activity log. Error: $_" -ForegroundColor Red
}
