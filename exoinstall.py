import os
import sys
import subprocess
import shutil

# Global variable for the standard config path
CONFIG_DIR = os.path.expanduser("~/.config/")

# Reusable function for user prompts
def get_user_choice(prompt, options):
    while True:
        option = input(prompt).lower()
        if option in options:
            return option
        print("Invalid input.")

def install_yay():
    yay_bin_dir = "yay-bin"
    if os.path.exists(yay_bin_dir):
        print(f"Directory '{yay_bin_dir}' already exists. Attempting to remove it...")
        try:
            shutil.rmtree(yay_bin_dir)
        except OSError as e:
            print(f"Error removing existing directory: {e}")
            return False

    try:
        print("Installing base-devel and git from official repos...")
        subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"], check=True)
        print("Cloning yay from the AUR...")
        subprocess.run(["git", "clone", "https://aur.archlinux.org/yay-bin.git"], check=True)
        
        os.chdir(yay_bin_dir)
        print("Running makepkg. Please follow the prompts for sudo password.")
        subprocess.run(["makepkg", "-si", "--noconfirm"], check=True)
        os.chdir("..")

        shutil.rmtree(yay_bin_dir)

        return True

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during yay installation.")
        print(f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.")
        if e.stdout: print(e.stdout.decode())
        if e.stderr: print(e.stderr.decode())
        # Ensure we are in the correct directory before returning
        if os.getcwd().endswith(yay_bin_dir):
            os.chdir("..")
        return False
    except FileNotFoundError:
        print("A required command was not found. Ensure git and base-devel are installed.")
        return False

def check_aur_helper():
    if shutil.which("paru"):
        return "paru"
    
    if shutil.which("yay"):
        return "yay"

    print("Neither paru nor yay found. Attempting to install yay...")
    if install_yay():
        if shutil.which("yay"):
            return "yay"
    
    print("Failed to find or install an AUR helper.")
    return None

def check_desktop():
    installed_desktops = []
    for desktop in ["niri", "hyprland"]:
        if shutil.which(desktop):
            installed_desktops.append(desktop)
    
    if len(installed_desktops) == 0:
        return install_desktop()
    elif len(installed_desktops) == 1:
        return installed_desktops[0]
    else:
        return "both"

def install_desktop():
    print("Neither Niri nor Hyprland found. Asking user which one to install.")
    print("Which desktop do you want to install?")
    print("1: Niri")
    print("2: Hyprland")
    print("3: Both")
    print("4: Ignore")
    print("q: Quit")

    options = {'1': 'niri', '2': 'hyprland', '3': 'both', '4': 'ignore', 'q': 'quit'}
    option = get_user_choice("1, 2, 3, 4 or 'q': ", options)
    
    if option == "1":
        print("Installing Niri...")
        try:
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "niri"], check=True)
            return "niri"
        except subprocess.CalledProcessError:
            print("Failed to install Niri.")
            return None
    elif option == "2":
        print("Installing Hyprland...")
        try:
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "hyprland"], check=True)
            return "hyprland"
        except subprocess.CalledProcessError:
            print("Failed to install Hyprland.")
            return None
    elif option == "3":
        print("Installing Niri and Hyprland...")
        try:
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "niri", "hyprland"], check=True)
            return "both"
        except subprocess.CalledProcessError:
            print("Failed to install Niri and Hyprland.")
            return None
    elif option == "4":
        print("Ignoring desktop installation.")
        return "ignore"
    elif option == "q":
        print("Quitting.")
        sys.exit(0)

def install_dependencies():
    dependencies = [
        "python-ignis-git",
        "ignis-gvc",
        "ttf-material-symbols-variable-git",
        "matugen-bin",
        "swww",
        "gnome-bluetooth-3.0",
        "adw-gtk-theme",
        "dart-sass"
    ]

    try:
        print("Installing dependencies...")
        subprocess.run(["yay", "-S", "--noconfirm"] + dependencies, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies. Error: {e.stderr.decode()}")

def install_optional_dependencies():
    print("Optional dependencies.")
    options = {
        "ttf-rubik": "Rubik Font",
        "bibata-cursor-theme-bin": "Bibata Cursors",
        "gpu-screen-recorder": "GPU Screen Recorder (required for screen recording)",
        "slurp": "Slurp (required for screen recording a region)"
    }

    selected = []

    for package, desc in options.items():
        answer = input(f"Install {desc}? (y/n): ").lower()
        if answer == "y":
            selected.append(package)
    
    if not selected:
        print("No optional dependencies selected.")
        return

    try:
        print(f"Installing {', '.join(selected)}...")
        subprocess.run(["yay", "-S", "--noconfirm"] + selected, check=True)
        
        if "ttf-rubik" in selected:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "font-name", "'Rubik 10'"], check=True)
        if "bibata-cursor-theme-bin" in selected:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", "'Bibata-Modern-Classic'"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install optional dependencies. Error: {e.stderr.decode()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def install_exo():
    print("Starting Exo config installation...")
    
    current_directory = os.getcwd()

    folders_to_copy = ["ignis", "matugen"]
    for folder in folders_to_copy:
        source = os.path.join(current_directory, folder)
        destination = os.path.join(CONFIG_DIR, folder)

        if os.path.exists(destination):
            backup_destination = destination + "-backup"
            print(f"{destination} already exists.")
            print(f"1: Backup to {backup_destination}")
            print("2: Overwrite")
            print("q: Quit")
            
            choice = get_user_choice("1, 2 or 'q': ", ['1', '2', 'q'])
            if choice == '1':
                print(f"Backing up {destination}...")
                shutil.move(destination, backup_destination)
            elif choice == '2':
                print(f"Overwriting {destination}...")
                shutil.rmtree(destination)
            elif choice == 'q':
                print("Quitting.")
                sys.exit(0)

        try:
            shutil.copytree(source, destination)
            print(f"'{source}' copied to '{destination}' successfully.")
        except FileNotFoundError:
            print(f"Error: Source folder '{source}' not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Copy default files
    default_wallpaper_path = os.path.join(current_directory, "exodefaults", "default_wallpaper.png")
    wallpaper_dir = os.path.expanduser("~/Pictures/Wallpapers")
    os.makedirs(wallpaper_dir, exist_ok=True)
    
    default_wallpaper_dest = os.path.join(wallpaper_dir, "default.png")
    if not os.path.exists(default_wallpaper_dest):
        try:
            shutil.copyfile(default_wallpaper_path, default_wallpaper_dest)
            print("Default wallpaper copied.")
        except Exception as e:
            print(f"An error occurred while copying the wallpaper: {e}")

    desktop_env = check_desktop()

    # Niri Config
    if desktop_env in ["niri", "both"]:
        print("Copying Niri config...")
        niri_config_dir = os.path.join(CONFIG_DIR, "niri")
        os.makedirs(niri_config_dir, exist_ok=True)
        
        niri_config_file = os.path.join(niri_config_dir, "config.kdl")
        niri_source = os.path.join(current_directory, "exodefaults", "config.kdl")

        if os.path.exists(niri_config_file):
            print("Existing Niri config.kdl detected.")
            print("1: Backup")
            print("2: Overwrite")
            print("3: Ignore")
            print("q: Quit")
            choice = get_user_choice("1, 2, 3 or 'q': ", ['1', '2', '3', 'q'])

            if choice == "1":
                shutil.copyfile(niri_config_file, niri_config_file + "-backup")
            elif choice == "2":
                os.remove(niri_config_file)
            elif choice == "q":
                sys.exit(0)

        shutil.copyfile(niri_source, niri_config_file)
        print("Default Niri config copied.")
        subprocess.run(["yay", "-S", "--noconfirm", "nautilus", "kitty", "hyprlock"], check=True)
    
    # Hyprland Config
    if desktop_env in ["hyprland", "both"]:
        print("Copying Hyprland config...")
        hyprland_config_dir = os.path.join(CONFIG_DIR, "hyprland")
        os.makedirs(hyprland_config_dir, exist_ok=True)
        
        hyprland_config_file = os.path.join(hyprland_config_dir, "hyprland.conf")
        hyprland_source = os.path.join(current_directory, "exodefaults", "hyprland.conf")

        if os.path.exists(hyprland_config_file):
            print("Existing hyprland.conf detected.")
            print("1: Backup")
            print("2: Overwrite")
            print("3: Ignore")
            print("q: Quit")
            choice = get_user_choice("1, 2, 3 or 'q': ", ['1', '2', '3', 'q'])

            if choice == "1":
                shutil.copyfile(hyprland_config_file, hyprland_config_file + "-backup")
            elif choice == "2":
                os.remove(hyprland_config_file)
            elif choice == "q":
                sys.exit(0)

        shutil.copyfile(hyprland_source, hyprland_config_file)
        print("Default Hyprland config copied.")
        subprocess.run(["yay", "-S", "--noconfirm", "nautilus", "kitty", "hyprlock"], check=True)
        
    # Create empty user_settings.json
    user_settings_file = os.path.join(CONFIG_DIR, "ignis", "user_settings.json")
    try:
        with open(user_settings_file, 'w') as file:
            file.write("{}")
        print(f"File '{user_settings_file}' created successfully.")
    except IOError as e:
        print(f"Error creating file: {e}")

    # Set default wallpaper and generate default color scheme
    subprocess.run(["matugen", "image", default_wallpaper_dest], check=True)

# Main execution logic
def main():
    print("Running initial checks...")
    aur_helper = check_aur_helper()
    if not aur_helper:
        return
        
    install_dependencies()
    install_optional_dependencies()
    install_exo()
    print("Installation complete.")

if __name__ == "__main__":
    main()