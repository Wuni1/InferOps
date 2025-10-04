# scripts/deploy.py

"""
InferOps - 模拟部署脚本

这个脚本模拟了一个自动化的部署流程，用于在服务器上设置和启动 InferOps 系统。
在真实世界中，这可能会被更复杂的工具替代，如 Ansible, Docker Compose, 或 Kubernetes 脚本。

功能:
1. 检查环境依赖。
2. 从版本控制系统拉取最新代码（模拟）。
3. 安装/更新所需的 Python 包。
4. 启动核心服务（网关和监控代理）。
"""

import os
import subprocess
import sys
import time

# --- 配置 ---
# 在真实脚本中，这些路径会更加动态
GATEWAY_DIR = os.path.join(os.path.dirname(__file__), '..', 'gateway')
AGENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'monitor_agent')
REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')

# --- 辅助函数 ---

def print_step(message):
    """打印带有统一样式步骤标题。"""
    print("\n" + "="*50)
    print(f" STEP: {message}")
    print("="*50)

def run_command(command, cwd='.'):
    """在指定目录下运行一个 shell 命令并打印输出。"""
    print(f"  > Running command: {' '.join(command)} in {cwd}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd, shell=True)
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(f"    {line}")
        process.stdout.close()
        return_code = process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)
        print(f"  > Command finished successfully.")
        return True
    except Exception as e:
        print(f"  > !!! Command failed: {e}")
        return False

# --- 部署步骤 ---

def check_dependencies():
    """检查部署所需的基本依赖是否存在。"""
    print_step("检查依赖 (git, python)")
    # 在真实场景中，这里会检查 `git --version`, `python --version` 等
    time.sleep(1)
    print("  > 依赖检查通过。")
    return True

def pull_latest_code():
    """从 Git 仓库拉取最新的代码。"""
    print_step("从 Git 拉取最新代码")
    # 这是一个模拟操作
    print("  > git pull origin main")
    for i in range(5):
        print(f"    Receiving objects: {i*20}%...", end='\r')
        time.sleep(0.3)
    print("\n  > 代码已是最新版本。")
    return True

def install_dependencies():
    """使用 pip 安装 requirements.txt 中的依赖。"""
    print_step("安装/更新 Python 依赖")
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"  > !!! 错误: requirements.txt 未找到于 {REQUIREMENTS_FILE}")
        return False
    
    # 使用 sys.executable 确保我们用的是当前 Python 环境的 pip
    return run_command([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE])

def start_services():
    """启动 InferOps 的核心服务。"""
    print_step("启动核心服务")
    
    print("\n  --- 启动 InferOps 网关 ---")
    # 在真实场景中，我们会使用 gunicorn 或其他进程管理器来启动
    print("  > 模拟命令: uvicorn gateway.main:app --host 0.0.0.0 --port 8000")
    time.sleep(1)
    print("  > 网关服务已在后台启动 (模拟)。")

    print("\n  --- 启动监控代理 (在每个节点上) ---")
    print("  > 模拟命令: python monitor_agent/agent.py")
    time.sleep(1)
    print("  > 监控代理已在后台启动 (模拟)。")
    
    return True

# --- 主函数 ---

def main():
    """执行完整的部署流程。"""
    start_time = time.time()
    print_step("开始 InferOps 部署流程")

    # 按顺序执行每个部署步骤
    if (check_dependencies() and
        pull_latest_code() and
        install_dependencies() and
        start_services()):
        
        duration = time.time() - start_time
        print("\n" + "*"*50)
        print("  ✅ InferOps 部署成功!")
        print(f"  总耗时: {duration:.2f} 秒。")
        print("  访问 http://localhost:8000 查看前端界面。")
        print("*"*50)
    else:
        duration = time.time() - start_time
        print("\n" + "!"*50)
        print("  ❌ InferOps 部署失败。")
        print(f"  总耗时: {duration:.2f} 秒。")
        print("  请检查以上步骤的错误日志。")
        print("!"*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
