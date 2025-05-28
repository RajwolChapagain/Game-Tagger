import sqlite3
import random
import sys

# ---- Configuration ----
DB_PATH = "data/tag_info.db"
SOURCE_TABLE = "games"
TRAIN_TABLE = "train"
TEST_TABLE = "test"
SPLIT_RATIO = 0.8  # 80% train, 20% test

# ------------------------
def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all data from the source table
    cursor.execute(f"SELECT * FROM {SOURCE_TABLE}")
    rows = cursor.fetchall()

    # Get column names to recreate the schema
    col_names = [description[0] for description in cursor.description]
    columns_def = (f"{col_names[0]} INTEGER, " + ", ".join(f"{col} BOOLEAN" for col in col_names[1:]))


    # Shuffle and split
    random.shuffle(rows)
    split_point = int(len(rows) * SPLIT_RATIO)
    train_rows = rows[:split_point]
    test_rows = rows[split_point:]

    # Drop old train/test tables if they exist
    cursor.execute(f"DROP TABLE IF EXISTS {TRAIN_TABLE}")
    cursor.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")

    # Create train and test tables
    cursor.execute(f"CREATE TABLE {TRAIN_TABLE} ({columns_def})")
    cursor.execute(f"CREATE TABLE {TEST_TABLE} ({columns_def})")

    # Insert data into train and test tables
    placeholders = ", ".join(["?"] * len(col_names))
    cursor.executemany(f"INSERT INTO {TRAIN_TABLE} VALUES ({placeholders})", train_rows)
    cursor.executemany(f"INSERT INTO {TEST_TABLE} VALUES ({placeholders})", test_rows)

    conn.commit()
    conn.close()
    print(f"Split complete. {len(train_rows)} train rows, {len(test_rows)} test rows.")

if __name__ == "__main__":
    main()

