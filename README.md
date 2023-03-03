# HoneyWalt_VM

HoneyWalt VM daemon

## Initialisation

When the HoneyWalt VM boots, it starts this daemon.
The daemon will connect to the HoneyWalt controller and wait for commands.

The first expected command sends the phase:

- COMMIT phase: some persistent modifications will be added to the VM (configuration, walt images).
- RUN phase: no persistent modification can be done, we will only use the existing configuration to manage walt and wireguard.
- DEBUG phase: the daemon will stop when learning it is in DEBUG phase. This mode allows the admin to connect and run manual (persistent) modifications to the VM.

## Runtime

The daemon has received a phase.

In the COMMIT phase, it will be able to:

- Receive devices information,
- Receive doors information,
- Send devices IPs,
- Generate wireguard keys for all devices,
- Commit all the modifications (store it in a configuration file).

In the RUN phase, it will be able to:

- Start and stop wireguard
- Reboot devices.

