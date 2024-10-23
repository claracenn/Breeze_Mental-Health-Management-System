
def validate_user_data(data):
    if len(data['username']) < 3:
        raise ValueError("Username must be at least 3 characters long")
    