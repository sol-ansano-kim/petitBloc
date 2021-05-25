import os


version = "1.3.1"


def GenerateVersion(target, source, env):
    info = """def version():
    return \"{}\"
""".format(version)

    tgt = target[0].get_abspath()
    with open(tgt, "w") as f:
        f.write(info)


env = Environment()


install_nodz = True
install_qtpy = True
install_enum = True
install_exts = True
install_das = True
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
    install_enum = int(ARGUMENTS.get("install-enum", "1")) != 0
except:
    install_enum = True


try:
    install_exts = int(ARGUMENTS.get("install-exts", "1")) != 0
except:
    install_exts = True


try:
    install_das = int(ARGUMENTS.get("install-das", "1")) != 0
except:
    install_das = True


version_file = env.Command(os.path.abspath("python/petitBloc/version.py"), None, GenerateVersion)
env.Install(os.path.join(dist_path, "python/petitBloc"), Glob("python/petitBloc/*.py"))
env.Install(os.path.join(dist_path, "python/petitBloc"), Glob("python/petitBloc/version.py"))
env.Install(os.path.join(dist_path, "bin"), Glob("bin/*"))
env.Install(os.path.join(dist_path, "python/petitBloc/ui"), Glob("python/petitBloc/ui/*.py"))
env.Install(os.path.join(dist_path, "python/petitBloc/ui"), Glob("python/petitBloc/ui/*.json"))
env.Install(os.path.join(dist_path, "python/petitBloc/ui"), Glob("python/petitBloc/ui/*.qss"))
env.Install(os.path.join(dist_path, "python/petitBloc/ui/icons"), Glob("python/petitBloc/ui/icons/*.png"))
env.Install(os.path.join(dist_path, "python/petitBloc/blocks"), Glob("blocks/*.py"))
env.Install(os.path.join(dist_path, "python/petitBloc/blocks"), Glob("blocks/*.config"))
env.Install(os.path.join(dist_path, "python/petitBloc/patches"), Glob("python/petitBloc/patches/*.py"))


if install_nodz:
    env.Install(os.path.join(dist_path, "python/Nodz"), "Nodz/__init__.py")
    env.Install(os.path.join(dist_path, "python/Nodz"), "Nodz/nodz_main.py")
    env.Install(os.path.join(dist_path, "python/Nodz"), "Nodz/nodz_utils.py")
    env.Install(os.path.join(dist_path, "python/Nodz"), "Nodz/default_config.json")

if install_qtpy:
    env.Install(os.path.join(dist_path, "python"), "Qt_dot_py/Qt.py")

if install_enum:
    env.Install(os.path.join(dist_path, "python"), "python/enum.py")

if install_exts:
    env.Install(os.path.join(dist_path, "python/petitBloc/exts"), Glob("python/petitBloc/exts/*.py"))

if install_das:
    env.Install(os.path.join(dist_path, "python"), Glob("das/python/das"))
