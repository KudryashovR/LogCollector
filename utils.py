import os
import sys
import tarfile
import host


def initialize_hosts(hostnames_list, hosts_list):
    """
    Инициализирует список хостов на основе предоставленных имен директорий и списка хостов.

    Для каждой директории из списка `hostnames_list` функция проверяет её существование. Если директория существует,
    производится поиск архива `.tgz` в данной директории. Если архив найден, его содержимое извлекается функцией
    `tar_to_dir`.

    Затем считывается дата последнего обновления из файла `last_update`, расположенного в директории. На основе этих
    данных создается объект класса `Host` с соответствующими параметрами.

    Если директория не существует, она создается, и в ней создается файл `last_update` с записанной в него датой
    '1970-01-01'. Также создается объект класса `Host` с датой последнего обновления, соответствующей указанной в файле.

    Параметры:
    - hostnames_list (list): список строк с путями к директориям, с которыми будет производиться работа.
    - hosts_list (list): список строк с именами хостов.

    Возвращает:
    - list: список инициализированных объектов класса `Host`.
    """

    hosts = []

    for index, item in enumerate(hostnames_list):
        if os.path.isdir(item):
            filename = os.listdir(item)[0]

            if ".tgz" in filename:
                tar_to_dir(item)

            with open(os.path.join(item, "last_update")) as file:
                last_update = file.readline().strip()

            hosts.append(host.Host(hosts_list[index], hostnames_list[index], int(last_update[:4]),
                                   int(last_update[5:7]), int(last_update[8:])))
        else:
            os.mkdir(item)

            with open(os.path.join(item, "last_update"), "wt") as file:
                file.write("1970-01-01")

            hosts.append(host.Host(hosts_list[index], hostnames_list[index], 1970, 1, 1))

    return hosts


def read_ip_to_list(filename):
    """
    Считывает IP-адреса и имена хостов из файла в два списка, игнорируя пустые строки и строки, начинающиеся с '#'.

    Функция открывает указанный файл и разделяет каждую строку по символу " - ", предполагая, что каждая строка файла
    содержит IP-адрес, за которым следует имя хоста. Каждый IP-адрес и имя хоста добавляются в отдельные списки.
    Возвращает два списка: список IP-адресов и список имен хостов.

    Если файл не существует, функция заканчивает выполнение программы, выводя сообщение об ошибке с абсолютным путем
    отсутствующего файла.

    Аргументы:
        filename (str): Путь к файлу с IP-адресами и именами хостов.

    Возвращает:
        tuple of list: Возвращает кортеж из двух списков:
                       первый список содержит IP-адреса, а второй - имена хостов.

    Вызывает:
        sys.exit: Завершает выполнение программы с сообщением об ошибке, если файл не существует.
    """

    if os.path.exists(filename):
        ips_list = []
        hostnames_list = []

        with open(filename) as file:
            for line in file:
                if line[0] != '#' or '':
                    ip, hostname = line.strip().split(" - ")
                    ips_list.append(ip)
                    hostnames_list.append(hostname)

        return ips_list, hostnames_list
    else:
        sys.exit(f"Файл {os.path.abspath(filename)} не существует!")


def recursive_sftp_get(sftp, remote_path, local_path):
    """
    Рекурсивно скачивает файлы и директории с удалённого сервера по SFTP.

    Эта функция проходится по всем файлам и поддиректориям в указанной удалённой директории и скачивает их в локальную
    директорию. Если в процессе скачивания обнаруживается, что текущий элемент является директорией, функция создает
    соответствующую поддиректорию в локальной файловой системе и рекурсивно вызывает саму себя для скачивания
    всех содержимых в ней файлов и поддиректорий.

    В случае ошибки `IOError` при попытке скачать файл, считается, что элемент является директорией, и соответственно
    инициируется процесс рекурсивного скачивания.

    Аргументы:
        sftp: Объект SFTP клиента, предоставляемый библиотекой paramiko для выполнения SFTP операций.
        remote_path (str): Путь к удалённой директории на SFTP сервере.
        local_path (str): Путь к локальной директории, куда будут скачены файлы.

    Ничего не возвращает.

    Вызывает:
        IOError: Если возникают проблемы при скачивании файлов.
    """

    files = sftp.listdir(remote_path)

    for file in files:
        remote_file = remote_path + '/' + file
        local_file = local_path + '/' + file

        try:
            sftp.get(remote_file, local_file)
        except IOError:
            os.remove(local_file)
            os.makedirs(local_file)
            recursive_sftp_get(sftp, remote_file, local_file)


def tar_to_dir(dir_name):
    """
    Распаковывает первый архив формата tar.gz из указанной директории.

    Функция находит первый файл в указанной директории и, предполагая, что это архив tar.gz, распаковывает
    его содержимое в текущую рабочую директорию. В случае если директория содержит несколько файлов, будет распакован
    только первый файл из списка, возвращенного функцией `os.listdir`.

    Аргументы:
        dir_name (str): Имя директории, в которой находится архив tar.gz для распаковки.

    Ничего не возвращает.

    Вызывает:
        Ошибки, связанные с работой с файловой системой или распаковкой файла, такие как FileNotFoundError,
        если директория не найдена, или tarfile.ReadError, если файл не является архивом tar.gz.
    """

    filename = os.listdir(dir_name)[0]

    if ".tgz" in filename:
        with tarfile.open(dir_name + "/" + filename, 'r:gz') as tar:
            tar.extractall(".")
