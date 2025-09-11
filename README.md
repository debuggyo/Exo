![Exo](https://github.com/user-attachments/assets/ca159dea-aa7c-4d52-bc65-9129a8c1becf)

A Material 3 inspired desktop shell for Niri and Hyprland created with Ignis.

For support or showcasing your Exo setup, you can join the Exo [Discord](https://discord.gg/XjyxD3y5a5) server!

## Automatic Install Script (recommended)

The installer script will automatically clone the repository to a temporary folder and copy the configuration files to the correct locations.

Automatic dependency installation is supported on Arch-based, Fedora-based, and Ubuntu-based distributions. The rest of the installation process should work on any distro, but you will have to manually install dependencies if your distro is not officially supported.

The script can also be used to update Exo on any distribution.

```sh
sudo apt install curl git python3  # For Debian/Ubuntu
sudo dnf install curl git python3  # For Fedora
sudo pacman -S curl git python3   # For Arch
curl -o exoinstall.py https://raw.githubusercontent.com/debuggyo/Exo/main/exoinstall.py
python3 exoinstall.py
```

## Manual Install Instructions

First install the dependencies.

### Dependencies

*   Niri or Hyprland
*   Ignis (git/dev)
*   `ignis-gvc`
*   `gpu-screen-recorder` _(optional for screen recording)_
*   `slurp` _(optional for region recording)_
*   Material Symbols Font
*   `matugen`
*   `swww`
*   `gnome-bluetooth`
*   `adw-gtk3` Theme
*   `dart-sass`

#### Dependency Notes:

*   **Arch-based:** Most dependencies are available in the AUR. Use your preferred AUR helper to install them (e.g., `paru -S <package_name>`). `Ignis` is available as `python-ignis-git`.
*   **Fedora-based:** Use `dnf install <package_name>` to install dependencies. Some packages may have slightly different names (e.g., `gnome-bluetooth-libs` instead of `gnome-bluetooth`).
*   **Ubuntu-based:** Use `apt install <package_name>` to install dependencies. Some packages may have slightly different names (e.g., `libgnome-bluetooth-3.0-13` instead of `gnome-bluetooth`).

Create an `ignis` folder in your `.config` if it's not already there.

```sh
git clone https://github.com/debuggyo/Exo
cd Exo
cp -r ignis ~/.config/
cp -r matugen ~/.config/
touch ~/.config/ignis/user_settings.json
```

In your Niri or Hyprland config add the following keybinds, bind them to anything you would like.

| Function                           | Command                                    |
| ------------------------------------ | -------------------------------------------- |
| Opens App Launcher                 | `ignis open-window Launcher`               |
| Opens Settings Window              | `ignis open-window Settings`               |
| Opens Power Menu                   | `ignis open-window PowerMenu`              |
| Record the screen                  | `ignis run-command recorder-record-screen` |
| Record a selected region           | `ignis run-command recorder-record-region` |
| Record a window _(Niri only)_      | `ignis run-command recorder-record-portal` |

Set up matugen (see below) and run `matugen image /path/to/wallpaper` to set a wallpaper and color scheme before starting ignis.

Set the gtk theme to adw-gtk3 by running `gsettings set org.gnome.desktop.interface gtk-theme "adw-gtk3"` or by setting the theme in your preferred gtk settings program.

Add `ignis init` and `swww-daemon` to auto start in your Niri/Hyprland config and you're ready to go!

### Matugen

In `~/.config/matugen/templates/` _(create if it doesn't exist)_ create a new file called `colors.scss` with the following contents:

```
<* for name, value in colors *>
    ${{name}}: {{value.default.hex}};
<* endfor *>
```

In `~/.config/matugen/config.toml` _(create if it doesn't exist)_ add this to the bottom of the file:

```
[config.wallpaper]
command = "swww"
arguments = ["img", "--transition-type", "simple"]
set = true

[templates.ignis]
input_path = './templates/colors.scss'
output_path = '~/.config/ignis/colors.scss'
```

Then if you want you can install more [Matugen Themes](https://github.com/InioX/matugen-themes/tree/main?tab=readme-ov-file#gtk)

## Recommended Hyprland/Niri Settings

| Option                             | Value                                      |
| ------------------------------------ | -------------------------------------------- |
| Outer Margin                       | 5                                          |
| Border Radius                      | 20                                         |

This is to make sure that the window corners match the screen/bar corners.

These can be set to any value, though looks better when the radius is set to `25 - Margin`

If you don't use bar or screen corners, these don't matter and you can pick your own values.

I intend to make this automatic when I implement Niri/Hyprland configuration in the settings window.

## Screenshots/Videos

<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/8179e2f8-0eea-4a55-96f3-c4746fdca45c" />
<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/e54530fe-6d85-453b-a819-80f8ad8a2b45" />
<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/8a75f825-0b2e-40ed-842b-fe957e865b45" />
<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/3c95c7ae-eeb5-4fd2-b252-72f597b2cb9a" />
<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/765efbf1-e482-4a50-a994-8d091c6aacc1" />
<img width="1920" height="1080" alt="image"
src="https://github.com/user-attachments/assets/569bd446-dd8b-4cac-aa32-61df811adc68" />

https://github.com/user-attachments/assets/c6b4ffcb-1be7-4a95-b03d-33bfe748756d

https://github.com/user-attachments/assets/78e35d82-5fe9-4986-b545-80fc59bc4784

## Credits

*   [Ignis](https://github.com/ignis-sh/ignis)
*   [linkfrg's dotfiles](https://github.com/linkfrg/dotfiles)
*   [Material 3 Guidelines](https://m3.material.io/)
*   [Illogical Impulse](https://github.com/end-4/dots-hyprland) _(inspiration)_