import os
from datetime import date, datetime, timedelta
import paramiko
import tarfile
import shutil
import utils


class Host:
    """
    Класс для представления хоста с информацией об IP-адресе, имени и дате последнего обновления.

    Атрибуты:
        ip (str): IP-адрес хоста.
        name (str): Имя хоста.
        last_update_date (date): Дата последнего обновления хоста.

    Методы:
        __init__(self, ip, name, year, month, day):
            Инициализирует экземпляр класса с заданными параметрами.

        __repr__(self):
            Возвращает представление объекта класса в виде строки.

        get_ip(self):
            Возвращает IP-адрес хоста.

        check_update_log(self):
            Проверяет, прошло ли более трех месяцев с последнего обновления хоста.

        set_new_update_day(self):
            Обновляет информацию о последней дате обновления в файле на хосте.

        get_host_log(self):
            Скачивает логи с хоста используя SSH и SFTP.

        dir_to_tar(self):
            Архивирует содержимое директории хоста в файл tar.gz с текущей датой.

        clear_folder(self):
            Очищает директорию хоста от всех файлов, кроме архивов tar.gz.

    Пример использования:
        host = Host('192.168.1.1', 'server01', 2023, 3, 25)
        if host.check_update_log():
            print("Требуется обновление!")
        else:
            print("Обновление не требуется.")
    """

    def __init__(self, ip, name, year, month, day):
        self.ip = ip
        self.name = name
        self.last_update_date = date(year, month, day)

    def __repr__(self):
        return f"{self.ip}\n{self.name}\n{self.last_update_date}\n"

    def get_ip(self):
        return self.ip

    def check_update_log(self):
        current_date = datetime.now().date()
        difference = current_date - self.last_update_date
        three_months = timedelta(days=3 * 30)

        return difference > three_months

    def set_new_update_day(self):
        current_date = datetime.now().date()
        formatted_date = current_date.strftime("%Y-%m-%d")

        with open(self.name + "/last_update", "wt") as file:
            file.write(formatted_date)

    def get_host_log(self):
        host = self.ip
        port = 22

        user = input(f"Введите имя пользователя локального администратора для хоста {self.name}: ")
        secret = input(f"Введите пароль для учетной записи {user} хоста {self.name}: ")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, user, secret)
        sftp = ssh.open_sftp()

        remote_path = '/var/log'
        local_path = self.name

        utils.recursive_sftp_get(sftp, remote_path, local_path)
        return 1

    def dir_to_tar(self):
        current_date = datetime.now().date()
        formatted_date = current_date.strftime("%Y_%m")

        with tarfile.open(self.name + "/" + formatted_date + ".tgz", "w:gz") as tar:
            tar.add(self.name)

        files = os.listdir(self.name)
        files.remove(formatted_date + ".tgz")

        for file in files:
            os.remove(self.name + "/" + file) if os.path.isfile(self.name + "/" + file) else shutil.rmtree(self.name +
                                                                                                           "/" + file)

    def clear_folder(self):
        files = [file for file in os.listdir(self.name) if ".tgz" not in file]

        for file in files:
            os.remove(self.name + "/" + file) if os.path.isfile(self.name + "/" + file) else shutil.rmtree(self.name +
                                                                                                           "/" + file)
