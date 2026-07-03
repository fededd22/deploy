#!/usr/bin/env python3
import json
import subprocess
import os
import sys
import time
import shutil
import platform

# Configuration
CONFIG = {
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [
        {
            "listen": "0.0.0.0",
            "port": 8080,
            "protocol": "vless",
            "settings": {
                "clients": [
                    {
                        "id": "d2cb8181-233c-4d18-9972-8a1b04db0044",
                        "level": 0
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "wsSettings": {
                    "path": "/by_moon"
                },
                "sockopt": {
                    "tcpFastOpen": True,
                    "tcpKeepAliveInterval": 15
                }
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {
                "domainStrategy": "UseIPv4"
            },
            "streamSettings": {
                "sockopt": {
                    "tcpFastOpen": True
                }
            }
        }
    ]
}

DOCKERFILE = """FROM teddysun/v2ray:latest

COPY config.json /etc/v2ray/config.json

EXPOSE 8080

CMD ["/usr/bin/v2ray", "run", "-config", "/etc/v2ray/config.json"]
"""

def install_docker():
    """Installe Docker automatiquement selon le système d'exploitation"""
    system = platform.system().lower()
    
    print("📦 Installation de Docker en cours...")
    
    if system == "linux":
        # Détecter la distribution Linux
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
        except:
            os_info = ""
        
        if 'ubuntu' in os_info or 'debian' in os_info:
            # Ubuntu/Debian
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common",
                "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
                "sudo add-apt-repository -y 'deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable'",
                "sudo apt-get update",
                "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
                "sudo usermod -aG docker $USER"
            ]
            
            for cmd in commands:
                print(f"⏳ Exécution: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0 and 'already' not in result.stderr:
                    print(f"⚠️  Warning: {result.stderr}")
            
            print("✅ Docker installé avec succès sur Ubuntu/Debian")
            print("⚠️  Veuillez vous déconnecter et vous reconnecter pour que les permissions prennent effet")
            return True
            
        elif 'centos' in os_info or 'rhel' in os_info or 'fedora' in os_info:
            # CentOS/RHEL/Fedora
            commands = [
                "sudo yum install -y yum-utils",
                "sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
                "sudo yum install -y docker-ce docker-ce-cli containerd.io",
                "sudo systemctl start docker",
                "sudo systemctl enable docker",
                "sudo usermod -aG docker $USER"
            ]
            
            for cmd in commands:
                print(f"⏳ Exécution: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0 and 'already' not in result.stderr:
                    print(f"⚠️  Warning: {result.stderr}")
            
            print("✅ Docker installé avec succès sur CentOS/RHEL/Fedora")
            return True
    
    elif system == "darwin":
        # macOS
        print("🍎 macOS détecté")
        print("📥 Téléchargement de Docker Desktop pour macOS...")
        
        # Vérifier si Homebrew est installé
        if shutil.which('brew'):
            print("⏳ Installation via Homebrew...")
            subprocess.run(['brew', 'install', '--cask', 'docker'], check=False)
            print("✅ Docker Desktop installé via Homebrew")
            print("⚠️  Veuillez lancer Docker Desktop depuis votre dossier Applications")
            return True
        else:
            print("❌ Homebrew n'est pas installé")
            print("📥 Téléchargez Docker Desktop manuellement depuis: https://www.docker.com/products/docker-desktop")
            return False
    
    elif system == "windows":
        # Windows
        print("🪟 Windows détecté")
        print("📥 Téléchargement de Docker Desktop pour Windows...")
        print("🔗 Téléchargez depuis: https://www.docker.com/products/docker-desktop")
        print("⚠️  Assurez-vous d'avoir WSL2 activé")
        return False
    
    else:
        print(f"❌ Système non supporté: {system}")
        print("📥 Installez Docker manuellement depuis: https://docs.docker.com/get-docker/")
        return False

def check_docker():
    """Vérifie si Docker est installé, l'installe sinon"""
    if shutil.which('docker') is not None:
        return True
    
    print("❌ Docker n'est pas installé")
    response = input("🔧 Voulez-vous installer Docker automatiquement ? (o/N): ").strip().lower()
    
    if response == 'o' or response == 'oui' or response == 'y' or response == 'yes':
        return install_docker()
    else:
        print("❌ Installation annulée. Veuillez installer Docker manuellement.")
        return False

def create_files():
    """Crée les fichiers config.json et Dockerfile"""
    try:
        with open('config.json', 'w') as f:
            json.dump(CONFIG, f, indent=2)
        print("✅ config.json créé avec succès")
        
        with open('Dockerfile', 'w') as f:
            f.write(DOCKERFILE)
        print("✅ Dockerfile créé avec succès")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des fichiers: {e}")
        return False

def build_image():
    """Construit l'image Docker"""
    print("\n📦 Construction de l'image Docker...")
    try:
        subprocess.run(
            ['docker', 'build', '-t', 'v2ray-moon', '.'],
            check=True,
            capture_output=False
        )
        print("✅ Image Docker construite avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la construction: {e}")
        return False

def run_container():
    """Exécute le conteneur Docker"""
    print("\n🚀 Lancement du conteneur V2Ray...")
    try:
        # Arrêter et supprimer l'ancien conteneur s'il existe
        subprocess.run(['docker', 'rm', '-f', 'v2ray-moon-container'], 
                      capture_output=True, check=False)
        
        # Lancer le nouveau conteneur
        subprocess.run([
            'docker', 'run', '-d',
            '--name', 'v2ray-moon-container',
            '-p', '8080:8080',
            '--restart', 'unless-stopped',
            'v2ray-moon'
        ], check=True)
        print("✅ Conteneur V2Ray lancé avec succès sur le port 8080")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False

def verify_docker():
    """Vérifie que Docker fonctionne correctement"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker version: {result.stdout.strip()}")
            return True
        return False
    except:
        return False

def show_container_status():
    """Affiche le statut du conteneur"""
    print("\n📊 Statut du conteneur:")
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=v2ray-moon-container'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage du statut: {e}")

def show_logs():
    """Affiche les logs du conteneur"""
    print("\n📜 Logs du conteneur (dernières lignes):")
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', '20', 'v2ray-moon-container'],
            capture_output=True,
            text=True
        )
        print(result.stdout or "Aucun log disponible")
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des logs: {e}")

def get_server_ip():
    """Récupère l'IP du serveur"""
    try:
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
        # Essayer d'obtenir l'IP publique
        try:
            import urllib.request
            public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            return public_ip
        except:
            return ip
    except:
        return "VOTRE_IP"

def main():
    print("=" * 50)
    print("🚀 Déploiement automatique V2Ray VLESS")
    print("=" * 50)
    print("👤 Telegram: @moonalgerie")
    print("")
    
    # Vérifier et installer Docker
    if not check_docker():
        print("\n❌ Impossible de continuer sans Docker.")
        sys.exit(1)
    
    # Attendre un peu pour que Docker soit prêt
    time.sleep(3)
    
    # Vérifier que Docker fonctionne
    if not verify_docker():
        print("❌ Docker n'est pas opérationnel. Veuillez redémarrer votre session et réessayer.")
        sys.exit(1)
    
    # Créer les fichiers
    if not create_files():
        sys.exit(1)
    
    # Construire l'image
    if not build_image():
        sys.exit(1)
    
    # Lancer le conteneur
    if not run_container():
        sys.exit(1)
    
    # Afficher les informations
    time.sleep(2)
    show_container_status()
    show_logs()
    
    server_ip = get_server_ip()
    
    print("\n" + "=" * 50)
    print("✅ Déploiement terminé avec succès!")
    print("📌 Votre serveur VLESS est accessible sur:")
    print(f"   ws://{server_ip}:8080/by_moon")
    print("🆔 Client ID: d2cb8181-233c-4d18-9972-8a1b04db0044")
    print("📝 Configuration sauvegardée dans config.json")
    print("=" * 50)
    
    print("\n💡 Commandes utiles:")
    print("  - Voir les logs: docker logs v2ray-moon-container")
    print("  - Arrêter: docker stop v2ray-moon-container")
    print("  - Démarrer: docker start v2ray-moon-container")
    print("  - Supprimer: docker rm -f v2ray-moon-container")
    
    print("\n⚠️  Si vous êtes sur Linux, vous pourriez avoir besoin de:")
    print("  sudo usermod -aG docker $USER && newgrp docker")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)