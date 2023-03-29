import os
import platform
import shutil
import urllib.request
import zipfile

# Set JAVA_HOME environment variable
java_home_path = input("Enter path to Java home: ")
os.environ["JAVA_HOME"] = java_home_path

# Set server directory
server_dir = input("Enter path to server directory: ")

# Download Minecraft server jar
server_jar_url = "https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar"
server_jar_path = os.path.join(server_dir, "server.jar")
with urllib.request.urlopen(server_jar_url) as response, open(server_jar_path, "wb") as out_file:
    shutil.copyfileobj(response, out_file)

# Download Fabric server jar
fabric_loader_version = "0.11.2"
fabric_server_jar_url = f"https://meta.fabricmc.net/v2/versions/loader/1.19.4/0.14.18/{fabric_loader_version}/server/jar"
os.rename('fabric-server-mc.1.19.4-loader.0.14.18-launcher.0.11.2.jar', 'fabric-server.jar')
fabric_server_jar_path = os.path.join(server_dir, "fabric-server.jar")
with urllib.request.urlopen(fabric_server_jar_url) as response, open(fabric_server_jar_path, "wb") as out_file:
    shutil.copyfileobj(response, out_file)

# Create mods directory
mods_dir = os.path.join(server_dir, "mods")
if not os.path.exists(mods_dir):
    os.makedirs(mods_dir)

# Download quality of life mods
qol_mods = [
    {
        "name": "Floodgate-Fabric",
        "url": "https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/fabric"
    },
    {
        "name": "Geyser-Fabric",
        "url": "https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/fabric"
    },
    {
        "name": "lithium-fabric-mc1.19.4-0.11.1",
        "url": "https://cdn.modrinth.com/data/gvQqBUqZ/versions/14hWYkog/lithium-fabric-mc1.19.4-0.11.1.jar"
    },
    {
        "name": "fabric-api-0.76.0+1.19.4",
        "url": "https://cdn.modrinth.com/data/P7dR8mSH/versions/Pz1hLqTB/fabric-api-0.76.0%2B1.19.4.jar"
    }
]

# Delete all existing files in the mods directory
for filename in os.listdir(mods_dir):
    file_path = os.path.join(mods_dir, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

# Install QoL mods
install_qol_mods = input("Do you want to install the QoL Mods? (y/n): ")
if install_qol_mods.lower() == 'y':
    for mod in qol_mods:
        mod_path = os.path.join(mods_dir, f"{mod['name']}.jar")
        with urllib.request.urlopen(mod["url"]) as response, open(mod_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

# Start server
os.chdir(server_dir)
os.system(f'java -jar "{fabric_server_jar_path}" nogui')
