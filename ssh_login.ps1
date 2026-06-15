$password = 'B3der#Luxe!2026'
$user = 'aquarius_admin'
$ip = '187.124.34.10'
$command = 'uname -a; lsmod | grep algif_aead; cat /etc/os-release'

$input = $password + "`n" + $command + "`nexit`n"
$input | ssh -o StrictHostKeyChecking=no $user@$ip
