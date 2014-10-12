from sys import stderr, exit, stdout
import shutil
import subprocess
import os
import requests
from resources import read_template, get_resource_root, get_kernel, get_kernel_inc
from project import Project
from knightos import prepare_environment
from util import copytree, which
from install import execute as cmd_install

def execute(project_name=None, root=None, emulator=None, debugger=None, assembler=None):
    if root == None: root = os.getcwd()
    exists = setup_root(root, project_name)
    proj = Project(root)
    if exists and not project_name:
        project_name = proj.get_config("name")
        print("Found existing project: " + project_name)
    template_vars = {
        'project_name': project_name,
        'assembler': assembler,
        'emulator': emulator,
        'debugger': debugger
    };
    print("Installing SDK...")
    proj.open(os.path.join(root, ".knightos", "sdk.make"), "w+").write(read_template("sdk.make", template_vars))
    proj.open(os.path.join(root, ".knightos", "variables.make"), "w+").write(read_template("variables.make", template_vars))
    install_kernel(os.path.join(root, ".knightos"))
    shutil.move(os.path.join(root, ".knightos", "kernel.inc"), os.path.join(root, ".knightos", "include", "kernel.inc"))
    shutil.move(os.path.join(root, ".knightos", "kernel-TI84pSE.rom"), os.path.join(root, ".knightos", "kernel.rom"))
    if not exists:
        print("Installing templates...")
        proj.open(os.path.join(root, ".gitignore"), "w+").write(read_template("gitignore", template_vars))
        proj.open(os.path.join(root, "main.asm"), "w+").write(read_template("main.asm", template_vars))
        proj.open(os.path.join(root, "Makefile"), "w+").write(read_template("Makefile", template_vars))
        proj.open(os.path.join(root, "package.config"), "w+").write(read_template("package.config", template_vars))
    default_packages = ["core/init"]
    cmd_install(default_packages, site_only=True)
    if which('git') != None:
        if not os.path.exists(os.path.join(root, ".git")):
            print("Initializing new git repository...")
            FNULL = open(os.devnull, 'w')
            subprocess.call(["git", "init", root], stdout=FNULL, stderr=subprocess.STDOUT)
    print("All done! You can use `make help` to find out what to do next.")

def setup_root(root, project_name):
    if os.path.exists(os.path.join(root, ".knightos")):
        stderr.write("{path} not empty. Aborting.\n".format(path=os.path.relpath(root)))
        exit(1)
    os.makedirs(root, mode=0o755, exist_ok=True)
    exists = False
    if len(os.listdir(root)) > 0:
        exists = True
    if not exists and not project_name:
        stderr.write("You must specify a project name for new projects.\n")
        exit(1)
    os.makedirs(os.path.join(root, ".knightos"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "include"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "packages"), mode=0o755)
    os.makedirs(os.path.join(root, ".knightos", "pkgroot"), mode=0o755)
    return exists

def install_kernel(root):
    release = get_latest_kernel()
    print("Installing kernel " + release['tag_name'])
    assets = list()
    assets.append([r for r in release['assets'] if r['name'] == 'kernel.inc'][0])
    assets.append([r for r in release['assets'] if r['name'] == 'kernel-TI84pSE.rom'][0])
    for asset in assets:
        stdout.write("\rDownloading {0}...".format(asset['name']))
        r = requests.get(asset['browser_download_url'])
        total = int(r.headers.get('content-length'))
        length = 0
        with open(os.path.join(root, asset['name']), 'wb') as fd:
            for chunk in r.iter_content(1024):
                fd.write(chunk)
                length += len(chunk)
                stdout.write("\rDownloading {:<20} {:<20}".format(asset['name'], str(int(length / total * 100)) + '%'))
        stdout.write("\n")
    with open(os.path.join(root, 'kernel-version'), 'w') as f:
        f.write(release['tag_name'])

def get_latest_kernel():
    releases = requests.get('https://api.github.com/repos/KnightOS/kernel/releases')
    return releases.json()[0]
