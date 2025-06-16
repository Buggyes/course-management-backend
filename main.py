import json
import requests
import base64
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session, create_engine, select
from sqlalchemy import and_
from models import *
from security import *
from fastapi.middleware.cors import CORSMiddleware

database_url = "postgresql://localhost/course_management_db"

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# API calls

@app.post("/users/")
def create_user(user: UserDTO, session: Session = Depends(get_session)):
    expression = select(User).where(User.login == user.login)
    result = session.exec(expression).first()

    if not result:
        converted_user = User(login=user.login, password=encrypt_pass(user.password))
        session.add(converted_user)
        session.commit()
        session.refresh(converted_user)
        return JSONResponse(status_code=200, content={"message": "created"})

    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/users/login/")
def login_user(user: UserDTO, session: Session = Depends(get_session)):
    expression = select(User).where(User.login == user.login)
    result = session.exec(expression).first()

    if not result:
        raise HTTPException(status_code=400, detail="Incorrect username")

    if not bcrypt.checkpw(user.password.encode('utf-8'), result.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return JSONResponse(status_code=200, content={"message": "logged in"})

@app.post("/area/")
def create_area(area: AreaActionDTO, session: Session = Depends(get_session)):
    expression = select(AreaAction).where(AreaAction.name == area.name)
    result = session.exec(expression).first()

    if not result:
        converted_area = AreaAction(name=area.name)
        session.add(converted_area)
        session.commit()
        session.refresh(converted_area)
        return JSONResponse(status_code=200, content={ "message": "area created" })

    raise HTTPException(status_code=400, detail="Area already exists")

@app.get("/areas/")
def get_areas(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[AreaAction]:
    areas = session.exec(select(AreaAction).offset(offset).limit(limit)).all()
    return areas

@app.post("/instructor/")
def create_instructor(
    name: str = Form(...),
    biography: str = Form(...),
    areas_id: list[int] = Form(...),
    pfp: UploadFile = File(...),
    banner: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    pfp_data = pfp.file.read()
    banner_data = banner.file.read()
    expression = select(Instructor).where(Instructor.name == name)
    result = session.exec(expression).first()

    if not result:
        converted_instructor = Instructor(
            name=name,
            biography=biography,
            pfp=pfp_data,
            banner=banner_data
        )

        session.add(converted_instructor)
        session.commit()
        session.refresh(converted_instructor)

        for a in areas_id:
            instructor_area = InstructorArea(instructor_id=converted_instructor.id, area_id=a)
            session.add(instructor_area)

        session.commit()
        return JSONResponse(status_code=200, content={"message": "Instructor created"})

    raise HTTPException(status_code=400, detail="Instructor already exists")

@app.patch("/instructor/", response_model=Instructor)
def update_instructor(instructor_id: int, instructor: InstructorUpdateDTO, session: Session = Depends(get_session)):
    expression = select(Instructor).where(Instructor.id == instructor_id)
    db_instructor = session.exec(expression).first()

    if not db_instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    instructor_data = instructor.dict(exclude_unset=True)

    for key, value in instructor_data.items():
        setattr(db_instructor, key, value)
    
    session.add(db_instructor)
    session.commit()
    session.refresh(db_instructor)
    return JSONResponse(status_code=200, content={"message": "instructor updated"})

@app.get("/instructors/")
def get_instructors(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    instructors = session.exec(
        select(Instructor).offset(offset).limit(limit)
    ).all()

    result = []

    for instructor in instructors:
        instructor_areas = session.exec(
            select(InstructorArea).where(InstructorArea.instructor_id == instructor.id)
        ).all()

        area_ids = [ia.area_id for ia in instructor_areas]

        areas = session.exec(
            select(AreaAction).where(AreaAction.id.in_(area_ids))
        ).all()

        result.append({
            "id": instructor.id,
            "name": instructor.name,
            "biography": instructor.biography,
            "pfp": f"data:image/png;base64,{base64.b64encode(instructor.pfp).decode()}" if instructor.pfp else None,
            "banner": f"data:image/png;base64,{base64.b64encode(instructor.banner).decode()}" if instructor.banner else None,
            "areas": [{"id": area.id, "name": area.name} for area in areas]
        })

    return JSONResponse(content=result)

@app.delete("/instructor/{instructor_id}")
def delete_instructor(instructor_id: int, session: SessionDep):
    instructor = session.get(Instructor, instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    courses = session.exec(
        select(Course).where(Course.instructor_id == instructor.id)
    ).all()
    if courses:
        raise HTTPException(status_code=400, detail="Instructor is attached to courses")
    instructorArea = session.exec(select(InstructorArea).where(InstructorArea.instructor_id == instructor_id)).all()
    for a in instructorArea:
        session.delete(a)
    session.commit()
    session.delete(instructor)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "Instructor deleted"})

@app.post("/course/")
def create_course(
    name: str = Form(...),
    description: str = Form(...),
    instructor_id: int = Form(...),
    area_id: int = Form(...),
    banner: UploadFile = File(...),
    session: Session = Depends(get_session)):
    
    result = session.exec(select(Course).where(Course.name == name)).first()

    if not result:
        converted_course = Course(name=name,
        description=description,
        banner=banner.file.read(),
        instructor_id=instructor_id,
        area_id=area_id
        )
        session.add(converted_course)
        session.commit()
        session.refresh(converted_course)
        return JSONResponse(status_code=200, content={"message":"Course added"})

    raise HTTPException(status_code=400, detail="Course already exists")

@app.get("/courses/")
def get_courses(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    courses = session.exec(
        select(Course).offset(offset).limit(limit)
    ).all()

    result = []

    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "banner": f"data:image/png;base64,{base64.b64encode(course.banner).decode()}" if course.banner else None,
            "instructor": course.instructor_id,
            "area": course.area_id,
        })

    return JSONResponse(content=result)

@app.get("/courses/{area_id}")
def get_courses(area_id: int, session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Course]:
    courses = session.exec(
        select(Course).offset(offset).limit(limit).where(Course.area_id == area_id)
    ).all()

    result = []

    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "banner": f"data:image/png;base64,{base64.b64encode(course.banner).decode()}" if course.banner else None,
            "instructor": course.instructor_id,
            "area": course.area_id,
        })

    return JSONResponse(content=result)

@app.patch("/course/", response_model=Course)
def update_course(course_id: int, course: CourseUpdateDTO, session: Session = Depends(get_session)):
    expression = select(Course).where(Course.id == course_id)
    db_course = session.exec(expression).first()

    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_data = course.dict(exclude_unset=True)

    for key, value in course_data.items():
        setattr(db_course, key, value)
    
    session.add(db_course)
    session.commit()
    session.refresh(db_course)
    return db_course

@app.delete("/course/{course_id}")
def delete_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course)
    session.commit()
    return JSONResponse(status_code=200, content={"message": "Course deleted"})
