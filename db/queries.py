from sqlalchemy import select, func, delete
from .database import AsyncSessionLocal
from .models import User, Workout, ExerciseLog
from datetime import datetime

async def get_or_create_user(telegram_id: int) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

async def start_workout(user_id: int) -> Workout:
    async with AsyncSessionLocal() as session:
        workout = Workout(user_id=user_id)
        session.add(workout)
        await session.commit()
        await session.refresh(workout)
        return workout

async def complete_workout(workout_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Workout).where(Workout.id == workout_id))
        workout = result.scalars().first()
        if workout:
            workout.completed_at = datetime.utcnow()
            await session.commit()

async def log_exercise(workout_id: int, exercise_name: str, reps: int):
    async with AsyncSessionLocal() as session:
        log = ExerciseLog(workout_id=workout_id, exercise_name=exercise_name, reps=reps)
        session.add(log)
        await session.commit()

async def get_last_exercise_record(user_id: int, exercise_name: str):
    async with AsyncSessionLocal() as session:
        stmt = (
            select(ExerciseLog)
            .join(Workout)
            .where(Workout.user_id == user_id)
            .where(ExerciseLog.exercise_name == exercise_name)
            .order_by(ExerciseLog.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

async def reset_user_stats(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Workout.id).where(Workout.user_id == user_id))
        workout_ids = result.scalars().all()
        
        if workout_ids:
            await session.execute(delete(ExerciseLog).where(ExerciseLog.workout_id.in_(workout_ids)))
            await session.execute(delete(Workout).where(Workout.id.in_(workout_ids)))
            await session.commit()

async def get_user_workout_history(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                Workout.completed_at,
                func.sum(ExerciseLog.reps).label('total_reps')
            )
            .join(ExerciseLog, Workout.id == ExerciseLog.workout_id)
            .where(Workout.user_id == user_id)
            .where(Workout.completed_at.is_not(None))
            .group_by(Workout.id)
            .order_by(Workout.completed_at.asc())
        )
        result = await session.execute(stmt)
        return result.all()

async def get_inactive_users(hours: int = 48):
    # Returns users whose last workout was more than `hours` ago
    # We find the latest workout for each user
    async with AsyncSessionLocal() as session:
        # A simple query: users where max(started_at) is older than 48h
        # First, find max started_at for each user
        subq = select(Workout.user_id, func.max(Workout.started_at).label('last_workout')).group_by(Workout.user_id).subquery()
        
        # Then join with User
        stmt = select(User, subq.c.last_workout).join(subq, User.id == subq.c.user_id)
        result = await session.execute(stmt)
        
        inactive_users = []
        now = datetime.utcnow()
        for row in result:
            user = row[0]
            last_workout = row[1]
            if (now - last_workout).total_seconds() > hours * 3600:
                inactive_users.append(user)
        return inactive_users
