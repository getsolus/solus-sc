from distutils.core import setup

setup(
    name            = "solus-sc",
    version         = "6.0",
    author          = "Ikey Doherty",
    author_email    = "ikey@solus-project.com",
    description     = ("Solus Software Center"),
    license         = "GPL-2.0",
    url             = "https://github.com/solus-project/os-installer",
    packages        = ['solus_sc'],
    scripts         = ['solus-sc'],
    classifiers     = [ "License :: OSI Approved :: GPL-2.0 License"],
    package_data    = {'solus_sc': ['update_dialog.ui', 'styling.css']},
    data_files      = [("/usr/share/applications", ["data/solus-sc.desktop"])]
)
