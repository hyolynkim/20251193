from heap import BirthdayHeap
import csv
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'birthday.csv')

def run_process():
    # 1. 힙 객체 생성 및 데이터 로드
    bh = BirthdayHeap()
    try:
        bh.build_heap_from_csv(csv_path)
    except Exception as e:
        print(f"오류 발생: {e}")
        return

    # 2. 생일이 느린 순서대로 10명 추출
    top_10 = bh.get_top_n(10)

    # 3. 기존 birthday.csv에 결과 저장 (덮어쓰기)
    if top_10:
        with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['이름', '생년', '생월', '생일'])  # 헤더 작성
            writer.writerows(top_10)
        print(f"생일이 가장 느린 {len(top_10)}명의 데이터가 {csv_path}에 저장되었습니다.")
    else:
        print("추출할 데이터가 없습니다.")

if __name__ == "__main__":
    run_process()