import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from final_complete_system import User, Base

# 데이터베이스 연결
engine = create_engine('sqlite:///final_complete_system.db')
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_admin_accounts():
    db = SessionLocal()
    try:
        # 1. adsketch 계정 확인 및 생성/업데이트
        adsketch = db.query(User).filter(User.username == "adsketch").first()
        if adsketch:
            # 이미 존재하면 비밀번호와 권한 확인
            password_hash = hashlib.sha256("doem1!".encode()).hexdigest()
            adsketch.password_hash = password_hash
            adsketch.role = 'super_admin'
            adsketch.is_active = True
            print("[OK] 'adsketch' 계정이 업데이트되었습니다.")
        else:
            # 새로 생성
            password_hash = hashlib.sha256("doem1!".encode()).hexdigest()
            new_admin = User(
                username="adsketch",
                password_hash=password_hash,
                full_name='시스템 관리자',
                role='super_admin',
                is_active=True
            )
            db.add(new_admin)
            print("[OK] 'adsketch' 관리자 계정이 생성되었습니다.")

        # 2. 기존 admin 계정 삭제
        old_admin = db.query(User).filter(User.username == "admin").first()
        if old_admin:
            db.delete(old_admin)
            print("[OK] 기존 'admin' 계정이 삭제되었습니다.")

        # 3. 다른 테스트 계정들도 확인하고 비활성화
        test_accounts = ["test", "test1", "admin1", "admin123"]
        for username in test_accounts:
            test_user = db.query(User).filter(User.username == username).first()
            if test_user:
                db.delete(test_user)
                print(f"[OK] 테스트 계정 '{username}'이(가) 삭제되었습니다.")

        db.commit()

        print("\n" + "="*50)
        print("관리자 계정 업데이트 완료!")
        print("="*50)
        print("\n새로운 관리자 계정:")
        print("  아이디: adsketch")
        print("  비밀번호: doem1!")
        print("  권한: super_admin")
        print("\n기존 'admin' 계정은 보안상 삭제되었습니다.")

        # 현재 모든 활성 사용자 표시
        print("\n현재 시스템의 모든 활성 사용자:")
        print("-" * 50)
        active_users = db.query(User).filter(User.is_active == True).all()
        for user in active_users:
            print(f"  - {user.username} ({user.role})")

    except Exception as e:
        db.rollback()
        print(f"오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_accounts()