from user_settings import user_settings

class LauncherLayout:
    launcher_instance = None

    @classmethod
    def set_launcher_instance(cls, launcher):
        cls.launcher_instance = launcher

    @classmethod
    def setLayout(cls, layout: str):
        if layout not in ["grid", "list"]:
            print(f"Invalid layout: {layout}. Must be 'grid' or 'list'.")
            return

        user_settings.interface.launcher.layout = layout
        if cls.launcher_instance:
            cls.launcher_instance._set_layout(layout)
