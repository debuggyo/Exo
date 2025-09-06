![Exo](https://github.com/user-attachments/assets/ca159dea-aa7c-4d52-bc65-9129a8c1becf)

A Material 3 inspired desktop shell for Niri and Hyprland created with Ignis.

For support or showcasing your Exo setup, you can join the Exo [Discord](https://discord.gg/XjyxD3y5a5) server!

## Automatic Install Script (recommended method, Arch-based distros only)
```
sudo pacman -S git python
git clone https://github.com/debuggyo/Exo
cd Exo
python exoinstall.py
``` 

## Manual Install Instructions
First install the dependencies.

# Dependencies
* Niri or Hyprland
* Ignis (git/dev) _(`python-ignis-git` on the AUR)_
* `ignis-gvc`
* `gpu-screen-recorder` _(optional for screen recording)_
* `slurp` _(optional for region recording)_
* Material Symbols Font _(`ttf-material-symbols-variable-git` on the AUR)_
* `matugen`
* `swww`
* `gnome-bluetooth-3.0`
* `adw-gtk3` Theme
* `dart-sass`

Create an `ignis` folder in your `.config` if it's not already there.

`git clone https://github.com/debuggyo/Exo ~/.config/ignis`

In your Niri or Hyprland config add the following keybinds, bind them to anything you would like.

| Function                           | Command                                    |
|------------------------------------|--------------------------------------------|
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
|------------------------------------|--------------------------------------------|
| Outer Margin                       | 5                                          |
| Border Radius                      | 20                                         |

This is to make sure that the window corners match the screen/bar corners.

These can be set to any value, though looks better when the radius is set to `25 - Margin`

If you don't use bar or screen corners, these don't matter and you can pick your own values.

I intend to make this automatic when I implement Niri/Hyprland configuration in the settings window.

## Screenshots/Videos
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8179e2f8-0eea-4a55-96f3-c4746fdca45c" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e54530fe-6d85-453b-a819-80f8ad8a2b45" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8a75f825-0b2e-40ed-842b-fe957e865b45" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/3c95c7ae-eeb5-4fd2-b252-72f597b2cb9a" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/765efbf1-e482-4a50-a994-8d091c6aacc1" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/569bd446-dd8b-4cac-aa32-61df811adc68" />


https://github.com/user-attachments/assets/c6b4ffcb-1be7-4a95-b03d-33bfe748756d

https://github.com/user-attachments/assets/78e35d82-5fe9-4986-b545-80fc59bc4784


## Credits

* [Ignis](https://github.com/ignis-sh/ignis)
* [linkfrg's dotfiles](https://github.com/linkfrg/dotfiles)
* [Material 3 Guidelines](https://m3.material.io/)
* [Illogical Impulse](https://github.com/end-4/dots-hyprland) _(inspiration)_
