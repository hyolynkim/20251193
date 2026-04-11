import csv
import heapq
import os

class BirthdayHeap:
    def __init__(self):
        self.heap = []

    def build_heap_from_csv(self, file_path):
        """CSV 파일을 읽어 최대 힙을 구성합니다."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} 파일이 존재하지 않습니다.")

        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 스킵
            
            for row in reader:
                # 이름, 생년, 생월, 생일 데이터가 모두 있는지 확인
                if len(row) >= 4 and row[1].strip():
                    try:
                        name = row[0]
                        year = int(float(row[1]))
                        month = int(float(row[2]))
                        day = int(float(row[3]))
                        
                        # 생일을 하나의 숫자로 변환 (예: 20061120)
                        # 큰 숫자가 우선순위를 갖도록 마이너스(-)를 붙여 저장
                        birth_value = year * 10000 + month * 100 + day
                        heapq.heappush(self.heap, (-birth_value, name, year, month, day))
                    except (ValueError, IndexError):
                        continue

    def get_top_n(self, n):
        """힙에서 우선순위가 높은(생일이 느린) n명을 추출합니다."""
        results = []
        for _ in range(min(n, len(self.heap))):
            neg_val, name, y, m, d = heapq.heappop(self.heap)
            results.append([name, y, m, d])
        return results
