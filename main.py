import os.path
from pythonping import ping
import utils


def main():
    hosts = os.path.join("data", "IPs")
    hosts_list, hostnames_list = utils.read_ip_to_list(hosts)
    hosts_check_list = utils.initialize_hosts(hostnames_list, hosts_list)

    for host in hosts_check_list:
        if host.check_update_log():
            if ping(host.get_ip()).success():
                print(f"Хост {host.get_ip()} доступен. Загрузка лог-файлов.")

                if host.get_host_log():
                    print(f"Лог хоста {host.get_ip()} загружен.")

                    host.set_new_update_day()
                    host.dir_to_tar()
                else:
                    print(f"Лог хоста {host.get_ip()} не загружен.")
            else:
                print(f"Хост {host.get_ip()} не доступен.")
        else:
            print(f"Хосту {host.get_ip()} загрузка лог-файлов не требуется.")

            host.clear_folder()


if __name__ == '__main__':
    main()
