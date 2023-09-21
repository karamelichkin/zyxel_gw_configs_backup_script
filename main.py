#!env python3
import paramiko
import time
import json

def routers_list():
    try:
        with open('config.json', 'r') as json_file:
            return json.load(json_file)

    except FileNotFoundError:
        raise Exception("Config file 'config.json' not found.")

    except json.JSONDecodeError:
        raise Exception("Error decoding JSON data from config.")

def send_ssh_command(ssh_client, command, delay=1):
    try:
        # Open an SSH channel
        with ssh_client.invoke_shell() as chan:
            # Send the command
            chan.send(command + '\n')
            time.sleep(delay)

            # Receive and decode the response
            resp = chan.recv(99999)
            output = resp.decode('ascii')

            # Split the output into lines
            output_lines = output.split('\n')
            return output_lines
    except Exception as e:
        print(f"Error sending command: {str(e)}")
        return []

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    for router_config in routers_list():

        ssh_client.connect(
            router_config['address'],
            port=router_config['port'],
            username=router_config['username'],
            password=router_config['password']
        )

        command_output = send_ssh_command(ssh_client, 'show running-config', delay=1)[3:]

        hostname_line = next((line for line in command_output if "hostname" in line), None)

        if hostname_line:
            hostname = hostname_line.split()[1]

        with open(hostname + '_running_config.txt', 'w') as file:
            file.write('\n'.join(command_output))
    print("All configs has been saved")

except paramiko.SSHException as ssh_error:
    print(f"SSH error for {router_config['address']}: {ssh_error}")

except Exception as e:
    print(f"Error for {router_config['address']}: {e}")
finally:
    ssh_client.close()
