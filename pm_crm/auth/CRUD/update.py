def pwd_attempt_increase(user):
    user.attempts += 1


def clear_attempts(user):
    user.attempts = 0
