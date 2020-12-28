from setuptools import setup


setup(
    name            = "solus-sc",
    version         = "23.0",
    author          = "Solus",
    author_email    = "copyright@getsol.us",
    description     = ("Solus Software Center"),
    license         = "GPL-2.0-only",
    url             = "https://github.com/getsolus/solus-sc",
    packages        = ['solus_sc', 'eopkg_assist', 'solus_update'],
    scripts         = ['solus-sc', 'solus-update-checker'],
    classifiers     = [ "License :: OSI Approved :: GPL-2.0 License"],
    package_data    = {'solus_sc': ['data/update_dialog.ui', 'data/styling.css', 'data/arc.css', 'data/settings.ui']},
    data_files      = [("/usr/share/applications", ["data/solus-sc.desktop"]),
                       ("/usr/share/dbus-1/system-services", ["data/dbus-1/system-services/com.solus_project.eopkgassist.service"]),
                       ("/usr/share/dbus-1/system.d", ["data/system.d/com.solus_project.eopkgassist.conf"]),
                       ("/usr/share/glib-2.0/schemas", ["data/com.solus-project.software-center.gschema.xml"]),
                       ("/usr/share/polkit-1/actions", ["data/polkit-1/actions/com.solus_project.eopkgassist.policy"]),
                       ("/usr/share/xdg/autostart", ["data/solus-update.desktop"]),
                       ("/usr/libexec", ["eopkg-assist-wrapper"])]
)
