# Exo
 A Material 3 inspired desktop shell for Niri and Hyprland created with Ignis.

## Dependencies
* Niri or Hyprland
* Ignis (git/dev) _(`python-ignis-git` on the AUR)_
* `hyprlock`
* `gpu-screen-recorder` _(optional for screen recording)_
* Material Symbols Font

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

Add `ignis init` to auto start in your Niri/Hyprland config and you're ready to go!

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
<img width="1920" height="1080" alt="Screenshot from 2025-08-19 18-53-31" src="https://github.com/user-attachments/assets/cd655499-0d40-47dc-bbf9-9a8bfd988a17" />
<img width="1920" height="1080" alt="Screenshot from 2025-08-19 18-54-38" src="https://github.com/user-attachments/assets/9149a48a-1387-4af9-a80a-828069b45863" />
<img width="1920" height="1080" alt="Screenshot from 2025-08-19 18-56-31" src="https://github.com/user-attachments/assets/a92c528a-c7fd-4cdd-90bb-4e6973ed39b2" />


https://github.com/user-attachments/assets/4d700643-197f-4a3a-a743-77e6b6f902f9

https://github.com/user-attachments/assets/bcd8b4b8-c3ce-4417-9297-511e451fa30c
