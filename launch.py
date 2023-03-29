import os
import urllib.request
import zipfile
import sys
import platform
import subprocess

server_path = input("Enter full server path: ")
username = os.getlogin()

if not os.path.exists(server_path):
    os.makedirs(server_path)

# Determine operating system
os_name = platform.system().lower()

# Determine username
if os_name == "windows":
    username = os.getlogin()
else:
    username = os.getenv("USER")

# Define download URL based on operating system
if os_name == "darwin":
    download_url = "https://download.oracle.com/java/17/latest/jdk-17_macos-aarch64_bin.dmg"
    mount_cmd = "hdiutil attach -quiet -noverify -nobrowse -mountpoint /tmp/jdk_mount /tmp/jdk.dmg"
    install_cmd = "sudo installer -pkg /tmp/jdk_mount/JDK\ 17.pkg -target /"
    unmount_cmd = "hdiutil detach -quiet /tmp/jdk_mount"
elif os_name == "windows":
    download_url = "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe"
    install_cmd = f"start /wait /D\"{os.getcwd()}\" jdk-17_windows-x64_bin.exe /s ADDLOCAL=\"ToolsFeature\" /INSTALLDIR=\"C:\\Program Files\\Java\\jdk-17\" /STATIC=1 /L %TEMP%\\jdk-install.log"
elif os_name == "linux":
    if "debian" in platform.linux_distribution()[0].lower():
        download_url = "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.deb"
        install_cmd = "sudo dpkg -i jdk-17_linux-x64_bin.deb"
    elif "arch" in platform.linux_distribution()[0].lower():
        download_url = "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz"
        install_cmd = "sudo tar -C /opt -xzf jdk-17_linux-x64_bin.tar.gz"
    else:
        print("Unsupported Linux distribution")
        exit()

# Download JDK installer
urllib.request.urlretrieve(download_url, "/tmp/jdk.dmg" if os_name == "darwin" else "jdk-17.exe" if os_name == "windows" else "jdk-17.deb" if "debian" in platform.linux_distribution()[0].lower() else "jdk-17.tar.gz")

# Mount JDK installer (Mac only)
if os_name == "darwin":
    os.system(mount_cmd)

# Install JDK
os.system(install_cmd)

# Unmount JDK installer (Mac only)
if os_name == "darwin":
    os.system(unmount_cmd)

# Set JAVA_HOME environment variable
if os_name == "windows":
    java_home_path = r"C:\Program Files\Java\jdk-17"
    os.environ["JAVA_HOME"] = java_home_path
    os.system(f'setx JAVA_HOME "{java_home_path}" /M')
elif os_name == "darwin":
    os.environ["JAVA_HOME"] = "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home"
    os.system('echo "export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home" >> ~/.bash_profile')
elif "debian" in platform.linux_distribution()[0].lower():
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/jdk-17"
    os.system('echo "export JAVA_HOME=/usr/lib/jvm/jdk-17" >> ~/.bashrc')
elif "arch" in platform.linux_distribution()[0].lower():
    os.environ["JAVA_HOME"] = "/opt/jdk-17"
    os.system('echo "export JAVA_HOME=/opt/jdk-17" >> ~/.bashrc')

# Download the latest version of Minecraft server
response = urllib.request.urlopen("https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar")
version_manifest = response.read().decode()
version_manifest = json.loads(version_manifest)

latest_version = version_manifest["latest"]["release"]
server_jar_url = None
for version in version_manifest["versions"]:
    if version["id"] == latest_version:
        version_url = version["url"]
        response = urllib.request.urlopen(version_url)
        version_manifest = response.read().decode()
        version_manifest = json.loads(version_manifest)
        server_jar_url = version_manifest["downloads"]["server"]["url"]
        break

if server_jar_url:
    server_jar_name = server_jar_url.split("/")[-1]
    server_jar_path = os.path.join(server_path, server_jar_name)

    urllib.request.urlretrieve(server_jar_url, server_jar_path)

    with zipfile.ZipFile(server_jar_path, "r") as zip_ref:
        zip_ref.extractall(server_path)

    os.remove(server_jar_path)

    os.chown(server_path, username, username)

    print("Minecraft server installed successfully!")
    # Start the Minecraft server
    os.chdir(server_path)
    os.system("java -Xmx1024M -Xms1024M -jar server.jar nogui &")
else:
    print("Failed to find the latest version of Minecraft server.")

# See if user would like to accept the minecraft EULA
eula_accepted = input("Do you accept the Minecraft EULA? (y/n): ")
if eula_accepted.lower() == "y":
    with open(os.path.join(server_path, "eula.txt"), "w") as f:
        f.write("eula=true\n")
    elif eula_accepted.lower() == "n":
        print("User must accept EULA to use Minecraft server")

# Check if user wants to install quality of life mods
install_mods = input("Do you want to install quality of life mods? (y/n): ")
if install_mods.lower() == "y":
    mods_dir = os.path.join(server_path, "mods")
    if not os.path.exists(mods_dir):
        os.makedirs(mods_dir)

    # Download and install quality of life mods
    mod_urls = [
        "https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/fabric",
        "https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/fabric",
        "https://cdn.modrinth.com/data/gvQqBUqZ/versions/14hWYkog/lithium-fabric-mc1.19.4-0.11.1.jar",
        "https://cdn.modrinth.com/data/P7dR8mSH/versions/Pz1hLqTB/fabric-api-0.76.0%2B1.19.4.jar"
    ]

    for url in mod_urls:
        mod_name = url.split("/")[-1]
        mod_path = os.path.join(mods_dir, mod_name)
        urllib.request.urlretrieve(url, mod_path)

    print("Quality of life mods installed successfully!")
else:
    print("Skipping quality of life mod installation.")

# Download Fabric loader
fabric_loader_url = "https://meta.fabricmc.net/v2/versions/loader/1.19.4/0.14.18/0.11.2/server/jar"
fabric_loader_path = os.path.join(server_path, "fabric-server.jar")

urllib.request.urlretrieve(fabric_loader_url, fabric_loader_path)

# Rename the downloaded file to "fabric-loader.jar"
os.rename('fabric-server-mc.1.19.4-loader.0.14.18-launcher.0.11.2', 'fabric-server')

# Ask if user wants to edit server.properties
answer = input('Do you want to edit server.properties? (Y/n) ')
if answer.lower() == 'y':
    with open('server.properties', 'r') as file:
        lines = file.readlines()

    # Edit the properties here
    for i, line in enumerate(lines):
        if line.startswith('property_name'):
            lines[i] = 'property_name=new_value\n'

    with open('server.properties', 'w') as file:
        file.writelines(lines)

# Launch the server with Fabric loader
os.chdir(server_path)
os.system(f"java -jar {fabric_loader_path} nogui")
