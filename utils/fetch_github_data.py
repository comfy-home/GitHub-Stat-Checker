import requests
import streamlit as st
from datetime import datetime

BASE_URL = "https://api.github.com/graphql"


def _graphql_query(query: str, headers: dict):
    """Execute GraphQL query and normalize errors."""
    try:
        response = requests.post(BASE_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, dict) and "errors" in result:
            error_items = result.get("errors") or []
            if isinstance(error_items, list):
                messages = []
                for item in error_items:
                    if isinstance(item, dict):
                        messages.append(item.get("message", str(item)))
                    else:
                        messages.append(str(item))
                return {"errors": "; ".join(messages)}
            return {"errors": str(error_items)}

        return result
    except requests.exceptions.RequestException as e:
        return {"errors": str(e)}

@st.cache_data(ttl=300)
def fetch_data_for_duration(username: str, token: str, from_date: str, to_date: str):
    """
    Fetch user data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing user data or error message.
    """
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{ 
      user(login: "{username}") {{
        createdAt
        contributionsCollection(from: "{from_date}T00:00:00Z", to: "{to_date}T23:59:59Z") {{
          restrictedContributionsCount
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          contributionCalendar {{
            totalContributions
            weeks {{
              contributionDays {{
                contributionCount
                date
              }}
            }}
          }}
        }}
      }}
    }}
    """
    return _graphql_query(query, headers)

@st.cache_data(ttl=300)    
def fetch_user_data(username: str, token: str):
    """
    Fetch user data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing user data or error message.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Don't exceed GitHub GraphQL 1-year window constraint; omit `from/to` and let GitHub provide the default contributions collection.
    query = f"""
    {{
        user(login: "{username}") {{
            name
            bio
            location
            createdAt
            avatarUrl
            followers {{
                totalCount
            }}
            following {{
                totalCount
            }}
            repositories(ownerAffiliations: OWNER, isFork: false){{
                totalCount
            }}
            issues(states: [OPEN, CLOSED]) {{
                totalCount
            }}
            pullRequests(states: [OPEN, CLOSED]) {{
                totalCount
            }}
            contributionsCollection {{
                totalCommitContributions
                totalPullRequestContributions
                totalIssueContributions
            }}
        }}
    }}
    """
    return _graphql_query(query, headers)

@st.cache_data(ttl=300)
def fetch_repo_data(username: str, token: str):
    """
    Fetch repository data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing repository data or error message.
    """
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {{
                totalCount
                edges {{
                    node {{
                        name
                        primaryLanguage {{
                            name
                            color
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    return _graphql_query(query, headers)

@st.cache_data(ttl=300)
def fetch_contribution_data(username: str, token: str):
    """
    Fetch contribution data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing contribution data or error message.
    """
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            contributionsCollection {{
                restrictedContributionsCount
                totalPullRequestContributions
                totalIssueContributions
                contributionCalendar {{
                    totalContributions
                    weeks {{
                        contributionDays {{
                            contributionCount
                            date
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    return _graphql_query(query, headers)


@st.cache_data(ttl=300)
def fetch_star_count():
    """
    Returns the number of stars for the GitHub-Stat-Checker repository.
    """
    url = "https://api.github.com/repos/TheCarbun/GitHub-Stat-Checker"
    try:
        response = requests.get(url).json()
        return response.get('stargazers_count', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stars: {e}")
        return 0