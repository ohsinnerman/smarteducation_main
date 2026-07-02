
def generate_student_insight(student_data):
    """Generate AI insight for a student (fallback without OpenAI)."""
    name = student_data.get('name', 'Student')
    attendance = student_data.get('attendance', 0)
    marks = student_data.get('marks', 0)
    
    insights = []
    
    # Performance summary
    if marks >= 80:
        insights.append(f"1. Performance Summary: {name} is performing excellently with strong academic performance.")
    elif marks >= 60:
        insights.append(f"1. Performance Summary: {name} is making satisfactory progress.")
    else:
        insights.append(f"1. Performance Summary: {name} needs significant improvement in academics.")
    
    # Attendance note
    if attendance >= 80:
        insights.append("2. Strengths: Excellent attendance, showing commitment to learning.")
    elif attendance >= 60:
        insights.append("2. Strengths: Regular attendance with some room for improvement.")
    else:
        insights.append("2. Areas for Improvement: Attendance needs immediate attention.")
    
    # Recommendations
    insights.append("3. Recommendations:")
    if marks < 70:
        insights.append("   - Focus on understanding core concepts through additional practice")
    if attendance < 75:
        insights.append("   - Improve attendance by attending all classes regularly")
    insights.append("   - Set clear, achievable weekly study goals")
    insights.append("   - Regular self-assessment quizzes")
    
    return '\n'.join(insights)


def generate_at_risk_intervention(student_data):
    """Generate intervention suggestions for at-risk students."""
    name = student_data.get('name', 'Student')
    return f"""
Intervention suggestions for {name}:
1. Schedule weekly one-on-one check-ins with teachers
2. Develop personalized study schedule
3. Attendance monitoring and incentives
4. Peer tutoring program
5. Regular feedback and progress tracking
    """.strip()
