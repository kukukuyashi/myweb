import re
import sys
from pathlib import Path

import bcrypt

MIN_LENGTH = 9
# 至少包含大写、小写、数字
STRONG_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")


def hash_password(password: str) -> str:
    if len(password) < MIN_LENGTH:
        raise SystemExit(f"密码至少 {MIN_LENGTH} 位")
    if not STRONG_PATTERN.match(password):
        raise SystemExit("密码须同时包含大写字母、小写字母和数字")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def update_env(env_path: Path, password_hash: str) -> None:
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    out: list[str] = []
    seen_hash = False
    seen_plain = False
    for line in lines:
        if line.startswith("ADMIN_PASSWORD_HASH="):
            out.append(f"ADMIN_PASSWORD_HASH={password_hash}")
            seen_hash = True
        elif line.startswith("ADMIN_PASSWORD="):
            continue  # 移除明文密码
        else:
            out.append(line)
    if not seen_hash:
        out.append(f"ADMIN_PASSWORD_HASH={password_hash}")
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("用法: python scripts/set_admin_password.py \"YourStrongPass123\"")

    password = sys.argv[1]
    password_hash = hash_password(password)
    env_path = Path(__file__).resolve().parent.parent / ".env"
    update_env(env_path, password_hash)
    print(f"已写入 {env_path} 的 ADMIN_PASSWORD_HASH（明文密码未保存）")
    print("请重启 uvicorn 后使用新密码登录 /admin")


if __name__ == "__main__":
    main()
