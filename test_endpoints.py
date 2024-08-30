import unittest
from fastapi.testclient import TestClient
from __init__ import app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_chat_message(self):
        response = self.client.post("/ai/chat/message/", json={
            "roomId": "room123",
            "content": "안녕, AI!",
            "senderType": "USER"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("AI response to: Hello, AI!", response.json()["content"])

    # def test_chat_remove(self):
    #     self.client.post("/ai/chat/message/", json={
    #         "roomId": "user1",
    #         "content": "안녕, AI!",
    #         "senderType": "USER"
    #     })
    #     response = self.client.post("/ai/chat/remove/", json={
    #         "roomId": "user1",
    #         "senderType": "USER"
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.json()["success"])

    # 추가적인 테스트 케이스를 여기 작성

if __name__ == "__main__":
    unittest.main()
