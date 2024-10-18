import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# 파일 수정 이벤트 핸들러 클래스 정의
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, directory, file_data):
        self.directory = directory
        self.file_data = file_data

    # 파일이 수정될 때 호출되는 함수
    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"파일이 수정되었습니다: {file_path}")

            # 수정 시간 가져오기
            modified_time = os.path.getmtime(file_path)
            formatted_time = convert_to_kst(modified_time)

            # 수정 시간을 업데이트하는 로직
            relative_path = os.path.relpath(file_path, self.directory)
            path_parts = relative_path.split(os.sep)

            # 파일이 딕셔너리에 없으면 추가
            if relative_path not in self.file_data:
                self.file_data[relative_path] = {
                    'Date_of_creation': convert_to_kst(os.path.getctime(file_path)),
                    'Modified_times': [formatted_time],
                    'Last_modified': formatted_time
                }
            else:
                # 수정 시간을 추가하고 마지막 수정 시간 갱신
                self.file_data[relative_path]['Modified_times'].append(formatted_time)
                self.file_data[relative_path]['Last_modified'] = formatted_time

            print(f"수정 내역: {self.file_data[relative_path]['Modified_times']}")

# 시간 포맷 변환 함수
def convert_to_kst(timestamp):
    dt = datetime.fromtimestamp(timestamp).astimezone()
    kst_time = dt.strftime('%Y-%m-%d %a %H:%M:%S')
    return kst_time

# 메인 함수
def track_file_changes(directory):
    file_data = {}

    event_handler = FileChangeHandler(directory, file_data)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)  # 하위 디렉토리까지 감지
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    directory_to_watch = "C:/your_directory_path_here"  # 감시할 디렉토리 경로
    track_file_changes(directory_to_watch)
