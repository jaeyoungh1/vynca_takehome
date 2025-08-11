import re
from typing import Annotated, List, Optional
from fastapi import FastAPI, File, UploadFile, Depends, Query
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
from datetime import datetime
from sqlmodel import Column, Field, Relationship, Session, SQLModel, create_engine, select
import pandas as pd
import phonenumbers

# TODO: Separate pydantic modeling for input validation

# database modeling
class AppointmentModel(SQLModel, table=True):
    __tablename__ = "appointment"
    
    id: int| None = Field(default=None, primary_key=True)
    appointment_id: int| None = Field(default=None)
    appointment_date: datetime | None = Field(default=None)
    appointment_type: str
    
    patient_id: int | None = Field(default=None, foreign_key="patient.patient_id")
    patient: Optional["PatientModel"] = Relationship(back_populates="appointments")
    

class PatientModel(SQLModel, table=True):
    __tablename__ = "patient"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int 
    first_name: str| None = Field(default=None)
    last_name: str | None = Field(default=None)
    dob: datetime | None = Field(default=None)
    email: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    address: str | None = Field(default=None)
    appointments: List[AppointmentModel] = Relationship(back_populates="patient", sa_relationship_kwargs={"lazy": "selectin"})

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# graphql classes
@strawberry.type
class Appointment:
    id: int
    appointment_id: Optional[int] 
    appointment_date: datetime | None
    appointment_type: str

@strawberry.type
class Patient:
    id: int 
    patient_id: int 
    first_name: str | None
    last_name: str| None
    dob: datetime| None
    email: str| None
    phone: str| None
    address: str| None
    appointments: List[Appointment]
    
@strawberry.type
class UploadResult:
    success: bool
    message: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def upload_demo_data(self, info) -> UploadResult:
        session: Session = next(get_session())
        # read file 
        txt_file_path = Path(__file__).parent / 'patients_and_appointments.txt'
        result = pd.read_csv(
            txt_file_path,
            on_bad_lines="warn",
            usecols=[
                "patient_id", "first_name", "last_name", "dob",
                "email", "phone", "address",
                "appointment_id", "appointment_date", "appointment_type"
            ]
        )
        def validate_email(email):
            if pd.isna(email):
                return None
            email_pattern = re.compile(r"^[a-zA-Z0-9._%+'-]+[@][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
            email = email.strip()
            if email_pattern.match(email):
                return email
            else:
                return None
        def validate_phone(phone, region="US"):
            if not phone or pd.isna(phone):
                return None
            number = phone.strip()
            phone_pattern = re.compile(r"^\d{10,14}$")
            if phone_pattern.match(number):
                return number
            # if we want to be more strict about picking numbers:
            # parsed = phonenumbers.parse(phone, region)
            # if phonenumbers.is_valid_number(parsed):
            #     return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            else:
                return None

        # clean data 
        result["appointment_date"] = pd.to_datetime(
            result["appointment_date"], format="mixed", errors="coerce"
        )
        result["appointment_id"] = result["appointment_id"].dropna()
        result["dob"] = pd.to_datetime(result["dob"], format="mixed", errors="coerce")
        result["first_name"] = result["first_name"].str.strip().str.capitalize().fillna('')
        result["last_name"] = result["last_name"].str.strip().str.capitalize().fillna('')
        result["phone"] = result["phone"].str.replace(r"\D+", "", regex=True).apply(validate_phone)
        result["email"] = result["email"].str.replace("[at]", "@").apply(validate_email)
        result["appointment_type"] = result["appointment_type"].str.upper().fillna('UNKNOWN')

        appointments = result[result['appointment_id'].notna()].copy()
        
        # POSSIBLE TODO: validate appointments by removing anything with missing field

        patient_objs = {}

        for obj in result.to_dict("records"):
            if obj["patient_id"] not in patient_objs.keys():
                patient_objs[obj['patient_id']] = obj
                patient = PatientModel(
                    patient_id=obj["patient_id"],
                    first_name=obj["first_name"],
                    last_name=obj["last_name"],
                    dob=obj["dob"] if pd.notna(obj["dob"]) else None,
                    email=obj["email"],
                    phone=obj["phone"],
                    address=obj["address"],
                )
                session.add(patient)

        for obj in appointments.to_dict("records"):
            appointment = AppointmentModel(
                appointment_id=obj["appointment_id"],
                appointment_date=obj["appointment_date"]
                    if pd.notna(obj["appointment_date"]) else None,
                appointment_type=obj["appointment_type"],
                patient_id=obj["patient_id"],
            )
            session.add(appointment)

        session.commit()

        return UploadResult(
            success=True,
            message="Demo data uploaded successfully",
        )
    
# RESOLVERS
def get_patients():
    with Session(engine) as session:
        patients = session.exec(select(PatientModel)).all()
        patient = session.exec(select(PatientModel).where(PatientModel.patient_id == 1)).all()
        return patients
def get_appointments():
    with Session(engine) as session:
        appointments = session.exec(select(AppointmentModel)).all()
        return appointments
def get_appointments_by_patient(id: int):
    with Session(engine) as session:
        patient = session.exec(
            select(PatientModel)
            .where(PatientModel.patient_id == id)
        ).first()
        if not patient:
            return None
        return patient

@strawberry.type
class Query:
    patients: List[Patient] = strawberry.field(resolver=get_patients)
    appointments: List[Appointment] = strawberry.field(resolver=get_appointments)
    patient: Optional[Patient] = strawberry.field(resolver=get_appointments_by_patient)

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)

# set up app 
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(graphql_app, prefix='/graphql')

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# REST ROUTES #########################
# TEST ROUTE
@app.get("/ping")
def read_ping_pong():
    return {"ping":"pong"}

# GET ROUTES
@app.get("/patients")
def read_patients(session: SessionDep):
    patients = session.exec(select(Patient)).all()
    return patients

@app.get("/appointments")
def read_appointments(session: SessionDep):
    appointments = session.exec(select(Appointment)).all()
    return appointments

# POST ROUTES
@app.get("/upload-demo-data")
def upload_demo_data(session: SessionDep):
    # reads txt file
    result = pd.read_csv("./patients_and_appointments.txt", on_bad_lines='warn', usecols=['patient_id','first_name','last_name','dob','email','phone','address','appointment_id','appointment_date','appointment_type'])
    # cleans data 
    result['appointment_date'] = pd.to_datetime(result['appointment_date'], format='mixed').fillna(pd.to_datetime(0))
    result['dob'] = pd.to_datetime(result['dob'], format='mixed')
    result['first_name'] = result['first_name'].str.strip().str.capitalize()
    result['last_name'] = result['last_name'].str.strip().str.capitalize()
    result['phone'] = result['phone'].str.replace(r'\D+', '', regex=True)
    result['email'] = result['email'].str.replace('[at]', '@')
    result['appointment_type'] = result['appointment_type'].str.upper()
    result['appointment_id'] = result['appointment_id'].fillna(0).astype(int).replace(0, None)
    
    result = result.fillna('')
    # TODO: add cleanup function for invalid emails

    patient_objs = {}
    appointment_objs = {}
    data = result.to_dict('records')

    for obj in data:
        if obj["patient_id"] not in patient_objs.keys():
            patient_objs[obj['patient_id']] = obj
            session.add(PatientModel(
                patient_id=obj['patient_id'],
                first_name=obj['first_name'],
                last_name=obj['last_name'],
                dob=obj['dob'],
                email=obj['email'],
                phone=obj['phone'],
                address=obj['address']
            ))
            session.commit()
        appointment = AppointmentModel(
            appointment_id=obj['appointment_id'],
            appointment_date=obj['appointment_date'],
            appointment_type=obj['appointment_type'],
            patient_id=obj["patient_id"],
            )
        session.add(appointment)
        session.commit()
    
    return {
        "data": data
    }

@app.post("/upload-file-data")
def upload_file_data(file: UploadFile, session: SessionDep):
    result = pd.read_csv(file, on_bad_lines='warn', usecols=['patient_id','first_name','last_name','dob','email','phone','address','appointment_id','appointment_date','appointment_type'])
    result['appointment_date'] = pd.to_datetime(result['appointment_date'], format='mixed').fillna(pd.to_datetime(0))
    result['dob'] = pd.to_datetime(result['dob'], format='mixed')
    result['first_name'] = result['first_name'].str.strip().str.capitalize()
    result['last_name'] = result['last_name'].str.strip().str.capitalize()
    result['phone'] = result['phone'].str.replace(r'\D+', '', regex=True)
    result['email'] = result['email'].str.replace('[at]', '@')
    result['appointment_type'] = result['appointment_type'].str.upper()
    result['appointment_id'] = result['appointment_id'].fillna(0).astype(int).replace(0, None)
    
    result = result.fillna('')
    # add cleanup function for invalid emails

    patient_objs = [Patient(**row) for row in result.to_dict('records')]
    appointment_objs = [Appointment(**row) for row in result.to_dict('records')]

    for obj in patient_objs:
        session.add(obj)
    for obj in appointment_objs:
        session.add(obj)

    session.commit()
    
    return {
        "patients": patient_objs,
        "appointments": appointment_objs
    }
