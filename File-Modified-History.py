import os
import json
from datetime import datetime

# 요일을 한글로 변환하기 위한 딕셔너리
weekday_korean = ['월', '화', '수', '목', '금', '토', '일']

# KST 시간으로 변환 및 포맷팅 함수 (YYYY-MM-DD ddd HH:mm:ss 형식, 한글 요일)
def convert_to_kst(timestamp):
    dt = datetime.fromtimestamp(timestamp).astimezone()
    kst_time = dt.strftime('%Y-%m-%d')  # 날짜 포맷
    korean_weekday = weekday_korean[dt.weekday()]  # weekday() -> isoweekday(): ISO 8601 포멧을 사용해 0부터 요일을 한글로 변환
    time_part = dt.strftime('%H:%M:%S')  # 시간 포맷
    return f"{kst_time} {korean_weekday} {time_part}"

# 중첩된 딕셔너리 구조로 파일 및 폴더 정보를 저장하는 함수
def add_to_nested_dict(nested_dict, path_parts, file_info=None):
    current = nested_dict
    for part in path_parts[:-1]:  # 마지막 부분을 제외한 경로만 탐색
        if part not in current:
            current[part] = {}
        current = current[part]
    if file_info:
        current[path_parts[-1]] = file_info

# 특정 경로 내 모든 파일의 정보를 가져오기 위한 함수
def get_file_info(directory, exclude_files=None, exclude_folders=None, exclude_extensions=None):
    file_data = {}
    exclude_files = exclude_files or []
    exclude_folders = exclude_folders or []
    exclude_extensions = exclude_extensions or []

    for root, dirs, files in os.walk(directory):
        # 제외할 폴더를 탐색에서 제외
        dirs[:] = [d for d in dirs if d not in exclude_folders]

        # 폴더와 파일 구분 후 딕셔너리에 추가
        for dir_name in dirs:
            relative_dir_path = os.path.relpath(os.path.join(root, dir_name), directory)
            path_parts = relative_dir_path.split(os.sep)
            add_to_nested_dict(file_data, path_parts)

        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1]  # 확장자 가져오기
            
            # 제외할 파일 또는 확장자 건너뜀
            if file in exclude_files or file_extension in exclude_extensions:
                continue

            # 파일 생성 시간과 수정 시간 정보 가져오기
            creation_time = os.path.getctime(file_path)
            modified_time = os.path.getmtime(file_path)

            # 기존에 수정 시간이 있는지 확인하고 없으면 추가
            if file_path not in file_data:
                # 파일 정보를 딕셔너리로 저장
                file_info = {
                    'Date_of_creation': convert_to_kst(creation_time),
                    'Modified_times': [convert_to_kst(modified_time)],
                    'Last_modified': convert_to_kst(modified_time)
                }
            else:
                # 이전에 기록된 정보가 있으면, 마지막 수정 시간만 갱신
                file_info = file_data[file_path]
                file_info['Modified_times'].append(convert_to_kst(modified_time))  # 새로운 수정 내역 추가
                file_info['Last_modified'] = convert_to_kst(modified_time)  # 마지막 수정 시간 갱신

            # 파일의 경로를 폴더와 파일로 분리하여 중첩된 딕셔너리 구조에 추가
            relative_path = os.path.relpath(file_path, directory)
            path_parts = relative_path.split(os.sep)
            add_to_nested_dict(file_data, path_parts, file_info)
    
    return file_data

# 파일 정보를 JSON에 저장하는 함수
def save_to_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"파일 정보를 '{output_file}'에 저장하였습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

# 사용 예시
directory_path = r"C:\Users\imsan\Documents\Obsidian"  # 경로를 지정하세요
output_file = "File-Modified-History.json"

# 제외할 파일, 폴더 및 확장자 설정
exclude_files = ['ignore_file_name.txt']  # 제외할 파일들
exclude_folders = ['folder1', 'folder2', 'folder3'] # 제외할 폴더들
exclude_extensions = ['.txt', 'png'] # 제외할 확장자들

# 파일 정보 가져오기
file_info = get_file_info(directory_path, exclude_files, exclude_folders, exclude_extensions)

# JSON 파일로 저장
save_to_json(file_info, output_file)
