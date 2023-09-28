import psycopg2
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

def connect_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="hkm",
        host="localhost"
    )

connection = connect_db()

def create_table():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            due_date DATE NOT NULL,
            status VARCHAR(50) NOT NULL
        )
        """,
    )

    try:
        cursor = connection.cursor()
        for command in commands:
            cursor.execute(command)
        cursor.close()
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

create_table()

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        title = data['title']
        description = data['description']
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        status = data['status']

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, due_date, status) VALUES (%s, %s, %s, %s) RETURNING task_id;",
            (title, description, due_date, status))
        task_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()

        return jsonify({'message': 'Task created', 'task_id': task_id}), 201

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error while creating task'}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        cursor.close()

        task_list = []
        for task in tasks:
            task_list.append({
                'task_id': task[0],
                'title': task[1],
                'description': task[2],
                'due_date': task[3].strftime('%Y-%m-%d'),
                'status': task[4]
            })

        return jsonify(task_list)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error while fetching tasks'}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.get_json()
        title = data['title']
        description = data['description']
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        status = data['status']

        cursor = connection.cursor()
        cursor.execute(
            "UPDATE tasks SET title=%s, description=%s, due_date=%s, status=%s WHERE task_id=%s;",
            (title, description, due_date, status, task_id))
        connection.commit()
        cursor.close()

        return jsonify({'message': 'Task updated'}), 200

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error while updating task'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id=%s;", (task_id,))
        connection.commit()
        cursor.close()

        return jsonify({'message': 'Task deleted'}), 200

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error while deleting task'}), 500

if __name__ == '__main__':
    app.run(debug=True)
