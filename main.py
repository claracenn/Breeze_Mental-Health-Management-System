import json
from controllers.patient import PatientController
from models.user import Patient  # 假设 Patient 类定义在 model.user 模块中
from utils.data_handler import *

# Display the welcome page
def display_welcome_page():
    print()
    print("🍃\033[1m Welcome to Breeze Mental Health System\033[0m 🍃", end='\n\n')
    print("-----------------------------------------------", end='\n\n')
    print(" ⬇️  Please login to continue. ⬇️", end='\n\n')


# Check whether the username and password match
def login(users):
    username = input('Enter username: ')
    password = input('Enter password: ')
    
    
    for user in users:
        if user['username'] == username and user['password'] == password and user['status'] == "ACTIVE":
            role = user['role']
            print(f'\nLogin successful! Welcome, {username}')
            print(f'Role: {role.capitalize()}')
            return role, user  

    print('\nInvalid username or password. Try again.')
    return None, None

def get_patient_info_by_userid(user_id, filename='data/patient_info.json'):
    """根据患者id从 patient_info.json 文件中查找对应信息。"""
    patient_data = read_json(filename)  # 使用前面定义的 read_json 函数加载数据
    
    # 查找匹配的患者信息
    for patient in patient_data:
        if patient['patient_id'] == user_id:
            return patient
    
    print(f"No patient found with userid '{user_id}' in {filename}.")
    return None

# Main function
def main():
    display_welcome_page()
    users = read_json('data/user.json')
    
    if not users:
        print("No users loaded. Exiting program.")
        return

    role, user_info = None, None
    while role is None:
        role, user_info = login(users)

    if role == 'patient':
            # 使用用户名作为外键查找患者详细信息
            patient_info = get_patient_info_by_userid(user_info['user_id'])
            
            if patient_info:
                # 创建 Patient 对象并传递给 PatientController
                patient = Patient(
                    user_id=patient_info['patient_id'],
                    username=user_info['username'],
                    password=user_info['password'],
                    email=patient_info['email'],
                    emergency_contact_email=patient_info['emergency_contact_email'],
                    mhwp_id=patient_info.get('mhwp_id', "")
                )
                patient_controller = PatientController(patient)
                patient_controller.display_patient_homepage()
            else:
                print("Patient information not found.")
    else:
        print(f"Role '{role}' not supported.")

if __name__ == "__main__":
    main()