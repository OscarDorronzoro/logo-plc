ipconfig
Get-NetAdapter
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.0.3 -PrefixLength 24 -DefaultGateway 192.168.0.1
New-NetIPAddress -InterfaceIndex 12 -IPAddress 192.168.0.3
Get-NetIPAddress -InterfaceAlias "Ethernet"
Remove-NetIPAddress -InterfaceAlias "Ethernet" -Confirm:$false
Remove-NetIPAddress -IPAddress 192.168.0.3 -Confirm:$false
Get-NetRoute -AddressFamily IPv4 | Where-Object -FilterScript {$_.NextHop -ne "0.0.0.0"} | %{ Remove-NetRoute -NextHop $_.NextHop -Confirm:$false }

