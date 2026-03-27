import unittest
from utils.process_github_data import process_language_data, process_user_data

class TestGitHubStats(unittest.TestCase):
    def setUp(self):
        # Mock data for testing
        self.mock_data = {
            "data": {
                "user": {
                    "repositories": {
                        "edges": [
                            {
                                "node": {
                                    "name": "repo1",
                                    "primaryLanguage": {
                                        "name": "Python",
                                        "color": "#3572A5"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo2",
                                    "primaryLanguage": {
                                        "name": "JavaScript",
                                        "color": "#f1e05a"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo3",
                                    "primaryLanguage": {
                                        "name": "Python",
                                        "color": "#3572A5"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo4",
                                    "primaryLanguage": None
                                }
                            }
                        ]
                    }
                }
            }
        }

    def test_process_language_data(self):
        # Test normal case
        result = process_language_data(self.mock_data)
        self.assertIsNotNone(result)
        self.assertEqual(result["Python"]["count"], 2)
        self.assertEqual(result["JavaScript"]["count"], 1)
        self.assertEqual(len(result), 2)  # Should not count None language

    def test_process_language_data_empty(self):
        # Test with empty data
        empty_data = {
            "data": {
                "user": {
                    "repositories": {
                        "edges": []
                    }
                }
            }
        }
        result = process_language_data(empty_data)
        self.assertEqual(result, {})

    def test_process_language_data_invalid(self):
        # Test with invalid data
        invalid_data = {"data": {"user": {}}}
        result = process_language_data(invalid_data)
        self.assertIsNone(result)

    def test_process_user_data_issues_sum(self):
        # Test user data issue contributions and issue comments are summed
        user_data = {
            "data": {
                "user": {
                    "name": "Test User",
                    "bio": "",
                    "location": "",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "avatarUrl": "",
                    "followers": {"totalCount": 0},
                    "following": {"totalCount": 0},
                    "repositories": {"totalCount": 1},
                    "contributionsCollection": {
                        "totalCommitContributions": 10,
                        "totalPullRequestContributions": 2,
                        "totalIssueContributions": 3,
                        "totalIssueCommentContributions": 5
                    }
                }
            }
        }

        result = process_user_data(user_data)
        self.assertEqual(result.get("total_issues"), 8)
        self.assertEqual(result.get("total_issue_contributions"), 3)
        self.assertEqual(result.get("total_issue_comments"), 5)


if __name__ == '__main__':
    unittest.main() 