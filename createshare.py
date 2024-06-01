import os
import subprocess

def install_samba():
    print("Installing Samba...")
    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'samba'], check=True)
    print("Samba installed successfully.")

def setup_samba_share(share_name, share_path):
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
   public = yes
   writable = yes
   guest ok = yes
"""

    with open('smb.conf.tmp', 'w') as temp_conf:
        with open(smb_conf_path, 'r') as original_conf:
            temp_conf.write(original_conf.read())
        temp_conf.write(share_config)

    # Replace the smb.conf with the new one
    subprocess.run(['sudo', 'mv', 'smb.conf.tmp', smb_conf_path], check=True)

    # Restart Samba to apply changes
    subprocess.run(['sudo', 'systemctl', 'restart', 'smbd'], check=True)

    # Change the group permission so anyone can access it
    subprocess.run(['sudo', 'chmod', '777', share_path], check=True)
    print(f"Samba share '{share_name}' setup successfully at '{share_path}'.")

def prompt_for_share_details():
    share_name = input("Enter the name for the Samba share: ")
    share_path = input("Enter the path for the Samba share: ")

    if not os.path.exists(share_path):
        os.makedirs(share_path)
        print(f"Directory '{share_path}' created.")

    return share_name, share_path

def main():
    # Check if Samba is installed
    try:
        subprocess.run(['which', 'smbd'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Samba is already installed.")
    except subprocess.CalledProcessError:
        install_samba()

    share_name, share_path = prompt_for_share_details()
    setup_samba_share(share_name, share_path)

if __name__ == "__main__":
    main()
