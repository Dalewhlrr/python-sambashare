import os
import subprocess

def install_samba():
    print("Installing Samba...")
    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'samba'], check=True)
    print("Samba installed successfully.")

def create_group(group_name):
    print(f"Creating group '{group_name}'...")
    subprocess.run(['sudo', 'groupadd', group_name], check=True)
    print(f"Group '{group_name}' created successfully.")

def add_user_to_group(username, group_name):
    print(f"Adding user '{username}' to group '{group_name}'...")
    subprocess.run(['sudo', 'usermod', '-aG', group_name, username], check=True)
    print(f"User '{username}' added to group '{group_name}'.")

def add_samba_user(username):
    print(f"Adding Samba user '{username}'...")
    subprocess.run(['sudo', 'smbpasswd', '-a', username], check=True)
    print(f"Samba user '{username}' added successfully.")

def setup_samba_share(share_name, share_path, group_name):
    smb_conf_path = "/etc/samba/smb.conf"

    # Backup the original smb.conf
    subprocess.run(['sudo', 'cp', smb_conf_path, smb_conf_path + '.backup'], check=True)

    # Add the new share to the smb.conf
    share_config = f"""
[{share_name}]
   path = {share_path}
   available = yes
   read only = no
   browsable = yes
   writable = yes
   valid users = @{group_name}
   create mask = 0660
   directory mask = 2770
   force group = {group_name}
"""

    with open('smb.conf.tmp', 'w') as temp_conf:
        with open(smb_conf_path, 'r') as original_conf:
            temp_conf.write(original_conf.read())
        temp_conf.write(share_config)

    # Replace the smb.conf with the new one
    subprocess.run(['sudo', 'mv', 'smb.conf.tmp', smb_conf_path], check=True)

    # Restart Samba to apply changes
    subprocess.run(['sudo', 'systemctl', 'restart', 'smbd'], check=True)

    # Set the ownership and permissions for the share directory
    subprocess.run(['sudo', 'chown', '-R', f':{group_name}', share_path], check=True)
    subprocess.run(['sudo', 'chmod', '-R', '2770', share_path], check=True)

    print(f"Samba share '{share_name}' setup successfully at '{share_path}' with group '{group_name}' access.")

def prompt_for_details():
    share_name = input("Enter the name for the Samba share: ")
    share_path = input("Enter the path for the Samba share: ")
    group_name = input("Enter the group name for accessing the share: ")

    if not os.path.exists(share_path):
        os.makedirs(share_path)
        print(f"Directory '{share_path}' created.")

    return share_name, share_path, group_name

def main():
    # Check if Samba is installed
    try:
        subprocess.run(['which', 'smbd'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Samba is already installed.")
    except subprocess.CalledProcessError:
        install_samba()

    share_name, share_path, group_name = prompt_for_details()

    # Create the group if it doesn't exist
    try:
        subprocess.run(['getent', 'group', group_name], check=True)
        print(f"Group '{group_name}' already exists.")
    except subprocess.CalledProcessError:
        create_group(group_name)

    # Prompt for user details to add them to the group and Samba
    while True:
        username = input("Enter a username to add to the group and as a Samba user (or 'done' to finish): ")
        if username.lower() == 'done':
            break
        add_user_to_group(username, group_name)
        add_samba_user(username)

    # Set up the Samba share with the specified group
    setup_samba_share(share_name, share_path, group_name)

if __name__ == "__main__":
    main()
