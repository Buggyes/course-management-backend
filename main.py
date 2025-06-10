from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response
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
        return Response(status_code=200)

    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/users/login/")
def login_user(user: UserDTO, session: Session = Depends(get_session)):
    expression = select(User).where(User.login == user.login)
    result = session.exec(expression).first()

    if not result:
        raise HTTPException(status_code=400, detail="Incorrect username")

    if not bcrypt.checkpw(user.password.encode(), result.password.encode()):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return Response(status_code=200)

@app.post("/area/")
def create_area(area: AreaActionDTO, session: Session = Depends(get_session)):
    expression = select(AreaAction).where(AreaAction.name == area.name)
    result = session.exec(expression).first()

    if not result:
        converted_area = AreaAction(name=area.name)
        session.add(converted_area)
        session.commit()
        session.refresh(converted_area)
        return Response(status_code=200)

    raise HTTPException(status_code=400, detail="Area already exists")

@app.get("/areas/")
def get_areas(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[AreaAction]:
    areas = session.exec(select(AreaAction).offset(offset).limit(limit)).all()
    return areas

@app.post("/instructor/")
def create_instructor(instructor: InstructorDTO, session: Session = Depends(get_session)):
    expression = select(Instructor).where(Instructor.name == instructor.name)
    result = session.exec(expression).first()

    if not result:
        converted_instructor = Instructor(name=instructor.name,
        biography=instructor.biography,
        pfp=instructor.pfp,
        banner=instructor.banner)
        session.add(converted_instructor)
        session.commit()
        session.refresh(converted_instructor)
        return Response(status_code=200)

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
    return db_instructor

@app.get("/instructors/")
def get_instructors(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Instructor]:
    instructors = session.exec(select(Instructor).offset(offset).limit(limit)).all()
    return instructors

@app.post("/course/")
def create_course(course: CourseDTO, session: Session = Depends(get_session)):
    expression = select(Course).where(Course.name == course.name)
    result = session.exec(expression).first()

    if not result:
        converted_course = Course(name=course.name,
        description=course.description,
        banner=course.banner,
        instructor_id=course.instructor_id)
        session.add(converted_course)
        session.commit()
        session.refresh(converted_course)
        return Response(status_code=200)

    raise HTTPException(status_code=400, detail="Course already exists")

@app.get("/courses/")
def get_courses(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Course]:
    courses = session.exec(select(Course).offset(offset).limit(limit)).all()
    return courses

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
    return Response(status_code=200)