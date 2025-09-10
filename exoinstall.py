import os
import sys
import subprocess
import shutil
import hashlib
import tempfile

class ExoInstaller:
    class Colors:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'

    REPO_URL = "https://github.com/debuggyo/Exo.git"

    def __init__(self):
        self.default_config_dir = os.path.expanduser("~/.config/")
        self.source_dir = None
        self.config_dir = self.default_config_dir
        self.aur_helper = None
        self.dry_run = False
        self.protected_files = ["user_settings.json", "colors.scss"]
        self.auto_confirm_overwrite = False
        self.auto_confirm_delete = False

    def run(self):
        self.print_header("Welcome to the Exo Installer")

        # The distro check is now done only for a full installation.
        # This allows the update function to be used on other distros.

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.clone_repo(self.REPO_URL, temp_dir)
                self.source_dir = temp_dir

                print("1: Full Installation")
                print("2: Update Existing Installation")
                print("3: Run in Test Mode (Dry Run)")
                print("q: Quit")
                choice = self.get_user_choice("Select an option: ", ["1", "2", "3", "q"])

                if choice == '1':
                    self.full_install()
                elif choice == '2':
                    self.update_install()
                elif choice == '3':
                    self.enter_test_mode()
                elif choice == 'q':
                    print("Quitting.")
        except Exception as e:
            print(f"{self.Colors.RED}An unexpected error occurred: {e}{self.Colors.ENDC}")
            sys.exit(1)
        finally:
            print("\nTemporary files have been cleaned up.")

    def clone_repo(self, repo_url, dest_dir):
        if not shutil.which("git"):
            print(f"{self.Colors.RED}Git command not found. Please install Git to continue.{self.Colors.ENDC}")
            sys.exit(1)

        print(f"Cloning '{repo_url}' into a temporary directory...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', repo_url, dest_dir],
            capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            print(f"{self.Colors.RED}Error cloning repository: {result.stderr}{self.Colors.ENDC}")
            sys.exit(1)

    def enter_test_mode(self):
        self.dry_run = True
        self.config_dir = "/tmp/exo_install_test/"
        self.print_header("Entering Test Mode")
        print(f"{self.Colors.YELLOW}All file changes will be applied to: {self.config_dir}{self.Colors.ENDC}")
        print(f"{self.Colors.YELLOW}System commands will be simulated.{self.Colors.ENDC}")
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
        os.makedirs(self.config_dir)

        print("\nWhich workflow would you like to test?")
        print("1: Full Installation")
        print("2: Update Existing Installation")
        print("q: Back to Main Menu")
        test_choice = self.get_user_choice("Select a test option: ", ["1", "2", "q"])

        if test_choice == '1':
            self.full_install()
        elif test_choice == '2':
            self.update_install()
        elif test_choice == 'q':
            self.dry_run = False
            self.config_dir = self.default_config_dir
            self.run()

    def run_command(self, cmd, **kwargs):
        if self.dry_run:
            print(f"{self.Colors.YELLOW}[DRY RUN] Would execute: {' '.join(cmd)}{self.Colors.ENDC}")
            return subprocess.CompletedProcess(cmd, 0)
        else:
            try:
                return subprocess.run(cmd, check=True, **kwargs)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"{self.Colors.RED}Error executing command: {e}{self.Colors.ENDC}")
                return None

    def print_header(self, title):
        print(f"\n{self.Colors.HEADER}{self.Colors.BOLD}{'='*50}{self.Colors.ENDC}")
        print(f" {self.Colors.HEADER}{self.Colors.BOLD}{title}{self.Colors.ENDC}")
        print(f"{self.Colors.HEADER}{self.Colors.BOLD}{'='*50}{self.Colors.ENDC}")

    def get_user_choice(self, prompt, options):
        # Check if we can use a raw terminal for immediate input
        try:
            # Unix-like systems (Linux, macOS)
            import termios, tty

            print(f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}", end='', flush=True)

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    char = sys.stdin.read(1)
                    if char.lower() in options:
                        print(char) # Echo the key press
                        return char.lower()

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        except ImportError:
            # Fallback for Windows
            try:
                import msvcrt
                print(f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}", end='', flush=True)
                while True:
                    char = msvcrt.getch().decode('utf-8')
                    if char.lower() in options:
                        print(char) # Echo the key press
                        return char.lower()
            except ImportError:
                # Fallback to standard line-buffered input if neither works
                print(f"\n{self.Colors.YELLOW}Warning: Immediate input is not supported. Please press 'Enter' after your choice.{self.Colors.ENDC}")
                while True:
                    option = input(f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}").lower()
                    if option in options:
                        return option
                    print(f"{self.Colors.RED}Invalid input.{self.Colors.ENDC}")

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except IOError:
            return None

    def check_arch_distro(self):
        self.print_header("Distro Check")
        if os.path.exists('/etc/arch-release'):
            print(f"{self.Colors.GREEN}Detected Arch-based distribution. Proceeding...{self.Colors.ENDC}")
            return True
        else:
            print(f"{self.Colors.RED}This full installation is designed for Arch-based distributions only.{self.Colors.ENDC}")
            print(f"{self.Colors.RED}Warning: '/etc/arch-release' not found. Cannot proceed with full installation.{self.Colors.ENDC}")
            return False

    def check_aur_helper(self):
        self.print_header("Checking for AUR Helper")
        if shutil.which("paru"):
            self.aur_helper = "paru"
        elif shutil.which("yay"):
            self.aur_helper = "yay"

        if self.aur_helper:
            print(f"{self.Colors.GREEN}Found AUR helper: {self.aur_helper}{self.Colors.ENDC}")
            return True

        print(f"{self.Colors.YELLOW}Neither paru nor yay found. Attempting to install yay...{self.Colors.ENDC}")
        if self.install_yay():
            if shutil.which("yay"):
                self.aur_helper = "yay"
                return True

        print(f"{self.Colors.RED}Failed to find or install an AUR helper.{self.Colors.ENDC}")
        return False

    def install_yay(self):
        print("Installing base-devel and git...")
        if not self.run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"]):
            return False

        yay_bin_dir = "yay-bin"
        if os.path.exists(yay_bin_dir):
            print(f"Directory '{yay_bin_dir}' already exists. Removing it...")
            shutil.rmtree(yay_bin_dir)

        print("Cloning yay from the AUR...")
        if not self.run_command(["git", "clone", "https://aur.archlinux.org/yay-bin.git"]):
            return False

        try:
            os.chdir(yay_bin_dir)
            print("Running makepkg to build and install yay...")
            result = self.run_command(["makepkg", "-si", "--noconfirm"])
            os.chdir("..")
            shutil.rmtree(yay_bin_dir)
            return result is not None
        except Exception as e:
            print(f"{self.Colors.RED}An error occurred during yay installation: {e}{self.Colors.ENDC}")
            if os.getcwd().endswith(yay_bin_dir):
                os.chdir("..")
            return False

    def install_dependencies(self):
        self.print_header("Installing Dependencies")
        dependencies = [
            "python-ignis-git", "ignis-gvc", "ttf-material-symbols-variable-git",
            "matugen-bin", "swww", "gnome-bluetooth-3.0", "adw-gtk-theme", "dart-sass"
        ]
        self.run_command([self.aur_helper, "-S", "--noconfirm"] + dependencies)

    def check_desktop(self):
        self.print_header("Checking Desktop Environment")
        installed_desktops = []
        if not self.dry_run:
            for desktop in ["niri", "hyprland"]:
                if shutil.which(desktop):
                    installed_desktops.append(desktop)

        if len(installed_desktops) == 0:
            return self.install_desktop()
        elif len(installed_desktops) == 1:
            print(f"Found existing desktop: {installed_desktops[0]}")
            return installed_desktops[0]
        else:
            print("Found both Niri and Hyprland.")
            return "both"

    def install_desktop(self):
        self.print_header("Desktop Environment Installation")
        print("Neither Niri nor Hyprland found. Would you like to install one?")
        print("1: Niri")
        print("2: Hyprland")
        print("3: Both")
        print("q: Quit")

        choice = self.get_user_choice("Select an option: ", ["1", "2", "3", "q"])

        if choice == "1":
            print("Installing Niri...")
            if self.run_command(["sudo", "pacman", "-S", "--noconfirm", "niri"]):
                return "niri"
        elif choice == "2":
            print("Installing Hyprland...")
            if self.run_command(["sudo", "pacman", "-S", "--noconfirm", "hyprland"]):
                return "hyprland"
        elif choice == "3":
            print("Installing Niri and Hyprland...")
            if self.run_command(["sudo", "pacman", "-S", "--noconfirm", "niri", "hyprland"]):
                return "both"
        elif choice == "q":
            print("Quitting.")
            sys.exit(0)

        print(f"{self.Colors.RED}Installation failed or cancelled. Cannot proceed.{self.Colors.ENDC}")
        return None

    def install_desktop_configs(self, desktop_env):
        if desktop_env in ["niri", "both"]:
            print("Copying Niri config...")
            niri_config_dir = os.path.join(self.config_dir, "niri")
            os.makedirs(niri_config_dir, exist_ok=True)
            niri_source = os.path.join(self.source_dir, "exodefaults", "config.kdl")
            niri_dest = os.path.join(niri_config_dir, "config.kdl")

            if os.path.exists(niri_dest):
                print(f"{self.Colors.YELLOW}Niri config already exists.{self.Colors.ENDC}")
                choice = self.get_user_choice("Backup (b), Overwrite (o), Skip (s)? ", ['b', 'o', 's'])
                if choice == 'b':
                    print(f"Backing up {niri_dest}...")
                    shutil.copy2(niri_dest, niri_dest + ".bak")
                elif choice == 'o':
                    print(f"Overwriting {niri_dest}...")
                elif choice == 's':
                    print(f"Skipping {niri_dest}...")
                    return
            shutil.copy2(niri_source, niri_dest)

        if desktop_env in ["hyprland", "both"]:
            print("Copying Hyprland config...")
            hypr_config_dir = os.path.join(self.config_dir, "hyprland")
            os.makedirs(hypr_config_dir, exist_ok=True)
            hypr_source = os.path.join(self.source_dir, "exodefaults", "hyprland.conf")
            hypr_dest = os.path.join(hypr_config_dir, "hyprland.conf")

            if os.path.exists(hypr_dest):
                print(f"{self.Colors.YELLOW}Hyprland config already exists.{self.Colors.ENDC}")
                choice = self.get_user_choice("Backup (b), Overwrite (o), Skip (s)? ", ['b', 'o', 's'])
                if choice == 'b':
                    print(f"Backing up {hypr_dest}...")
                    shutil.copy2(hypr_dest, hypr_dest + ".bak")
                elif choice == 'o':
                    print(f"Overwriting {hypr_dest}...")
                elif choice == 's':
                    print(f"Skipping {hypr_dest}...")
                    return
            shutil.copy2(hypr_source, hypr_dest)

    def final_setup(self):
        self.print_header("Final Setup")
        default_wallpaper_path = os.path.join(self.source_dir, "exodefaults", "default_wallpaper.png")
        wallpaper_dir = os.path.expanduser("~/Pictures/Wallpapers")
        if self.dry_run:
            wallpaper_dir = os.path.join(self.config_dir, "Pictures/Wallpapers")

        os.makedirs(wallpaper_dir, exist_ok=True)
        default_wallpaper_dest = os.path.join(wallpaper_dir, "default.png")
        if not os.path.exists(default_wallpaper_dest):
            print("Copying default wallpaper...")
            shutil.copyfile(default_wallpaper_path, default_wallpaper_dest)

        print(f"{self.Colors.GREEN}Default wallpaper placed in {wallpaper_dir}{self.Colors.ENDC}")
        print("Wallpaper will be set on first desktop launch.")

    def full_install(self):
        self.print_header("Starting Full Exo Installation")

        # Perform the distro check here
        if not self.check_arch_distro():
            return

        if not self.dry_run:
            if not self.check_aur_helper():
                return
            self.install_dependencies()
        else:
            print(f"{self.Colors.YELLOW}[DRY RUN] Skipping AUR helper check and dependency installation.{self.Colors.ENDC}")

        desktop_env = self.check_desktop()
        if not desktop_env:
            return

        core_folders = ["ignis", "matugen"]
        for folder in core_folders:
            source = os.path.join(self.source_dir, folder)
            destination = os.path.join(self.config_dir, folder)
            if os.path.exists(destination):
                print(f"{self.Colors.YELLOW}Warning: '{destination}' already exists.{self.Colors.ENDC}")
                choice = self.get_user_choice("Backup (b), Overwrite (o), or Quit (q)? ", ['b', 'o', 'q'])
                if choice == 'b':
                    print(f"Backing up {destination}...")
                    shutil.move(destination, destination + "-backup")
                elif choice == 'o':
                    print(f"Overwriting {destination}...")
                    shutil.rmtree(destination)
                elif choice == 'q':
                    sys.exit(0)
            try:
                shutil.copytree(source, destination)
                print(f"{self.Colors.GREEN}Copied '{source}' to '{destination}'.{self.Colors.ENDC}")
            except Exception as e:
                print(f"{self.Colors.RED}Error copying '{source}': {e}{self.Colors.ENDC}")

        self.install_desktop_configs(desktop_env)
        self.final_setup()
        print(f"\n{self.Colors.GREEN}Installation complete.{self.Colors.ENDC}")

    def update_install(self):
        self.print_header("Updating Existing Exo Installation")

        overwrite_choice = self.get_user_choice("\nHow to handle file overwrites? (y: Yes to all, n: Prompt for each): ", ['y', 'n'])
        if overwrite_choice == 'y':
            self.auto_confirm_overwrite = True

        delete_choice = self.get_user_choice("How to handle orphaned files? (y: Yes to all, n: Prompt for each): ", ['y', 'n'])
        if delete_choice == 'y':
            self.auto_confirm_delete = True

        core_folders = ["ignis", "matugen"]
        for folder in core_folders:
            source_path = os.path.join(self.source_dir, folder)
            dest_path = os.path.join(self.config_dir, folder)

            if not os.path.isdir(dest_path):
                print(f"{self.Colors.YELLOW}Warning: '{dest_path}' not found. Skipping update for this folder.{self.Colors.ENDC}")
                continue

            print(f"\n--- Comparing folder: {self.Colors.BLUE}{folder}{self.Colors.ENDC} ---")

            for root, dirs, files in os.walk(source_path):
                dirs[:] = [d for d in dirs if d != '__pycache__']

                for file in files:
                    if os.path.basename(file) in self.protected_files:
                        continue

                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_path)
                    dest_file = os.path.join(dest_path, rel_path)
                    self.compare_and_copy(source_file, dest_file)

            for root, dirs, files in os.walk(dest_path):
                dirs[:] = [d for d in dirs if d != '__pycache__']

                for file in files:
                    if os.path.basename(file) in self.protected_files:
                        continue

                    dest_file = os.path.join(root, file)
                    rel_path = os.path.relpath(dest_file, dest_path)
                    source_file = os.path.join(source_path, rel_path)

                    if not os.path.exists(source_file):
                        self.prompt_and_delete(dest_file)

        print(f"\n{self.Colors.GREEN}Update check complete.{self.Colors.ENDC}")

    def compare_and_copy(self, source, dest):
        source_hash = self.get_file_hash(source)
        dest_hash = self.get_file_hash(dest)

        if dest_hash is None:
            print(f"{self.Colors.GREEN}New file found: Copying '{os.path.basename(source)}'{self.Colors.ENDC}")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(source, dest)
        elif source_hash != dest_hash:
            print(f"{self.Colors.YELLOW}File mismatch: '{os.path.basename(source)}'{self.Colors.ENDC}")

            if self.auto_confirm_overwrite:
                print(f"  Updating '{os.path.basename(source)}' (automatic).")
                shutil.copy2(source, dest)
            else:
                choice = self.get_user_choice("  Overwrite with latest version? (y/n): ", ['y', 'n'])
                if choice == 'y':
                    print(f"  Updating '{os.path.basename(source)}'...")
                    shutil.copy2(source, dest)

    def prompt_and_delete(self, file_path):
        print(f"{self.Colors.YELLOW}Orphaned file found: '{os.path.basename(file_path)}' exists in your config but not in the source.{self.Colors.ENDC}")

        if self.auto_confirm_delete:
            print(f"  Deleting '{os.path.basename(file_path)}' (automatic).")
            os.remove(file_path)
        else:
            choice = self.get_user_choice("  Delete this file? (y/n): ", ['y', 'n'])
            if choice == 'y':
                print(f"  Deleting '{os.path.basename(file_path)}'...")
                os.remove(file_path)

if __name__ == "__main__":
    if os.geteuid() == 0:
        print("This script should not be run as root. Please run as a regular user.")
        sys.exit(1)

    installer = ExoInstaller()
    installer.run()
