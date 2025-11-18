from app import app, db
from models import Student, Application

with app.app_context():
    # 检查Student模型定义
    print('Student模型student_id字段定义:', Student.student_id)
    print('Student模型student_id是否唯一:', Student.student_id.unique)
    print('数据库连接信息:', app.config['SQLALCHEMY_DATABASE_URI'])
    
    # 检查Application模型的application_type字段
    print('\nApplication模型application_type字段定义:', Application.application_type)
    
    # 尝试查询学生数据
    try:
        students = Student.query.all()[:5]
        print('\n学生数据示例:', [s.student_id for s in students])
    except Exception as e:
        print('\n查询学生数据时出错:', str(e))
        import traceback
        traceback.print_exc()
    
    # 检查数据库中是否仍有performance_detail表
    try:
        result = db.engine.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        tables = [row[0] for row in result]
        print('\n数据库表列表:', tables)
        print('performance_detail表是否存在:', 'performance_detail' in tables)
        print('comprehensive_performance_detail表是否存在:', 'comprehensive_performance_detail' in tables)
    except Exception as e:
        print('\n查询数据库表时出错:', str(e))