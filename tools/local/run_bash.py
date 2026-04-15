from langchain_core.tools import tool

DANGEROUS_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~/*",
    "chmod -R 000 /",
    "chown -R nobody /",
    "mkfs.ext4 /dev/sd",
    "dd if=/dev/zero of=/dev/sd",
    "iptables -F",
    ":(){ :|: & };:",  # fork 炸弹
    "find / -delete",
    "> /etc/passwd",
    "> /etc/shadow",
]

@tool("run_bash")
def run_bash(command: str) -> str:
    """
    执行安全的 bash 命令，禁止执行任何高危系统命令。
    只能执行查看、查询、非破坏性命令（如 ls, pwd, echo, cat 等）。

    Args:
        command: 你要执行的 bash 命令
    """
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command:
            return f"❌ 不可执行危险命令！！！ \n 拦截到的命令：{dangerous}"

    try:
        import subprocess
        # 超时 100 秒，防止卡死
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=100,
            check=True,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()
        return f"✅ 执行成功\n输出：{output}\n错误：{error}"

    except subprocess.TimeoutExpired:
        return "❌ bash工具执行超时（超过100秒），已终止"
    except Exception as e:
        return f"❌ 执行失败：{str(e)}"