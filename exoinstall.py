#!/usr/bin/env python3
import sys

try:
    import termios, tty
except ImportError:
    termios = None
    tty = None
import os
import sys
import subprocess
import shutil
import hashlib
import tempfile


class ExoInstaller:
    class Colors:
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"

    REPO_URL = "https://github.com/debuggyo/Exo.git"

    def __init__(self):
        self.default_config_dir = os.path.expanduser("~/.config/")
        self.source_dir = None
        self.config_dir = self.default_config_dir
        self.aur_helper = None
        self.dry_run = False
        self.protected_files = [
            "user_settings.json",
            "colors.scss",
            "preview-colors.scss",
        ]
        self.auto_confirm_overwrite = False
        self.auto_confirm_delete = False
        self.distro = None
        self.package_manager = None

    def run(self):
        self.print_header("Welcome to the Exo Installer")

        command_exists = shutil.which("exoupdate") is not None

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.clone_repo(self.REPO_URL, temp_dir)
                self.source_dir = temp_dir
                self.update_installed_command_if_needed()

                print("1: Full Installation")
                print("2: Update Existing Installation")
                print("3: Run in Test Mode (Dry Run)")
                print(f"{self.Colors.RED}4: Uninstall Exo{self.Colors.ENDC}")
                print("q: Quit")
                options = ["1", "2", "3", "4", "q"]
                choice = self.get_user_choice("Select an option: ", options)

                if not command_exists and choice in ["1", "2"]:
                    self.install_as_command()

                if choice == "1":
                    self.full_install()
                elif choice == "2":
                    self.update_install()
                elif choice == "3":
                    self.enter_test_mode()
                elif choice == "4":
                    self.uninstall_exo()
                elif choice == "q":
                    print("Quitting.")
        except Exception as e:
            print(
                f"{self.Colors.RED}An unexpected error occurred: {e}{self.Colors.ENDC}"
            )
            sys.exit(1)
        finally:
            print("\nTemporary files have been cleaned up.")

    def clone_repo(self, repo_url, dest_dir):
        if not shutil.which("git"):
            print(
                f"{self.Colors.RED}Git command not found. Please install Git to continue.{self.Colors.ENDC}"
            )
            sys.exit(1)

        print(f"Cloning '{repo_url}' into a temporary directory...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, dest_dir],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(
                f"{self.Colors.RED}Error cloning repository: {result.stderr}{self.Colors.ENDC}"
            )
            sys.exit(1)

    def enter_test_mode(self):
        self.dry_run = True
        self.config_dir = "/tmp/exo_install_test/"
        self.print_header("Entering Test Mode")
        print(
            f"{self.Colors.YELLOW}All file changes will be applied to: {self.config_dir}{self.Colors.ENDC}"
        )
        print(
            f"{self.Colors.YELLOW}System commands will be simulated.{self.Colors.ENDC}"
        )
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
        os.makedirs(self.config_dir)

        print("\nWhich workflow would you like to test?")
        print("1: Full Installation")
        print("2: Update Existing Installation")
        print(f"{self.Colors.RED}3: Uninstall Exo{self.Colors.ENDC}")
        print("q: Back to Main Menu")
        test_choice = self.get_user_choice(
            "Select a test option: ", ["1", "2", "3", "q"]
        )

        if test_choice == "1":
            self.full_install()
        elif test_choice == "2":
            self.update_install()
        elif test_choice == "3":
            self.uninstall_exo()
        elif test_choice == "q":
            self.dry_run = False
            self.config_dir = self.default_config_dir
            self.run()

    def run_command(self, cmd, **kwargs):
        if self.dry_run:
            print(
                f"{self.Colors.YELLOW}[DRY RUN] Would execute: {' '.join(cmd)}{self.Colors.ENDC}"
            )
            return subprocess.CompletedProcess(cmd, 0)
        else:
            try:
                return subprocess.run(cmd, check=True, **kwargs)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(
                    f"{self.Colors.RED}Error executing command: {e}{self.Colors.ENDC}"
                )
                return None

    def print_header(self, title):
        print(f"\n{self.Colors.HEADER}{self.Colors.BOLD}{'=' * 50}{self.Colors.ENDC}")
        print(f" {self.Colors.HEADER}{self.Colors.BOLD}{title}{self.Colors.ENDC}")
        print(f"{self.Colors.HEADER}{self.Colors.BOLD}{'=' * 50}{self.Colors.ENDC}")

    def get_user_choice(self, prompt, options):
        if (
            termios and tty
        ):  # Check if termios and tty were successfully imported at the top
            try:
                print(
                    f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}",
                    end="",
                    flush=True,
                )
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        char = sys.stdin.read(1)
                        if char.lower() in options:
                            print(char)
                            return char.lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except (
                termios.error
            ):  # Only catch termios.error here; ImportError is handled globally
                print(
                    f"\n{self.Colors.YELLOW}Warning: Immediate input is not supported. Please press 'Enter' after your choice.{self.Colors.ENDC}"
                )
                while True:
                    option = input(
                        f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}"
                    ).lower()
                    if option in options:
                        return option
                    print(f"{self.Colors.RED}Invalid input.{self.Colors.ENDC}")
        else:  # Fallback if termios or tty were not imported (e.g., on non-Unix systems)
            print(
                f"\n{self.Colors.YELLOW}Warning: Immediate input is not supported. Please press 'Enter' after your choice.{self.Colors.ENDC}"
            )
            while True:
                option = input(
                    f"{self.Colors.YELLOW}{prompt}{self.Colors.ENDC}"
                ).lower()
                if option in options:
                    return option
                print(f"{self.Colors.RED}Invalid input.{self.Colors.ENDC}")

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except IOError:
            return None

    def detect_distro(self):
        self.print_header("Distro Check")
        if os.path.exists("/etc/arch-release"):
            self.distro = "arch"
            print(
                f"{self.Colors.GREEN}Detected Arch-based distribution.{self.Colors.ENDC}"
            )
        elif os.path.exists("/etc/fedora-release"):
            self.distro = "fedora"
            print(
                f"{self.Colors.GREEN}Detected Fedora-based distribution.{self.Colors.ENDC}"
            )
        elif os.path.exists("/etc/lsb-release"):
            try:
                with open("/etc/lsb-release") as f:
                    for line in f:
                        if "Ubuntu" in line or "Debian" in line.capitalize():
                            self.distro = "ubuntu"
                            print(
                                f"{self.Colors.GREEN}Detected Debian/Ubuntu-based distribution.{self.Colors.ENDC}"
                            )
                            break
            except IOError:
                pass

        if self.distro:
            return True
        else:
            print(
                f"{self.Colors.YELLOW}Unsupported distribution detected.{self.Colors.ENDC}"
            )
            print("You will need to install the required dependencies manually.")
            print(
                "Dependencies: python-ignis, ignis-gvc, matugen, swww, gnome-bluetooth, adw-gtk-theme, dart-sass, material-symbols-font"
            )
            return False

    def get_package_manager(self):
        if self.distro == "arch":
            self.package_manager = "pacman"
        elif self.distro == "fedora":
            self.package_manager = "dnf"
        elif self.distro == "ubuntu":
            self.package_manager = "apt"

    def check_aur_helper(self):
        self.print_header("Checking for AUR Helper")
        if shutil.which("paru"):
            self.aur_helper = "paru"
        elif shutil.which("yay"):
            self.aur_helper = "yay"

        if self.aur_helper:
            print(
                f"{self.Colors.GREEN}Found AUR helper: {self.aur_helper}{self.Colors.ENDC}"
            )
            return True

        print(
            f"{self.Colors.YELLOW}Neither paru nor yay found. Attempting to install yay...{self.Colors.ENDC}"
        )
        if self.install_yay():
            if shutil.which("yay"):
                self.aur_helper = "yay"
                return True

        print(
            f"{self.Colors.RED}Failed to find or install an AUR helper.{self.Colors.ENDC}"
        )
        return False

    def install_yay(self):
        print("Installing base-devel and git...")
        if not self.run_command(
            ["sudo", "pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"]
        ):
            return False

        yay_bin_dir = "yay-bin"
        if os.path.exists(yay_bin_dir):
            print(f"Directory '{yay_bin_dir}' already exists. Removing it...")
            shutil.rmtree(yay_bin_dir)

        print("Cloning yay from the AUR...")
        if not self.run_command(
            ["git", "clone", "https://aur.archlinux.org/yay-bin.git"]
        ):
            return False

        try:
            os.chdir(yay_bin_dir)
            print("Running makepkg to build and install yay...")
            result = self.run_command(["makepkg", "-si", "--noconfirm"])
            os.chdir("..")
            shutil.rmtree(yay_bin_dir)
            return result is not None
        except Exception as e:
            print(
                f"{self.Colors.RED}An error occurred during yay installation: {e}{self.Colors.ENDC}"
            )
            if os.getcwd().endswith(yay_bin_dir):
                os.chdir("..")
            return False

    def install_dependencies(self):
        self.print_header("Installing Dependencies")

        choice = self.get_user_choice(
            "Do you want to automatically install dependencies? (y/n): ", ["y", "n"]
        )
        if choice == "n":
            print(
                "Skipping dependency installation. Please ensure all required packages are installed manually."
            )
            return

        dependencies = {
            "arch": [
                "python-ignis-git",
                "ignis-gvc",
                "ttf-material-symbols-variable-git",
                "matugen-bin",
                "swww",
                "gnome-bluetooth-3.0",
                "adw-gtk-theme",
                "dart-sass",
            ],
            "fedora": [
                "python3-pip",
                "cargo",
                "gnome-bluetooth-libs",
                "adw-gtk3-theme",
                "meson",
                "ninja-build",
                "pkg-config",
                "scdoc",
                "libxkbcommon-devel",
                "wayland-devel",
                "libdisplay-info-devel",
                "libliftoff-devel",
                "pulseaudio-libs-devel",
                "lz4-devel",
                "glib2-devel",
                "gobject-introspection-devel",
                "libgee-devel",
                "vala",
                "gcc",
                "make",
                "wayland-protocols-devel",
                "python3-devel",
            ],
            "ubuntu": [
                "python3-pip",
                "cargo",
                "libgnome-bluetooth-3.0-13",
                "adw-gtk-theme",
                "dart-sass",
                "fonts-material-design-icons-iconfont",
                "meson",
                "ninja-build",
                "pkg-config",
                "scdoc",
                "libxkbcommon-dev",
                "wayland-dev",
                "libdisplay-info-dev",
                "libliftoff-dev",
            ],
        }

        if self.distro in dependencies:
            packages = dependencies[self.distro]
            print(
                f"Attempting to install the following packages: {', '.join(packages)}"
            )
            if self.distro == "arch":
                result = self.run_command(
                    [self.aur_helper, "-S", "--noconfirm"] + packages
                )
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install some packages with AUR helper.{self.Colors.ENDC}"
                    )
            elif self.distro == "fedora":
                result = self.run_command(["sudo", "dnf", "install", "-y"] + packages)
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install some packages with dnf.{self.Colors.ENDC}"
                    )

                print("\nInstalling ignis via pip...")
                result = self.run_command(
                    [
                        "pip",
                        "install",
                        "--user",
                        "git+https://github.com/ignis-sh/ignis.git",
                    ]
                )
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install ignis via pip.{self.Colors.ENDC}"
                    )

                print("\nInstalling matugen via cargo...")
                result = self.run_command(["cargo", "install", "matugen"])
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install matugen via cargo.{self.Colors.ENDC}"
                    )
                else:
                    self.run_command(["export", "PATH=\"$PATH:~/.cargo/bin\""])
                
                print("\n Installing required fonts...")
                result = self.run_command(["wget", "https://github.com/google/material-design-icons/raw/refs/heads/master/variablefont/MaterialSymbolsOutlined%5BFILL,GRAD,opsz,wght%5D.ttf"])
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to download the font.{self.Colors.ENDC}"
                    )
                else:
                    result = self.run_command(["mkdir", "/usr/share/fonts/material-symbols-icons"])
                    if result is None or (
                        hasattr(result, "returncode") and result.returncode != 0
                    ):
                        print(
                            f"{self.Colors.RED}Failed to create the folder for the font.{self.Colors.ENDC}"
                        )
                    else:
                        result = self.run_command(["mv", "MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf", "/usr/share/fonts/material-symbols-icons"])
                        if result is None or (
                            hasattr(result, "returncode") and result.returncode != 0
                        ):
                            print(
                                f"{self.Colors.RED}Failed to install the font.{self.Colors.ENDC}"
                            )
            elif self.distro == "ubuntu":
                result = self.run_command(["sudo", "apt", "update"])
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to update apt repositories.{self.Colors.ENDC}"
                    )
                result = self.run_command(["sudo", "apt", "install", "-y"] + packages)
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install some packages with apt.{self.Colors.ENDC}"
                    )

                print("\nInstalling ignis via pip...")
                result = self.run_command(
                    [
                        "pip",
                        "install",
                        "--user",
                        "git+https://github.com/ignis-sh/ignis.git",
                    ]
                )
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install ignis via pip.{self.Colors.ENDC}"
                    )

                print("\nInstalling matugen via cargo...")
                result = self.run_command(["cargo", "install", "matugen"])
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install matugen via cargo.{self.Colors.ENDC}"
                    )

        else:
            print(
                f"{self.Colors.YELLOW}No automatic dependency installation for your distribution.{self.Colors.ENDC}"
            )

        if self.distro in ["fedora", "ubuntu"]:
            print("\nChecking for dart-sass...")
            if not shutil.which("sass"):
                print(
                    "dart-sass is not available as a native package. Attempting to install via npm (user-local)..."
                )
                if shutil.which("npm"):
                    result_local = self.run_command(
                        [
                            "npm",
                            "install",
                            "--prefix",
                            os.path.expanduser("~/.local"),
                            "sass",
                        ]
                    )
                    if result_local is None or (
                        hasattr(result_local, "returncode")
                        and result_local.returncode != 0
                    ):
                        print(
                            f"{self.Colors.RED}Failed to install dart-sass via npm. You may need to add ~/.local/bin to your PATH if using user-local install.{self.Colors.ENDC}"
                        )
                    else:
                        print(
                            f"{self.Colors.GREEN}Installed dart-sass locally via npm. Add ~/.local/bin to your PATH if not already present.{self.Colors.ENDC}"
                        )
                        user_local_bin = os.path.expanduser("~/.local/bin")
                        if user_local_bin not in os.environ.get("PATH", ""):
                            print(
                                f"{self.Colors.YELLOW}Reminder: ~/.local/bin is not in your PATH. Add it to use 'sass' globally.{self.Colors.ENDC}"
                            )
                else:
                    print(
                        f"{self.Colors.RED}npm is not installed. Please install npm and then run 'npm install --prefix ~/.local sass'.{self.Colors.ENDC}"
                    )
            else:
                print("dart-sass (sass) is already installed.")

        print("\nInstalling ignis-gvc from source...")
        gvc_temp_dir = tempfile.mkdtemp()
        gvc_repo_url = "https://github.com/ignis-sh/ignis-gvc.git"
        gvc_repo_dir = os.path.join(gvc_temp_dir, "ignis-gvc")
        self.run_command(["git", "clone", gvc_repo_url, gvc_repo_dir])

        def check_pkgconfig_file(pc_name):
            paths = [
                "/usr/lib64/pkgconfig",
                "/usr/lib/pkgconfig",
                "/usr/share/pkgconfig",
            ]
            for path in paths:
                if os.path.exists(os.path.join(path, pc_name)):
                    return path
            return None

        env = os.environ.copy()
        pc_path = check_pkgconfig_file("gobject-introspection-1.0.pc")
        if pc_path:
            env["PKG_CONFIG_PATH"] = f"{pc_path}:{env.get('PKG_CONFIG_PATH', '')}"
        else:
            print(
                f"{self.Colors.RED}gobject-introspection-1.0.pc not found. Please install gobject-introspection-devel.{self.Colors.ENDC}"
            )

        result = self.run_command(
            ["meson", "setup", "build", "--prefix=/usr"], cwd=gvc_repo_dir, env=env
        )
        if result is None or (hasattr(result, "returncode") and result.returncode != 0):
            print(
                f"{self.Colors.RED}Failed to run meson setup for ignis-gvc.{self.Colors.ENDC}"
            )
        else:
            result = self.run_command(
                ["meson", "compile", "-C", "build"], cwd=gvc_repo_dir, env=env
            )
            if result is None or (
                hasattr(result, "returncode") and result.returncode != 0
            ):
                print(
                    f"{self.Colors.RED}Failed to compile ignis-gvc with meson.{self.Colors.ENDC}"
                )
            else:
                result = self.run_command(
                    ["sudo", "meson", "install", "-C", "build"],
                    cwd=gvc_repo_dir,
                    env=env,
                )
                if result is None or (
                    hasattr(result, "returncode") and result.returncode != 0
                ):
                    print(
                        f"{self.Colors.RED}Failed to install ignis-gvc with meson.{self.Colors.ENDC}"
                    )
                else:
                    print(
                        f"{self.Colors.GREEN}Installed ignis-gvc from source using meson.{self.Colors.ENDC}"
                    )
        shutil.rmtree(gvc_temp_dir)

        if not shutil.which("swww"):
            print("\nswww not found, attempting to build from source...")
            temp_dir = tempfile.mkdtemp()
            swww_repo_url = "https://github.com/LGFae/swww.git"
            swww_repo_dir = os.path.join(temp_dir, "swww")

            print(f"Cloning {swww_repo_url} to {swww_repo_dir}...")
            result = self.run_command(
                ["git", "clone", swww_repo_url, swww_repo_dir], cwd=temp_dir
            )
            if result and result.returncode == 0:
                env = os.environ.copy()
                pc_path = check_pkgconfig_file("wayland-protocols.pc")
                if pc_path:
                    env["PKG_CONFIG_PATH"] = (
                        f"{pc_path}:{env.get('PKG_CONFIG_PATH', '')}"
                    )
                else:
                    print(
                        f"{self.Colors.RED}wayland-protocols.pc not found. Please install wayland-protocols-devel.{self.Colors.ENDC}"
                    )

                print("Building swww with cargo...")
                result = self.run_command(
                    ["cargo", "build", "--release"], cwd=swww_repo_dir, env=env
                )
                if result and result.returncode == 0:
                    for binary in ["swww", "swww-daemon"]:
                        src = os.path.join(swww_repo_dir, "target", "release", binary)
                        dest = os.path.join("/usr/local/bin", binary)
                        if os.path.exists(src):
                            copy_result = self.run_command(["sudo", "cp", src, dest])
                            if copy_result and copy_result.returncode == 0:
                                print(
                                    f"{self.Colors.GREEN}Installed {binary} to /usr/local/bin.{self.Colors.ENDC}"
                                )
                            else:
                                print(
                                    f"{self.Colors.RED}Failed to copy {binary} to /usr/local/bin.{self.Colors.ENDC}"
                                )
                        else:
                            print(
                                f"{self.Colors.RED}Binary {binary} not found after build.{self.Colors.ENDC}"
                            )
                    print(
                        f"{self.Colors.YELLOW}Optional: Autocompletion scripts are available in the completions directory of the swww repo.{self.Colors.ENDC}"
                    )
                else:
                    print(
                        f"{self.Colors.RED}Error building swww with cargo.{self.Colors.ENDC}"
                    )
            else:
                print(
                    f"{self.Colors.RED}Error cloning swww repository.{self.Colors.ENDC}"
                )

            shutil.rmtree(temp_dir)
        else:
            print("swww found in PATH.")

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

        install_cmd = ["sudo", self.package_manager]
        if self.distro == "fedora":
            install_cmd.extend(["install", "-y"])
        else:
            install_cmd.extend(
                ["-S", "--noconfirm"] if self.distro == "arch" else ["install", "-y"]
            )

        if choice == "1":
            print("Installing Niri...")
            if self.run_command(install_cmd + ["niri"]):
                return "niri"
        elif choice == "2":
            print("Installing Hyprland...")
            if self.run_command(install_cmd + ["hyprland"]):
                return "hyprland"
        elif choice == "3":
            print("Installing Niri and Hyprland...")
            if self.run_command(install_cmd + ["niri", "hyprland"]):
                return "both"
        elif choice == "q":
            print("Quitting.")
            sys.exit(0)

        print(
            f"{self.Colors.RED}Installation failed or cancelled. Cannot proceed.{self.Colors.ENDC}"
        )
        return None

    def install_desktop_configs(self, desktop_env):
        if desktop_env in ["niri", "both"]:
            print("Copying Niri config...")
            niri_config_dir = os.path.join(self.config_dir, "niri")
            os.makedirs(niri_config_dir, exist_ok=True)
            niri_source = os.path.join(self.source_dir, "exodefaults", "config.kdl")
            niri_dest = os.path.join(niri_config_dir, "config.kdl")

            if os.path.exists(niri_dest):
                print(
                    f"{self.Colors.YELLOW}Niri config already exists.{self.Colors.ENDC}"
                )
                choice = self.get_user_choice(
                    "Backup (b), Overwrite (o), Skip (s)? ", ["b", "o", "s"]
                )
                if choice == "b":
                    print(f"Backing up {niri_dest}...")
                    shutil.copy2(niri_dest, niri_dest + ".bak")
                elif choice == "o":
                    print(f"Overwriting {niri_dest}...")
                elif choice == "s":
                    print(f"Skipping {niri_dest}...")
                    return
            shutil.copy2(niri_source, niri_dest)

        if desktop_env in ["hyprland", "both"]:
            print("Copying Hyprland config...")
            hypr_config_dir = os.path.join(self.config_dir, "hypr", "hyprland")
            os.makedirs(hypr_config_dir, exist_ok=True)
            hypr_source = os.path.join(self.source_dir, "exodefaults", "hyprland.conf")
            hypr_dest = os.path.join(hypr_config_dir, "hyprland.conf")

            if os.path.exists(hypr_dest):
                print(
                    f"{self.Colors.YELLOW}Hyprland config already exists.{self.Colors.ENDC}"
                )
                choice = self.get_user_choice(
                    "Backup (b), Overwrite (o), Skip (s)? ", ["b", "o", "s"]
                )
                if choice == "b":
                    print(f"Backing up {hypr_dest}...")
                    shutil.copy2(hypr_dest, hypr_dest + ".bak")
                elif choice == "o":
                    print(f"Overwriting {hypr_dest}...")
                elif choice == "s":
                    print(f"Skipping {hypr_dest}...")
                    return
            shutil.copy2(hypr_source, hypr_dest)

    def final_setup(self):
        self.print_header("Final Setup")
        default_wallpaper_path = os.path.join(
            self.source_dir, "exodefaults", "default_wallpaper.png"
        )
        wallpaper_dir = os.path.expanduser("~/Pictures/Wallpapers")
        if self.dry_run:
            wallpaper_dir = os.path.join(self.config_dir, "Pictures/Wallpapers")

        os.makedirs(wallpaper_dir, exist_ok=True)
        default_wallpaper_dest = os.path.join(wallpaper_dir, "default.png")
        if not os.path.exists(default_wallpaper_dest):
            print("Copying default wallpaper...")
            shutil.copyfile(default_wallpaper_path, default_wallpaper_dest)

        print(
            f"{self.Colors.GREEN}Default wallpaper placed in {wallpaper_dir}{self.Colors.ENDC}"
        )
        print("Wallpaper will be set on first desktop launch.")

        ignis_config_dir = os.path.join(self.config_dir, "ignis")
        user_settings_path = os.path.join(ignis_config_dir, "user_settings.json")

        print("\nGenerating initial color scheme with Matugen...")
        if shutil.which("matugen"):
            matugen_command = ["matugen", "image", default_wallpaper_dest]
            result = self.run_command(matugen_command)
            if result is None or (
                hasattr(result, "returncode") and result.returncode != 0
            ):
                print(
                    f"{self.Colors.RED}Failed to generate color scheme with Matugen.{self.Colors.ENDC}"
                )
            else:
                print(
                    f"{self.Colors.GREEN}Initial color scheme generated.{self.Colors.ENDC}"
                )
        else:
            print(
                f"{self.Colors.RED}Matugen is not installed or not in PATH. Skipping color scheme generation. Please install matugen and run manually if desired.{self.Colors.ENDC}"
            )

        if not os.path.exists(user_settings_path):
            print("Creating default user_settings.json...")
            os.makedirs(ignis_config_dir, exist_ok=True)
            with open(user_settings_path, "w") as f:
                f.write("{}")

        preview_colors = os.path.join(
            self.source_dir, "exodefaults", "preview-colors.scss"
        )
        preview_colors_dest = os.path.join(
            self.config_dir, "ignis", "styles", "preview-colors.scss"
        )
        if not os.path.exists(preview_colors_dest):
            print("Copying default preview-colors.scss...")
            shutil.copyfile(preview_colors, preview_colors_dest)

        if shutil.which("exoupdate") is None:
            self.install_as_command()

    def full_install(self):
        self.print_header("Starting Full Exo Installation")

        if not self.detect_distro():
            choice = self.get_user_choice(
                "Continue with installation without automatic dependency management? (y/n): ",
                ["y", "n"],
            )
            if choice == "n":
                return

        self.get_package_manager()

        if not self.dry_run:
            if self.distro == "arch" and not self.check_aur_helper():
                return
            self.install_dependencies()
        else:
            print(
                f"{self.Colors.YELLOW}[DRY RUN] Skipping AUR helper check and dependency installation.{self.Colors.ENDC}"
            )

        desktop_env = self.check_desktop()
        if not desktop_env:
            return

        core_folders = ["ignis", "matugen"]
        for folder in core_folders:
            source = os.path.join(self.source_dir, folder)
            destination = os.path.join(self.config_dir, folder)
            if os.path.exists(destination):
                print(
                    f"{self.Colors.YELLOW}Warning: '{destination}' already exists.{self.Colors.ENDC}"
                )
                choice = self.get_user_choice(
                    "Backup (b), Overwrite (o), or Quit (q)? ", ["b", "o", "q"]
                )
                if choice == "b":
                    print(f"Backing up {destination}...")
                    shutil.move(destination, destination + "-backup")
                elif choice == "o":
                    print(f"Overwriting {destination}...")
                    shutil.rmtree(destination)
                elif choice == "q":
                    sys.exit(0)
            try:
                shutil.copytree(source, destination)
                print(
                    f"{self.Colors.GREEN}Copied '{source}' to '{destination}'.{self.Colors.ENDC}"
                )
            except Exception as e:
                print(
                    f"{self.Colors.RED}Error copying '{source}': {e}{self.Colors.ENDC}"
                )

        self.install_desktop_configs(desktop_env)
        self.final_setup()
        print(f"\n{self.Colors.GREEN}Installation complete.{self.Colors.ENDC}")

    def update_install(self):
        self.print_header("Updating Existing Exo Installation")

        overwrite_choice = self.get_user_choice(
            "\nHow to handle file overwrites? (y: Yes to all, n: Prompt for each): ",
            ["y", "n"],
        )
        if overwrite_choice == "y":
            self.auto_confirm_overwrite = True

        delete_choice = self.get_user_choice(
            "How to handle orphaned files? (y: Yes to all, n: Prompt for each): ",
            ["y", "n"],
        )
        if delete_choice == "y":
            self.auto_confirm_delete = True

        core_folders = ["ignis", "matugen"]
        for folder in core_folders:
            source_path = os.path.join(self.source_dir, folder)
            dest_path = os.path.join(self.config_dir, folder)

            if not os.path.isdir(dest_path):
                print(
                    f"{self.Colors.YELLOW}Warning: '{dest_path}' not found. Skipping update for this folder.{self.Colors.ENDC}"
                )
                continue

            print(
                f"\n--- Comparing folder: {self.Colors.BLUE}{folder}{self.Colors.ENDC} ---"
            )

            for root, dirs, files in os.walk(source_path):
                dirs[:] = [d for d in dirs if d != "__pycache__"]

                for file in files:
                    if os.path.basename(file) in self.protected_files:
                        continue

                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_path)
                    dest_file = os.path.join(dest_path, rel_path)
                    self.compare_and_copy(source_file, dest_file)

            for root, dirs, files in os.walk(dest_path):
                dirs[:] = [d for d in dirs if d != "__pycache__"]

                for file in files:
                    if os.path.basename(file) in self.protected_files:
                        continue

                    dest_file = os.path.join(root, file)
                    rel_path = os.path.relpath(dest_file, dest_path)
                    source_file = os.path.join(source_path, rel_path)

                    if not os.path.exists(source_file):
                        self.prompt_and_delete(dest_file)

        preview_colors = os.path.join(
            self.source_dir, "exodefaults", "preview-colors.scss"
        )
        preview_colors_dest = os.path.join(
            self.config_dir, "ignis", "styles", "preview-colors.scss"
        )
        if not os.path.exists(preview_colors_dest):
            print("Copying default preview-colors.scss...")
            shutil.copyfile(preview_colors, preview_colors_dest)

        print(f"\n{self.Colors.GREEN}Update check complete.{self.Colors.ENDC}")

    def compare_and_copy(self, source, dest):
        source_hash = self.get_file_hash(source)
        dest_hash = self.get_file_hash(dest)

        if dest_hash is None:
            print(
                f"{self.Colors.GREEN}New file found: Copying '{os.path.basename(source)}'{self.Colors.ENDC}"
            )
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(source, dest)
        elif source_hash != dest_hash:
            print(
                f"{self.Colors.YELLOW}File mismatch: '{os.path.basename(source)}'{self.Colors.ENDC}"
            )

            if self.auto_confirm_overwrite:
                print(f"  Updating '{os.path.basename(source)}' (automatic).")
                shutil.copy2(source, dest)
            else:
                choice = self.get_user_choice(
                    "  Overwrite with latest version? (y/n): ", ["y", "n"]
                )
                if choice == "y":
                    print(f"  Updating '{os.path.basename(source)}'...")
                    shutil.copy2(source, dest)

    def prompt_and_delete(self, file_path):
        print(
            f"{self.Colors.YELLOW}Orphaned file found: '{os.path.basename(file_path)}' exists in your config but not in the source.{self.Colors.ENDC}"
        )

        if self.auto_confirm_delete:
            print(f"  Deleting '{os.path.basename(file_path)}' (automatic).")
            os.remove(file_path)
        else:
            choice = self.get_user_choice("  Delete this file? (y/n): ", ["y", "n"])
            if choice == "y":
                print(f"  Deleting '{os.path.basename(file_path)}'...")
                os.remove(file_path)

    def install_as_command(self):
        self.print_header("Installing as Command")
        prefix = "/usr/local"
        dest_dir = os.path.join(prefix, "bin")
        if not os.path.exists(dest_dir):
            print(
                f"{self.Colors.YELLOW}Creating directory: {dest_dir}{self.Colors.ENDC}"
            )
            try:
                os.makedirs(dest_dir)
            except OSError as e:
                print(
                    f"{self.Colors.RED}Error creating directory: {e}{self.Colors.ENDC}"
                )
                return

        dest_file = os.path.join(dest_dir, "exoupdate")
        try:
            cmd = ["sudo", "cp", sys.argv[0], dest_file]
            result = self.run_command(cmd)
            if result and result.returncode == 0:
                print(
                    f"{self.Colors.GREEN}Copied script to: {dest_file}{self.Colors.ENDC}"
                )
            else:
                print(f"{self.Colors.RED}Error copying script.{self.Colors.ENDC}")
                return
        except Exception as e:
            print(f"{self.Colors.RED}Error copying script: {e}{self.Colors.ENDC}")
            return

        try:
            cmd = ["sudo", "chmod", "755", dest_file]
            result = self.run_command(cmd)
            if result and result.returncode == 0:
                print(f"{self.Colors.GREEN}Made script executable.{self.Colors.ENDC}")
            else:
                print(
                    f"{self.Colors.RED}Error making script executable.{self.Colors.ENDC}"
                )
                return
        except Exception as e:
            print(
                f"{self.Colors.RED}Error making script executable: {e}{self.Colors.ENDC}"
            )
            return

        print(
            f"{self.Colors.GREEN}Installation as command complete. You can now run 'exoupdate' from anywhere.{self.Colors.ENDC}"
        )

    def update_installed_command_if_needed(self):
        installed_path = "/usr/local/bin/exoupdate"
        cloned_script = sys.argv[0]
        if os.path.basename(cloned_script) == "exoupdate":
            cloned_script = os.path.join(self.source_dir, "exoinstall.py")
        if not os.path.exists(installed_path):
            return

        def file_hash(path):
            hasher = hashlib.sha256()
            try:
                with open(path, "rb") as f:
                    hasher.update(f.read())
                return hasher.hexdigest()
            except Exception:
                return None

        installed_hash = file_hash(installed_path)
        cloned_hash = file_hash(cloned_script)

        if installed_hash and cloned_hash and installed_hash != cloned_hash:
            print(
                f"{self.Colors.YELLOW}Updating installed exoupdate command...{self.Colors.ENDC}"
            )
            cmd = ["sudo", "cp", cloned_script, installed_path]
            result = self.run_command(cmd)
            if result and result.returncode == 0:
                print(
                    f"{self.Colors.GREEN}exoupdate command updated successfully.{self.Colors.ENDC}"
                )
            else:
                print(
                    f"{self.Colors.RED}Failed to update exoupdate command.{self.Colors.ENDC}"
                )
        else:
            print(
                f"{self.Colors.GREEN}Installed exoupdate command is up to date.{self.Colors.ENDC}"
            )

    def uninstall_exo(self):
        self.print_header("Exo Uninstaller")
        print(
            f"{self.Colors.RED}{self.Colors.BOLD}WARNING: This will remove Exo configuration files.{self.Colors.ENDC}"
        )
        print("This action is irreversible. Backup files (.bak) will NOT be removed.")

        choice = self.get_user_choice(
            "Are you sure you want to continue? (y/n): ", ["y", "n"]
        )
        if choice == "n":
            print("Uninstallation cancelled.")
            return

        paths_to_remove = {
            "ignis config": os.path.join(self.config_dir, "ignis"),
            "matugen config": os.path.join(self.config_dir, "matugen"),
            "Niri config file": os.path.join(self.config_dir, "niri", "config.kdl"),
            "Hyprland config file": os.path.join(
                self.config_dir, "hypr", "hyprland.conf"
            ),
        }

        print("\nThe following Exo configuration items will be removed if they exist:")
        items_found = False
        for name, path in paths_to_remove.items():
            if os.path.exists(path):
                print(f"- {name} ({path})")
                items_found = True

        command_path = "/usr/local/bin/exoupdate"
        if os.path.exists(command_path):
            print(f"- exoupdate command ({command_path})")
            items_found = True

        if not items_found and not self.dry_run:
            print(
                f"{self.Colors.YELLOW}No Exo files found to uninstall.{self.Colors.ENDC}"
            )
            return

        choice = self.get_user_choice("\nProceed with removal? (y/n): ", ["y", "n"])
        if choice == "n":
            print("Uninstallation cancelled.")
            return

        for name, path in paths_to_remove.items():
            if os.path.exists(path):
                if self.dry_run:
                    print(
                        f"{self.Colors.YELLOW}[DRY RUN] Would remove {name} at {path}{self.Colors.ENDC}"
                    )
                    continue
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"{self.Colors.GREEN}Removed {name}.{self.Colors.ENDC}")
                except OSError as e:
                    print(
                        f"{self.Colors.RED}Error removing {name}: {e}{self.Colors.ENDC}"
                    )
                    print(
                        f"{self.Colors.YELLOW}You may need to remove it manually.{self.Colors.ENDC}"
                    )

        if os.path.exists(command_path):
            print("Removing exoupdate command (requires sudo)...")
            cmd = ["sudo", "rm", command_path]
            result = self.run_command(cmd)
            if not self.dry_run:
                if result and result.returncode == 0:
                    print(
                        f"{self.Colors.GREEN}Removed exoupdate command.{self.Colors.ENDC}"
                    )
                else:
                    print(
                        f"{self.Colors.RED}Failed to remove exoupdate command.{self.Colors.ENDC}"
                    )
                    print(
                        f"{self.Colors.YELLOW}Please remove it manually: sudo rm {command_path}{self.Colors.ENDC}"
                    )

        wallpaper_path = os.path.expanduser("~/Pictures/Wallpapers/default.png")
        if self.dry_run:
            wallpaper_path = os.path.join(
                self.config_dir, "Pictures/Wallpapers/default.png"
            )

        if os.path.exists(wallpaper_path):
            choice = self.get_user_choice(
                f"\nAlso remove the default wallpaper at '{wallpaper_path}'? (y/n): ",
                ["y", "n"],
            )
            if choice == "y":
                if self.dry_run:
                    print(
                        f"{self.Colors.YELLOW}[DRY RUN] Would remove wallpaper: {wallpaper_path}{self.Colors.ENDC}"
                    )
                else:
                    try:
                        os.remove(wallpaper_path)
                        print(
                            f"{self.Colors.GREEN}Removed default wallpaper.{self.Colors.ENDC}"
                        )
                    except OSError as e:
                        print(
                            f"{self.Colors.RED}Error removing wallpaper: {e}{self.Colors.ENDC}"
                        )

        self.print_header("Post-Uninstall Steps")
        print(
            f"{self.Colors.YELLOW}Uninstallation of configuration files is complete.{self.Colors.ENDC}"
        )
        print(
            "This script does NOT remove dependencies to avoid breaking other parts of your system."
        )
        print("If you wish to remove them, you can do so with your package manager.")
        print("Dependencies to consider removing:")
        print(
            "- Niri or Hyprland, python-ignis-git, ignis-gvc, matugen, swww, gnome-bluetooth, adw-gtk-theme, dart-sass"
        )


if __name__ == "__main__":
    if os.geteuid() == 0:
        print("This script should not be run as root. Please run as a regular user.")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        installer = ExoInstaller()
        installer.uninstall_exo()
    else:
        installer = ExoInstaller()
        installer.run()
