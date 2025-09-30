import sys
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from final_complete_system import User, Base

# 데이터베이스 연결
engine = create_engine('sqlite:///final_complete_system.db')
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin_user(username, password):
    db = SessionLocal()
    try:
        # 기존 사용자 확인
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"사용자 '{username}'가 이미 존재합니다.")
            # 비밀번호 업데이트
            response = input("비밀번호를 업데이트하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                existing.password_hash = password_hash
                existing.role = 'super_admin'
                existing.is_active = True
                db.commit()
                print(f"사용자 '{username}'의 비밀번호가 업데이트되었습니다.")
            return

        # 새 관리자 생성
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        admin = User(
            username=username,
            password_hash=password_hash,
            full_name='관리자',
            role='super_admin',
            is_active=True
        )

        db.add(admin)
        db.commit()
        print(f"관리자 계정이 생성되었습니다:")
        print(f"  아이디: {username}")
        print(f"  비밀번호: {password}")
        print(f"  권한: super_admin")

    except Exception as e:
        db.rollback()
        print(f"오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    # 새로운 관리자 계정 생성
    create_admin_user("adsketch", "doem1!")

    # 기존 관리자 계정도 유지
    create_admin_user("admin", "admin123")