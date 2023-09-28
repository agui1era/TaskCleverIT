import unittest
import json
from app import app, connection

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.connection = connection

    def test_create_task(self):
        response = self.app.post('/tasks', 
                                 data=json.dumps({
                                     'title': 'Test Task',
                                     'description': 'Test Description',
                                     'due_date': '2023-09-28',
                                     'status': 'pending'
                                 }), 
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('task_id', response.get_json())

    def test_get_tasks(self):
        response = self.app.get('/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_update_task(self):
        create_response = self.app.post('/tasks', 
                                        data=json.dumps({
                                            'title': 'Test Task',
                                            'description': 'Test Description',
                                            'due_date': '2023-09-28',
                                            'status': 'pending'
                                        }), 
                                        content_type='application/json')
        task_id = create_response.get_json().get('task_id')
        update_response = self.app.put(f'/tasks/{task_id}', 
                                       data=json.dumps({
                                           'title': 'Updated Test Task',
                                           'description': 'Updated Test Description',
                                           'due_date': '2023-10-01',
                                           'status': 'completed'
                                       }), 
                                       content_type='application/json')
        self.assertEqual(update_response.status_code, 200)

    def test_delete_task(self):
        create_response = self.app.post('/tasks', 
                                        data=json.dumps({
                                            'title': 'Task to Delete',
                                            'description': 'This task will be deleted',
                                            'due_date': '2023-09-28',
                                            'status': 'pending'
                                        }), 
                                        content_type='application/json')
        task_id = create_response.get_json().get('task_id')
        delete_response = self.app.delete(f'/tasks/{task_id}')
        self.assertEqual(delete_response.status_code, 200)

    def tearDown(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE title LIKE 'Test Task%' OR title LIKE 'Updated Test Task' OR title LIKE 'Task to Delete';")
            self.connection.commit()

if __name__ == '__main__':
    unittest.main()
