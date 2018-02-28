import os
env = Environment()


install_nodz = True
install_qtpy = True
install_exts = True
dist_path = os.path.abspath(ARGUMENTS.get("dist", "release"))


try:
    install_nodz = int(ARGUMENTS.get("install-nodz", "1")) != 0
except:
    install_nodz = True


try:
    install_qtpy = int(ARGUMENTS.get("install-qtpy", "1")) != 0
except:
    install_qtpy = True


try:
    install_exts = int(ARGUMENTS.get("install-exts", "1")) != 0
except:
    install_exts = True


env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc"), Glob("python/petitBloc/*.py"))
env.Install(os.path.join(dist_path, "petitBloc/bin"), Glob("bin/*"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui"), Glob("python/petitBloc/ui/*.py"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui"), Glob("python/petitBloc/ui/*.json"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui"), Glob("python/petitBloc/ui/*.qss"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/icons"), Glob("python/petitBloc/ui/icons/*.png"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/blocks"), Glob("blocks/*.py"))
env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/blocks"), Glob("blocks/*.config"))


if install_nodz:
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/external/Nodz"), "Nodz/__init__.py")
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/external/Nodz"), "Nodz/nodz_main.py")
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/external/Nodz"), "Nodz/nodz_utils.py")
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/external/Nodz"), "Nodz/default_config.json")

if install_qtpy:
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/ui/external"), "Qt.py/Qt.py")

if install_exts:
    env.Install(os.path.join(dist_path, "petitBloc/python/petitBloc/exts"), Glob("python/petitBloc/exts/*.py"))
