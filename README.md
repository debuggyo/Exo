![Exo](https://github.com/user-attachments/assets/ca159dea-aa7c-4d52-bc65-9129a8c1becf)

A Material 3 inspired desktop shell for Niri and Hyprland created with Ignis.

## Dependencies
* Niri or Hyprland
* Ignis (git/dev) _(`python-ignis-git` on the AUR)_
* `gpu-screen-recorder` _(optional for screen recording)_
* Material Symbols Font
* Matugen
* SWWW
* gnome-bluetooth-3.0

## Install Instructions
First install the dependencies.

Create an `ignis` folder in your `.config` if it's not already there.

`git clone https://github.com/debuggyo/Exo ~/.config/ignis`

In your Niri or Hyprland config add the following keybinds, bind them to anything you would like.

| Function                           | Command                                    |
|------------------------------------|--------------------------------------------|
| Opens App Launcher                 | `ignis open-window Launcher`               |
| Opens Settings Window              | `ignis open-window Settings`               |
| Opens Power Menu                   | `ignis open-window PowerMenu`              |
| Record the screen                  | `ignis run-command recorder-record-screen` |
| Record with options _(Niri only)_  | `ignis run-command recorder-record-portal` |

Set up matugen (see below) and run `matugen image /path/to/wallpaper` to set a wallpaper and color scheme before starting ignis.

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