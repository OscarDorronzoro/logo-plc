$arch = (Get-WmiObject Win32_OperatingSystem).OSArchitecture
$arch = $arch -replace '[\s-]', '' -replace 's', '' -replace 'bit', '' -replace 'bits', ''

if ($arch -eq "64") {
    Write-Host "64-bit architecture detected."
    cp libsnap7/win64/snap7.dll C:/Windows/System32/

} elseif ($arch -eq "32") {
    Write-Host "32-bit architecture detected."
    cp libsnap7/win32/snap7.dll C:/Windows/System32/

} else {
    Write-Host "Unsupported architecture: $arch"
    exit 1
}

py -m pip install -r requirements.txt

exit 0

