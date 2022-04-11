def pwd_attempt_increase(user):
    user.attempts += 1
    return "Incorrect password."


def clear_attempts(user):
    if user.attempts > 0:
        user.attempts = 0
        return True
