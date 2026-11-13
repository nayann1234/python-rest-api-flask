import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_NAME = "database.db"


def init_db():
  """Initialize SQLite database and create table if it doesn't exist."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)
  conn.commit()
  conn.close()


@app.route("/")
def home():
  return jsonify({
      "message": "Welcome to the Advanced Python REST API (Module 05)",
      "endpoints": {
          "GET /items": "Retrieve all items",
          "POST /items": "Create a new item",
          "PUT /items/<id>": "Update an item",
          "DELETE /items/<id>": "Delete an item",
      },
  })


@app.route("/items", methods=["GET"])
def get_items():
  """Retrieve all items from SQLite database (Read)."""
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM items")
  rows = cursor.fetchall()
  conn.close()

  items = [dict(row) for row in rows]
  return jsonify({"success": True, "count": len(items), "data": items}), 200


@app.route("/items", methods=["POST"])
def create_item():
  """Create a new item in the database (Create)."""
  data = request.get_json()
  if not data or "title" not in data:
    return (
        jsonify({"success": False, "error": "Title field is required"}),
        400,
    )

  title = data["title"]
  description = data.get("description", "")
  status = data.get("status", "Pending")

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO items (title, description, status) VALUES (?, ?, ?)",
      (title, description, status),
  )
  conn.commit()
  item_id = cursor.lastrowid
  conn.close()

  return (
      jsonify({
          "success": True,
          "message": "Item created successfully",
          "data": {
              "id": item_id,
              "title": title,
              "description": description,
              "status": status,
          },
      }),
      201,
  )


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
  """Update an existing item (Update)."""
  data = request.get_json()
  if not data:
    return (
        jsonify({"success": False, "error": "No update data provided"}),
        400,
    )

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
  if not cursor.fetchone():
    conn.close()
    return jsonify({"success": False, "error": "Item not found"}), 404

  title = data.get("title")
  description = data.get("description")
  status = data.get("status")

  cursor.execute(
      """
        UPDATE items 
        SET title = COALESCE(?, title), 
            description = COALESCE(?, description), 
            status = COALESCE(?, status) 
        WHERE id = ?
    """,
      (title, description, status, item_id),
  )
  conn.commit()
  conn.close()

  return (
      jsonify({
          "success": True,
          "message": f"Item {item_id} updated successfully",
      }),
      200,
  )


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
  """Delete an item by ID (Delete)."""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
  if not cursor.fetchone():
    conn.close()
    return jsonify({"success": False, "error": "Item not found"}), 404

  cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
  conn.commit()
  conn.close()

  return (
      jsonify({
          "success": True,
          "message": f"Item {item_id} deleted successfully",
      }),
      200,
  )


if __name__ == "__main__":
  init_db()
  app.run(debug=True, port=5000)
