from app import app, db
from models import Application

with app.app_context():
    # 打印Application模型的所有字段
    print('Application模型字段:')
    for c in Application.__table__.columns:
        print(f'  {c.name}: {c.type}')
    
    # 特别检查关键字段
    print('\n关键字段验证:')
    try:
        print('student_id字段:', Application.student_id)
    except Exception as e:
        print('student_id字段错误:', str(e))
    
    try:
        print('title字段:', Application.title)
    except Exception as e:
        print('title字段错误:', str(e))
    
    try:
        print('application_type字段:', Application.application_type)
    except Exception as e:
        print('application_type字段错误:', str(e))
    
    try:
        print('status字段:', Application.status)
    except Exception as e:
        print('status字段错误:', str(e))
    
    try:
        print('final_score字段:', Application.final_score)
    except Exception as e:
        print('final_score字段错误:', str(e))
    
    # 尝试执行一个简单的查询
    try:
        sample = Application.query.first()
        if sample:
            print('\n示例数据:')
            print(f'  student_id: {sample.student_id}')
            print(f'  title: {sample.title}')
            print(f'  application_type: {sample.application_type}')
            print(f'  status: {sample.status}')
    except Exception as e:
        print('\n查询示例数据错误:', str(e))
        import traceback
        traceback.print_exc()