from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.testclient import TestClient
from main import app, create_db_and_tables, engine
from sqlmodel import Session, create_engine
from main import SQLModel

client = TestClient(app)

def test_all_patients():
    query = """
    query {
        patients {
            patientId
            firstName
            lastName
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert "patients" in data["data"]
    assert isinstance(data["data"]["patients"], list)

def test_all_appointments():
    query = """
    query {
        appointments {
            appointmentId
            appointmentDate
            appointmentType
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "appointments" in data["data"]
    assert isinstance(data["data"]["appointments"], list)

def test_patient_by_id():
    query = """
    query Patient($id: Int!) {
        patient(id: $id) {
            patientId
            firstName
            lastName
            appointments {
                appointmentId
                appointmentDate
                appointmentType
            }
        }
    }
    """
    variables = {"id": 1} 

    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    patient = data["data"]["patient"]
    assert patient is not None
    assert patient["patientId"] == 1
    assert isinstance(patient["appointments"], list)

def test_query_nonexistent_patient():
    query = """
    query Patient($id: Int!) {
        patient(id: $id) {
            patientId
            firstName
        }
    }
    """
    variables = {"id": 999999}  
    response = client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["patient"] is None or "errors" in data
