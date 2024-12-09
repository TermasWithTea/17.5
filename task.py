from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import select, update, delete
from slugify import slugify
router = APIRouter(prefix='/task', tags= ['task'])



@router.get('/')
async def all_tasks(db:Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task).where(Task.id == True)).scalars().all()
    return tasks

@router.get('/task_id')
async def task_by_id(user_id: int, db:Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task).where(Task.id == user_id)).scalar_one_or_none()

    if tasks is None:
        raise HTTPException(status_code=404, detail='User was not found')
    return tasks

@router.post('/creat')
async def create_task(user_id: int, db:Annotated[Session, Depends(get_db)],create_task: CreateTask):
    tasks = db.scalar(select(User).where(User.id == user_id))
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_task = Task(
        title=create_task.title,
        content=create_task.content,
        priority = create_task.priority,
        slug = slugify(create_task.title)
    )

    db.add(new_task)
    db.commit()

    return {'status_code': status.HTTP_201_CREATED, 'transaction':'Successful'}

@router.put('/update')
async def update_task(db:Annotated[Session, Depends(get_db)], update_task: UpdateTask, user_id:int):
        tasks = db.scalar(update(Task).where(Task.id == update_task).values(
        title = update_task.title,
        content = update_task.content,
        priority = update_task.priority,
        slug = slugify(update_task.title)
        ))
        if tasks is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

@router.delete('/delete')
async def delete_task(db:Annotated[Session, Depends(get_db)], update_task: UpdateTask, user_id:int):
    existing_user = db.scalar(select(Task).where(Task.id == user_id))
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    tasks = delete(Task).where(Task.id == user_id)
    db.execute(tasks)
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User deletion is successful!'}