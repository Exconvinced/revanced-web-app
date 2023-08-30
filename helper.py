import os, re, sys, json
import subprocess as sp
import requests


revanced_dir = 'revanced'
database = os.path.join('static', 'packages.db')

java = os.path.join(revanced_dir, 'jdk', 'bin', 'java.exe')
revanced_cli = os.path.join(revanced_dir, 'revanced-cli.jar')
dependencies_dir = os.path.join(revanced_dir, 'dependencies')
patches = os.path.join(dependencies_dir, 'patches.jar')
integrations = os.path.join(dependencies_dir, 'integrations.apk')

aapt = os.path.join(revanced_dir, 'aapt', 'aapt_64.exe')
apk_directory = os.path.join(revanced_dir, 'apk')
unpatched_apk = os.path.join(apk_directory, 'unpatched.apk')
patched_apk = os.path.join(apk_directory, 'patched.apk')


def get_revanced_patches_json() -> dict:
    """
    Download ReVanced patches.json
    """
    url = "https://raw.githubusercontent.com/ReVanced/revanced-patches/v2.186.0/patches.json"
    response = requests.get(url)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print("Failed to fetch the JSON data. Status code:", response.status_code)
        return None

patches_json = get_revanced_patches_json()

def get_all_app_versions(package_name) -> list:
    """
    Return all compatible app versions for a given package name
    """
    def version_key(version):
        return tuple(map(int, (version.split("."))))
    versions = set(version for patch in patches_json for package in patch['compatiblePackages'] if package['name'] == package_name for version in package['versions'])
    try:
        return sorted(versions, key=version_key)
    except:
        return 'Any'


def get_compatible_patches(package_name=None, package_version=None) -> set:
    """
    Return all compatible patches for a given package name and version
    """
    class Patch:
        def __init__(self, name: str, description: str, version: str, excluded: bool):
            self.name = name
            self.token = self.name.lower().replace(" ", "-")
            self.description = description
            self.version = version
            self.excluded = excluded

    for p in patches_json:
        # If no compatible package is specified
        if not p["compatiblePackages"] or package_name is None and package_version is None:  
            yield Patch(p["name"], p["description"], p["version"], p["excluded"]).__dict__
        else:
            for package in p["compatiblePackages"]:
                if package_name == package["name"]:
                    # If no compatible version is specified or the version is compatible
                    if not package["versions"] or package_version in package["versions"]:
                        yield Patch(p["name"], p["description"], p["version"], p["excluded"]).__dict__


def check_patch_exclusion(patch_name) -> bool:
    """
    Return True if a patch is excluded by default
    """
    for patch in get_compatible_patches():
        if patch['name'].lower().replace(' ', '-') == patch_name:
            return patch['excluded']
    return False


def generate_revanced_args(data, args=str()) -> str:
    """
    Return additional commandline arguments for included/excluded patches
    """
    for patch in data['included_patches']:
        if check_patch_exclusion(patch):
            args += f'-i {patch} '
    for patch in data['excluded_patches']:
        if not check_patch_exclusion(patch):
            args += f'-e {patch} '
    return args


def data_stream(string) -> str:
    """
    Return a string in the format of Server-Sent Events
    """
    return 'data:' + string.rstrip() + '\n\n'



def read_apk_file(file):
    """
    Return package name, version and label of an APK file
    """
    try:
        aapt_command = [aapt, 'dump', 'badging', file]
        aapt_output_bytes = sp.check_output(aapt_command)
        aapt_output = aapt_output_bytes.decode('utf-8')

        for line in aapt_output.splitlines():
            if line.startswith('package:'):
                package_name = re.search(r"name='(.+?)'", line).group(1)
                package_version = re.search(r"versionName='(.+?)'", line).group(1)
                package_version = package_version if package_version else 'Any'
            elif line.startswith('application-label:'):
                app_label = line.split(':')[1].strip("'")

        try:
            recommended_version = get_all_app_versions(package_name)[-1]
        except:
            recommended_version = 'Any'

        apk_info = {
            'package_name': package_name, 
            'package_version': package_version, 
            'recommended_version': recommended_version, 
            'app_label': app_label
            }
        return apk_info
    except:
        return None


def delete_uploaded_files():
    """
    Delete uploaded files
    """
    try:
        os.remove(unpatched_apk)
        print(f"File '{unpatched_apk}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{unpatched_apk}' not found.")
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")


def remove_files_in_directory():
    """
    Remove all patched and unpatched APK files
    """
    try:
        for file in os.listdir(apk_directory):
            file_path = os.path.join(apk_directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Error occurred while removing files: {e}")


def start_revanced_patch(args):
    """
    Start patching the APK file
    """
    if not read_apk_file(unpatched_apk):
        error = 'Check if you uploaded a valid APK file.'
        yield data_stream(json.dumps({'error': error}))
        return
    
    command = ["java", '-jar', revanced_cli, '-a', unpatched_apk, '-o', patched_apk, '-b', patches, '-m', integrations] + args.split()

    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    for line in process.stdout: # Print both output and error messages
        last_line = line

        if 'PatchResultError' in line:
            break
        elif line.startswith("INFO:"):
            yield data_stream(json.dumps({'data': line}))

    if 'Finished' not in last_line:
        error = 'An error occurred while patching the APK file.'
        yield data_stream(json.dumps({'error': f'ERROR: {error}'}))
        process.terminate()
        
    return


def retrieve_patched_apk():
    """
    Return the patched APK file
    """
    return patched_apk


def is_java_sdk_installed():
    """
    Return True if Java SDK is installed
    """
    try:
        result = sp.run(['java', '--version'], stdout=sp.PIPE, stderr=sp.PIPE, text=True)
        if result.returncode == 0:
            return True
        return False
    
    except FileNotFoundError:
        return False


def get_jdk_url():
    """
    Return the download link for Java SDK
    """
    jdk_download_links = {
        "windows": "https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_windows-x64_bin.zip",
        "mac": "https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_osx-x64_bin.tar.gz",
        "linux": "https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz"
    }
    match sys.platform:
        case "win32":
            return jdk_download_links["windows"]
        case "darwin":
            return jdk_download_links["mac"]
        case "linux":
            return jdk_download_links["linux"]