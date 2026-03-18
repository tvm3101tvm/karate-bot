from database import Session, Technique, UserProgress
from datetime import datetime
import random

def get_next_test_technique(user_id):
    """Возвращает технику для теста с учётом интервальных повторений."""
    session = Session()
    all_techs = session.query(Technique).all()
    progresses = {p.technique_id: p for p in session.query(UserProgress).filter_by(user_id=user_id)}
    now = datetime.utcnow()
    weights = []
    for tech in all_techs:
        if tech.id in progresses:
            p = progresses[tech.id]
            last = p.last_shown
            total = p.total_attempts
            correct = p.correct_attempts
            if total == 0:
                error_rate = 1
            else:
                error_rate = (total - correct) / total
            delta = (now - last).total_seconds() / 3600  # часы
            weight = delta * (1 + error_rate)
        else:
            weight = 1000  # техника ни разу не показывалась
        weights.append(weight)
    chosen = random.choices(all_techs, weights=weights, k=1)[0]
    session.close()
    return chosen

def get_recommendations(user_id, limit=3):
    """Возвращает список техник, в которых пользователь чаще всего ошибается."""
    session = Session()
    progresses = session.query(UserProgress).filter_by(user_id=user_id).all()
    recommendations = []
    for p in progresses:
        if p.total_attempts > 0:
            error_rate = (p.total_attempts - p.correct_attempts) / p.total_attempts
            recommendations.append((p.technique_id, error_rate))
    # Сортируем по убыванию ошибок
    recommendations.sort(key=lambda x: x[1], reverse=True)
    tech_ids = [r[0] for r in recommendations[:limit]]
    techs = session.query(Technique).filter(Technique.id.in_(tech_ids)).all()
    session.close()
    return techs