"""Seed default forum categories. Run from backend: python -m scripts.seed_forum_categories"""

from app.services.forum_seed import seed_forum_categories

if __name__ == "__main__":
    seed_forum_categories()
    print("Forum categories seeded.")
