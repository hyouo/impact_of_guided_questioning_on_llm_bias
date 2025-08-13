import subprocess
import sys
import os
import pkg_resources # To check installed packages

def _check_package_installed(package_name):
    """Checks if a package is installed and returns its version, or None if not found."""
    try:
        dist = pkg_resources.get_distribution(package_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return None

def setup_environment():
    venv_dir = "venv"
    pip_path = os.path.join(venv_dir, "Scripts", "pip.exe") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "pip")
    requirements_file = "requirements.txt"

    print("--- 环境检查与依赖管理 ---")

    # 1. Check and create virtual environment
    if not os.path.exists(venv_dir) or not os.path.exists(pip_path):
        print(f"虚拟环境 '{venv_dir}' 不存在或不完整，正在创建...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print(f"虚拟环境 '{venv_dir}' 创建成功。")
        except subprocess.CalledProcessError as e:
            print(f"创建虚拟环境失败: {e}")
            sys.exit(1)
    else:
        print(f"虚拟环境 '{venv_dir}' 已存在。")

    # 2. Check dependencies from requirements.txt
    print(f"\n正在检查项目依赖项 (来自 {requirements_file})...")
    
    missing_packages = []
    try:
        with open(requirements_file, "r", encoding="utf-8") as f:
            required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"错误: {requirements_file} 文件未找到。请确保它存在。", file=sys.stderr)
        sys.exit(1)

    for req_package in required_packages:
        # pkg_resources.Requirement handles parsing "package==version", "package>=version" etc.
        try:
            req = pkg_resources.Requirement.parse(req_package)
            installed_version = _check_package_installed(req.name)
            
            if installed_version:
                # Check if installed version satisfies the requirement
                if req.specifier.contains(installed_version):
                    print(f"  - {req.name} {installed_version} (已安装并满足要求)")
                else:
                    print(f"  - {req.name} {installed_version} (已安装但版本不满足要求: {req.specifier})")
                    missing_packages.append(req_package) # Treat as missing for re-installation
            else:
                print(f"  - {req.name} (未安装)")
                missing_packages.append(req_package)
        except Exception as e:
            print(f"  - 无法解析依赖项 '{req_package}': {e}", file=sys.stderr)
            missing_packages.append(req_package) # Try to install anyway if parsing fails

    # 3. Install missing/unsatisfied dependencies
    if missing_packages:
        print(f"\n检测到 {len(missing_packages)} 个缺失或版本不符的依赖项，正在安装/更新...")
        try:
            # Use the pip from the venv
            subprocess.check_call([pip_path, "install", "-r", requirements_file])
            print("所有依赖项安装/更新成功。")
        except subprocess.CalledProcessError as e:
            print(f"安装依赖项失败: {e}")
            sys.exit(1)
    else:
        print("\n所有依赖项均已安装并满足要求。")

    print("\n--- 环境设置完成 ---")

if __name__ == "__main__":
    setup_environment()