# USB & File Access Activity Monitor (PowerShell)

A lightweight PowerShell script designed for Incident Response, Security Auditing, and Data Loss Prevention (DLP) monitoring. This script queries Windows Event Logs (`System` and `Security`) to identify USB device connection/disconnection events alongside file access activity, displays the formatted output in the console, and exports a detailed report to a CSV file.

---

##Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites & Requirements](#prerequisites--requirements)
- [Monitored Event IDs](#monitored-event-ids)
- [How It Works](#how-it-works)
- [Usage Instructions](#usage-instructions)
- [Output Details](#output-details)
- [Error Handling & Security Considerations](#error-handling--security-considerations)

---

##Overview

When conducting forensic investigations or auditing potential unauthorized data exfiltration via removable media, tracking USB connections alone is often insufficient. Correlating hardware events (USB insertion/removal) with file access auditing logs provides actionable visibility into user activity on a Windows system.

This script automates that correlation by collecting relevant events, formatting them into a readable summary table, and persisting the data to disk for further forensic analysis.

---

##Key Features

- **Multi-Log Querying**: Simultaneously pulls from the Windows **System** log (hardware events) and **Security** log (file access events).
- **Console Visualization**: Displays color-coded terminal alerts and cleanly auto-formatted table results.
- **CSV Export**: Automatically exports log results (`TimeCreated`, `Id`, `Message`) to the user's Desktop (`USBActivityLog.csv`).
- **Resilient Error Handling**: Uses `try/catch` blocks to ensure graceful degradation if log querying or file writing fails.

---

##Prerequisites & Requirements

1. **Operating System**: Windows 10, Windows 11, or Windows Server.
2. **PowerShell Version**: Windows PowerShell 5.1 or PowerShell 7+.
3. **Administrator Privileges**: Querying the Windows `Security` event log requires **Elevated / Administrator** privileges (`Run as Administrator`).
4. **Audit Policy Setup** *(For File Access Events)*:
   - File Access Event IDs `4656` and `4663` require Windows Object Access Auditing to be enabled via Group Policy (`GPO`) or Local Security Policy:
     - `Computer Configuration -> Windows Settings -> Security Settings -> Advanced Audit Policy Configuration -> Audit Policies -> Object Access -> Audit File System` (Success/Failure).

---

##Monitored Event IDs

| Event ID | Log Provider | Category / Description | Security Context |
| :---: | :---: | :--- | :--- |
| **2003** | System | USB / Removable Device Connected | Indicates a driver load or connection for a USB storage device. |
| **2100** | System | USB / Removable Device Disconnected | Indicates a device suspension, removal, or disconnection event. |
| **4656** | Security | Handle Requested to an Object | Triggered when a handle to an object (e.g., file/folder) is requested. |
| **4663** | Security | An Attempt Was Made to Access an Object | Indicates specific access rights (read, write, delete) were exercised on a file. |

---

##How It Works (Code Breakdown)

### 1. Defining Target Event IDs
```powershell
$usbEventIDs = @(2003, 2100)  # USB connect/disconnect event IDs
$fileEventIDs = @(4663, 4656) # File access event IDs
```
Defines array parameters containing the specific Windows Event IDs to filter.

### 2. Querying Event Logs
```powershell
$usbEvents = Get-WinEvent -LogName System -ErrorAction SilentlyContinue | Where-Object { $_.Id -in $usbEventIDs }
$fileEvents = Get-WinEvent -LogName Security -ErrorAction SilentlyContinue | Where-Object { $_.Id -in $fileEventIDs }
```
Uses `Get-WinEvent` with `-ErrorAction SilentlyContinue` to avoid terminating on non-critical retrieval errors (such as empty log categories).

### 3. Log Validation Check
```powershell
if (!$usbEvents -and !$fileEvents) {
    Write-Host "No relevant USB or file transfer events found in logs." -ForegroundColor Yellow
    exit
}
```
Validates if any matching records were retrieved. If both queries return empty results, the script alerts the operator in yellow text and safely terminates.

### 4. Merging and Formatting
```powershell
$allEvents = @()
if ($usbEvents) { $allEvents += $usbEvents }
if ($fileEvents) { $allEvents += $fileEvents }

$eventLogs = $allEvents | Select-Object TimeCreated, Id, Message
```
Combines both arrays into `$allEvents` and standardizes the output schema to extract timestamp, event ID, and detailed event message.

### 5. Console Display & CSV Export
```powershell
Write-Host "=== USB and File Transfer Activity ===" -ForegroundColor Cyan
$eventLogs | Format-Table -AutoSize

$logFilePath = "$env:USERPROFILE\Desktop\USBActivityLog.csv"

try {
    $eventLogs | Export-Csv -Path $logFilePath -NoTypeInformation -Force
    Write-Host "USB activity log saved to: $logFilePath" -ForegroundColor Green
} catch {
    Write-Host "Failed to save USB activity log. Error: $_" -ForegroundColor Red
}
```
Displays results cleanly in the terminal, then attempts to overwrite or write a fresh CSV file to `$env:USERPROFILE\Desktop\USBActivityLog.csv`.

---

##Usage Instructions

1. **Open PowerShell as Administrator**:
   - Press `Win + X` and select **Windows Terminal (Admin)** or **Windows PowerShell (Admin)**.

2. **Execute the Script**:
   - If running as a `.ps1` script file:
     ```powershell
     .\Get-USBActivityLog.ps1
     ```
   - If Execution Policy blocks script execution:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
     .\Get-USBActivityLog.ps1
     ```

3. **View Output**:
   - Immediate results appear in your console session.
   - The CSV file is generated on your Desktop at `C:\Users\<YourUsername>\Desktop\USBActivityLog.csv`.

---

##Output Details

The generated `USBActivityLog.csv` file contains the following columns:

| Column Name | Description |
| :--- | :--- |
| `TimeCreated` | Exact timestamp when the event was logged by Windows. |
| `Id` | The numerical Windows Event ID (e.g., 2003, 4663). |
| `Message` | Detailed event properties (Device instance ID, process name, object path, requested permissions). |

---

##Error Handling & Security Considerations

- **Security Log Access Permissions**: If run without administrative credentials, querying the `Security` log will fail silently or return permission errors. Always run in an elevated shell.
- **Log Retention & Overwriting**: Large security logs may rotate quickly depending on domain audit policies. Adjust Windows Event Log max sizes if historical auditing is required over extended periods.
- **CSV Overwrites**: The script uses the `-Force` parameter in `Export-Csv`, which will overwrite any existing `USBActivityLog.csv` file on the Desktop.
