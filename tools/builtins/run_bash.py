from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

from langchain_core.tools import tool


# 禁止直接调用的程序（按程序名匹配，不看完整路径）。
# 覆盖文件删除/格式化/权限修改/网络传输/提权/关机重启等高危操作。
BLOCKED_PROGRAMS = {
    # 文件删除 / 磁盘操作
    "rm", "rmdir", "shred", "wipefs",
    "dd", "mkfs", "fdisk", "sfdisk", "cfdisk", "parted", "mkswap",
    # 关机 / 系统管理
    "shutdown", "reboot", "halt", "poweroff", "init", "telinit",
    "systemctl", "service", "rc-service", "launchctl", "chkconfig",
    # 权限 / 挂载
    "chmod", "chown", "chattr", "setfacl",
    "mount", "umount",
    # 账户管理
    "passwd", "useradd", "userdel", "usermod",
    "groupadd", "groupdel", "visudo",
    # 提权
    "sudo", "su", "doas", "pkexec",
    # 防火墙
    "iptables", "ip6tables", "nft", "ufw", "firewall-cmd",
    # 计划任务
    "crontab", "at", "batch",
    # 进程控制
    "kill", "killall", "pkill",
    # 网络下载 / 远程执行（容易被利用成 RCE / 数据外泄）
    "curl", "wget", "ncat", "nc", "socat", "telnet",
    "ssh", "scp", "sftp", "rsync",
    "tcpdump", "nmap", "masscan",
    # 容器 / 编排（可绕过沙箱）
    "docker", "podman", "kubectl", "helm",
}

# 命令字符串级别的危险模式（无法仅靠 argv 检测）。
DANGEROUS_PATTERNS = [
    re.compile(r":\s*\(\s*\)\s*\{"),              # fork 炸弹 :(){ :|: & };:
    re.compile(r">\s*/etc/"),                     # 覆盖 /etc
    re.compile(r">\s*/dev/(sd|nvme|xvd|hd)"),     # 写入磁盘设备
    re.compile(r"/dev/(sd|nvme|xvd|hd)[a-z]\d?"), # 直接引用磁盘设备
    re.compile(r"\brm\s+-[a-zA-Z]*[rf]"),         # 任意形式的 rm -rf
]

# 禁止的 shell 元字符：命令替换、后台执行、命令链接等。
# 允许管道 `|` 以便常规数据处理（ls | grep ...）。
FORBIDDEN_SHELL_CHARS = re.compile(r"`|\$\(|\$\{|&&|\|\||(?<!\|);|(?<!&)&(?!$)|<|>>|>")


def _tokenize_segments(command: str) -> list[list[str]]:
    """按管道切分命令并分别分词，供程序名白名单检查使用。"""
    segments = re.split(r"\|(?!\|)", command)
    tokenized: list[list[str]] = []
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        tokenized.append(shlex.split(segment))
    return tokenized


def _classify(command: str) -> str | None:
    """返回拒绝原因，None 表示通过检查。"""
    stripped = command.strip()
    if not stripped:
        return "空命令"

    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(stripped):
            return f"命令匹配危险模式: {pattern.pattern}"

    if FORBIDDEN_SHELL_CHARS.search(stripped):
        return (
            "命令包含不允许的 shell 元字符 "
            "（反引号、$()、${}、&&、||、;、后台执行、重定向等）"
        )

    try:
        segments = _tokenize_segments(stripped)
    except ValueError as exc:
        return f"命令解析失败: {exc}"

    for tokens in segments:
        if not tokens:
            continue
        program = Path(tokens[0]).name
        if program in BLOCKED_PROGRAMS:
            return f"禁止调用命令: {program}"

    return None


@tool("run_bash")
def run_bash(command: str) -> str:
    """
    执行安全的只读 bash 命令。只允许查看/查询/非破坏性命令（如 ls, pwd, echo,
    cat, grep, head, tail, wc, find 等），并显式禁止删除、格式化、权限修改、
    网络下载、提权、关机重启等高危操作。

    为避免命令注入与越权执行，不允许使用命令替换（`、$()、${}）、后台执行（&）、
    命令链接（;、&&、||）以及文件重定向（>、>>、<），仅允许管道 `|`。

    Args:
        command: 要执行的 bash 命令
    """
    reason = _classify(command)
    if reason is not None:
        return f"❌ 拒绝执行命令：{reason}"

    try:
        # 超时 100 秒，防止卡死。
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
    except subprocess.CalledProcessError as exc:
        stdout = (exc.stdout or "").strip()
        stderr = (exc.stderr or "").strip()
        return (
            f"❌ 命令以非零状态码 {exc.returncode} 退出\n"
            f"输出：{stdout}\n错误：{stderr}"
        )
    except Exception as e:
        return f"❌ 执行失败：{str(e)}"
