from distutils.core import setup

setup(
    name            = "solus-sc",
    version         = "12.0",
    author          = "Ikey Doherty",
    author_email    = "ikey@solus-project.com",
    description     = ("Solus Software Center"),
    license         = "GPL-2.0",
    url             = "https://github.com/solus-project/os-installer",
    packages        = ['solus_sc', 'eopkg_assist'],
    scripts         = ['solus-sc'],
    classifiers     = [ "License :: OSI Approved :: GPL-2.0 License"],
    package_data    = {'solus_sc': ['update_dialog.ui', 'styling.css']},
    data_files      = [("/usr/share/applications", ["data/solus-sc.desktop"]),
                       ("/usr/share/dbus-1/system-services", ["data/dbus-1/system-services/com.solus_project.eopkgassist.service"]),
                       ("/etc/dbus-1/system.d", ["data/system.d/com.solus_project.eopkgassist.conf"]),
                       ("/usr/share/polkit-1/actions", ["data/polkit-1/actions/com.solus_project.eopkgassist.policy"]),
                       ("/usr/libexec", ["eopkg-assist-wrapper"])]
)
