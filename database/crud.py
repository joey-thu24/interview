from sqlalchemy.orm import Session
from database.models import StudyPlan, InterviewSession
from datetime import date
import json

def get_today_plan(db: Session, user_id: int):
    return db.query(StudyPlan).filter(StudyPlan.user_id == user_id, StudyPlan.date == date.today()).first()

def create_daily_plan(db: Session, user_id: int, plan_data: dict, encouragement: str):
    # plan_data is list of tasks
    db_plan = StudyPlan(
        user_id=user_id,
        content=plan_data,
        encouragement=encouragement,
        date=date.today()
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan_status(db: Session, plan_id: int, tasks: list):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    if plan:
        plan.content = tasks # tasks should have updated status
        db.commit()
        db.refresh(plan)
    return plan

def create_interview_session(db: Session, user_id: int, topic: str):
    session = InterviewSession(user_id=user_id, topic=topic, messages=[])
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def add_message_to_session(db: Session, session_id: int, role: str, content: str):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if session:
        # SQLAlchemy JSON mutations tracking issues, so we copy, append, reassign
        current_msgs = list(session.messages) if session.messages else []
        current_msgs.append({"role": role, "content": content, "timestamp": str(date.today())})
        session.messages = current_msgs
        db.commit()
        db.refresh(session)
    return session

def update_session_feedback(db: Session, session_id: int, score: float, feedback: str):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if session:
        session.score = score
        session.feedback = feedback
        db.commit()
    return session

def get_recent_weaknesses(db: Session, user_id: int, limit: int = 3):
    """
    获取最近 N 场面试中暴露的弱点 (Weaknesses)
    """
    # 获取最近的有反馈的面试记录
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id,
        InterviewSession.feedback.isnot(None)
    ).order_by(InterviewSession.created_at.desc()).limit(limit).all()
    
    weaknesses = []
    for s in sessions:
        try:
            # 这里的 feedback 是 JSON 字符串
            report = json.loads(s.feedback)
            # 提取 weaknesses 列表
            w_list = report.get("weaknesses", [])
            for w in w_list:
                # 简单去重
                val = f"{w} (From: {s.topic})"
                if val not in weaknesses:
                    weaknesses.append(val)
        except:
            continue
            
    return weaknesses

def get_all_finished_sessions(db: Session, user_id: int):
    """获取所有已完成评价的面试"""
    return db.query(InterviewSession).filter(InterviewSession.user_id == user_id, InterviewSession.score.isnot(None)).all()

def get_study_stats(db: Session, user_id: int):
    """计算学习任务完成率"""
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).all()
    total_tasks = 0
    completed_tasks = 0
    for p in plans:
        if p.content:
            for t in p.content:
                total_tasks += 1
                if t.get("status") == "completed":
                    completed_tasks += 1
    
    finished_sessions_count = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id,
        InterviewSession.score.isnot(None)
    ).count()

    return {
        "total_days": len(plans),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "finished_sessions": finished_sessions_count
    }
