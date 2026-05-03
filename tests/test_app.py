import pytest
from app import app
import json
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test if the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CIVIX AI' in response.data

@patch('google.generativeai.GenerativeModel')
def test_chat_api(mock_model, client):
    """Test the chat API endpoint with mocked Gemini response."""
    # Setup mock
    mock_instance = MagicMock()
    mock_model.return_value = mock_instance
    mock_response = MagicMock()
    mock_response.text = "This is a neutral civic answer."
    mock_instance.generate_content.return_value = mock_response

    response = client.post('/api/chat', 
                          data=json.dumps({'message': 'How to vote?', 'mode': 'simple'}),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert data['response'] == "This is a neutral civic answer."

@patch('google.generativeai.GenerativeModel')
def test_election_data_api(mock_model, client):
    """Test the election data API endpoint with mocked Gemini response."""
    # Setup mock
    mock_instance = MagicMock()
    mock_model.return_value = mock_instance
    mock_response = MagicMock()
    
    # Mock valid JSON response from Gemini
    mock_response.text = json.dumps({
        "nextElection": "2029",
        "registeredVoters": "968M+",
        "turnoutGoal": "75%",
        "turnout": {
            "labels": ["2014", "2019", "2024"],
            "data": [66, 67, 65]
        },
        "partySeats": {
            "labels": ["Party A", "Party B"],
            "data": [300, 200]
        },
        "timeline": [
            {"date": "May 2029", "event": "General Election"}
        ]
    })
    mock_instance.generate_content.return_value = mock_response

    response = client.post('/api/election-data', 
                          data=json.dumps({'type': 'general', 'state': ''}),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['nextElection'] == "2029"
    assert 'partySeats' in data
    assert len(data['partySeats']['labels']) == 2
