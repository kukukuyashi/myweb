import secrets
import string
import subprocess
import sys
from pathlib import Path


def generate_password(length: int = 16) -> str:
    # 保证三类字符都有
    lowers = secrets.choice(string.ascii_lowercase)
    uppers = secrets.choice(string.ascii_uppercase)
    digits = secrets.choice(string.digits)
    pool = string.ascii_letters + string.digits
    rest = "".join(secrets.choice(pool) for _ in range(length - 3))
    chars = list(lowers + uppers + digits + rest)
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def main() -> None:
    password = generate_password()
    script = Path(__file__).resolve().parent / "set_admin_password.py"
    subprocess.check_call([sys.executable, str(script), password])
    print("\n=== 管理员新密码（仅显示这一次，请自行保存）===")
    print(password)
    print("============================================")


if __name__ == "__main__":
    main()
