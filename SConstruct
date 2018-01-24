env = Environment()


install_nodz = True
install_qtpy = True


try:
    install_nodz = int(ARGUMENTS.get("install-nodz", "1")) != 0
except:
    install_nodz = True


try:
    install_qtpy = int(ARGUMENTS.get("install-qtpy", "1")) != 0
except:
    install_qtpy = True


env.Install("release/petitBloc", Glob("python/petitBloc/*.py"))
env.Install("release/petitBloc/ui", Glob("python/petitBloc/ui/*.py"))
env.Install("release/petitBloc/ui", Glob("python/petitBloc/ui/*.json"))


if install_nodz:
    env.Install("release/petitBloc/ui/external/Nodz", "Nodz/__init__.py")
    env.Install("release/petitBloc/ui/external/Nodz", "Nodz/nodz_main.py")
    env.Install("release/petitBloc/ui/external/Nodz", "Nodz/nodz_utils.py")
    env.Install("release/petitBloc/ui/external/Nodz", "Nodz/default_config.json")

if install_qtpy:
    env.Install("release/petitBloc/ui/external", "Qt.py/Qt.py")
