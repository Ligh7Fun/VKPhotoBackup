import datetime


class Logger:

    def __init__(self, filename: str = 'VKPhotoBackup.log') -> None:
        self.filename = filename

    def log(self, message: str) -> None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_message = f'[{timestamp}] {message}'
        print(log_message)
        with open(self.filename, 'a') as file:
            file.write(log_message + '\n')
