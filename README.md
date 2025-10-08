<div align="center">

![Exo](https://github.com/user-attachments/assets/ca159dea-aa7c-4d52-bc65-9129a8c1becf)

**A Material 3 inspired desktop shell for Niri and Hyprland**

*Built with Ignis for the modern Wayland experience*

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-5865F2?logo=discord&logoColor=white)](https://discord.gg/XjyxD3y5a5)
![Stars](https://img.shields.io/github/stars/debuggyo/Exo)
![Last Commit](https://img.shields.io/github/last-commit/debuggyo/Exo)

**[Join the Exo Discord](https://discord.gg/XjyxD3y5a5)** for support and to showcase your Exo setup!

</div>

---

## ✨ Overview

Exo is a sleek, modern desktop shell that brings Material 3 design principles to your Wayland compositor. Designed specifically for Niri and Hyprland, Exo provides a beautiful and functional interface built with the powerful Ignis framework.

### Key Features

- 🎨 **Material 3 Design** - Modern, adaptive UI with smooth animations and transitions
- 🌊 **Wayland Native** - Built for the future of Linux desktop environments
- ⚙️ **Highly Customizable** - Dual bar layouts, moveable and toggleable modules
- 🎨 **Dynamic Theming** - Automatic color scheme generation with Matugen
- 🔒 **Lock Screen Theming** - Automatically themes Hyprlock (if installed)
- 📦 **Modular Design** - Enable or disable components as needed
- 🎥 **Screen Recording** - Built-in screen recording capabilities

---

## 📸 Screenshots

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/c60deecf-02e0-4288-a61d-de355cb12aba" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/c65f5bfb-c72d-4f36-bdef-b68613759f59" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/286a527a-bd9b-478b-bc1d-d852b7cdbf16" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/cccad6cd-8866-40b4-b90a-d36bde8d20c6" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/3a02e717-42de-4c5e-9aba-78d9840e5d5a" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/5e4b3080-8950-4e3c-9870-40439c58180c" />

<img width="1920" height="1080" src="https://github.com/user-attachments/assets/8c12f006-3659-4c63-94c5-e262b854a22a" />


### Videos

https://github.com/user-attachments/assets/c6b4ffcb-1be7-4a95-b03d-33bfe748756d

https://github.com/user-attachments/assets/78e35d82-5fe9-4986-b545-80fc59bc4784

---

## 📋 Dependencies

### Essential

- **Compositor**: [Niri](https://github.com/YaLTeR/niri) or [Hyprland](https://github.com/hyprwm/Hyprland)
- **Shell Framework**: [Ignis](https://github.com/ignis-sh/ignis) (git/dev version)
- **GVC**: [Ignis GVC](https://github.com/ignis-sh/ignis-gvc)
- **Color Generation**: [Matugen](https://github.com/InioX/matugen)
- **Wallpaper**: [swww](https://github.com/LGFae/swww)
- **Icons**: Material Symbols Font
- **Bluetooth**: `gnome-bluetooth`
- **GTK Theme**: `adw-gtk3`
- **Sass Compiler**: `dart-sass`

### Optional

- **Lock Screen**: [Hyprlock](https://github.com/hyprwm/hyprlock) - Automatically themed by Exo
- **Screen Recording**: `gpu-screen-recorder`
- **Region Selection**: `slurp` (for region recording)

### Dependency Notes

- **Arch-based:** Most dependencies are available in the AUR. Use your preferred AUR helper (e.g., `yay -S <package_name>`). Ignis is available as `python-ignis-git`.
- **Fedora-based:** Use `dnf install <package_name>`. Some packages may have different names (e.g., `gnome-bluetooth-libs` instead of `gnome-bluetooth`).
- **Ubuntu-based:** Use `apt install <package_name>`. Some packages may have different names (e.g., `libgnome-bluetooth-3.0-13` instead of `gnome-bluetooth`).

---

## 🚀 Installation

### Automatic Installation (Recommended)

The installer script automatically handles cloning, dependency installation, and configuration for Arch-based, Fedora-based, and Ubuntu-based distributions.

```bash
# Install prerequisites
sudo apt install curl git python3  # For Debian/Ubuntu
sudo dnf install curl git python3  # For Fedora
sudo pacman -S curl git python3    # For Arch

# Download and run installer
curl -sSL https://raw.githubusercontent.com/debuggyo/Exo/main/exoinstall.py -o exoinstall.py && python3 exoinstall.py
```

The installer will:
- Install all required dependencies for your distribution
- Clone Exo and set up configuration files
- Configure Matugen templates
- Set up GTK theme
- Add a basic Niri/Hyprland config set up to run Exo

---

## 🔄 Updating and Uninstalling

### Updating

Run the installer script again to update Exo:

```bash
# If installed as system command
exoupdate

# Otherwise
python3 exoinstall.py
```

### Uninstalling

Select "Uninstall Exo" from the script's main menu. The uninstaller will:
- Remove `~/.config/ignis` and `~/.config/matugen` folders
- Remove the `exoupdate` command from `/usr/local/bin/`
- Remove Niri/Hyprland config files copied by the installer
- Remove the default wallpaper from `~/Pictures/Wallpapers`

**Note:** The uninstaller will NOT remove installed dependencies or `.bak` backup files.

---

## 🔧 Manual Installation

If the automatic installer doesn't support your distribution, you can install manually.

### 1. Install Dependencies

Install all dependencies listed above using your distribution's package manager.

### 2. Clone and Copy Configuration

```bash
# Create ignis config directory if needed
mkdir -p ~/.config/ignis

# Clone repository
git clone https://github.com/debuggyo/Exo
cd Exo

# Copy configuration files
cp -r ignis ~/.config/
cp -r matugen ~/.config/
touch ~/.config/ignis/user_settings.json
```

### 3. Configure Matugen

Create the templates directory:
```bash
mkdir -p ~/.config/matugen/templates/
```

Create `~/.config/matugen/templates/colors.scss` with:
```scss
<* for name, value in colors *>
    ${{name}}: {{value.default.hex}};
<* endfor *>
```

Create or edit `~/.config/matugen/config.toml` and add:
```toml
[config.wallpaper]
command = "swww"
arguments = ["img", "--transition-type", "simple"]
set = true

[templates.ignis]
input_path = './templates/colors.scss'
output_path = '~/.config/ignis/colors.scss'
```

Optional: Install additional [Matugen Themes](https://github.com/InioX/matugen-themes/tree/main?tab=readme-ov-file#gtk)

### 4. Set GTK Theme

```bash
gsettings set org.gnome.desktop.interface gtk-theme "adw-gtk3"
```

### 5. Set Initial Wallpaper

```bash
matugen image /path/to/your/wallpaper
```

### 6. Configure Compositor Autostart

**For Niri** (`~/.config/niri/config.kdl`):
```kdl
spawn-at-startup "ignis" "init"
spawn-at-startup "swww-daemon"
```

**For Hyprland** (`~/.config/hypr/hyprland.conf`):
```conf
exec-once = ignis init
exec-once = swww-daemon
```

---

## ⌨️ Keybindings

Configure these keybindings in your compositor to control Exo's windows and features.

| Function | Command |
|----------|---------|
| Opens App Launcher | `ignis open-window Launcher` |
| Opens Settings Window | `ignis open-window Settings` |
| Opens Power Menu | `ignis open-window PowerMenu` |
| Record the screen | `ignis run-command recorder-record-screen` |
| Record a selected region | `ignis run-command recorder-record-region` |
| Record a window *(Niri only)* | `ignis run-command recorder-record-portal` |

### Example Niri Keybindings

```kdl
binds {
    // App Launcher
    Mod { spawn "ignis" "open-window" "Launcher"; }
    
    // Settings Window
    Mod+Comma { spawn "ignis" "open-window" "Settings"; }
    
    // Power Menu
    Mod+Escape { spawn "ignis" "open-window" "PowerMenu"; }
    
    // Screen Recording
    Mod+Shift+R { spawn "ignis" "run-command" "recorder-record-screen"; }
    Mod+Shift+S { spawn "ignis" "run-command" "recorder-record-region"; }
    Mod+Shift+W { spawn "ignis" "run-command" "recorder-record-portal"; }
    
    // Lock Screen (if Hyprlock is installed)
    Super+L { spawn "hyprlock"; }
}
```

### Example Hyprland Keybindings

```conf
# App Launcher
bind = SUPER, SUPER_L, exec, ignis open-window Launcher

# Settings Window
bind = SUPER, Comma, exec, ignis open-window Settings

# Power Menu
bind = SUPER, Escape, exec, ignis open-window PowerMenu

# Screen Recording
bind = SUPER SHIFT, R, exec, ignis run-command recorder-record-screen
bind = SUPER SHIFT, S, exec, ignis run-command recorder-record-region

# Lock Screen (if Hyprlock is installed)
bind = SUPER, L, exec, hyprlock
```

---

## ⚙️ Configuration

### Settings Window

Exo is configured entirely through its built-in **Settings Window**. All customization options are available through this graphical interface - there are no manual configuration files to edit.

Access the settings window using your configured keybinding or through the system menu.

### Available Customization Options

#### Layout & Modules
- **Dual Bar Layout**: Choose between single or dual bar configurations
- **Module Positioning**: Modules can be repositioned on the bar
- **Toggleable Modules**: Enable or disable individual bar components

#### Appearance
- **Theme Mode**: Switch between light and dark themes
- **Color Schemes**: Choose from Material You color schemes
- **Wallpaper Selection**: Set wallpaper with automatic color generation
- **Font Settings**: Customize font family and sizes

#### System
- **Network**: WiFi and network configuration
- **Bluetooth**: Bluetooth device management
- **Audio**: Audio device selection and volume controls
- **Display**: Brightness settings and display configuration

### Automatic Theming

When you change your wallpaper through the settings window, Exo automatically:
- Generates a Material You color scheme using Matugen
- Updates the shell theme to match your wallpaper
- Updates GTK applications with the new theme
- **Automatically themes Hyprlock** (if installed) - no configuration needed!

The theming is seamless and requires no manual intervention.

---

## 🎨 Recommended Compositor Settings

For optimal visual consistency, configure your compositor with these settings:

| Option | Value |
|--------|-------|
| Outer Margin | 5 |
| Border Radius | 20 |

This ensures window corners match the screen/bar corners. These can be adjusted to your preference - the radius typically looks best when set to `25 - Margin`.

**Note:** If you don't use bar or screen corners, these values can be customized freely. Future updates will make this automatic through the settings window.

---

## 🐛 Troubleshooting

### Common Issues

**Exo doesn't start / Black screen:**
- Ensure Ignis (git/dev version) is properly installed: `ignis --version`
- Check that your compositor is running
- Verify all essential dependencies are installed
- Try running `ignis init` manually from terminal to see error messages

**Dynamic theming not working:**
- Check that Matugen is installed and configured: `matugen --version`
- Verify Matugen templates are correctly set up in `~/.config/matugen/`
- Try setting a wallpaper through the settings window
- Check terminal output for Matugen errors

**Screen recording not working:**
- Ensure `gpu-screen-recorder` is installed
- For region recording, ensure `slurp` is installed
- Check permissions for screen capture
- For Niri portal recording, ensure `xdg-desktop-portal-gnome` or another portal is running

**GTK apps not themed:**
- Verify `adw-gtk3` theme is installed
- Check GTK theme setting: `gsettings get org.gnome.desktop.interface gtk-theme`
- Set theme if needed: `gsettings set org.gnome.desktop.interface gtk-theme "adw-gtk3"`
- Add `@import 'colors.css'` to the top of `~/.config/gtk-3.0/gtk.css` and `~/.config/gtk-4.0/gtk.css`

### Getting Help

- 💬 **[Join the Exo Discord](https://discord.gg/XjyxD3y5a5)** for support and community help
- 📝 Check the [Issues](https://github.com/debuggyo/Exo/issues) page for known problems
- 🐛 Report bugs with detailed logs and system information

---

## 🙏 Credits

- [Ignis](https://github.com/ignis-sh/ignis) - The powerful framework that makes Exo possible
- [linkfrg's dotfiles](https://github.com/linkfrg/dotfiles) - Inspiration and guidance
- [Material 3 Guidelines](https://m3.material.io/) - Design principles and specifications
- [Illogical Impulse](https://github.com/end-4/dots-hyprland) - Design inspiration
- [Niri](https://github.com/YaLTeR/niri) - Beautiful scrollable tiling compositor
- [Hyprland](https://github.com/hyprwm/Hyprland) - Dynamic tiling compositor
---

<div align="center">

**[⭐ Star this repo](https://github.com/debuggyo/Exo)** • **[💬 Join Discord](https://discord.gg/XjyxD3y5a5)** • **[🐛 Report Issues](https://github.com/debuggyo/Exo/issues)**

</div>
