# Syncthing

Continuous file sync between your devices, using this server as the
always-on peer and offsite copy. Deploy:

    teploy template install syncthing --server <name> --var domain=sync.example.com

Then, immediately: open https://<domain>, go to Settings > GUI, and set a
user and password - the GUI starts unauthenticated. (Or gate it up front by
adding an `access: basic_auth` block to the generated teploy.yml.)

Pair devices by showing this server's ID (Actions > Show ID) to the
Syncthing app on each device. Port 22000 (tcp+udp) is published for direct
sync; open it in your firewall for full speed, otherwise transfers fall back
to community relays.
